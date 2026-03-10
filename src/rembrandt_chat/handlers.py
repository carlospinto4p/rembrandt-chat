"""Telegram command handlers."""

from rembrandt import PostgresDatabase, Session
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

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


async def hint(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/hint` — get a progressive hint for the current exercise."""
    if update.message is None:
        return

    user_data = context.user_data
    session: Session | None = user_data.get(_SESSION)
    if session is None:
        await update.message.reply_text("No active session.")
        return

    if user_data.get(_EXERCISE) is None:
        await update.message.reply_text("No active exercise.")
        return

    h = session.hint()
    await update.message.reply_text(format_hint(h))


async def skip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/skip` — skip the current exercise."""
    if update.message is None:
        return

    user_data = context.user_data
    session: Session | None = user_data.get(_SESSION)
    if session is None:
        await update.message.reply_text("No active session.")
        return

    if user_data.get(_EXERCISE) is None:
        await update.message.reply_text("No active exercise.")
        return

    skipped = session.skip()
    await update.message.reply_text(
        f"Skipped: {skipped.word.word_from}"
    )

    await _send_next(session, user_data, update)


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


# --- /addword conversation states ---
AWAITING_WORD, AWAITING_DEFINITION = range(2)


async def addword_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """`/addword` — begin the add-word conversation."""
    if update.effective_user is None or update.message is None:
        return ConversationHandler.END

    mapper: UserMapper = context.bot_data["user_mapper"]
    mapper.ensure_user(update.effective_user)

    await update.message.reply_text("Send the word:")
    return AWAITING_WORD


async def addword_word(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Receive the word text in the /addword conversation."""
    if update.message is None:
        return ConversationHandler.END

    context.user_data["_addword_word"] = (
        update.message.text or ""
    ).strip()
    await update.message.reply_text("Send the definition:")
    return AWAITING_DEFINITION


async def addword_definition(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Receive the definition and save the word."""
    if (
        update.effective_user is None
        or update.message is None
    ):
        return ConversationHandler.END

    word_from = context.user_data.pop("_addword_word", "")
    word_to = (update.message.text or "").strip()

    if not word_from or not word_to:
        await update.message.reply_text(
            "Word or definition was empty. Try /addword again."
        )
        return ConversationHandler.END

    mapper: UserMapper = context.bot_data["user_mapper"]
    user = mapper.ensure_user(update.effective_user)
    db: PostgresDatabase = context.bot_data["db"]

    db.add_word(
        language_from="es",
        language_to="es",
        word_from=word_from,
        word_to=word_to,
        owner_id=user.id,
    )
    await update.message.reply_text(
        f'Added "{word_from}" \u2014 {word_to}'
    )
    return ConversationHandler.END


async def addword_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Cancel the /addword conversation."""
    if update.message is not None:
        await update.message.reply_text("Cancelled.")
    context.user_data.pop("_addword_word", None)
    return ConversationHandler.END


# --- /mywords ---


async def mywords(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/mywords` — list the user's private words."""
    if update.effective_user is None or update.message is None:
        return

    mapper: UserMapper = context.bot_data["user_mapper"]
    user = mapper.ensure_user(update.effective_user)
    db: PostgresDatabase = context.bot_data["db"]

    words = db.get_words("es", "es", owner_id=user.id)
    if not words:
        await update.message.reply_text(
            "You have no private words yet. "
            "Use /addword to add one."
        )
        return

    lines = [
        f"{i}. {w.word_from} \u2014 {w.word_to}"
        for i, w in enumerate(words, 1)
    ]
    await update.message.reply_text("\n".join(lines))


# --- /deleteword ---

DEL_CB_PREFIX = "delw:"


async def deleteword(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/deleteword` — show private words as buttons to delete."""
    if update.effective_user is None or update.message is None:
        return

    mapper: UserMapper = context.bot_data["user_mapper"]
    user = mapper.ensure_user(update.effective_user)
    db: PostgresDatabase = context.bot_data["db"]

    words = db.get_words("es", "es", owner_id=user.id)
    if not words:
        await update.message.reply_text(
            "You have no private words to delete."
        )
        return

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    buttons = [
        [
            InlineKeyboardButton(
                w.word_from,
                callback_data=f"{DEL_CB_PREFIX}{w.id}",
            )
        ]
        for w in words
    ]
    await update.message.reply_text(
        "Tap a word to delete it:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def handle_deleteword_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle a delete-word button press."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    data = query.data or ""
    if not data.startswith(DEL_CB_PREFIX):
        return

    word_id = int(data[len(DEL_CB_PREFIX):])
    db: PostgresDatabase = context.bot_data["db"]
    db.delete_word(word_id)

    await query.edit_message_text("Word deleted.")


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
