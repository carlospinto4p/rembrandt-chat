"""Bot application factory and entry point."""

from rembrandt import PostgresDatabase
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from rembrandt_chat.config import get_bot_token, get_database_url
from rembrandt_chat.handlers import (
    handle_answer_callback,
    handle_answer_text,
    hint,
    play,
    skip,
    start,
    stop,
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
