"""Telegram command handlers."""

from rembrandt import PostgresDatabase, Session, User
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from rembrandt_chat.config import LANG_FROM, LANG_TO
from rembrandt_chat.formatting import (
    DEL_CB_PREFIX,
    MC_PREFIX,
    QUALITY_PREFIX,
    REVEAL_CB,
    flashcard_reveal,
    format_answer,
    format_daily_stats,
    format_exercise,
    format_hint,
    format_summary,
    format_weak_words,
)
from rembrandt_chat.user_mapping import UserMapper

# Keys used in context.user_data
_SESSION = "session"
_EXERCISE = "exercise"


# --- shared helpers ---


def _resolve_user(
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


def _get_session(
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[Session | None, dict]:
    """Return the active session and user_data dict."""
    user_data = context.user_data
    session: Session | None = user_data.get(_SESSION)
    return session, user_data


def _require_session(
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[Session, dict] | None:
    """Return ``(session, user_data)`` if both session and
    exercise are active, otherwise ``None``.
    """
    session, user_data = _get_session(context)
    if session is None:
        return None
    if user_data.get(_EXERCISE) is None:
        return None
    return session, user_data


# --- /start ---


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/start` — greet the user and auto-register if new."""
    if update.effective_user is None or update.message is None:
        return

    user, _ = _resolve_user(update, context)

    name = user.display_name or user.username
    await update.message.reply_text(
        f"Welcome, {name}!\n\n"
        "Use /play to start an exercise session."
    )


# --- /play, /stop ---


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

    user, db = _resolve_user(update, context)

    session = Session(
        db=db,
        user_id=user.id,
        language_from=LANG_FROM,
        language_to=LANG_TO,
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

    session, user_data = _get_session(context)
    if session is None:
        await update.message.reply_text("No active session.")
        return

    summary = session.summary()
    user_data.pop(_SESSION, None)
    user_data.pop(_EXERCISE, None)
    await update.message.reply_text(format_summary(summary))


# --- /hint, /skip ---


async def hint(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/hint` — get a progressive hint for the current exercise."""
    if update.message is None:
        return

    result = _require_session(context)
    if result is None:
        session, _ = _get_session(context)
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

    result = _require_session(context)
    if result is None:
        session, _ = _get_session(context)
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

    await _send_next(session, user_data, update)


# --- answer handlers ---


async def handle_answer_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle a typed answer (reverse flashcard, conjugation, etc.)."""
    if update.effective_user is None or update.message is None:
        return

    result = _require_session(context)
    if result is None:
        return

    session, user_data = result
    answer = session.answer(text=update.message.text or "")
    await update.message.reply_text(format_answer(answer))

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

    result = _require_session(context)
    if result is None:
        return

    session, user_data = result
    exercise = user_data[_EXERCISE]
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
        answer = session.answer(quality=quality)
        await query.edit_message_text(format_answer(answer))
        await _send_next(session, user_data, update)
        return

    # Multiple choice
    if data.startswith(MC_PREFIX):
        idx = int(data[len(MC_PREFIX):])
        chosen = exercise.options[idx]
        answer = session.answer(text=chosen)
        await query.edit_message_text(format_answer(answer))
        await _send_next(session, user_data, update)
        return


# --- /addword conversation ---

AWAITING_WORD, AWAITING_DEFINITION = range(2)


async def addword_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """`/addword` — begin the add-word conversation."""
    if update.effective_user is None or update.message is None:
        return ConversationHandler.END

    _resolve_user(update, context)

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

    user, db = _resolve_user(update, context)

    db.add_word(
        language_from=LANG_FROM,
        language_to=LANG_TO,
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


# --- /mywords, /deleteword ---


async def mywords(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/mywords` — list the user's private words."""
    if update.effective_user is None or update.message is None:
        return

    user, db = _resolve_user(update, context)

    words = db.get_words(LANG_FROM, LANG_TO, owner_id=user.id)
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


async def deleteword(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/deleteword` — show private words as buttons to delete."""
    if update.effective_user is None or update.message is None:
        return

    user, db = _resolve_user(update, context)

    words = db.get_words(LANG_FROM, LANG_TO, owner_id=user.id)
    if not words:
        await update.message.reply_text(
            "You have no private words to delete."
        )
        return

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


# --- /stats, /weak ---


async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/stats` — show daily stats."""
    if update.effective_user is None or update.message is None:
        return

    user, db = _resolve_user(update, context)

    daily = db.daily_stats(user.id, days=7)
    await update.message.reply_text(format_daily_stats(daily))


async def weak(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/weak` — show weakest words."""
    if update.effective_user is None or update.message is None:
        return

    user, db = _resolve_user(update, context)

    words = db.weak_words(
        user.id, LANG_FROM, LANG_TO, limit=10
    )
    await update.message.reply_text(format_weak_words(words))


# --- internal ---


async def _send_next(
    session: Session,
    user_data: dict,
    update: Update,
) -> None:
    """Advance to the next exercise or end the session."""
    exercise = session.next_exercise()
    if exercise is None:
        summary = session.summary()
        user_data.pop(_SESSION, None)
        user_data.pop(_EXERCISE, None)
        chat = update.effective_chat
        if chat is not None:
            await chat.send_message(format_summary(summary))
        return

    user_data[_EXERCISE] = exercise
    text, keyboard = format_exercise(exercise)
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(text, reply_markup=keyboard)
