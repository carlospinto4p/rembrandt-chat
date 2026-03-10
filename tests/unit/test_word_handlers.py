"""Tests for word management handlers."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from rembrandt import User, Word
from telegram.ext import ConversationHandler

from rembrandt_chat.handlers import (
    AWAITING_DEFINITION,
    AWAITING_WORD,
    DEL_CB_PREFIX,
    addword_cancel,
    addword_definition,
    addword_start,
    addword_word,
    deleteword,
    handle_deleteword_callback,
    mywords,
)
from rembrandt_chat.user_mapping import UserMapper


# --- Helpers ---


def _user() -> User:
    return User(
        id=1,
        username="tg_12345",
        display_name="Alice",
        password_hash="",
        created_at=datetime.now(timezone.utc),
    )


def _word(word_id: int = 1, word_from: str = "efimero") -> Word:
    return Word(
        id=word_id,
        language_from="es",
        language_to="es",
        word_from=word_from,
        word_to="Que dura poco tiempo",
        tags=[],
        owner_id=1,
    )


def _context() -> MagicMock:
    mapper = MagicMock(spec=UserMapper)
    mapper.ensure_user.return_value = _user()
    ctx = MagicMock()
    ctx.bot_data = {"user_mapper": mapper, "db": MagicMock()}
    ctx.user_data = {}
    return ctx


def _update(text: str = "") -> MagicMock:
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    update.message = AsyncMock()
    update.message.text = text
    return update


def _callback_update(data: str) -> MagicMock:
    update = MagicMock()
    update.callback_query = AsyncMock()
    update.callback_query.data = data
    return update


# --- /addword conversation ---


@pytest.mark.asyncio
async def test_addword_start_asks_for_word():
    update = _update()
    ctx = _context()
    state = await addword_start(update, ctx)
    assert state == AWAITING_WORD
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Send the word" in text


@pytest.mark.asyncio
async def test_addword_word_stores_and_asks_definition():
    update = _update(text="efimero")
    ctx = _context()
    state = await addword_word(update, ctx)
    assert state == AWAITING_DEFINITION
    assert ctx.user_data["_addword_word"] == "efimero"
    text = update.message.reply_text.call_args[0][0]
    assert "definition" in text.lower()


@pytest.mark.asyncio
async def test_addword_definition_saves_word():
    update = _update(text="Que dura poco tiempo")
    ctx = _context()
    ctx.user_data["_addword_word"] = "efimero"

    state = await addword_definition(update, ctx)

    assert state == ConversationHandler.END
    ctx.bot_data["db"].add_word.assert_called_once_with(
        language_from="es",
        language_to="es",
        word_from="efimero",
        word_to="Que dura poco tiempo",
        owner_id=1,
    )
    text = update.message.reply_text.call_args[0][0]
    assert "efimero" in text


@pytest.mark.asyncio
async def test_addword_empty_word_aborts():
    update = _update(text="Que dura poco tiempo")
    ctx = _context()
    ctx.user_data["_addword_word"] = ""

    state = await addword_definition(update, ctx)

    assert state == ConversationHandler.END
    ctx.bot_data["db"].add_word.assert_not_called()


@pytest.mark.asyncio
async def test_addword_cancel():
    update = _update()
    ctx = _context()
    ctx.user_data["_addword_word"] = "something"

    state = await addword_cancel(update, ctx)

    assert state == ConversationHandler.END
    assert "_addword_word" not in ctx.user_data


# --- /mywords ---


@pytest.mark.asyncio
async def test_mywords_lists_words():
    update = _update()
    ctx = _context()
    ctx.bot_data["db"].get_words.return_value = [
        _word(1, "efimero"),
        _word(2, "perpetuo"),
    ]

    await mywords(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "efimero" in text
    assert "perpetuo" in text


@pytest.mark.asyncio
async def test_mywords_empty():
    update = _update()
    ctx = _context()
    ctx.bot_data["db"].get_words.return_value = []

    await mywords(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "no private words" in text.lower()


# --- /deleteword ---


@pytest.mark.asyncio
async def test_deleteword_shows_buttons():
    update = _update()
    ctx = _context()
    ctx.bot_data["db"].get_words.return_value = [
        _word(1, "efimero"),
    ]

    await deleteword(update, ctx)

    call_kwargs = update.message.reply_text.call_args
    kb = call_kwargs[1]["reply_markup"]
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert flat[0].text == "efimero"
    assert flat[0].callback_data == f"{DEL_CB_PREFIX}1"


@pytest.mark.asyncio
async def test_deleteword_empty():
    update = _update()
    ctx = _context()
    ctx.bot_data["db"].get_words.return_value = []

    await deleteword(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "no private words" in text.lower()


@pytest.mark.asyncio
async def test_deleteword_callback_deletes():
    update = _callback_update(f"{DEL_CB_PREFIX}42")
    ctx = _context()

    await handle_deleteword_callback(update, ctx)

    ctx.bot_data["db"].delete_word.assert_called_once_with(42)
    update.callback_query.edit_message_text.assert_called_once()
