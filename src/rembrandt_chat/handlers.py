"""Telegram command handlers."""

from telegram import Update
from telegram.ext import ContextTypes

from rembrandt_chat.user_mapping import UserMapper


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/start` — greet the user and auto-register if new.

    :param update: Incoming Telegram update.
    :param context: Callback context (must carry ``bot_data["user_mapper"]``).
    """
    if update.effective_user is None or update.message is None:
        return

    mapper: UserMapper = context.bot_data["user_mapper"]
    user = mapper.ensure_user(update.effective_user)

    name = user.display_name or user.username
    await update.message.reply_text(
        f"Welcome, {name}!\n\n"
        "Use /play to start an exercise session."
    )
