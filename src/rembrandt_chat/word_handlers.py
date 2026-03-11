"""Word management handlers."""

from rembrandt import PostgresDatabase
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from rembrandt_chat._helpers import resolve_user
from rembrandt_chat.config import LANG_FROM, LANG_TO
from rembrandt_chat.formatting import DEL_CB_PREFIX

AWAITING_WORD, AWAITING_DEFINITION = range(2)


async def addword_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """`/addword` — begin the add-word conversation."""
    if update.effective_user is None or update.message is None:
        return ConversationHandler.END

    await resolve_user(update, context)

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

    user, db = await resolve_user(update, context)

    await db.add_word(
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


async def mywords(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/mywords` — list the user's private words."""
    if update.effective_user is None or update.message is None:
        return

    user, db = await resolve_user(update, context)

    words = await db.get_words(
        LANG_FROM, LANG_TO, owner_id=user.id,
    )
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

    user, db = await resolve_user(update, context)

    words = await db.get_words(
        LANG_FROM, LANG_TO, owner_id=user.id,
    )
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
    await db.delete_word(word_id)

    await query.edit_message_text("Word deleted.")
