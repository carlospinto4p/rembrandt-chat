"""Tests for rembrandt_chat.config."""

import pytest

from rembrandt_chat.config import (
    get_base_vocab_path,
    get_bot_token,
    get_bundled_vocab_dir,
    get_database_path,
    get_max_new_cards,
    get_max_review_cards,
)


# --- get_bot_token ---


def test_get_bot_token_returns_value(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    assert get_bot_token() == "fake-token"


def test_get_bot_token_raises_when_missing(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        get_bot_token()


# --- get_database_path ---


def test_get_database_path_returns_value(monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", "/data/rembrandt.db")
    assert get_database_path() == "/data/rembrandt.db"


def test_get_database_path_raises_when_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_PATH"):
        get_database_path()


# --- get_base_vocab_path ---


def test_get_base_vocab_path_returns_value(monkeypatch):
    monkeypatch.setenv("BASE_VOCAB_PATH", "/data/vocab.csv")
    assert get_base_vocab_path() == "/data/vocab.csv"


def test_get_base_vocab_path_returns_none_when_missing(monkeypatch):
    monkeypatch.delenv("BASE_VOCAB_PATH", raising=False)
    assert get_base_vocab_path() is None


def test_get_base_vocab_path_returns_none_when_empty(monkeypatch):
    monkeypatch.setenv("BASE_VOCAB_PATH", "")
    assert get_base_vocab_path() is None


# --- get_max_new_cards ---


def test_get_max_new_cards_returns_value(monkeypatch):
    monkeypatch.setenv("MAX_NEW_CARDS", "20")
    assert get_max_new_cards() == 20


def test_get_max_new_cards_defaults_to_zero(monkeypatch):
    monkeypatch.delenv("MAX_NEW_CARDS", raising=False)
    assert get_max_new_cards() == 0


# --- get_max_review_cards ---


def test_get_max_review_cards_returns_value(monkeypatch):
    monkeypatch.setenv("MAX_REVIEW_CARDS", "50")
    assert get_max_review_cards() == 50


def test_get_max_review_cards_defaults_to_zero(monkeypatch):
    monkeypatch.delenv("MAX_REVIEW_CARDS", raising=False)
    assert get_max_review_cards() == 0


# --- get_bundled_vocab_dir ---


def test_get_bundled_vocab_dir_returns_value(monkeypatch):
    monkeypatch.setenv("BUNDLED_VOCAB_DIR", "/data")
    assert get_bundled_vocab_dir() == "/data"


def test_get_bundled_vocab_dir_returns_none_when_missing(
    monkeypatch,
):
    monkeypatch.delenv("BUNDLED_VOCAB_DIR", raising=False)
    assert get_bundled_vocab_dir() is None


def test_get_bundled_vocab_dir_returns_none_when_empty(
    monkeypatch,
):
    monkeypatch.setenv("BUNDLED_VOCAB_DIR", "")
    assert get_bundled_vocab_dir() is None
