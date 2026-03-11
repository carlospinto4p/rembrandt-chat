"""Statistics handlers."""

from telegram import Update
from telegram.ext import ContextTypes

from rembrandt_chat._helpers import resolve_user
from rembrandt_chat.config import LANG_FROM, LANG_TO
from rembrandt_chat.formatting import (
    format_daily_stats,
    format_forecast,
    format_retention,
    format_weak_words,
)


async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/stats` — show daily stats."""
    if update.effective_user is None or update.message is None:
        return

    user, db = await resolve_user(update, context)

    daily = await db.daily_stats(user.id, days=7)
    await update.message.reply_text(format_daily_stats(daily))


async def weak(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/weak` — show weakest words."""
    if update.effective_user is None or update.message is None:
        return

    user, db = await resolve_user(update, context)

    words = await db.weak_words(
        user.id, LANG_FROM, LANG_TO, limit=10
    )
    await update.message.reply_text(format_weak_words(words))


async def forecast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/forecast` — show upcoming review workload."""
    if update.effective_user is None or update.message is None:
        return

    user, db = await resolve_user(update, context)

    days = await db.forecast(user.id, days=7)
    await update.message.reply_text(format_forecast(days))


async def retention(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/retention` — show overall retention rate."""
    if update.effective_user is None or update.message is None:
        return

    user, db = await resolve_user(update, context)

    rate = await db.retention_rate(user.id, days=30)
    await update.message.reply_text(format_retention(rate))
