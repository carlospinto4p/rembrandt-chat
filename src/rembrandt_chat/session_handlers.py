"""Session lifecycle and exercise handlers."""

import asyncio
from typing import Any

from rembrandt import Database, ReviewConfig, Session, topic_progress
from rembrandt.models import SessionMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from rembrandt_chat._helpers import (
    EXERCISE,
    LANGUAGE,
    SESSION,
    TRANSLATION,
    TRANSLATION_MAP,
    _lookup_translation,
    get_session,
    require_callback,
    require_message,
    require_session,
    resolve_user,
    resolve_user_with_typing,
    send_next,
)
from rembrandt_chat.config import (
    get_max_new_cards,
    get_max_review_cards,
)
from rembrandt_chat.formatting import (
    CAT_CB_PREFIX,
    LANG_CB_PREFIX,
    PLAY_CAT_PREFIX,
    TOPIC_CB_PREFIX,
    MC_PREFIX,
    QUALITY_PREFIX,
    REVEAL_CB,
    flashcard_reveal,
    format_answer,
    format_categories,
    format_exercise,
    format_hint,
    format_languages,
    format_play_categories,
    format_play_languages,
    format_play_topics,
    format_topics,
    format_summary,
)
from rembrandt_chat.topic_translations import (
    get_category,
    topic_title,
)

PLAY_MODE_PREFIX = "play_mode:"
PLAY_TOPIC_PREFIX = "play_topic:"
PLAY_LANG_PREFIX = "play_lang:"

# user_data key for topic concept_ids chosen during /play
_PLAY_CONCEPT_IDS = "_play_concept_ids"

_ACTIVE_SESSION_MSG = (
    "You already have an active session. "
    "Use /stop to end it first."
)


def _review_config() -> ReviewConfig | None:
    """Build a `ReviewConfig` from env vars, or ``None``."""
    new = get_max_new_cards()
    rev = get_max_review_cards()
    if new == 0 and rev == 0:
        return None
    return ReviewConfig(
        max_new_cards=new,
        max_review_cards=rev,
    )

async def _build_translation_map(
    db: Database,
    lang: str,
) -> dict[str, str]:
    """Build a mapping from native text to translated text.

    Maps both ``front`` and ``back`` of every concept that
    has a translation in `lang`.
    """
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


async def _start_session(
    update: Update,
    user_data: dict,
    db: Database,
    user_id: int,
    *,
    no_words_msg: str,
    confirm_msg: str,
    **session_kwargs: Any,
) -> None:
    """Create a session, fetch the first exercise, and send it.

    :param no_words_msg: Message when no exercises available.
    :param confirm_msg: Confirmation sent via
        ``query.edit_message_text``.
    :param session_kwargs: Forwarded to `Session()` (e.g.
        ``mode`` or ``concept_ids``).
    """
    query = update.callback_query
    session = Session(
        db=db,
        user_id=user_id,
        review_config=_review_config(),
        **session_kwargs,
    )
    user_data[SESSION] = session

    exercise = await session.next_exercise()
    if exercise is None:
        user_data.pop(SESSION, None)
        await query.edit_message_text(no_words_msg)
        return

    user_data[EXERCISE] = exercise

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

    await query.edit_message_text(confirm_msg)
    text, keyboard = format_exercise(
        exercise, translation=translation, tr_map=tr_map
    )
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(text, reply_markup=keyboard)


_MODE_LABELS = {
    SessionMode.MIXED: "Mixed",
    SessionMode.LEARN_NEW: "Learn new",
    SessionMode.REVIEW_DUE: "Review due",
}


