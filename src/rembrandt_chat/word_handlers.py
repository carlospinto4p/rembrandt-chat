"""Word management handlers."""

from rembrandt import Database
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from rembrandt_chat._helpers import (
    require_callback,
    require_message,
    require_message_conv,
    resolve_user,
    resolve_user_with_typing,
)
from rembrandt_chat.formatting import DEL_CB_PREFIX

AWAITING_WORD, AWAITING_DEFINITION, AWAITING_TAGS = range(3)


@require_message_conv
async def addword_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """`/addword` — begin the add-word conversation."""
    # Clear leftovers from a previously abandoned conversation
    context.user_data.pop("_addword_word", None)
    context.user_data.pop("_addword_def", None)

    await resolve_user(update, context)

    await update.message.reply_text("Send the word:")
    return AWAITING_WORD


@require_message_conv
async def addword_word(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Receive the word text in the /addword conversation."""
    context.user_data["_addword_word"] = (
        update.message.text or ""
    ).strip()
    await update.message.reply_text("Send the definition:")
    return AWAITING_DEFINITION


@require_message_conv
async def addword_definition(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Receive the definition, then ask for optional tags."""
    definition = (update.message.text or "").strip()
    word_from = context.user_data.get("_addword_word", "")

    if not word_from or not definition:
        await update.message.reply_text(
            "Word or definition was empty. "
            "Try /addword again."
        )
        context.user_data.pop("_addword_word", None)
        return ConversationHandler.END

    context.user_data["_addword_def"] = definition
    await update.message.reply_text(
        "Send tags (comma-separated) or /skip:"
    )
    return AWAITING_TAGS


@require_message_conv
async def addword_tags(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Receive tags and save the word."""
    raw = (update.message.text or "").strip()
    tags = [t.strip() for t in raw.split(",") if t.strip()]

    return await _save_word(update, context, tags=tags)


@require_message_conv
async def addword_skip_tags(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """`/skip` — save the word without tags."""
    return await _save_word(update, context, tags=[])


async def _save_word(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    tags: list[str],
) -> int:
    """Save the word from the conversation state."""
    front = context.user_data.pop("_addword_word", "")
    back = context.user_data.pop("_addword_def", "")

    user, db = await resolve_user(update, context)

    await db.add_concept(
        front=front,
        back=back,
        tags=tags or None,
        owner_id=user.id,
    )

    msg = f'Added "{front}" \u2014 {back}'
    if tags:
        msg += f" [{', '.join(tags)}]"
    await update.message.reply_text(msg)
    return ConversationHandler.END


async def addword_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Cancel the /addword conversation."""
    if update.message is not None:
        await update.message.reply_text("Cancelled.")
    context.user_data.pop("_addword_word", None)
    context.user_data.pop("_addword_def", None)
    return ConversationHandler.END


@require_message
async def mywords(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/mywords [tag]` — list the user's private words.

    If a tag is given, only words with that tag are shown.
    """
    user, db = await resolve_user_with_typing(update, context)

    concepts = await db.get_concepts(owner_id=user.id)

    # Optional tag filter from command argument
    text = (update.message.text or "").strip()
    parts = text.split(maxsplit=1)
    tag_filter = parts[1].strip() if len(parts) > 1 else ""
    if tag_filter:
        concepts = [
            c for c in concepts if tag_filter in c.tags
        ]

    if not concepts:
        msg = (
            f"No words with tag \u201c{tag_filter}\u201d."
            if tag_filter
            else "You have no private words yet. "
            "Use /addword to add one."
        )
        await update.message.reply_text(msg)
        return

    lines = []
    for i, c in enumerate(concepts, 1):
        line = f"{i}. {c.front} \u2014 {c.back}"
        if c.tags:
            line += f" [{', '.join(c.tags)}]"
        lines.append(line)
    await update.message.reply_text("\n".join(lines))


@require_message
async def deleteword(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/deleteword` — show private words as buttons to delete."""
    user, db = await resolve_user_with_typing(update, context)

    concepts = await db.get_concepts(owner_id=user.id)
    if not concepts:
        await update.message.reply_text(
            "You have no private words to delete."
        )
        return

    buttons = [
        [
            InlineKeyboardButton(
                c.front,
                callback_data=f"{DEL_CB_PREFIX}{c.id}",
            )
        ]
        for c in concepts
    ]
    await update.message.reply_text(
        "Tap a word to delete it:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@require_callback
async def handle_deleteword_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle a delete-word button press."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(DEL_CB_PREFIX):
        return

    concept_id = int(data[len(DEL_CB_PREFIX):])
    db: Database = context.bot_data["db"]
    await db.delete_concept(concept_id)

    await query.edit_message_text("Word deleted.")
