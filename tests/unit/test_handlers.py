"""Tests for rembrandt_chat.handlers."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from rembrandt import User

from rembrandt_chat.handlers import start
from rembrandt_chat.user_mapping import UserMapper


def _rembrandt_user(display_name: str = "Alice") -> User:
    return User(
        id=1,
        username="tg_12345",
        display_name=display_name,
        password_hash="",
        created_at=datetime.now(timezone.utc),
    )


def _make_update_and_context(
    user: User,
    *,
    has_effective_user: bool = True,
    has_message: bool = True,
) -> tuple[MagicMock, MagicMock]:
    mapper = MagicMock(spec=UserMapper)
    mapper.ensure_user.return_value = user

    context = MagicMock()
    context.bot_data = {"user_mapper": mapper}

    update = MagicMock()
    if has_effective_user:
        update.effective_user = MagicMock()
        update.effective_user.id = 12345
    else:
        update.effective_user = None

    if has_message:
        update.message = AsyncMock()
    else:
        update.message = None

    return update, context


# --- /start handler ---


@pytest.mark.asyncio
async def test_start_greets_user():
    user = _rembrandt_user("Alice")
    update, context = _make_update_and_context(user)

    await start(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Alice" in text
    assert "/play" in text


@pytest.mark.asyncio
async def test_start_uses_username_when_no_display_name():
    user = _rembrandt_user(display_name="")
    # When display_name is falsy, fallback to username
    update, context = _make_update_and_context(user)

    await start(update, context)

    text = update.message.reply_text.call_args[0][0]
    assert "tg_12345" in text


@pytest.mark.asyncio
async def test_start_no_effective_user():
    user = _rembrandt_user()
    update, context = _make_update_and_context(
        user, has_effective_user=False
    )

    await start(update, context)

    update.message.reply_text.assert_not_called()


@pytest.mark.asyncio
async def test_start_no_message():
    user = _rembrandt_user()
    update, context = _make_update_and_context(
        user, has_message=False
    )

    await start(update, context)