@require_message
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/start` — greet the user and auto-register if new."""
    user, _ = await resolve_user(update, context)

    name = user.display_name or user.username
    await update.message.reply_text(
        f"Welcome, {name}!\n\n"
        "Use /play to start an exercise session."
    )


@require_message
async def play(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/play` — pick language, topic, then session mode."""
    if context.user_data.get(SESSION) is not None:
        await update.message.reply_text(
            _ACTIVE_SESSION_MSG
        )
        return

    _, db = await resolve_user_with_typing(update, context)
    languages = await db.get_languages()
    text, keyboard = format_play_languages(languages)
    await update.message.reply_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_play_language(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle language selection from `/play`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(PLAY_LANG_PREFIX):
        return

    user_data = context.user_data
    if user_data.get(SESSION) is not None:
        await query.edit_message_text(_ACTIVE_SESSION_MSG)
        return

    lang_code = data[len(PLAY_LANG_PREFIX):]
    user_data[LANGUAGE] = lang_code

    text, keyboard = format_play_categories(lang=lang_code)
    await query.edit_message_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_play_category(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle category selection from `/play`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(PLAY_CAT_PREFIX):
        return

    user_data = context.user_data
    if user_data.get(SESSION) is not None:
        await query.edit_message_text(_ACTIVE_SESSION_MSG)
        return

    cat_key = data[len(PLAY_CAT_PREFIX):]
    cat = get_category(cat_key)
    if cat is None:
        await query.edit_message_text("Category not found.")
        return

    lang = user_data.get(LANGUAGE)
    user, db = await resolve_user(update, context)
    all_topics = await db.get_topics()
    filtered = [
        t for t in all_topics if t.id in cat.topic_ids
    ]
    progress = await asyncio.gather(
        *(
            topic_progress(db, user.id, t)
            for t in filtered
        )
    )
    text, keyboard = format_play_topics(
        filtered, progress, lang=lang
    )
    await query.edit_message_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_play_topic(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle topic selection from `/play`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(PLAY_TOPIC_PREFIX):
        return

    user_data = context.user_data
    if user_data.get(SESSION) is not None:
        await query.edit_message_text(_ACTIVE_SESSION_MSG)
        return

    topic_value = data[len(PLAY_TOPIC_PREFIX):]
    if topic_value == "all":
        user_data.pop(_PLAY_CONCEPT_IDS, None)
        lang = user_data.get(LANGUAGE)
        topic_label = (
            "All topics" if lang == "en"
            else "Todos los temas"
        )
    else:
        topic_id = int(topic_value)
        _, db = await resolve_user(update, context)
        topic = await db.get_topic(topic_id)
        if topic is None:
            await query.edit_message_text("Topic not found.")
            return
        user_data[_PLAY_CONCEPT_IDS] = topic.concept_ids
        lang = user_data.get(LANGUAGE)
        topic_label = topic_title(
            topic.id, topic.title, lang
        )

    buttons = [
        InlineKeyboardButton(
            label,
            callback_data=f"{PLAY_MODE_PREFIX}{mode.value}",
        )
        for mode, label in _MODE_LABELS.items()
    ]
    await query.edit_message_text(
        f"Topic: {topic_label}\n\nChoose a session mode:",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


@require_callback
async def handle_play_mode(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle session-mode button press from `/play`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(PLAY_MODE_PREFIX):
        return

    mode_value = data[len(PLAY_MODE_PREFIX):]
    mode = SessionMode(mode_value)

    user_data = context.user_data
    if user_data.get(SESSION) is not None:
        await query.edit_message_text(_ACTIVE_SESSION_MSG)
        return

    user, db = await resolve_user(update, context)
    label = _MODE_LABELS[mode]

    concept_ids = user_data.pop(_PLAY_CONCEPT_IDS, None)
    session_kwargs: dict[str, Any] = {"mode": mode}
    if concept_ids is not None:
        session_kwargs["concept_ids"] = concept_ids

    await _start_session(
        update, user_data, db, user.id,
        no_words_msg=(
            "No words available. "
            "Add words first with /addword."
        ),
        confirm_msg=f"Session started ({label}).",
        **session_kwargs,
    )


@require_message
async def stop(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/stop` — end the current session and show summary."""
    session, user_data = get_session(context)
    if session is None:
        await update.message.reply_text("No active session.")
        return

    summary = session.summary()
    user_data.pop(SESSION, None)
    user_data.pop(EXERCISE, None)
    user_data.pop(TRANSLATION, None)
    user_data.pop(TRANSLATION_MAP, None)
    await update.message.reply_text(format_summary(summary))


