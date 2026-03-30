"""Bot application factory and entry point."""

import logging

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

from rembrandt import Database, import_concepts_csv
from rembrandt.topics import load_topics
from telegram import BotCommand, Update
from telegram.ext import (
    ContextTypes,
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
    get_state_path,
)
from rembrandt_chat.formatting import (
    CAT_CB_PREFIX,
    DEL_CANCEL_CB,
    DEL_CB_PREFIX,
    DEL_CONFIRM_PREFIX,
    LANG_CB_PREFIX,
    PLAY_TPAGE_PREFIX,
    TOPIC_CB_PREFIX,
    TPAGE_PREFIX,
)
from rembrandt_chat.handlers import (
    AWAITING_BULK_FILE,
    AWAITING_DEFINITION,
    AWAITING_FILE,
    AWAITING_TAGS,
    AWAITING_WORD,
    PLAY_BACK_PREFIX,
    PLAY_CAT_PREFIX,
    PLAY_LANG_PREFIX,
    PLAY_MODE_PREFIX,
    PLAY_TOPIC_PREFIX,
    addword_cancel,
    bulkimport_cancel,
    bulkimport_file,
    bulkimport_start,
    cancel,
    addword_definition,
    addword_skip_tags,
    addword_start,
    addword_tags,
    addword_word,
    deleteword,
    export_progress,
    forecast,
    help_command,
    handle_answer_callback,
    handle_answer_text,
    handle_category_callback,
    handle_deleteword_callback,
    handle_deleteword_cancel,
    handle_deleteword_confirm,
    handle_language_callback,
    handle_play_back,
    handle_play_category,
    handle_play_language,
    handle_play_topic,
    handle_play_topic_page,
    handle_topic_callback,
    handle_topic_page,
    handle_play_mode,
    hint,
    history,
    import_cancel,
    import_file,
    import_start,
    language,
    reminders,
    topics,
    mywords,
    play,
    retention,
    review,
    search,
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


async def _register_default_languages(
    db: Database,
) -> None:
    """Register Spanish and English if not yet present."""
    existing = await db.get_languages()
    codes = {lang.code for lang in existing}
    if "es" not in codes:
        await db.add_language("es", "Spanish")
        log.info("Registered language: Spanish (es)")
    if "en" not in codes:
        await db.add_language("en", "English")
        log.info("Registered language: English (en)")


_BOT_COMMANDS = [
    BotCommand("play", "Start an exercise session"),
    BotCommand("review", "Quick review of last topic"),
    BotCommand("stop", "End session and show summary"),
    BotCommand("hint", "Get a hint"),
    BotCommand("skip", "Skip the current exercise"),
    BotCommand("language", "Set preferred language"),
    BotCommand("topics", "Browse topics by category"),
    BotCommand("addword", "Add a new word"),
    BotCommand("mywords", "List your words"),
    BotCommand("deleteword", "Delete one of your words"),
    BotCommand("search", "Search vocabulary"),
    BotCommand("bulkimport", "Import words from file"),
    BotCommand("stats", "Show daily stats"),
    BotCommand("weak", "Show your weakest words"),
    BotCommand("forecast", "Review workload (7 days)"),
    BotCommand("retention", "Retention rate (30 days)"),
    BotCommand("history", "Recent answer history"),
    BotCommand("export", "Export progress as JSON"),
    BotCommand("import", "Import progress from JSON"),
    BotCommand("reminders", "Daily review reminders"),
    BotCommand("cancel", "Cancel current operation"),
    BotCommand("help", "List all commands"),
]


async def _post_init(app) -> None:
    """Connect to the database after the application starts."""
    await app.bot.set_my_commands(_BOT_COMMANDS)
    db = await Database.connect(get_database_path())
    try:
        await db._conn.execute("PRAGMA journal_mode=WAL")
    except Exception:
        log.warning("Could not enable WAL mode")
    await _load_base_vocab(db)
    await _load_bundled_topics(db)
    await _register_default_languages(db)
    mapper = UserMapper(db)
    app.bot_data["user_mapper"] = mapper
    app.bot_data["db"] = db
    app.bot_data["state_path"] = Path(get_state_path())


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
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("review", review))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("hint", hint))
    app.add_handler(CommandHandler("skip", skip))
    app.add_handler(CommandHandler("mywords", mywords))
    app.add_handler(CommandHandler("deleteword", deleteword))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("weak", weak))
    app.add_handler(CommandHandler("forecast", forecast))
    app.add_handler(CommandHandler("retention", retention))
    app.add_handler(CommandHandler("topics", topics))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("language", language))
    app.add_handler(CommandHandler("export", export_progress))
    app.add_handler(CommandHandler("reminders", reminders))

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

    bulkimport_conv = ConversationHandler(
        entry_points=[
            CommandHandler("bulkimport", bulkimport_start),
        ],
        states={
            AWAITING_BULK_FILE: [
                MessageHandler(
                    filters.Document.ALL,
                    bulkimport_file,
                ),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", bulkimport_cancel),
        ],
    )
    app.add_handler(bulkimport_conv)

    # Global /cancel — must be after conversation handlers
    # so their fallbacks take priority.
    app.add_handler(CommandHandler("cancel", cancel))

    app.add_handler(
        CallbackQueryHandler(
            handle_play_language,
            pattern=f"^{PLAY_LANG_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_play_category,
            pattern=f"^{PLAY_CAT_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_play_topic,
            pattern=f"^{PLAY_TOPIC_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_play_topic_page,
            pattern=f"^{PLAY_TPAGE_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_play_mode,
            pattern=f"^{PLAY_MODE_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_play_back,
            pattern=f"^{PLAY_BACK_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_language_callback,
            pattern=f"^{LANG_CB_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_category_callback,
            pattern=f"^{CAT_CB_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_topic_page,
            pattern=f"^{TPAGE_PREFIX}",
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
    app.add_handler(
        CallbackQueryHandler(
            handle_deleteword_confirm,
            pattern=f"^{DEL_CONFIRM_PREFIX}",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_deleteword_cancel,
            pattern=f"^{DEL_CANCEL_CB}$",
        )
    )
    app.add_handler(CallbackQueryHandler(handle_answer_callback))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_answer_text,
        )
    )

    app.add_error_handler(_error_handler)
    app.run_polling()


async def _error_handler(
    update: object, context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Log the error and notify the user."""
    log.error(
        "Unhandled exception while processing an update",
        exc_info=context.error,
    )
    if not isinstance(update, Update):
        return
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(
            "Something went wrong. Please try again."
        )


if __name__ == "__main__":
    create_app()
