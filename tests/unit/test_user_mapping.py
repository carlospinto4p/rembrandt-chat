"""Tests for rembrandt_chat.user_mapping."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from rembrandt import User

from rembrandt_chat.user_mapping import (
    UserMapper,
    _display_name,
    _make_username,
)


# --- Helpers ---


def _telegram_user(
    user_id: int = 12345,
    first_name: str = "Alice",
    last_name: str | None = None,
) -> MagicMock:
    tg = MagicMock()
    tg.id = user_id
    tg.first_name = first_name
    tg.last_name = last_name
    return tg


def _rembrandt_user(
    user_id: int = 1,
    username: str = "tg_12345",
    display_name: str = "Alice",
) -> User:
    return User(
        id=user_id,
        username=username,
        display_name=display_name,
        password_hash="",
        created_at=datetime.now(timezone.utc),
    )


# --- _make_username ---


def test_make_username():
    assert _make_username(99) == "tg_99"


# --- _display_name ---


def test_display_name_first_only():
    tg = _telegram_user(first_name="Bob")
    assert _display_name(tg) == "Bob"


def test_display_name_first_and_last():
    tg = _telegram_user(first_name="Bob", last_name="Smith")
    assert _display_name(tg) == "Bob Smith"


def test_display_name_fallback():
    tg = _telegram_user(first_name="", last_name=None)
    assert _display_name(tg) == "tg_12345"


# --- UserMapper.ensure_user ---


@pytest.fixture
def mock_db():
    return MagicMock()


def test_ensure_user_returns_existing(mock_db):
    existing = _rembrandt_user()
    mock_db.get_user.return_value = existing

    mapper = UserMapper(mock_db)
    result = mapper.ensure_user(_telegram_user())

    assert result is existing
    mock_db.get_user.assert_called_once_with("tg_12345")
    mock_db.register_user.assert_not_called()


def test_ensure_user_registers_new(mock_db):
    mock_db.get_user.return_value = None
    registered = _rembrandt_user()
    mock_db.register_user.return_value = registered

    mapper = UserMapper(mock_db)
    result = mapper.ensure_user(_telegram_user())

    assert result is registered
    mock_db.get_user.assert_called_once_with("tg_12345")
    mock_db.register_user.assert_called_once()
    call_kwargs = mock_db.register_user.call_args
    assert call_kwargs[0][0] == "tg_12345"
    assert call_kwargs[1]["display_name"] == "Alice"
