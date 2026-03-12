"""Shared handler helpers and user-data keys."""

from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

from rembrandt import PostgresDatabase, Session, User
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from rembrandt_chat.formatting import format_exercise, format_summary
from rembrandt_chat.user_mapping import UserMapper

# Keys used in context.user_data
SESSION = "session"
EXERCISE = "exercise"

# Type alias for handler functions
_Handler = Callable[
    [Update, ContextTypes.DEFAULT_TYPE],
    Coroutine[Any, Any, None],
]


def require_message(func: _Handler) -> _Handler:
    """Decorator that skips the handler when
    ``effective_user`` or ``message`` is missing.
    """

    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if (
            update.effective_user is None
            or update.message is None
        ):
            return
        await func(update, context)

    return wrapper


def require_callback(
    func: _Handler,
) -> _Handler:
    """Decorator that skips the handler when
    ``callback_query`` is missing, and auto-acknowledges it.
    """

    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        query = update.callback_query
        if query is None:
            return
        await query.answer()
        await func(update, context)

    return wrapper


async def send_typing(update: Update) -> None:
    """Send a typing indicator to the user's chat.

    :param update: The incoming Telegram update.
    """
    chat = update.effective_chat
    if chat is not None:
        await chat.send_action(ChatAction.TYPING)


async def resolve_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[User, PostgresDatabase]:
    """Return the rembrandt user and database from context.

    Ensures the Telegram user is registered.
    """
    mapper: UserMapper = context.bot_data["user_mapper"]
    user = await mapper.ensure_user(update.effective_user)
    db: PostgresDatabase = context.bot_data["db"]
    return user, db


async def resolve_user_with_typing(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[User, PostgresDatabase]:
    """Send a typing indicator, then resolve the user."""
    await send_typing(update)
    return await resolve_user(update, context)


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
    exercise = await session.next_exercise()
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
