"""Tests for rembrandt_chat.bot."""

from unittest.mock import AsyncMock, MagicMock, patch

from telegram import Update

import pytest

from rembrandt_chat.bot import (
    _BOT_COMMANDS,
    _error_handler,
    _load_base_vocab,
    _load_bundled_topics,
    _post_init,
)


# --- _post_init: bot commands ---


@pytest.mark.asyncio
async def test_post_init_sets_bot_commands(monkeypatch, tmp_path):
    monkeypatch.delenv("BASE_VOCAB_PATH", raising=False)
    monkeypatch.setenv("BUNDLED_VOCAB_DIR", str(tmp_path))

    db = AsyncMock()
    db.get_concepts.return_value = []
    db._conn = AsyncMock()
    db.get_languages.return_value = []

    with patch(
        "rembrandt_chat.bot.Database.connect",
        new_callable=AsyncMock,
        return_value=db,
    ):
        app = AsyncMock()
        app.bot_data = {}
        await _post_init(app)

    app.bot.set_my_commands.assert_called_once_with(
        _BOT_COMMANDS
    )


# --- _load_base_vocab ---


@pytest.mark.asyncio
async def test_load_base_vocab_imports_when_empty(monkeypatch):
    monkeypatch.setenv("BASE_VOCAB_PATH", "/data/vocab.csv")
    db = AsyncMock()
    db.get_concepts.return_value = []

    with patch(
        "rembrandt_chat.bot.import_concepts_csv",
        new_callable=AsyncMock,
        return_value=[],
    ) as mock_import:
        await _load_base_vocab(db)

    mock_import.assert_called_once_with(db, "/data/vocab.csv")


@pytest.mark.asyncio
async def test_load_base_vocab_skips_when_concepts_exist(
    monkeypatch,
):
    monkeypatch.setenv("BASE_VOCAB_PATH", "/data/vocab.csv")
    db = AsyncMock()
    db.get_concepts.return_value = [AsyncMock()]

    with patch(
        "rembrandt_chat.bot.import_concepts_csv",
        new_callable=AsyncMock,
    ) as mock_import:
        await _load_base_vocab(db)

    mock_import.assert_not_called()


@pytest.mark.asyncio
async def test_load_base_vocab_skips_when_no_path(monkeypatch):
    monkeypatch.delenv("BASE_VOCAB_PATH", raising=False)
    db = AsyncMock()

    with patch(
        "rembrandt_chat.bot.import_concepts_csv",
        new_callable=AsyncMock,
    ) as mock_import:
        await _load_base_vocab(db)

    mock_import.assert_not_called()
    db.get_concepts.assert_not_called()


# --- _load_bundled_topics ---


@pytest.mark.asyncio
async def test_load_bundled_topics_loads_when_empty(
    monkeypatch, tmp_path,
):
    vocab_csv = tmp_path / "vocab.csv"
    vocab_csv.write_text("front,back\n")
    topics_json = tmp_path / "topics.json"
    topics_json.write_text("[]")
    monkeypatch.setenv("BUNDLED_VOCAB_DIR", str(tmp_path))

    db = AsyncMock()
    db.get_concepts.return_value = []

    with (
        patch(
            "rembrandt_chat.bot.import_concepts_csv",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_import,
        patch(
            "rembrandt_chat.bot.load_topics",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_topics,
    ):
        await _load_bundled_topics(db)

    mock_import.assert_called_once()
    mock_topics.assert_called_once()


@pytest.mark.asyncio
async def test_load_bundled_topics_skips_when_concepts_exist(
    monkeypatch, tmp_path,
):
    vocab_csv = tmp_path / "vocab.csv"
    vocab_csv.write_text("front,back\n")
    topics_json = tmp_path / "topics.json"
    topics_json.write_text("[]")
    monkeypatch.setenv("BUNDLED_VOCAB_DIR", str(tmp_path))

    db = AsyncMock()
    db.get_concepts.return_value = [AsyncMock()]

    with patch(
        "rembrandt_chat.bot.import_concepts_csv",
        new_callable=AsyncMock,
    ) as mock_import:
        await _load_bundled_topics(db)

    mock_import.assert_not_called()


@pytest.mark.asyncio
async def test_load_bundled_topics_skips_when_files_missing(
    monkeypatch, tmp_path,
):
    monkeypatch.setenv("BUNDLED_VOCAB_DIR", str(tmp_path))
    db = AsyncMock()

    await _load_bundled_topics(db)

    db.get_concepts.assert_not_called()


# --- _error_handler ---


@pytest.mark.asyncio
async def test_error_handler_sends_message():
    update = MagicMock(spec=Update)
    update.effective_chat = AsyncMock()
    ctx = AsyncMock()
    ctx.error = RuntimeError("test")

    await _error_handler(update, ctx)

    update.effective_chat.send_message.assert_called_once()
    text = update.effective_chat.send_message.call_args[0][0]
    assert "wrong" in text.lower()


@pytest.mark.asyncio
async def test_error_handler_no_update():
    ctx = AsyncMock()
    ctx.error = RuntimeError("test")

    await _error_handler(None, ctx)
