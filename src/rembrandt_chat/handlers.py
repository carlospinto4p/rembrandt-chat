"""Telegram command handlers."""

from rembrandt import Session
from telegram import Update
from telegram.ext import ContextTypes

from rembrandt_chat.formatting import (
    MC_PREFIX,
    QUALITY_PREFIX,
    REVEAL_CB,
    flashcard_reveal,
    format_answer,
    format_exercise,
    format_summary,
)
from rembrandt_chat.user_mapping import UserMapper

# Keys used in context.user_data
_SESSION = "session"
_EXERCISE = "exercise"


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/start` — greet the user and auto-register if new."""
    if update.effective_user is None or update.message is None:
        return

    mapper: UserMapper = context.bot_data["user_mapper"]
    user = mapper.ensure_user(update.effective_user)

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
    if user_data.get(_SESSION) is not None:
        await update.message.reply_text(
            "You already have an active session. "
            "Use /stop to end it first."
        )
        return

    mapper: UserMapper = context.bot_data["user_mapper"]
    user = mapper.ensure_user(update.effective_user)

    db = context.bot_data["db"]
    session = Session(
        db=db,
        user_id=user.id,
        language_from="es",
        language_to="es",
    )
    user_data[_SESSION] = session

    exercise = session.next_exercise()
    if exercise is None:
        user_data.pop(_SESSION, None)
        await update.message.reply_text(
            "No words available. Add words first with /addword."
        )
        return

    user_data[_EXERCISE] = exercise
    text, keyboard = format_exercise(exercise)
    await update.message.reply_text(text, reply_markup=keyboard)


async def stop(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/stop` — end the current session and show summary."""
    if update.message is None:
        return

    user_data = context.user_data
    session: Session | None = user_data.get(_SESSION)
    if session is None:
        await update.message.reply_text("No active session.")
        return

    stats = session.summary()
    user_data.pop(_SESSION, None)
    user_data.pop(_EXERCISE, None)
    await update.message.reply_text(format_summary(stats))


async def handle_answer_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle a typed answer (reverse flashcard, conjugation, etc.)."""
    if update.effective_user is None or update.message is None:
        return

    user_data = context.user_data
    session: Session | None = user_data.get(_SESSION)
    if session is None:
        return

    exercise = user_data.get(_EXERCISE)
    if exercise is None:
        return

    result = session.answer(text=update.message.text or "")
    await update.message.reply_text(format_answer(result))

    await _send_next(session, user_data, update)


async def handle_answer_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle inline-keyboard button presses."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    user_data = context.user_data
    session: Session | None = user_data.get(_SESSION)
    if session is None:
        return

    exercise = user_data.get(_EXERCISE)
    if exercise is None:
        return

    data = query.data or ""

    # Flashcard reveal — show answer + quality buttons
    if data == REVEAL_CB:
        text, keyboard = flashcard_reveal(exercise)
        await query.edit_message_text(
            text, reply_markup=keyboard
        )
        return

    # Quality rating (self-graded / flashcard)
    if data.startswith(QUALITY_PREFIX):
        quality = int(data[len(QUALITY_PREFIX):])
        result = session.answer(quality=quality)
        await query.edit_message_text(format_answer(result))
        await _send_next(session, user_data, update)
        return

    # Multiple choice
    if data.startswith(MC_PREFIX):
        idx = int(data[len(MC_PREFIX):])
        chosen = exercise.options[idx]
        result = session.answer(text=chosen)
        await query.edit_message_text(format_answer(result))
        await _send_next(session, user_data, update)
        return


async def _send_next(
    session: Session,
    user_data: dict,
    update: Update,
) -> None:
    """Advance to the next exercise or end the session."""
    exercise = session.next_exercise()
    if exercise is None:
        stats = session.summary()
        user_data.pop(_SESSION, None)
        user_data.pop(_EXERCISE, None)
        chat = update.effective_chat
        if chat is not None:
            await chat.send_message(format_summary(stats))
        return

    user_data[_EXERCISE] = exercise
    text, keyboard = format_exercise(exercise)
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(text, reply_markup=keyboard)
