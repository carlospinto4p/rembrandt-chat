"""Statistics handlers."""

import asyncio
import io
import json
import logging
from datetime import datetime, time, timedelta, timezone

from rembrandt import Database, topic_progress
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from rembrandt_chat._helpers import (
    require_message,
    require_message_conv,
    resolve_user,
    resolve_user_with_typing,
)
from rembrandt_chat.formatting import (
    compute_streak,
    format_daily_stats,
    format_forecast,
    format_history,
    format_retention,
    format_topic_progress,
    format_weak_concepts,
)

log = logging.getLogger(__name__)


@require_message
async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/stats` — show daily stats and topic progress."""
    user, db = await resolve_user_with_typing(update, context)

    daily, streak_days, all_topics = await asyncio.gather(
        db.daily_stats(user.id, days=7),
        db.daily_stats(user.id, days=365),
        db.get_topics(),
    )
    streak = compute_streak(streak_days)
    text = format_daily_stats(daily, streak=streak)

    if all_topics:
        progress = await asyncio.gather(
            *(
                topic_progress(db, user.id, t)
                for t in all_topics
            )
        )
        studied = [
            (t, p) for t, p in zip(all_topics, progress)
            if p.completion_pct > 0
        ]
        if studied:
            topics_list, prog_list = zip(*studied)
            tp_text = format_topic_progress(
                list(topics_list), list(prog_list),
            )
            text += "\n\n" + tp_text

    await update.message.reply_text(text)


@require_message
async def weak(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/weak` — show weakest words."""
    user, db = await resolve_user_with_typing(update, context)

    concepts = await db.weak_concepts(user.id, limit=10)
    await update.message.reply_text(
        format_weak_concepts(concepts)
    )


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

    records, concepts, user_concepts = await asyncio.gather(
        db.get_answer_history(
            user.id, limit=50, since=since,
        ),
        db.get_concepts(),
        db.get_concepts(owner_id=user.id),
    )
    concept_map = {
        c.id: c.front for c in concepts + user_concepts
    }

    await update.message.reply_text(
        format_history(records, concept_map)
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


# --- Daily reminders ---

_REMINDER_JOB = "reminder_{chat_id}"
_DEFAULT_HOUR = 9
_DEFAULT_MINUTE = 0


def _parse_reminder_args(
    text: str,
) -> tuple[str, int, int]:
    """Parse ``/reminders [on [HH:MM]|off]``.

    :return: ``(action, hour, minute)`` where action is
        ``"on"``, ``"off"``, or ``"status"``.
    """
    parts = text.strip().split()
    # parts[0] is "/reminders"
    if len(parts) < 2:
        return "status", _DEFAULT_HOUR, _DEFAULT_MINUTE

    action = parts[1].lower()
    if action == "off":
        return "off", _DEFAULT_HOUR, _DEFAULT_MINUTE

    hour, minute = _DEFAULT_HOUR, _DEFAULT_MINUTE
    if len(parts) >= 3:
        try:
            h, m = parts[2].split(":")
            hour, minute = int(h), int(m)
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                hour, minute = _DEFAULT_HOUR, _DEFAULT_MINUTE
        except (ValueError, TypeError):
            pass

    return "on", hour, minute


async def _reminder_callback(
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Job callback: check due reviews and notify user."""
    job = context.job
    chat_id = job.chat_id
    data = job.data or {}
    user_id = data.get("user_id")
    db: Database = context.bot_data["db"]

    try:
        days = await db.forecast(user_id, days=1)
        due = days[0].due_count if days else 0
    except Exception:
        log.exception("Reminder: failed to fetch forecast")
        return

    if due > 0:
        await context.bot.send_message(
            chat_id,
            f"You have {due} review(s) due today! "
            "Use /play to start.",
        )


@require_message
async def reminders(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/reminders [on [HH:MM]|off]` — manage reminders."""
    user, _ = await resolve_user(update, context)
    chat_id = update.effective_chat.id
    job_name = _REMINDER_JOB.format(chat_id=chat_id)
    text = update.message.text or ""

    action, hour, minute = _parse_reminder_args(text)

    if action == "off":
        jobs = context.job_queue.get_jobs_by_name(job_name)
        for j in jobs:
            j.schedule_removal()
        await update.message.reply_text(
            "Daily reminders disabled."
        )
        return

    if action == "status":
        jobs = context.job_queue.get_jobs_by_name(job_name)
        if jobs:
            await update.message.reply_text(
                "Reminders are ON.\n"
                "Use /reminders off to disable."
            )
        else:
            await update.message.reply_text(
                "Reminders are OFF.\n"
                "Use /reminders on [HH:MM] to enable "
                "(default 09:00 UTC)."
            )
        return

    # action == "on"
    jobs = context.job_queue.get_jobs_by_name(job_name)
    for j in jobs:
        j.schedule_removal()

    context.job_queue.run_daily(
        _reminder_callback,
        time=time(hour=hour, minute=minute, tzinfo=timezone.utc),
        chat_id=chat_id,
        name=job_name,
        data={"user_id": user.id},
    )
    await update.message.reply_text(
        f"Daily reminders enabled at "
        f"{hour:02d}:{minute:02d} UTC."
    )
