"""Statistics handlers."""

import io
import json
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from rembrandt_chat._helpers import (
    require_message,
    require_message_conv,
    resolve_user,
    resolve_user_with_typing,
)
from rembrandt_chat.config import LANG_FROM, LANG_TO
from rembrandt_chat.formatting import (
    format_daily_stats,
    format_forecast,
    format_history,
    format_retention,
    format_weak_words,
)


@require_message
async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/stats` — show daily stats."""
    user, db = await resolve_user_with_typing(update, context)

    daily = await db.daily_stats(user.id, days=7)
    await update.message.reply_text(format_daily_stats(daily))


@require_message
async def weak(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/weak` — show weakest words."""
    user, db = await resolve_user_with_typing(update, context)

    words = await db.weak_words(
        user.id, LANG_FROM, LANG_TO, limit=10
    )
    await update.message.reply_text(format_weak_words(words))


@require_message
async def forecast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/forecast` — show upcoming review workload."""
    user, db = await resolve_user_with_typing(update, context)

    days = await db.forecast(user.id, days=7)
    await update.message.reply_text(format_forecast(days))


@require_message
async def retention(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/retention` — show overall retention rate."""
    user, db = await resolve_user_with_typing(update, context)

    rate = await db.retention_rate(user.id, days=30)
    await update.message.reply_text(format_retention(rate))


_DAYS_MAP = {"1d": 1, "3d": 3, "7d": 7, "30d": 30}


@require_message
async def history(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/history [1d|3d|7d|30d]` — show recent answers."""
    user, db = await resolve_user_with_typing(update, context)

    text = (update.message.text or "").strip()
    parts = text.split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""

    since = None
    if arg in _DAYS_MAP:
        since = datetime.now(timezone.utc) - timedelta(
            days=_DAYS_MAP[arg]
        )

    records = await db.get_answer_history(
        user.id, limit=50, since=since,
    )

    words = await db.get_words(LANG_FROM, LANG_TO)
    user_words = await db.get_words(
        LANG_FROM, LANG_TO, owner_id=user.id,
    )
    word_map = {w.id: w.word_from for w in words + user_words}

    await update.message.reply_text(
        format_history(records, word_map)
    )


@require_message
async def export_progress(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/export` — send progress as a JSON file."""
    user, db = await resolve_user_with_typing(update, context)

    records = await db.export_progress(user.id)
    if not records:
        await update.message.reply_text(
            "No progress to export yet. "
            "Start a session with /play!"
        )
        return

    payload = json.dumps(records, indent=2)
    buf = io.BytesIO(payload.encode())
    buf.name = "rembrandt_progress.json"
    await update.message.reply_document(
        document=buf,
        caption=f"Exported {len(records)} card(s).",
    )


AWAITING_FILE = 10


@require_message_conv
async def import_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """`/import` — ask the user for a JSON file."""
    await resolve_user(update, context)

    await update.message.reply_text(
        "Send the JSON file exported with /export."
    )
    return AWAITING_FILE


@require_message_conv
async def import_file(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Receive the JSON file and restore progress."""
    user, db = await resolve_user_with_typing(update, context)

    doc = update.message.document
    if doc is None:
        await update.message.reply_text(
            "Please send a JSON file."
        )
        return AWAITING_FILE

    tg_file = await doc.get_file()
    data = await tg_file.download_as_bytearray()

    try:
        records = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        await update.message.reply_text(
            "Could not read the file. "
            "Please send a valid JSON file."
        )
        return ConversationHandler.END

    if not isinstance(records, list):
        await update.message.reply_text(
            "Invalid format: expected a JSON array."
        )
        return ConversationHandler.END

    for rec in records:
        rec["user_id"] = user.id

    count = await db.import_progress(records)
    await update.message.reply_text(
        f"Imported {count} card(s) successfully."
    )
    return ConversationHandler.END


async def import_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Cancel the /import conversation."""
    if update.message is not None:
        await update.message.reply_text("Cancelled.")
    return ConversationHandler.END