async def _require_active_exercise(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[Session, dict] | None:
    """Return ``(session, user_data)`` or send an error and
    return ``None``.
    """
    result = require_session(context)
    if result is not None:
        return result
    session, _ = get_session(context)
    msg = (
        "No active exercise."
        if session is not None
        else "No active session."
    )
    await update.message.reply_text(msg)
    return None


@require_message
async def hint(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/hint` — get a progressive hint for the current exercise."""
    result = await _require_active_exercise(update, context)
    if result is None:
        return

    session, _ = result
    h = session.hint()
    await update.message.reply_text(format_hint(h))


@require_message
async def skip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/skip` — skip the current exercise."""
    result = await _require_active_exercise(update, context)
    if result is None:
        return

    session, user_data = result
    skipped = session.skip()
    tr = user_data.get(TRANSLATION)
    front = tr.front if tr else skipped.concept.front
    await update.message.reply_text(f"Skipped: {front}")

    db: Database = context.bot_data["db"]
    await send_next(session, user_data, update, db=db)


@require_message
async def handle_answer_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle a typed answer."""
    result = require_session(context)
    if result is None:
        return

    session, user_data = result
    answer = await session.answer(
        text=update.message.text or ""
    )
    await update.message.reply_text(format_answer(answer))

    db: Database = context.bot_data["db"]
    await send_next(session, user_data, update, db=db)


@require_callback
async def handle_answer_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle inline-keyboard button presses."""
    result = require_session(context)
    if result is None:
        return

    query = update.callback_query
    session, user_data = result
    exercise = user_data[EXERCISE]
    data = query.data or ""

    db: Database = context.bot_data["db"]

    if data == REVEAL_CB:
        tr = user_data.get(TRANSLATION)
        text, keyboard = flashcard_reveal(
            exercise, translation=tr
        )
        await query.edit_message_text(
            text, reply_markup=keyboard
        )
        return

    if data.startswith(QUALITY_PREFIX):
        quality = int(data[len(QUALITY_PREFIX):])
        answer = await session.answer(quality=quality)
        await query.edit_message_text(format_answer(answer))
        await send_next(session, user_data, update, db=db)
        return

    if data.startswith(MC_PREFIX):
        idx = int(data[len(MC_PREFIX):])
        chosen = exercise.options[idx]
        answer = await session.answer(text=chosen)
        await query.edit_message_text(format_answer(answer))
        await send_next(session, user_data, update, db=db)
        return


@require_message
async def topics(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/topics` — list categories, then topics."""
    lang = context.user_data.get(LANGUAGE)
    text, keyboard = format_categories(lang=lang)
    await update.message.reply_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_category_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show topics in a category from `/topics`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(CAT_CB_PREFIX):
        return

    cat_key = data[len(CAT_CB_PREFIX):]
    cat = get_category(cat_key)
    if cat is None:
        await query.edit_message_text(
            "Category not found."
        )
        return

    lang = context.user_data.get(LANGUAGE)
    user, db = await resolve_user(update, context)
    all_topics = await db.get_topics()
    filtered = [
        t for t in all_topics if t.id in cat.topic_ids
    ]
    progress = await asyncio.gather(
        *(
            topic_progress(db, user.id, t)
            for t in filtered
        )
    )
    text, keyboard = format_topics(
        filtered, progress, lang=lang
    )
    await query.edit_message_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_topic_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Start a session scoped to a topic's concepts."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(TOPIC_CB_PREFIX):
        return

    user_data = context.user_data
    if user_data.get(SESSION) is not None:
        await query.edit_message_text(_ACTIVE_SESSION_MSG)
        return

    topic_id = int(data[len(TOPIC_CB_PREFIX):])
    user, db = await resolve_user(update, context)

    topic = await db.get_topic(topic_id)
    if topic is None:
        await query.edit_message_text("Topic not found.")
        return

    await _start_session(
        update, user_data, db, user.id,
        no_words_msg="No words available in this topic.",
        confirm_msg="Topic: {}".format(
            topic_title(
                topic.id, topic.title,
                context.user_data.get(LANGUAGE),
            )
        ),
        concept_ids=topic.concept_ids,
    )


@require_message
async def language(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/language` — set preferred language."""
    _, db = await resolve_user_with_typing(update, context)
    languages = await db.get_languages()
    text, keyboard = format_languages(languages)
    await update.message.reply_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_language_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle language selection from `/language`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(LANG_CB_PREFIX):
        return

    lang_code = data[len(LANG_CB_PREFIX):]
    context.user_data[LANGUAGE] = lang_code

    _, db = await resolve_user(update, context)
    lang = await db.get_language(lang_code)
    name = lang.name if lang else lang_code
    await query.edit_message_text(
        f"Language set to {name}."
    )
