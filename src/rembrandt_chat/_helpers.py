"""Shared handler helpers and user-data keys."""

from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

from rembrandt import Database, Session, User
from rembrandt.models import ConceptTranslation
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, ConversationHandler

from rembrandt_chat.formatting import format_exercise, format_summary
from rembrandt_chat.user_mapping import UserMapper

# Keys used in context.user_data
SESSION = "session"
EXERCISE = "exercise"
LANGUAGE = "language"
TRANSLATION = "translation"
TRANSLATION_MAP = "_translation_map"

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


# Type alias for conversation handler functions
_ConvHandler = Callable[
    [Update, ContextTypes.DEFAULT_TYPE],
    Coroutine[Any, Any, int],
]


def require_message_conv(
    func: _ConvHandler,
) -> _ConvHandler:
    """Like `require_message` but returns
    ``ConversationHandler.END`` for conversation handlers.
    """

    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> int:
        if (
            update.effective_user is None
            or update.message is None
        ):
            return ConversationHandler.END
        return await func(update, context)

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
) -> tuple[User, Database]:
    """Return the rembrandt user and database from context.

    Ensures the Telegram user is registered.
    """
    mapper: UserMapper = context.bot_data["user_mapper"]
    user = await mapper.ensure_user(update.effective_user)
    db: Database = context.bot_data["db"]
    return user, db


async def resolve_user_with_typing(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[User, Database]:
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


async def _lookup_translation(
    db: Database,
    concept_id: int,
    lang: str | None,
) -> ConceptTranslation | None:
    """Fetch a concept translation for the given language.

    Returns ``None`` when no language is set or no
    translation exists.
    """
    if not lang:
        return None
    return await db.get_translation(concept_id, lang)


async def send_next(
    session: Session,
    user_data: dict,
    update: Update,
    db: Database | None = None,
) -> None:
    """Advance to the next exercise or end the session.

    :param db: Database for translation lookups.  Required
        when the user has a language set.
    """
    exercise = await session.next_exercise()
    if exercise is None:
        summary = session.summary()
        user_data.pop(SESSION, None)
        user_data.pop(EXERCISE, None)
        user_data.pop(TRANSLATION, None)
        chat = update.effective_chat
        if chat is not None:
            await chat.send_message(format_summary(summary))
        return

    user_data[EXERCISE] = exercise
    lang = user_data.get(LANGUAGE)
    translation = None
    if db and lang:
        translation = await _lookup_translation(
            db, exercise.concept.id, lang
        )
    user_data[TRANSLATION] = translation
    tr_map = user_data.get(TRANSLATION_MAP)
    text, keyboard = format_exercise(
        exercise, translation=translation, tr_map=tr_map
    )
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(text, reply_markup=keyboard)
