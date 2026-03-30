"""Shared handler helpers and user-data keys."""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from functools import wraps
from pathlib import Path
from typing import Any

from rembrandt import Database, ReviewConfig, Session, User, topic_progress
from rembrandt.models import (
    ConceptTranslation,
    SessionMode,
    Topic,
    TopicProgress,
)
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, ConversationHandler

from rembrandt_chat.config import (
    get_max_new_cards,
    get_max_review_cards,
)
from rembrandt_chat.formatting import format_exercise, format_summary
from rembrandt_chat.i18n import t
from rembrandt_chat.persistence import (
    SESSION_CONFIG,
    clear_session_config,
    load_user_state,
    save_user_state,
)
from rembrandt_chat.user_mapping import UserMapper

from rembrandt_chat.topic_translations import Category, get_category

log = logging.getLogger(__name__)

# Keys used in context.user_data
SESSION = "session"
EXERCISE = "exercise"
LANGUAGE = "language"
TRANSLATION = "translation"
TRANSLATION_MAP = "_translation_map"
LAST_TOPIC = "_last_topic"


def get_lang(
    context: ContextTypes.DEFAULT_TYPE,
) -> str | None:
    """Return the user's language code from user_data."""
    return context.user_data.get(LANGUAGE)


def cleanup_session(user_data: dict) -> None:
    """Remove all session-related keys from user_data."""
    user_data.pop(SESSION, None)
    user_data.pop(EXERCISE, None)
    user_data.pop(TRANSLATION, None)
    user_data.pop(TRANSLATION_MAP, None)
    user_data.pop(SESSION_CONFIG, None)


def extract_command_arg(
    message_text: str | None,
) -> str:
    """Extract the first argument after a ``/command``.

    :param message_text: Raw message text.
    :return: The argument string, or ``""`` if absent.
    """
    text = (message_text or "").strip()
    parts = text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""


async def require_category(
    query: object,
    cat_key: str,
    lang: str | None,
) -> Category | None:
    """Look up a category or send an error message.

    :param query: The callback query to respond on.
    :param cat_key: Category key string.
    :param lang: User language code.
    :return: The `Category`, or ``None`` if not found.
    """
    cat = get_category(cat_key)
    if cat is None:
        await query.edit_message_text(
            t("category_not_found", lang)
        )
    return cat

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


CONVERSATION_TIMEOUT = 300  # 5 minutes


