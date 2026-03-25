"""Tests for word management handlers."""

import pytest
from telegram.ext import ConversationHandler

from rembrandt_chat.formatting import DEL_CB_PREFIX
from unittest.mock import AsyncMock

from rembrandt_chat.handlers import (
    AWAITING_BULK_FILE,
    AWAITING_DEFINITION,
    AWAITING_TAGS,
    AWAITING_WORD,
    addword_cancel,
    addword_definition,
    addword_skip_tags,
    addword_start,
    addword_tags,
    addword_word,
    bulkimport_file,
    bulkimport_start,
    deleteword,
    handle_deleteword_callback,
    mywords,
    search,
)
from rembrandt_chat.word_handlers import (
    _parse_bulk_file,
)

from .conftest import (
    make_callback_update,
    make_concept,
    make_context,
    make_update,
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
async def test_addword_definition_asks_for_tags():
    update = make_update(text="Que dura poco tiempo")
    ctx = make_context()
    ctx.user_data["_addword_word"] = "efimero"

    state = await addword_definition(update, ctx)

    assert state == AWAITING_TAGS
    assert ctx.user_data["_addword_def"] == (
        "Que dura poco tiempo"
    )
    text = update.message.reply_text.call_args[0][0]
    assert "tags" in text.lower()


@pytest.mark.asyncio
async def test_addword_tags_saves_word():
    update = make_update(text="vocab, A1")
    ctx = make_context()
    ctx.user_data["_addword_word"] = "efimero"
    ctx.user_data["_addword_def"] = "Que dura poco tiempo"

    state = await addword_tags(update, ctx)

    assert state == ConversationHandler.END
    ctx.bot_data["db"].add_concept.assert_called_once_with(
        front="efimero",
        back="Que dura poco tiempo",
        tags=["vocab", "A1"],
        owner_id=1,
    )
    text = update.message.reply_text.call_args[0][0]
    assert "efimero" in text
    assert "vocab" in text


@pytest.mark.asyncio
async def test_addword_skip_tags_saves_without_tags():
    update = make_update(text="/skip")
    ctx = make_context()
    ctx.user_data["_addword_word"] = "efimero"
    ctx.user_data["_addword_def"] = "Que dura poco tiempo"

    state = await addword_skip_tags(update, ctx)

    assert state == ConversationHandler.END
    ctx.bot_data["db"].add_concept.assert_called_once_with(
        front="efimero",
        back="Que dura poco tiempo",
        tags=None,
        owner_id=1,
    )


@pytest.mark.asyncio
async def test_addword_empty_word_aborts():
    update = make_update(text="Que dura poco tiempo")
    ctx = make_context()
    ctx.user_data["_addword_word"] = ""

    state = await addword_definition(update, ctx)

    assert state == ConversationHandler.END
    ctx.bot_data["db"].add_concept.assert_not_called()


@pytest.mark.asyncio
async def test_addword_cancel():
    update = make_update()
    ctx = make_context()
    ctx.user_data["_addword_word"] = "something"
    ctx.user_data["_addword_def"] = "definition"

    state = await addword_cancel(update, ctx)

    assert state == ConversationHandler.END
    assert "_addword_word" not in ctx.user_data
    assert "_addword_def" not in ctx.user_data


# --- /mywords ---


@pytest.mark.asyncio
async def test_mywords_lists_words():
    update = make_update(text="/mywords")
    ctx = make_context()
    ctx.bot_data["db"].get_concepts.return_value = [
        make_concept(1, "efimero"),
        make_concept(2, "perpetuo"),
    ]

    await mywords(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "efimero" in text
    assert "perpetuo" in text


@pytest.mark.asyncio
async def test_mywords_shows_tags():
    update = make_update(text="/mywords")
    ctx = make_context()
    ctx.bot_data["db"].get_concepts.return_value = [
        make_concept(1, "efimero", tags=["vocab", "A1"]),
    ]

    await mywords(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "vocab" in text
    assert "A1" in text


@pytest.mark.asyncio
async def test_mywords_filters_by_tag():
    update = make_update(text="/mywords vocab")
    ctx = make_context()
    ctx.bot_data["db"].get_concepts.return_value = [
        make_concept(1, "efimero", tags=["vocab"]),
        make_concept(2, "perpetuo", tags=["other"]),
    ]

    await mywords(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "efimero" in text
    assert "perpetuo" not in text


@pytest.mark.asyncio
async def test_mywords_filter_no_match():
    update = make_update(text="/mywords nonexistent")
    ctx = make_context()
    ctx.bot_data["db"].get_concepts.return_value = [
        make_concept(1, "efimero", tags=["vocab"]),
    ]

    await mywords(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "nonexistent" in text


@pytest.mark.asyncio
async def test_mywords_empty():
    update = make_update(text="/mywords")
    ctx = make_context()
    ctx.bot_data["db"].get_concepts.return_value = []

    await mywords(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "no private words" in text.lower()


# --- /search ---


@pytest.mark.asyncio
async def test_search_finds_match():
    update = make_update(text="/search efimero")
    ctx = make_context()
    ctx.bot_data["db"].get_concepts.return_value = [
        make_concept(1, "efimero"),
        make_concept(2, "perpetuo"),
    ]

    await search(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "efimero" in text
    assert "perpetuo" not in text


@pytest.mark.asyncio
async def test_search_no_match():
    update = make_update(text="/search xyz")
    ctx = make_context()
    ctx.bot_data["db"].get_concepts.return_value = [
        make_concept(1, "efimero"),
    ]

    await search(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No results" in text


@pytest.mark.asyncio
async def test_search_no_term():
    update = make_update(text="/search")
    ctx = make_context()

    await search(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "Usage" in text


# --- /deleteword ---


@pytest.mark.asyncio
async def test_deleteword_shows_buttons():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].get_concepts.return_value = [
        make_concept(1, "efimero"),
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
    ctx.bot_data["db"].get_concepts.return_value = []

    await deleteword(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "no private words" in text.lower()


@pytest.mark.asyncio
async def test_deleteword_callback_deletes():
    update = make_callback_update(f"{DEL_CB_PREFIX}42")
    ctx = make_context()

    await handle_deleteword_callback(update, ctx)

    ctx.bot_data["db"].delete_concept.assert_called_once_with(
        42
    )
    update.callback_query.edit_message_text.assert_called_once()


# --- /bulkimport ---


@pytest.mark.asyncio
async def test_bulkimport_start_asks_for_file():
    update = make_update()
    ctx = make_context()
    state = await bulkimport_start(update, ctx)
    assert state == AWAITING_BULK_FILE
    text = update.message.reply_text.call_args[0][0]
    assert "file" in text.lower()


@pytest.mark.asyncio
async def test_bulkimport_csv():
    update = make_update()
    ctx = make_context()

    csv_content = "front,back\nhello,hola\nbye,adios\n"
    doc = AsyncMock()
    tg_file = AsyncMock()
    tg_file.download_as_bytearray.return_value = (
        csv_content.encode()
    )
    doc.get_file.return_value = tg_file
    update.message.document = doc

    state = await bulkimport_file(update, ctx)

    assert state == ConversationHandler.END
    assert ctx.bot_data["db"].add_concept.call_count == 2
    text = update.message.reply_text.call_args[0][0]
    assert "2 word" in text


@pytest.mark.asyncio
async def test_bulkimport_text():
    update = make_update()
    ctx = make_context()

    content = "hello \u2014 hola\nbye \u2014 adios\n"
    doc = AsyncMock()
    tg_file = AsyncMock()
    tg_file.download_as_bytearray.return_value = (
        content.encode()
    )
    doc.get_file.return_value = tg_file
    update.message.document = doc

    state = await bulkimport_file(update, ctx)

    assert state == ConversationHandler.END
    assert ctx.bot_data["db"].add_concept.call_count == 2


@pytest.mark.asyncio
async def test_bulkimport_empty_file():
    update = make_update()
    ctx = make_context()

    doc = AsyncMock()
    tg_file = AsyncMock()
    tg_file.download_as_bytearray.return_value = b""
    doc.get_file.return_value = tg_file
    update.message.document = doc

    state = await bulkimport_file(update, ctx)

    assert state == ConversationHandler.END
    text = update.message.reply_text.call_args[0][0]
    assert "No valid words" in text


# --- _parse_bulk_file ---


def test_parse_csv_with_header():
    text = "front,back,tags\nhello,hola,greetings\n"
    words = _parse_bulk_file(text)
    assert len(words) == 1
    assert words[0] == ("hello", "hola", ["greetings"])


def test_parse_csv_without_header():
    text = "hello,hola\nbye,adios\n"
    words = _parse_bulk_file(text)
    assert len(words) == 2


def test_parse_csv_tags_semicolon():
    text = "word,def,a;b;c\n"
    words = _parse_bulk_file(text)
    assert words[0][2] == ["a", "b", "c"]


def test_parse_text_emdash():
    text = "hello \u2014 hola\nbye \u2014 adios"
    words = _parse_bulk_file(text)
    assert len(words) == 2
    assert words[0] == ("hello", "hola", [])


def test_parse_text_hyphen():
    text = "hello - hola\n"
    words = _parse_bulk_file(text)
    assert len(words) == 1


def test_parse_empty():
    assert _parse_bulk_file("") == []
    assert _parse_bulk_file("  \n\n ") == []
