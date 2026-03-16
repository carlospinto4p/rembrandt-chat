"""Tests for rembrandt_chat.bot."""

from unittest.mock import AsyncMock, patch

import pytest

from rembrandt_chat.bot import _load_base_vocab, _load_bundled_lessons


# --- _load_base_vocab ---


@pytest.mark.asyncio
async def test_load_base_vocab_imports_when_empty(monkeypatch):
    monkeypatch.setenv("BASE_VOCAB_PATH", "/data/vocab.csv")
    db = AsyncMock()
    db.get_words.return_value = []

    with patch(
        "rembrandt_chat.bot.import_words_csv",
        new_callable=AsyncMock,
        return_value=[],
    ) as mock_import:
        await _load_base_vocab(db)

    mock_import.assert_called_once_with(
        db, "/data/vocab.csv", "es", "es"
    )


@pytest.mark.asyncio
async def test_load_base_vocab_skips_when_words_exist(
    monkeypatch,
):
    monkeypatch.setenv("BASE_VOCAB_PATH", "/data/vocab.csv")
    db = AsyncMock()
    db.get_words.return_value = [AsyncMock()]

    with patch(
        "rembrandt_chat.bot.import_words_csv",
        new_callable=AsyncMock,
    ) as mock_import:
        await _load_base_vocab(db)

    mock_import.assert_not_called()


@pytest.mark.asyncio
async def test_load_base_vocab_skips_when_no_path(monkeypatch):
    monkeypatch.delenv("BASE_VOCAB_PATH", raising=False)
    db = AsyncMock()

    with patch(
        "rembrandt_chat.bot.import_words_csv",
        new_callable=AsyncMock,
    ) as mock_import:
        await _load_base_vocab(db)

    mock_import.assert_not_called()
    db.get_words.assert_not_called()


# --- _load_bundled_lessons ---


@pytest.mark.asyncio
async def test_load_bundled_lessons_loads_when_empty(
    monkeypatch, tmp_path,
):
    vocab_csv = tmp_path / "vocab.csv"
    vocab_csv.write_text("word_from,word_to\n")
    vocab_json = tmp_path / "vocab.json"
    vocab_json.write_text("[]")
    lessons_json = tmp_path / "lessons.json"
    lessons_json.write_text("[]")
    monkeypatch.setenv("BUNDLED_VOCAB_DIR", str(tmp_path))

    db = AsyncMock()
    db.get_words.return_value = []

    with (
        patch(
            "rembrandt_chat.bot.import_words_csv",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_import,
        patch(
            "rembrandt_chat.bot.load_lessons",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_lessons,
    ):
        await _load_bundled_lessons(db)

    mock_import.assert_called_once()
    mock_lessons.assert_called_once()


@pytest.mark.asyncio
async def test_load_bundled_lessons_skips_when_words_exist(
    monkeypatch, tmp_path,
):
    vocab_csv = tmp_path / "vocab.csv"
    vocab_csv.write_text("word_from,word_to\n")
    lessons_json = tmp_path / "lessons.json"
    lessons_json.write_text("[]")
    monkeypatch.setenv("BUNDLED_VOCAB_DIR", str(tmp_path))

    db = AsyncMock()
    db.get_words.return_value = [AsyncMock()]

    with patch(
        "rembrandt_chat.bot.import_words_csv",
        new_callable=AsyncMock,
    ) as mock_import:
        await _load_bundled_lessons(db)

    mock_import.assert_not_called()


@pytest.mark.asyncio
async def test_load_bundled_lessons_skips_when_files_missing(
    monkeypatch, tmp_path,
):
    monkeypatch.setenv("BUNDLED_VOCAB_DIR", str(tmp_path))
    db = AsyncMock()

    await _load_bundled_lessons(db)

    db.get_words.assert_not_called()
