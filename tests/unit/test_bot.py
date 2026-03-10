"""Tests for rembrandt_chat.bot."""

from unittest.mock import MagicMock, patch

from rembrandt_chat.bot import _load_base_vocab


# --- _load_base_vocab ---


def test_load_base_vocab_imports_when_empty(monkeypatch):
    monkeypatch.setenv("BASE_VOCAB_PATH", "/data/vocab.csv")
    db = MagicMock()
    db.get_words.return_value = []

    with patch(
        "rembrandt_chat.bot.import_words_csv", return_value=[]
    ) as mock_import:
        _load_base_vocab(db)

    mock_import.assert_called_once_with(
        db, "/data/vocab.csv", "es", "es"
    )


def test_load_base_vocab_skips_when_words_exist(monkeypatch):
    monkeypatch.setenv("BASE_VOCAB_PATH", "/data/vocab.csv")
    db = MagicMock()
    db.get_words.return_value = [MagicMock()]

    with patch(
        "rembrandt_chat.bot.import_words_csv"
    ) as mock_import:
        _load_base_vocab(db)

    mock_import.assert_not_called()


def test_load_base_vocab_skips_when_no_path(monkeypatch):
    monkeypatch.delenv("BASE_VOCAB_PATH", raising=False)
    db = MagicMock()

    with patch(
        "rembrandt_chat.bot.import_words_csv"
    ) as mock_import:
        _load_base_vocab(db)

    mock_import.assert_not_called()
    db.get_words.assert_not_called()
