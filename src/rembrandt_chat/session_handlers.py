"""Session lifecycle and exercise handlers."""

import asyncio
from typing import Any

from rembrandt import PostgresDatabase, ReviewConfig, Session, lesson_progress
from rembrandt.models import SessionMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from rembrandt_chat._helpers import (
    EXERCISE,
    SESSION,
    get_session,
    require_callback,
    require_message,
    require_session,
    resolve_user,
    resolve_user_with_typing,
    send_next,
)
from rembrandt_chat.config import (
    LANG_FROM,
    LANG_TO,
    get_max_new_cards,
    get_max_review_cards,
)
from rembrandt_chat.formatting import (
    LESSON_CB_PREFIX,
    MC_PREFIX,
    QUALITY_PREFIX,
    REVEAL_CB,
    flashcard_reveal,
    format_answer,
    format_exercise,
    format_hint,
    format_lessons,
    format_summary,
)

PLAY_MODE_PREFIX = "play_mode:"

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

async def _start_session(
    update: Update,
    user_data: dict,
    db: PostgresDatabase,
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
        ``mode`` or ``word_ids``).
    """
    query = update.callback_query
    session = Session(
        db=db,
        user_id=user_id,
        language_from=LANG_FROM,
        language_to=LANG_TO,
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
    await query.edit_message_text(confirm_msg)
    text, keyboard = format_exercise(exercise)
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
    """`/play` — pick a session mode, then start."""
    if context.user_data.get(SESSION) is not None:
        await update.message.reply_text(
            _ACTIVE_SESSION_MSG
        )
        return

    buttons = [
        InlineKeyboardButton(
            label,
            callback_data=f"{PLAY_MODE_PREFIX}{mode.value}",
        )
        for mode, label in _MODE_LABELS.items()
    ]
    await update.message.reply_text(
        "Choose a session mode:",
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

    await _start_session(
        update, user_data, db, user.id,
        no_words_msg=(
            "No words available. "
            "Add words first with /addword."
        ),
        confirm_msg=f"Session started ({label}).",
        mode=mode,
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
    await update.message.reply_text(
        f"Skipped: {skipped.word.word_from}"
    )

    await send_next(session, user_data, update)


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
    answer = await session.answer(text=update.message.text or "")
    await update.message.reply_text(format_answer(answer))

    await send_next(session, user_data, update)


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

    if data == REVEAL_CB:
        text, keyboard = flashcard_reveal(exercise)
        await query.edit_message_text(
            text, reply_markup=keyboard
        )
        return

    if data.startswith(QUALITY_PREFIX):
        quality = int(data[len(QUALITY_PREFIX):])
        answer = await session.answer(quality=quality)
        await query.edit_message_text(format_answer(answer))
        await send_next(session, user_data, update)
        return

    if data.startswith(MC_PREFIX):
        idx = int(data[len(MC_PREFIX):])
        chosen = exercise.options[idx]
        answer = await session.answer(text=chosen)
        await query.edit_message_text(format_answer(answer))
        await send_next(session, user_data, update)
        return


@require_message
async def lessons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/lessons` — list available lessons with progress."""
    user, db = await resolve_user_with_typing(update, context)

    all_lessons = await db.get_lessons(LANG_FROM, LANG_TO)
    progress = await asyncio.gather(
        *(
            lesson_progress(db, user.id, ls)
            for ls in all_lessons
        )
    )
    text, keyboard = format_lessons(all_lessons, progress)
    await update.message.reply_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_lesson_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Start a session scoped to a lesson's words."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(LESSON_CB_PREFIX):
        return

    user_data = context.user_data
    if user_data.get(SESSION) is not None:
        await query.edit_message_text(_ACTIVE_SESSION_MSG)
        return

    lesson_id = int(data[len(LESSON_CB_PREFIX):])
    user, db = await resolve_user(update, context)

    lesson = await db.get_lesson(lesson_id)
    if lesson is None:
        await query.edit_message_text("Lesson not found.")
        return

    await _start_session(
        update, user_data, db, user.id,
        no_words_msg="No words available in this lesson.",
        confirm_msg=f"Lesson: {lesson.title}",
        word_ids=lesson.word_ids,
    )
