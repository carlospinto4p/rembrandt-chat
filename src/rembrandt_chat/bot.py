"""Bot application factory and entry point."""

from rembrandt import PostgresDatabase
from telegram.ext import ApplicationBuilder, CommandHandler

from rembrandt_chat.config import get_bot_token, get_database_url
from rembrandt_chat.handlers import start
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

    app.add_handler(CommandHandler("start", start))

    app.run_polling()


if __name__ == "__main__":
    create_app()
