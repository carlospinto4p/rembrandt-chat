"""Session lifecycle and exercise handlers."""

from rembrandt import Session
from telegram import Update
from telegram.ext import ContextTypes

from rembrandt_chat._helpers import (
    EXERCISE,
    SESSION,
    get_session,
    require_session,
    resolve_user,
    send_next,
)
from rembrandt_chat.config import LANG_FROM, LANG_TO
from rembrandt_chat.formatting import (
    MC_PREFIX,
    QUALITY_PREFIX,
    REVEAL_CB,
    flashcard_reveal,
    format_answer,
    format_exercise,
    format_hint,
    format_summary,
)


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
    """`/play` — start an exercise session."""
    if update.effective_user is None or update.message is None:
        return

    user_data = context.user_data
    if user_data.get(SESSION) is not None:
        await update.message.reply_text(
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
    )
    user_data[SESSION] = session

    exercise = await session.next_exercise()
    if exercise is None:
        user_data.pop(SESSION, None)
        await update.message.reply_text(
            "No words available. Add words first with /addword."
        )
        return

    user_data[EXERCISE] = exercise
    text, keyboard = format_exercise(exercise)
    await update.message.reply_text(text, reply_markup=keyboard)


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
