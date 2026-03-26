"""Tests for rembrandt_chat.handlers."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from rembrandt import Hint, SessionStats
from rembrandt.models import (
    DailyStats,
    ExerciseType,
    ReviewForecast,
    WeakConcept,
)

from rembrandt_chat.formatting import MC_PREFIX, QUALITY_PREFIX, REVEAL_CB
from rembrandt_chat.handlers import (
    export_progress,
    forecast,
    handle_answer_callback,
    handle_language_callback,
    handle_play_language,
    handle_play_topic,
    handle_topic_callback,
    handle_play_mode,
    help_command,
    history,
    import_file,
    import_start,
    language,
    topics,
    reminders,
    retention,
    handle_answer_text,
    cancel,
    hint,
    play,
    review,
    skip,
    start,
    stats,
    stop,
    weak,
)

from .conftest import (
    make_answer_result,
    make_callback_update,
    make_concept,
    make_context,
    make_exercise,
    make_language,
    make_languages,
    make_topic,
    make_topic_progress,
    make_translation,
    make_update,
)



# --- /start ---


@pytest.mark.asyncio
async def test_start_greets_user():
    update = make_update()
    ctx = make_context()
    await start(update, ctx)
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Alice" in text


@pytest.mark.asyncio
async def test_start_no_effective_user():
    update = make_update(has_user=False)
    ctx = make_context()
    await start(update, ctx)
    update.message.reply_text.assert_not_called()


# --- /help ---


@pytest.mark.asyncio
async def test_help_lists_commands():
    update = make_update()
    ctx = make_context()
    await help_command(update, ctx)
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "/play" in text
    assert "/help" in text


# --- /cancel ---


@pytest.mark.asyncio
async def test_cancel_outside_conversation():
    update = make_update()
    ctx = make_context()
    await cancel(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "Nothing to cancel" in text


# --- /play ---


@pytest.mark.asyncio
async def test_play_shows_language_keyboard():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].get_languages.return_value = (
        make_languages()
    )

    await play(update, ctx)

    call_kwargs = update.message.reply_text.call_args
    assert "language" in call_kwargs[0][0].lower()
    kb = call_kwargs[1]["reply_markup"]
    flat = [btn for row in kb.inline_keyboard for btn in row]
    labels = [btn.text for btn in flat]
    assert "Spanish" in labels
    assert "English" in labels


@pytest.mark.asyncio
async def test_play_rejects_when_session_active():
    update = make_update()
    ctx = make_context(session=MagicMock())
    await play(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "already have an active session" in text


@pytest.mark.asyncio
async def test_play_language_shows_category_keyboard():
    update = make_callback_update("play_lang:es")
    ctx = make_context()

    await handle_play_language(update, ctx)

    assert ctx.user_data["language"] == "es"
    query = update.callback_query
    call_args = query.edit_message_text.call_args
    text = call_args[0][0]
    assert "categoría" in text.lower()
    kb = call_args[1]["reply_markup"]
    flat = [btn for row in kb.inline_keyboard for btn in row]
    labels = [btn.text for btn in flat]
    assert "Vocabulario" in labels


@pytest.mark.asyncio
async def test_play_topic_all_shows_mode_keyboard():
    update = make_callback_update("play_topic:all")
    ctx = make_context()

    await handle_play_topic(update, ctx)

    query = update.callback_query
    call_args = query.edit_message_text.call_args
    text = call_args[0][0]
    assert "All topics" in text
    assert "mode" in text.lower()
    kb = call_args[1]["reply_markup"]
    flat = [btn for row in kb.inline_keyboard for btn in row]
    labels = [btn.text for btn in flat]
    assert "Mixed" in labels
    assert "Learn new" in labels
    assert "Review due" in labels
    assert "_play_concept_ids" not in ctx.user_data


@pytest.mark.asyncio
async def test_play_topic_specific_shows_mode_keyboard():
    update = make_callback_update("play_topic:1")
    ctx = make_context()
    topic = make_topic()
    ctx.bot_data["db"].get_topic.return_value = topic

    await handle_play_topic(update, ctx)

    query = update.callback_query
    call_args = query.edit_message_text.call_args
    text = call_args[0][0]
    # topic_id=1 maps to "Data Science - Basics" in EN
    assert "Data Science - Basics" in text
    assert ctx.user_data["_play_concept_ids"] == [1, 2, 3]


@pytest.mark.asyncio
async def test_play_topic_not_found():
    update = make_callback_update("play_topic:99")
    ctx = make_context()
    ctx.bot_data["db"].get_topic.return_value = None

    await handle_play_topic(update, ctx)

    text = (
        update.callback_query
        .edit_message_text.call_args[0][0]
    )
    assert "not found" in text.lower()


@pytest.mark.asyncio
async def test_play_mode_creates_session():
    update = make_callback_update("play_mode:mixed")
    ctx = make_context()
    ex = make_exercise()

    with patch(
        "rembrandt_chat.session_handlers.Session"
    ) as MockSession:
        mock_session = MockSession.return_value
        mock_session.next_exercise = AsyncMock(
            return_value=ex
        )
        await handle_play_mode(update, ctx)

    assert ctx.user_data["session"] is mock_session
    assert ctx.user_data["exercise"] is ex


@pytest.mark.asyncio
async def test_play_mode_with_topic_passes_concept_ids():
    update = make_callback_update("play_mode:mixed")
    ctx = make_context()
    ctx.user_data["_play_concept_ids"] = [1, 2, 3]
    ex = make_exercise()

    with patch(
        "rembrandt_chat.session_handlers.Session"
    ) as MockSession:
        mock_session = MockSession.return_value
        mock_session.next_exercise = AsyncMock(
            return_value=ex
        )
        await handle_play_mode(update, ctx)

    call_kw = MockSession.call_args[1]
    assert call_kw["concept_ids"] == [1, 2, 3]
    assert "_play_concept_ids" not in ctx.user_data


@pytest.mark.asyncio
async def test_play_mode_with_language_builds_tr_map():
    update = make_callback_update("play_mode:mixed")
    ctx = make_context()
    ctx.user_data["language"] = "en"
    ex = make_exercise()
    tr = make_translation()
    ctx.bot_data["db"].get_translation.return_value = tr
    ctx.bot_data["db"].get_concepts.return_value = [
        make_concept(),
    ]

    with patch(
        "rembrandt_chat.session_handlers.Session"
    ) as MockSession:
        mock_session = MockSession.return_value
        mock_session.next_exercise = AsyncMock(
            return_value=ex
        )
        await handle_play_mode(update, ctx)

    assert ctx.user_data["translation"] is tr
    assert ctx.user_data["_translation_map"] == {
        "efimero": "ephemeral",
        "Que dura poco tiempo": "Lasting for a very short time",
    }


@pytest.mark.asyncio
async def test_play_mode_passes_review_config(monkeypatch):
    monkeypatch.setenv("MAX_NEW_CARDS", "10")
    monkeypatch.setenv("MAX_REVIEW_CARDS", "30")

    update = make_callback_update("play_mode:mixed")
    ctx = make_context()
    ex = make_exercise()

    with patch(
        "rembrandt_chat.session_handlers.Session"
    ) as MockSession:
        mock_session = MockSession.return_value
        mock_session.next_exercise = AsyncMock(
            return_value=ex
        )
        await handle_play_mode(update, ctx)

    call_kw = MockSession.call_args[1]
    rc = call_kw["review_config"]
    assert rc.max_new_cards == 10
    assert rc.max_review_cards == 30


@pytest.mark.asyncio
async def test_play_mode_no_words_available():
    update = make_callback_update("play_mode:learn_new")
    ctx = make_context()

    with patch(
        "rembrandt_chat.session_handlers.Session"
    ) as MockSession:
        MockSession.return_value.next_exercise = AsyncMock(
            return_value=None
        )
        await handle_play_mode(update, ctx)

    assert "session" not in ctx.user_data


# --- /review ---


@pytest.mark.asyncio
async def test_review_starts_session():
    update = make_update(text="/review")
    ex = make_exercise()
    ctx = make_context()
    ctx.user_data["_last_topic"] = {
        "user_id": 1,
        "concept_ids": [1, 2, 3],
    }

    with patch(
        "rembrandt_chat.session_handlers.Session",
    ) as mock_cls:
        session = mock_cls.return_value
        session.next_exercise = AsyncMock(return_value=ex)
        await review(update, ctx)

    assert ctx.user_data["session"] is session
    assert ctx.user_data["exercise"] is ex


@pytest.mark.asyncio
async def test_review_no_last_topic():
    update = make_update(text="/review")
    ctx = make_context()

    await review(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No previous topic" in text


@pytest.mark.asyncio
async def test_review_no_reviews_due():
    update = make_update(text="/review")
    ctx = make_context()
    ctx.user_data["_last_topic"] = {
        "user_id": 1,
        "concept_ids": [1, 2, 3],
    }

    with patch(
        "rembrandt_chat.session_handlers.Session",
    ) as mock_cls:
        session = mock_cls.return_value
        session.next_exercise = AsyncMock(
            return_value=None
        )
        await review(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No reviews due" in text


# --- /stop ---


@pytest.mark.asyncio
async def test_stop_shows_summary():
    session = MagicMock()
    session.summary.return_value = SessionStats(
        total=5, correct=4, incorrect=1,
        streak=2, best_streak=3, accuracy_pct=80.0,
    )
    update = make_update()
    ctx = make_context(session=session)

    await stop(update, ctx)

    assert "session" not in ctx.user_data
    text = update.message.reply_text.call_args[0][0]
    assert "80%" in text


@pytest.mark.asyncio
async def test_stop_no_session():
    update = make_update()
    ctx = make_context()
    await stop(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No active session" in text


# --- handle_answer_text ---


@pytest.mark.asyncio
async def test_answer_text_correct():
    session = MagicMock()
    session.answer = AsyncMock(
        return_value=make_answer_result(correct=True)
    )
    session.next_exercise = AsyncMock(
        return_value=make_exercise()
    )
    ex = make_exercise(
        exercise_type=ExerciseType.MULTIPLE_CHOICE
    )

    update = make_update(text="efimero")
    ctx = make_context(session=session, exercise=ex)

    await handle_answer_text(update, ctx)

    session.answer.assert_called_once_with(text="efimero")
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_answer_text_no_session():
    update = make_update(text="hello")
    ctx = make_context()
    await handle_answer_text(update, ctx)
    update.message.reply_text.assert_not_called()


# --- handle_answer_callback: multiple choice ---


@pytest.mark.asyncio
async def test_callback_multiple_choice():
    session = MagicMock()
    session.answer = AsyncMock(
        return_value=make_answer_result(correct=True)
    )
    session.next_exercise = AsyncMock(
        return_value=make_exercise()
    )
    ex = make_exercise()

    update = make_callback_update(f"{MC_PREFIX}0")
    ctx = make_context(session=session, exercise=ex)

    await handle_answer_callback(update, ctx)

    session.answer.assert_called_once_with(text="efimero")
    update.callback_query.edit_message_text.assert_called_once()


# --- handle_answer_callback: quality ---


@pytest.mark.asyncio
async def test_callback_quality():
    session = MagicMock()
    session.answer = AsyncMock(
        return_value=make_answer_result(correct=True)
    )
    session.next_exercise = AsyncMock(
        return_value=make_exercise()
    )
    ex = make_exercise(exercise_type=ExerciseType.FLASHCARD)

    update = make_callback_update(f"{QUALITY_PREFIX}4")
    ctx = make_context(session=session, exercise=ex)

    await handle_answer_callback(update, ctx)

    session.answer.assert_called_once_with(quality=4)


# --- handle_answer_callback: reveal ---


@pytest.mark.asyncio
async def test_callback_reveal():
    session = MagicMock()
    ex = make_exercise(exercise_type=ExerciseType.FLASHCARD)

    update = make_callback_update(REVEAL_CB)
    ctx = make_context(session=session, exercise=ex)

    await handle_answer_callback(update, ctx)

    session.answer.assert_not_called()
    update.callback_query.edit_message_text.assert_called_once()


# --- session ends when no more exercises ---


@pytest.mark.asyncio
async def test_session_ends_on_last_exercise():
    session = MagicMock()
    session.answer = AsyncMock(
        return_value=make_answer_result(correct=True)
    )
    session.next_exercise = AsyncMock(return_value=None)
    session.summary.return_value = SessionStats(
        total=1, correct=1, incorrect=0,
        streak=1, best_streak=1, accuracy_pct=100.0,
    )
    ex = make_exercise(
        exercise_type=ExerciseType.MULTIPLE_CHOICE
    )

    update = make_update(text="efimero")
    ctx = make_context(session=session, exercise=ex)

    await handle_answer_text(update, ctx)

    assert "session" not in ctx.user_data


# --- /hint ---


@pytest.mark.asyncio
async def test_hint_returns_pattern():
    session = MagicMock()
    session.hint.return_value = Hint(
        first_letter="e",
        word_length=7,
        pattern="ef_____",
        reveal_count=2,
    )
    ex = make_exercise(
        exercise_type=ExerciseType.MULTIPLE_CHOICE
    )
    update = make_update()
    ctx = make_context(session=session, exercise=ex)

    await hint(update, ctx)

    session.hint.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "ef_____" in text


@pytest.mark.asyncio
async def test_hint_no_session():
    update = make_update()
    ctx = make_context()
    await hint(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No active session" in text


@pytest.mark.asyncio
async def test_hint_no_exercise():
    update = make_update()
    ctx = make_context(session=MagicMock())
    await hint(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No active exercise" in text


# --- /skip ---


@pytest.mark.asyncio
async def test_skip_advances_to_next():
    session = MagicMock()
    skipped_ex = make_exercise()
    session.skip.return_value = skipped_ex
    session.next_exercise = AsyncMock(
        return_value=make_exercise()
    )

    update = make_update()
    ctx = make_context(session=session, exercise=skipped_ex)

    await skip(update, ctx)

    session.skip.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Skipped" in text
    assert "efimero" in text


@pytest.mark.asyncio
async def test_skip_no_session():
    update = make_update()
    ctx = make_context()
    await skip(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No active session" in text


@pytest.mark.asyncio
async def test_skip_no_exercise():
    update = make_update()
    ctx = make_context(session=MagicMock())
    await skip(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No active exercise" in text


# --- /stats ---


@pytest.mark.asyncio
async def test_stats_shows_daily():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].daily_stats.return_value = [
        DailyStats(
            date="2026-03-10", answers=20,
            correct=18, accuracy_pct=90.0,
        ),
    ]
    ctx.bot_data["db"].get_topics.return_value = []

    await stats(update, ctx)

    assert ctx.bot_data["db"].daily_stats.call_count == 2
    text = update.message.reply_text.call_args[0][0]
    assert "2026-03-10" in text


@pytest.mark.asyncio
async def test_stats_empty():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].daily_stats.return_value = []
    ctx.bot_data["db"].get_topics.return_value = []

    await stats(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No activity" in text


# --- /weak ---


@pytest.mark.asyncio
async def test_weak_shows_concepts():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].weak_concepts.return_value = [
        WeakConcept(
            concept=make_concept(),
            attempts=10,
            errors=7,
            error_rate=0.7,
            last_attempt=datetime.now(timezone.utc),
        ),
    ]

    await weak(update, ctx)

    ctx.bot_data["db"].weak_concepts.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "efimero" in text


@pytest.mark.asyncio
async def test_weak_empty():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].weak_concepts.return_value = []

    await weak(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No weak words" in text


# --- /forecast ---


@pytest.mark.asyncio
async def test_forecast_shows_days():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].forecast.return_value = [
        ReviewForecast(date="2026-03-11", due_count=15),
        ReviewForecast(date="2026-03-12", due_count=8),
    ]

    await forecast(update, ctx)

    ctx.bot_data["db"].forecast.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "2026-03-11" in text
    assert "15" in text


@pytest.mark.asyncio
async def test_forecast_empty():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].forecast.return_value = []

    await forecast(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No reviews scheduled" in text


# --- /retention ---


@pytest.mark.asyncio
async def test_retention_shows_rate():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].retention_rate.return_value = 85.0

    await retention(update, ctx)

    ctx.bot_data["db"].retention_rate.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "85%" in text


@pytest.mark.asyncio
async def test_retention_no_answers():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].retention_rate.return_value = 0.0

    await retention(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No answers recorded" in text


# --- /topics ---


@pytest.mark.asyncio
async def test_topics_shows_categories():
    update = make_update()
    ctx = make_context()

    await topics(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "category" in text.lower()
    kb = update.message.reply_text.call_args[1][
        "reply_markup"
    ]
    flat = [btn for row in kb.inline_keyboard for btn in row]
    labels = [btn.text for btn in flat]
    assert "Vocabulary" in labels
    assert "Culture" in labels


@pytest.mark.asyncio
async def test_topic_callback_starts_session():
    update = make_callback_update("topic:1")
    ctx = make_context()
    topic = make_topic()
    ctx.bot_data["db"].get_topic.return_value = topic
    ex = make_exercise()

    with patch(
        "rembrandt_chat.session_handlers.Session"
    ) as MockSession:
        mock_session = MockSession.return_value
        mock_session.next_exercise = AsyncMock(
            return_value=ex
        )
        await handle_topic_callback(update, ctx)

    assert ctx.user_data["session"] is mock_session
    assert ctx.user_data["exercise"] is ex
    MockSession.assert_called_once_with(
        db=ctx.bot_data["db"],
        user_id=1,
        concept_ids=[1, 2, 3],
        review_config=None,
    )


@pytest.mark.asyncio
async def test_topic_callback_not_found():
    update = make_callback_update("topic:99")
    ctx = make_context()
    ctx.bot_data["db"].get_topic.return_value = None

    await handle_topic_callback(update, ctx)

    text = (
        update.callback_query
        .edit_message_text.call_args[0][0]
    )
    assert "not found" in text.lower()


# --- /export ---


@pytest.mark.asyncio
async def test_export_sends_file():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].export_progress.return_value = [
        {"concept_id": 1, "easiness_factor": 2.5},
    ]

    await export_progress(update, ctx)

    ctx.bot_data["db"].export_progress.assert_called_once()
    update.message.reply_document.assert_called_once()
    call_kw = update.message.reply_document.call_args
    assert "1 card" in call_kw[1]["caption"]


@pytest.mark.asyncio
async def test_export_empty():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].export_progress.return_value = []

    await export_progress(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No progress" in text


# --- /import ---


@pytest.mark.asyncio
async def test_import_start_asks_for_file():
    update = make_update()
    ctx = make_context()

    from rembrandt_chat.stats_handlers import AWAITING_FILE

    result = await import_start(update, ctx)

    assert result == AWAITING_FILE
    text = update.message.reply_text.call_args[0][0]
    assert "JSON file" in text


@pytest.mark.asyncio
async def test_import_file_success():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].import_progress.return_value = 3

    mock_doc = AsyncMock()
    mock_tg_file = AsyncMock()
    mock_tg_file.download_as_bytearray.return_value = (
        b'[{"concept_id":1},{"concept_id":2},'
        b'{"concept_id":3}]'
    )
    mock_doc.get_file.return_value = mock_tg_file
    update.message.document = mock_doc

    from telegram.ext import ConversationHandler

    result = await import_file(update, ctx)

    assert result == ConversationHandler.END
    ctx.bot_data["db"].import_progress.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "3 card" in text


@pytest.mark.asyncio
async def test_import_file_invalid_json():
    update = make_update()
    ctx = make_context()

    mock_doc = AsyncMock()
    mock_tg_file = AsyncMock()
    mock_tg_file.download_as_bytearray.return_value = (
        b"not json"
    )
    mock_doc.get_file.return_value = mock_tg_file
    update.message.document = mock_doc

    from telegram.ext import ConversationHandler

    result = await import_file(update, ctx)

    assert result == ConversationHandler.END
    text = update.message.reply_text.call_args[0][0]
    assert "Could not read" in text


@pytest.mark.asyncio
async def test_import_file_not_array():
    update = make_update()
    ctx = make_context()

    mock_doc = AsyncMock()
    mock_tg_file = AsyncMock()
    mock_tg_file.download_as_bytearray.return_value = (
        b'{"not": "an array"}'
    )
    mock_doc.get_file.return_value = mock_tg_file
    update.message.document = mock_doc

    from telegram.ext import ConversationHandler

    result = await import_file(update, ctx)

    assert result == ConversationHandler.END
    text = update.message.reply_text.call_args[0][0]
    assert "expected a JSON array" in text


# --- /history ---


@pytest.mark.asyncio
async def test_history_shows_answers():
    from rembrandt import AnswerHistory

    update = make_update(text="/history")
    ctx = make_context()
    ctx.bot_data["db"].get_answer_history.return_value = [
        AnswerHistory(
            user_id=1,
            concept_id=1,
            exercise_type="multiple_choice",
            correct=True,
            quality=5,
        ),
    ]
    ctx.bot_data["db"].get_concepts.return_value = [
        make_concept(1, "efimero"),
    ]

    await history(update, ctx)

    ctx.bot_data["db"].get_answer_history.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "efimero" in text


@pytest.mark.asyncio
async def test_history_empty():
    update = make_update(text="/history")
    ctx = make_context()
    ctx.bot_data["db"].get_answer_history.return_value = []
    ctx.bot_data["db"].get_concepts.return_value = []

    await history(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No answer history" in text


@pytest.mark.asyncio
async def test_history_with_date_filter():
    update = make_update(text="/history 7d")
    ctx = make_context()
    ctx.bot_data["db"].get_answer_history.return_value = []
    ctx.bot_data["db"].get_concepts.return_value = []

    await history(update, ctx)

    call_kw = (
        ctx.bot_data["db"]
        .get_answer_history.call_args[1]
    )
    assert call_kw["since"] is not None


# --- typing indicator ---


@pytest.mark.asyncio
async def test_stats_sends_typing():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].daily_stats.return_value = []

    await stats(update, ctx)

    update.effective_chat.send_action.assert_called_once()


@pytest.mark.asyncio
async def test_export_sends_typing():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].export_progress.return_value = []

    await export_progress(update, ctx)

    update.effective_chat.send_action.assert_called_once()


# --- /language ---


@pytest.mark.asyncio
async def test_language_shows_options():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].get_languages.return_value = (
        make_languages()
    )

    await language(update, ctx)

    call_kwargs = update.message.reply_text.call_args
    assert "language" in call_kwargs[0][0].lower()
    kb = call_kwargs[1]["reply_markup"]
    flat = [btn for row in kb.inline_keyboard for btn in row]
    labels = [btn.text for btn in flat]
    assert "Spanish" in labels
    assert "English" in labels


@pytest.mark.asyncio
async def test_language_callback_stores_choice():
    update = make_callback_update("lang:en")
    ctx = make_context()
    ctx.bot_data["db"].get_language.return_value = (
        make_language("en", "English")
    )

    await handle_language_callback(update, ctx)

    assert ctx.user_data["language"] == "en"
    text = (
        update.callback_query
        .edit_message_text.call_args[0][0]
    )
    assert "English" in text


# --- /reminders ---


@pytest.mark.asyncio
async def test_reminders_on():
    update = make_update(text="/reminders on 08:30")
    ctx = make_context()
    ctx.job_queue = MagicMock()
    ctx.job_queue.get_jobs_by_name.return_value = []

    await reminders(update, ctx)

    ctx.job_queue.run_daily.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "08:30" in text


@pytest.mark.asyncio
async def test_reminders_off():
    update = make_update(text="/reminders off")
    ctx = make_context()
    mock_job = MagicMock()
    ctx.job_queue = MagicMock()
    ctx.job_queue.get_jobs_by_name.return_value = [mock_job]

    await reminders(update, ctx)

    mock_job.schedule_removal.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "disabled" in text.lower()


@pytest.mark.asyncio
async def test_reminders_status_off():
    update = make_update(text="/reminders")
    ctx = make_context()
    ctx.job_queue = MagicMock()
    ctx.job_queue.get_jobs_by_name.return_value = []

    await reminders(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "OFF" in text


@pytest.mark.asyncio
async def test_reminders_status_on():
    update = make_update(text="/reminders")
    ctx = make_context()
    ctx.job_queue = MagicMock()
    ctx.job_queue.get_jobs_by_name.return_value = [MagicMock()]

    await reminders(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "ON" in text


# --- session persistence (require_session restoration) ---


@pytest.mark.asyncio
async def test_require_session_restores_from_config():
    """After a restart, require_session recreates session."""
    from rembrandt_chat._helpers import require_session
    from rembrandt_chat.persistence import SESSION_CONFIG

    ex = make_exercise()
    session_mock = MagicMock()
    session_mock.next_exercise = AsyncMock(return_value=ex)

    ctx = make_context()
    ctx.user_data[SESSION_CONFIG] = {
        "user_id": 1,
        "tg_id": 12345,
        "mode": "mixed",
        "concept_ids": None,
    }

    with patch(
        "rembrandt_chat._helpers.Session",
        return_value=session_mock,
    ):
        result = await require_session(ctx)

    assert result is not None
    session, user_data = result
    assert session is session_mock
    assert user_data["exercise"] is ex
