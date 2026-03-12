"""Session lifecycle and exercise handlers."""

from rembrandt import Session, lesson_progress
from rembrandt.models import SessionMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from rembrandt_chat._helpers import (
    EXERCISE,
    SESSION,
    get_session,
    require_session,
    resolve_user,
    send_next,
    send_typing,
)
from rembrandt_chat.config import LANG_FROM, LANG_TO
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

_MODE_LABELS = {
    SessionMode.MIXED: "Mixed",
    SessionMode.LEARN_NEW: "Learn new",
    SessionMode.REVIEW_DUE: "Review due",
}


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/start` — greet the user and auto-register if new."""
    if update.effective_user is None or update.message is None:
        return

    user, _ = await resolve_user(update, context)

    name = user.display_name or user.username
    await update.message.reply_text(
        f"Welcome, {name}!\n\n"
        "Use /play to start an exercise session."
    )


async def play(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/play` — pick a session mode, then start."""
    if update.effective_user is None or update.message is None:
        return

    if context.user_data.get(SESSION) is not None:
        await update.message.reply_text(
            "You already have an active session. "
            "Use /stop to end it first."
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


async def handle_play_mode(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle session-mode button press from `/play`."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    data = query.data or ""
    if not data.startswith(PLAY_MODE_PREFIX):
        return

    mode_value = data[len(PLAY_MODE_PREFIX):]
    mode = SessionMode(mode_value)

    user_data = context.user_data
    if user_data.get(SESSION) is not None:
        await query.edit_message_text(
            "You already have an active session. "
            "Use /stop to end it first."
        )
        return

    user, db = await resolve_user(update, context)

    session = Session(
        db=db,
        user_id=user.id,
        language_from=LANG_FROM,
        language_to=LANG_TO,
        mode=mode,
    )
    user_data[SESSION] = session

    exercise = await session.next_exercise()
    if exercise is None:
        user_data.pop(SESSION, None)
        await query.edit_message_text(
            "No words available. Add words first with /addword."
        )
        return

    user_data[EXERCISE] = exercise
    label = _MODE_LABELS[mode]
    text, keyboard = format_exercise(exercise)
    await query.edit_message_text(
        f"Session started ({label}).",
    )
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(text, reply_markup=keyboard)


async def stop(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/stop` — end the current session and show summary."""
    if update.message is None:
        return

    session, user_data = get_session(context)
    if session is None:
        await update.message.reply_text("No active session.")
        return

    summary = session.summary()
    user_data.pop(SESSION, None)
    user_data.pop(EXERCISE, None)
    await update.message.reply_text(format_summary(summary))


async def hint(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/hint` — get a progressive hint for the current exercise."""
    if update.message is None:
        return

    result = require_session(context)
    if result is None:
        session, _ = get_session(context)
        msg = (
            "No active exercise."
            if session is not None
            else "No active session."
        )
        await update.message.reply_text(msg)
        return

    session, _ = result
    h = session.hint()
    await update.message.reply_text(format_hint(h))


async def skip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/skip` — skip the current exercise."""
    if update.message is None:
        return

    result = require_session(context)
    if result is None:
        session, _ = get_session(context)
        msg = (
            "No active exercise."
            if session is not None
            else "No active session."
        )
        await update.message.reply_text(msg)
        return

    session, user_data = result
    skipped = session.skip()
    await update.message.reply_text(
        f"Skipped: {skipped.word.word_from}"
    )

    await send_next(session, user_data, update)


async def handle_answer_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle a typed answer."""
    if update.effective_user is None or update.message is None:
        return

    result = require_session(context)
    if result is None:
        return

    session, user_data = result
    answer = await session.answer(text=update.message.text or "")
    await update.message.reply_text(format_answer(answer))

    await send_next(session, user_data, update)


async def handle_answer_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle inline-keyboard button presses."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    result = require_session(context)
    if result is None:
        return

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


async def lessons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/lessons` — list available lessons with progress."""
    if update.effective_user is None or update.message is None:
        return

    await send_typing(update)
    user, db = await resolve_user(update, context)

    all_lessons = await db.get_lessons(LANG_FROM, LANG_TO)
    progress = [
        await lesson_progress(db, user.id, ls)
        for ls in all_lessons
    ]
    text, keyboard = format_lessons(all_lessons, progress)
    await update.message.reply_text(
        text, reply_markup=keyboard
    )


async def handle_lesson_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Start a session scoped to a lesson's words."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    data = query.data or ""
    if not data.startswith(LESSON_CB_PREFIX):
        return

    user_data = context.user_data
    if user_data.get(SESSION) is not None:
        await query.edit_message_text(
            "You already have an active session. "
            "Use /stop to end it first."
        )
        return

    lesson_id = int(data[len(LESSON_CB_PREFIX):])
    user, db = await resolve_user(update, context)

    lesson = await db.get_lesson(lesson_id)
    if lesson is None:
        await query.edit_message_text("Lesson not found.")
        return

    session = Session(
        db=db,
        user_id=user.id,
        language_from=LANG_FROM,
        language_to=LANG_TO,
        word_ids=lesson.word_ids,
    )
    user_data[SESSION] = session

    exercise = await session.next_exercise()
    if exercise is None:
        user_data.pop(SESSION, None)
        await query.edit_message_text(
            "No words available in this lesson."
        )
        return

    user_data[EXERCISE] = exercise
    await query.edit_message_text(
        f"Lesson: {lesson.title}",
    )
    text, keyboard = format_exercise(exercise)
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(text, reply_markup=keyboard)
