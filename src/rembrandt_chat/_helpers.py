"""Shared handler helpers and user-data keys."""

from rembrandt import PostgresDatabase, Session, User
from telegram import Update
from telegram.ext import ContextTypes

from rembrandt_chat.formatting import format_exercise, format_summary
from rembrandt_chat.user_mapping import UserMapper

# Keys used in context.user_data
SESSION = "session"
EXERCISE = "exercise"


def resolve_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[User, PostgresDatabase]:
    """Return the rembrandt user and database from context.

    Ensures the Telegram user is registered.
    """
    mapper: UserMapper = context.bot_data["user_mapper"]
    user = mapper.ensure_user(update.effective_user)
    db: PostgresDatabase = context.bot_data["db"]
    return user, db


def get_session(
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[Session | None, dict]:
    """Return the active session and user_data dict."""
    user_data = context.user_data
    session: Session | None = user_data.get(SESSION)
    return session, user_data


def require_session(
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[Session, dict] | None:
    """Return ``(session, user_data)`` if both session and
    exercise are active, otherwise ``None``.
    """
    session, user_data = get_session(context)
    if session is None:
        return None
    if user_data.get(EXERCISE) is None:
        return None
    return session, user_data


async def send_next(
    session: Session,
    user_data: dict,
    update: Update,
) -> None:
    """Advance to the next exercise or end the session."""
    exercise = session.next_exercise()
    if exercise is None:
        summary = session.summary()
        user_data.pop(SESSION, None)
        user_data.pop(EXERCISE, None)
        chat = update.effective_chat
        if chat is not None:
            await chat.send_message(format_summary(summary))
        return

    user_data[EXERCISE] = exercise
    text, keyboard = format_exercise(exercise)
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(text, reply_markup=keyboard)
