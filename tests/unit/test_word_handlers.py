"""Tests for word management handlers."""

import pytest
from telegram.ext import ConversationHandler

from rembrandt_chat.formatting import DEL_CB_PREFIX
from rembrandt_chat.handlers import (
    AWAITING_DEFINITION,
    AWAITING_WORD,
    addword_cancel,
    addword_definition,
    addword_start,
    addword_word,
    deleteword,
    handle_deleteword_callback,
    mywords,
)

from .conftest import (
    make_callback_update,
    make_context,
    make_update,
    make_word,
)


# --- /addword conversation ---


@pytest.mark.asyncio
async def test_addword_start_asks_for_word():
    update = make_update()
    ctx = make_context()
    state = await addword_start(update, ctx)
    assert state == AWAITING_WORD
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Send the word" in text


@pytest.mark.asyncio
async def test_addword_word_stores_and_asks_definition():
    update = make_update(text="efimero")
    ctx = make_context()
    state = await addword_word(update, ctx)
    assert state == AWAITING_DEFINITION
    assert ctx.user_data["_addword_word"] == "efimero"
    text = update.message.reply_text.call_args[0][0]
    assert "definition" in text.lower()


@pytest.mark.asyncio
async def test_addword_definition_saves_word():
    update = make_update(text="Que dura poco tiempo")
    ctx = make_context()
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
    update = make_update(text="Que dura poco tiempo")
    ctx = make_context()
    ctx.user_data["_addword_word"] = ""

    state = await addword_definition(update, ctx)

    assert state == ConversationHandler.END
    ctx.bot_data["db"].add_word.assert_not_called()


@pytest.mark.asyncio
async def test_addword_cancel():
    update = make_update()
    ctx = make_context()
    ctx.user_data["_addword_word"] = "something"

    state = await addword_cancel(update, ctx)

    assert state == ConversationHandler.END
    assert "_addword_word" not in ctx.user_data


# --- /mywords ---


@pytest.mark.asyncio
async def test_mywords_lists_words():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].get_words.return_value = [
        make_word(1, "efimero"),
        make_word(2, "perpetuo"),
    ]

    await mywords(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "efimero" in text
    assert "perpetuo" in text


@pytest.mark.asyncio
async def test_mywords_empty():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].get_words.return_value = []

    await mywords(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "no private words" in text.lower()


# --- /deleteword ---


@pytest.mark.asyncio
async def test_deleteword_shows_buttons():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].get_words.return_value = [
        make_word(1, "efimero"),
    ]

    await deleteword(update, ctx)

    call_kwargs = update.message.reply_text.call_args
    kb = call_kwargs[1]["reply_markup"]
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert flat[0].text == "efimero"
    assert flat[0].callback_data == f"{DEL_CB_PREFIX}1"


@pytest.mark.asyncio
async def test_deleteword_empty():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].get_words.return_value = []

    await deleteword(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "no private words" in text.lower()


@pytest.mark.asyncio
async def test_deleteword_callback_deletes():
    update = make_callback_update(f"{DEL_CB_PREFIX}42")
    ctx = make_context()

    await handle_deleteword_callback(update, ctx)

    ctx.bot_data["db"].delete_word.assert_called_once_with(42)
    update.callback_query.edit_message_text.assert_called_once()
