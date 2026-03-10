"""Bot application factory and entry point."""

from rembrandt import PostgresDatabase
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from rembrandt_chat.config import get_bot_token, get_database_url
from rembrandt_chat.handlers import (
    AWAITING_DEFINITION,
    AWAITING_WORD,
    DEL_CB_PREFIX,
    addword_cancel,
    addword_definition,
    addword_start,
    addword_word,
    deleteword,
    handle_answer_callback,
    handle_answer_text,
    handle_deleteword_callback,
    hint,
    mywords,
    play,
    skip,
    start,
    stats,
    stop,
    weak,
)
from rembrandt_chat.user_mapping import UserMapper


def create_app() -> None:
    """Build and run the Telegram bot application."""
    db = PostgresDatabase(get_database_url())
    mapper = UserMapper(db)

    app = (
        ApplicationBuilder()
        .token(get_bot_token())
        .build()
    )
    app.bot_data["user_mapper"] = mapper
    app.bot_data["db"] = db

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("hint", hint))
    app.add_handler(CommandHandler("skip", skip))
    app.add_handler(CommandHandler("mywords", mywords))
    app.add_handler(CommandHandler("deleteword", deleteword))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("weak", weak))

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
