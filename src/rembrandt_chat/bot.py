"""Bot application factory and entry point."""

import logging

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

from rembrandt import Database, import_concepts_csv
from rembrandt.topics import load_topics
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from rembrandt_chat.config import (
    get_base_vocab_path,
    get_bot_token,
    get_bundled_vocab_dir,
    get_database_path,
)
from rembrandt_chat.formatting import DEL_CB_PREFIX, TOPIC_CB_PREFIX
from rembrandt_chat.handlers import (
    AWAITING_DEFINITION,
    AWAITING_FILE,
    AWAITING_TAGS,
    AWAITING_WORD,
    PLAY_MODE_PREFIX,
    addword_cancel,
    addword_definition,
    addword_skip_tags,
    addword_start,
    addword_tags,
    addword_word,
    deleteword,
    export_progress,
    forecast,
    handle_answer_callback,
    handle_answer_text,
    handle_deleteword_callback,
    handle_topic_callback,
    handle_play_mode,
    hint,
    history,
    import_cancel,
    import_file,
    import_start,
    topics,
    mywords,
    play,
    retention,
    skip,
    start,
    stats,
    stop,
    weak,
)
from rembrandt_chat.user_mapping import UserMapper


log = logging.getLogger(__name__)


async def _load_base_vocab(db: Database) -> None:
    """Import shared vocabulary on first run if configured."""
    path = get_base_vocab_path()
    if path is None:
        return
    existing = await db.get_concepts()
    if existing:
        return
    concepts = await import_concepts_csv(db, path)
    log.info(
        "Loaded %d base vocabulary words from %s",
        len(concepts), path,
    )


async def _load_bundled_topics(db: Database) -> None:
    """Load bundled vocabulary and topics on first run."""
    d = Path(get_bundled_vocab_dir())
    vocab_csv = d / "vocab.csv"
    topics_json = d / "topics.json"
    if not vocab_csv.exists() or not topics_json.exists():
        return
    existing = await db.get_concepts()
    if existing:
        return
    concepts = await import_concepts_csv(db, str(vocab_csv))
    log.info("Loaded %d bundled vocabulary words", len(concepts))
    loaded = await load_topics(topics_json, db)
    log.info("Loaded %d bundled topics", len(loaded))


async def _post_init(app) -> None:
    """Connect to the database after the application starts."""
    db = await Database.connect(get_database_path())
    try:
        await db._conn.execute("PRAGMA journal_mode=WAL")
    except Exception:
        log.warning("Could not enable WAL mode")
    await _load_base_vocab(db)
    await _load_bundled_topics(db)
    mapper = UserMapper(db)
    app.bot_data["user_mapper"] = mapper
    app.bot_data["db"] = db


def create_app() -> None:
    """Build and run the Telegram bot application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    app = (
        ApplicationBuilder()
        .token(get_bot_token())
        .post_init(_post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("hint", hint))
    app.add_handler(CommandHandler("skip", skip))
    app.add_handler(CommandHandler("mywords", mywords))
    app.add_handler(CommandHandler("deleteword", deleteword))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("weak", weak))
    app.add_handler(CommandHandler("forecast", forecast))
    app.add_handler(CommandHandler("retention", retention))
    app.add_handler(CommandHandler("topics", topics))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("export", export_progress))

    import_conv = ConversationHandler(
        entry_points=[
            CommandHandler("import", import_start),
        ],
        states={
            AWAITING_FILE: [
                MessageHandler(
                    filters.Document.ALL,
                    import_file,
                ),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", import_cancel),
        ],
    )
    app.add_handler(import_conv)

    addword_conv = ConversationHandler(
        entry_points=[
            CommandHandler("addword", addword_start),
        ],
        states={
            AWAITING_WORD: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    addword_word,
                ),
            ],
            AWAITING_DEFINITION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    addword_definition,
                ),
            ],
            AWAITING_TAGS: [
                CommandHandler("skip", addword_skip_tags),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    addword_tags,
                ),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", addword_cancel),
        ],
    )
    app.add_handler(addword_conv)

    app.add_handler(
        CallbackQueryHandler(
            handle_play_mode,
            pattern=f"^{PLAY_MODE_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_topic_callback,
            pattern=f"^{TOPIC_CB_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_deleteword_callback,
            pattern=f"^{DEL_CB_PREFIX}",
        )
    )
    app.add_handler(CallbackQueryHandler(handle_answer_callback))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_answer_text,
        )
    )

    app.run_polling()


if __name__ == "__main__":
    create_app()
