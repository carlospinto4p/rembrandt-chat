"""Tests for rembrandt_chat.config."""

import pytest

from rembrandt_chat.config import get_bot_token, get_database_url


# --- get_bot_token ---


def test_get_bot_token_returns_value(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    assert get_bot_token() == "fake-token"


def test_get_bot_token_raises_when_missing(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        get_bot_token()


# --- get_database_url ---


def test_get_database_url_returns_value(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/test")
    assert get_database_url() == "postgresql://localhost/test"


def test_get_database_url_raises_when_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        get_database_url()
