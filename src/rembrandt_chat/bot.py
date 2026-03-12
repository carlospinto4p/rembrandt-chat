"""Bot application factory and entry point."""

import logging

from rembrandt import PostgresDatabase, import_words_csv
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from rembrandt_chat.config import (
    LANG_FROM,
    LANG_TO,
    get_base_vocab_path,
    get_bot_token,
    get_database_url,
)
from rembrandt_chat.formatting import DEL_CB_PREFIX, LESSON_CB_PREFIX
from rembrandt_chat.handlers import (
    AWAITING_DEFINITION,
    AWAITING_WORD,
    PLAY_MODE_PREFIX,
    addword_cancel,
    addword_definition,
    addword_start,
    addword_word,
    deleteword,
    AWAITING_FILE,
    export_progress,
    forecast,
    handle_answer_callback,
    handle_answer_text,
    handle_deleteword_callback,
    handle_lesson_callback,
    handle_play_mode,
    hint,
    import_cancel,
    import_file,
    import_start,
    lessons,
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


async def _load_base_vocab(db: PostgresDatabase) -> None:
    """Import shared vocabulary on first run if configured."""
    path = get_base_vocab_path()
    if path is None:
        return
    existing = await db.get_words(LANG_FROM, LANG_TO)
    if existing:
        return
    words = await import_words_csv(db, path, LANG_FROM, LANG_TO)
    log.info("Loaded %d base vocabulary words from %s", len(words), path)


async def _post_init(app) -> None:
    """Connect to the database after the application starts."""
    db = await PostgresDatabase.connect(get_database_url())
    await _load_base_vocab(db)
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
    app.add_handler(CommandHandler("lessons", lessons))
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
            handle_lesson_callback,
            pattern=f"^{LESSON_CB_PREFIX}",
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
