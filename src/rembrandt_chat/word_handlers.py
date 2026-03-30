"""Word management handlers."""

import asyncio
import csv
import io

from rembrandt import Database
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from rembrandt_chat._helpers import (
    extract_command_arg,
    get_lang,
    require_callback,
    require_message,
    require_message_conv,
    resolve_user,
    resolve_user_with_typing,
)
from rembrandt_chat.formatting import (
    DEL_CANCEL_CB,
    DEL_CB_PREFIX,
    DEL_CONFIRM_PREFIX,
    format_concepts_list,
    format_search_results,
)
from rembrandt_chat.i18n import t

AWAITING_WORD, AWAITING_DEFINITION, AWAITING_TAGS = range(3)
AWAITING_BULK_FILE = 20

#: ``(front, back, tags)`` tuple returned by file parsers.
WordEntry = tuple[str, str, list[str]]


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

    lang = get_lang(context)
    await update.message.reply_text(t("send_word", lang))
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
    lang = get_lang(context)
    await update.message.reply_text(
        t("send_definition", lang)
    )
    return AWAITING_DEFINITION


@require_message_conv
async def addword_definition(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Receive the definition, then ask for optional tags."""
    definition = (update.message.text or "").strip()
    word_from = context.user_data.get("_addword_word", "")
    lang = get_lang(context)

    if not word_from or not definition:
        await update.message.reply_text(
            t("word_empty", lang)
        )
        context.user_data.pop("_addword_word", None)
        return ConversationHandler.END

    context.user_data["_addword_def"] = definition
    await update.message.reply_text(t("send_tags", lang))
    return AWAITING_TAGS


@require_message_conv
async def addword_tags(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Receive tags and save the word."""
    raw = (update.message.text or "").strip()
    tags = [
        tag.strip() for tag in raw.split(",")
        if tag.strip()
    ]

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

    lang = get_lang(context)
    if tags:
        msg = t(
            "word_added_tags", lang,
            front=front, back=back,
            tags=", ".join(tags),
        )
    else:
        msg = t("word_added", lang, front=front, back=back)
    await update.message.reply_text(msg)
    return ConversationHandler.END


async def addword_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Cancel the /addword conversation."""
    if update.message is not None:
        lang = get_lang(context)
        await update.message.reply_text(
            t("cancelled", lang)
        )
    context.user_data.pop("_addword_word", None)
    context.user_data.pop("_addword_def", None)
    return ConversationHandler.END


@require_message_conv
async def bulkimport_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """`/bulkimport` — ask user for a CSV or text file."""
    await resolve_user(update, context)
    lang = get_lang(context)
    await update.message.reply_text(
        t("bulkimport_prompt", lang)
    )
    return AWAITING_BULK_FILE


@require_message_conv
async def bulkimport_file(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Receive the file and import words."""
    user, db = await resolve_user_with_typing(update, context)
    lang = get_lang(context)

    doc = update.message.document
    if doc is None:
        await update.message.reply_text(
            t("send_file", lang)
        )
        return AWAITING_BULK_FILE

    tg_file = await doc.get_file()
    raw = await tg_file.download_as_bytearray()

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        await update.message.reply_text(
            t("file_read_error", lang)
        )
        return ConversationHandler.END

    words = _parse_bulk_file(text)
    if not words:
        await update.message.reply_text(
            t("no_valid_words", lang)
        )
        return ConversationHandler.END

    await asyncio.gather(
        *(
            db.add_concept(
                front=front,
                back=back,
                tags=tags or None,
                owner_id=user.id,
            )
            for front, back, tags in words
        )
    )

    await update.message.reply_text(
        t("imported_words", lang, count=len(words))
    )
    return ConversationHandler.END


async def bulkimport_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Cancel the /bulkimport conversation."""
    if update.message is not None:
        lang = get_lang(context)
        await update.message.reply_text(
            t("cancelled", lang)
        )
    return ConversationHandler.END


def _parse_bulk_file(
    text: str,
) -> list[WordEntry]:
    """Parse a CSV or text file into word tuples.

    :return: List of ``(front, back, tags)`` tuples.
    """
    lines = text.strip().splitlines()
    if not lines:
        return []

    # Try CSV first (detect comma in first line)
    if "," in lines[0]:
        return _parse_csv(text)
    return _parse_text(lines)


def _parse_csv(
    text: str,
) -> list[WordEntry]:
    """Parse CSV with ``front,back[,tags]`` columns."""
    reader = csv.reader(io.StringIO(text))
    words: list[WordEntry] = []
    for i, row in enumerate(reader):
        if len(row) < 2:
            continue
        front = row[0].strip()
        back = row[1].strip()
        # Skip header row
        if i == 0 and back.lower() in (
            "back", "definition"
        ):
            continue
        if not front or not back:
            continue
        tags: list[str] = []
        if len(row) >= 3 and row[2].strip():
            tags = [
                tag.strip()
                for tag in row[2].split(";")
                if tag.strip()
            ]
        words.append((front, back, tags))
    return words


def _parse_text(
    lines: list[str],
) -> list[WordEntry]:
    """Parse text with ``word \u2014 definition`` per line."""
    words: list[WordEntry] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Try em-dash, en-dash, then hyphen
        for sep in ("\u2014", "\u2013", " - "):
            if sep in line:
                parts = line.split(sep, 1)
                front = parts[0].strip()
                back = parts[1].strip()
                if front and back:
                    words.append((front, back, []))
                break
    return words


@require_message
async def mywords(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/mywords [tag]` — list the user's private words.

    If a tag is given, only words with that tag are shown.
    """
    user, db = await resolve_user_with_typing(update, context)
    lang = get_lang(context)

    concepts = await db.get_concepts(owner_id=user.id)

    # Optional tag filter from command argument
    tag_filter = extract_command_arg(update.message.text)
    if tag_filter:
        concepts = [
            c for c in concepts if tag_filter in c.tags
        ]

    if not concepts:
        if tag_filter:
            msg = t(
                "no_words_with_tag", lang, tag=tag_filter,
            )
        else:
            msg = t("no_private_words", lang)
        await update.message.reply_text(msg)
        return

    await update.message.reply_text(
        format_concepts_list(concepts)
    )


@require_message
async def search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/search <term>` — search vocabulary by text match."""
    user, db = await resolve_user_with_typing(update, context)
    lang = get_lang(context)

    term = extract_command_arg(update.message.text).lower()

    if not term:
        await update.message.reply_text(
            t("search_usage", lang)
        )
        return

    shared, own = await asyncio.gather(
        db.get_concepts(),
        db.get_concepts(owner_id=user.id),
    )
    matches = [
        c for c in shared + own
        if term in c.front.lower()
        or term in c.back.lower()
    ]

    if not matches:
        await update.message.reply_text(
            t("search_no_results", lang, term=term)
        )
        return

    await update.message.reply_text(
        format_search_results(matches, term, lang)
    )


@require_message
async def deleteword(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/deleteword` — show private words as buttons to delete."""
    user, db = await resolve_user_with_typing(update, context)
    lang = get_lang(context)

    concepts = await db.get_concepts(owner_id=user.id)
    if not concepts:
        await update.message.reply_text(
            t("no_words_to_delete", lang)
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
        t("tap_to_delete", lang),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@require_callback
async def handle_deleteword_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle a delete-word button — show confirmation."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(DEL_CB_PREFIX):
        return

    lang = get_lang(context)
    concept_id = data[len(DEL_CB_PREFIX):]
    _, db = await resolve_user(update, context)
    concept = await db.get_concept(int(concept_id))
    word = concept.front if concept else concept_id
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                t("yes_delete", lang),
                callback_data=(
                    f"{DEL_CONFIRM_PREFIX}{concept_id}"
                ),
            ),
            InlineKeyboardButton(
                t("no_keep", lang),
                callback_data=DEL_CANCEL_CB,
            ),
        ]
    ])
    await query.edit_message_text(
        t("confirm_delete", lang, word=word),
        reply_markup=keyboard,
    )


@require_callback
async def handle_deleteword_confirm(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle confirmed deletion."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(DEL_CONFIRM_PREFIX):
        return

    lang = get_lang(context)
    concept_id = int(data[len(DEL_CONFIRM_PREFIX):])
    db: Database = context.bot_data["db"]
    await db.delete_concept(concept_id)
    await query.edit_message_text(t("word_deleted", lang))


@require_callback
async def handle_deleteword_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle cancelled deletion."""
    query = update.callback_query
    lang = get_lang(context)
    await query.edit_message_text(
        t("deletion_cancelled", lang)
    )