async def conversation_timeout(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Notify user when a conversation times out."""
    lang = get_lang(context)
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(
            t("conversation_timeout", lang)
        )
    return ConversationHandler.END


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

    Ensures the Telegram user is registered.  On the first
    call after a restart, restores persisted language
    preference from the state file.
    """
    mapper: UserMapper = context.bot_data["user_mapper"]
    user = await mapper.ensure_user(update.effective_user)
    db: Database = context.bot_data["db"]

    _restore_user_state(update, context)
    return user, db


def _restore_user_state(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Restore persisted language and last topic."""
    user_data = context.user_data
    if user_data.get("_state_restored"):
        return
    user_data["_state_restored"] = True
    state_path: Path | None = context.bot_data.get(
        "state_path"
    )
    if state_path is None:
        return
    tg_id = update.effective_user.id
    state = load_user_state(state_path, tg_id)
    if LANGUAGE not in user_data:
        lang = state.get(LANGUAGE)
        if lang:
            user_data[LANGUAGE] = lang
    if LAST_TOPIC not in user_data:
        lt = state.get(LAST_TOPIC)
        if lt:
            user_data[LAST_TOPIC] = lt


async def resolve_user_with_typing(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[User, Database]:
    """Send a typing indicator, then resolve the user."""
    await send_typing(update)
    return await resolve_user(update, context)


async def check_active_session(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Send an error and return ``True`` if a session exists.

    Works for both message and callback-query updates.
    """
    user_data = context.user_data
    if user_data.get(SESSION) is None:
        return False

    lang = user_data.get(LANGUAGE)
    msg = t("active_session", lang)
    query = update.callback_query
    if query is not None:
        await query.edit_message_text(msg)
    elif update.message is not None:
        await update.message.reply_text(msg)
    return True


def get_session(
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[Session | None, dict]:
    """Return the active session and user_data dict."""
    user_data = context.user_data
    session: Session | None = user_data.get(SESSION)
    return session, user_data


async def require_session(
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[Session, dict] | None:
    """Return ``(session, user_data)`` if both session and
    exercise are active, otherwise ``None``.

    If the in-memory session is gone but a persisted
    `SESSION_CONFIG` exists (e.g. after a restart),
    the session is silently recreated.
    """
    session, user_data = get_session(context)
    if session is not None and user_data.get(EXERCISE):
        return session, user_data

    # Try to restore from persisted config
    config = user_data.get(SESSION_CONFIG)
    if config is None:
        return None

    db: Database = context.bot_data["db"]
    review_cfg = _build_review_config()
    session = Session(
        db=db,
        user_id=config["user_id"],
        mode=SessionMode(config["mode"]),
        concept_ids=config.get("concept_ids"),
        review_config=review_cfg,
    )
    user_data[SESSION] = session

    exercise = await session.next_exercise()
    if exercise is None:
        user_data.pop(SESSION, None)
        user_data.pop(SESSION_CONFIG, None)
        state_path = context.bot_data.get("state_path")
        if state_path:
            tg_id = config.get("tg_id", 0)
            clear_session_config(state_path, tg_id)
        return None

    user_data[EXERCISE] = exercise
    await setup_translations(user_data, db, exercise)

    log.info("Restored session from persisted config")
    return session, user_data


def _build_review_config() -> ReviewConfig | None:
    """Build a `ReviewConfig` from env vars, or ``None``."""
    new = get_max_new_cards()
    rev = get_max_review_cards()
    if new == 0 and rev == 0:
        return None
    return ReviewConfig(
        max_new_cards=new,
        max_review_cards=rev,
    )


async def setup_translations(
    user_data: dict,
    db: Database,
    exercise: 'Exercise',
) -> None:
    """Load and cache translations for the current exercise.

    Sets ``TRANSLATION`` and ``TRANSLATION_MAP`` in
    *user_data* when the user has a language preference.
    """
    lang = user_data.get(LANGUAGE)
    translation = None
    tr_map = None
    if lang:
        translation = await _lookup_translation(
            db, exercise.concept.id, lang
        )
        tr_map = await _build_translation_map(db, lang)
        user_data[TRANSLATION_MAP] = tr_map
    user_data[TRANSLATION] = translation


async def get_category_topics(
    db: Database,
    user_id: int,
    topic_ids: list[int],
) -> tuple[list[Topic], list[TopicProgress]]:
    """Fetch topics in a category with user progress.

    :param topic_ids: IDs of topics belonging to the category.
    :return: ``(topics, progress)`` lists in matching order.
    """
    all_topics = await db.get_topics()
    filtered = [
        t for t in all_topics if t.id in topic_ids
    ]
    progress = await asyncio.gather(
        *(
            topic_progress(db, user_id, t)
            for t in filtered
        )
    )
    return filtered, list(progress)


async def _build_translation_map(
    db: Database,
    lang: str,
) -> dict[str, str]:
    """Map native concept text to translated text."""
    concepts = await db.get_concepts()
    translations = await asyncio.gather(
        *(
            db.get_translation(c.id, lang)
            for c in concepts
        )
    )
    tr_map: dict[str, str] = {}
    for concept, tr in zip(concepts, translations):
        if tr is not None:
            tr_map[concept.front] = tr.front
            tr_map[concept.back] = tr.back
    return tr_map


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
    *,
    context: ContextTypes.DEFAULT_TYPE | None = None,
) -> None:
    """Advance to the next exercise or end the session.

    :param db: Database for translation lookups.  Required
        when the user has a language set.
    :param context: Used to clear persisted session config
        on session end.
    """
    lang = user_data.get(LANGUAGE)
    exercise = await session.next_exercise()
    if exercise is None:
        summary = session.summary()
        cleanup_session(user_data)
        _clear_persisted_session(update, context)
        chat = update.effective_chat
        if chat is not None:
            await chat.send_message(
                format_summary(summary, lang)
            )
        return

    user_data[EXERCISE] = exercise
    translation = None
    if db and lang:
        translation = await _lookup_translation(
            db, exercise.concept.id, lang
        )
    user_data[TRANSLATION] = translation
    tr_map = user_data.get(TRANSLATION_MAP)
    text, keyboard = format_exercise(
        exercise, translation=translation,
        tr_map=tr_map, lang=lang,
    )
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(text, reply_markup=keyboard)


def _clear_persisted_session(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE | None,
) -> None:
    """Remove the persisted session config for this user."""
    if context is None:
        return
    state_path: Path | None = context.bot_data.get(
        "state_path"
    )
    if state_path is None:
        return
    tg_user = update.effective_user
    if tg_user is not None:
        clear_session_config(state_path, tg_user.id)


def persist_session_config(
    context: ContextTypes.DEFAULT_TYPE,
    tg_id: int,
    user_id: int,
    mode: str,
    concept_ids: list[int] | None = None,
) -> None:
    """Save session config to ``user_data`` and disk.

    Also saves ``_last_topic`` so ``/review`` can reuse it.
    """
    config = {
        "user_id": user_id,
        "tg_id": tg_id,
        "mode": mode,
        "concept_ids": concept_ids,
    }
    context.user_data[SESSION_CONFIG] = config
    last_topic = {
        "user_id": user_id,
        "concept_ids": concept_ids,
    }
    context.user_data[LAST_TOPIC] = last_topic
    state_path: Path | None = context.bot_data.get(
        "state_path"
    )
    if state_path:
        save_user_state(
            state_path, tg_id,
            **{SESSION_CONFIG: config, LAST_TOPIC: last_topic},
        )


def persist_language(
    context: ContextTypes.DEFAULT_TYPE,
    tg_id: int,
    lang: str,
) -> None:
    """Save language preference to disk."""
    state_path: Path | None = context.bot_data.get(
        "state_path"
    )
    if state_path:
        save_user_state(
            state_path, tg_id, language=lang,
        )
