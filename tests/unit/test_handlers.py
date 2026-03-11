"""Tests for rembrandt_chat.handlers."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from rembrandt import Hint, SessionStats
from rembrandt.models import (
    DailyStats,
    ExerciseType,
    Lesson,
    LessonProgress,
    ReviewForecast,
    WeakWord,
)

from rembrandt_chat.formatting import MC_PREFIX, QUALITY_PREFIX, REVEAL_CB
from rembrandt_chat.handlers import (
    forecast,
    handle_answer_callback,
    handle_lesson_callback,
    handle_play_mode,
    lessons,
    retention,
    handle_answer_text,
    hint,
    play,
    skip,
    start,
    stats,
    stop,
    weak,
)

from .conftest import (
    make_answer_result,
    make_callback_update,
    make_context,
    make_exercise,
    make_update,
    make_word,
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


# --- /play ---


@pytest.mark.asyncio
async def test_play_shows_mode_keyboard():
    update = make_update()
    ctx = make_context()
    await play(update, ctx)

    call_kwargs = update.message.reply_text.call_args
    assert "mode" in call_kwargs[0][0].lower()
    kb = call_kwargs[1]["reply_markup"]
    flat = [btn for row in kb.inline_keyboard for btn in row]
    labels = [btn.text for btn in flat]
    assert "Mixed" in labels
    assert "Learn new" in labels
    assert "Review due" in labels


@pytest.mark.asyncio
async def test_play_rejects_when_session_active():
    update = make_update()
    ctx = make_context(session=MagicMock())
    await play(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "already have an active session" in text


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
        exercise_type=ExerciseType.REVERSE_FLASHCARD
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
    ex = make_exercise(exercise_type=ExerciseType.SELF_GRADED)

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
        exercise_type=ExerciseType.REVERSE_FLASHCARD
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
        exercise_type=ExerciseType.REVERSE_FLASHCARD
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

    await stats(update, ctx)

    ctx.bot_data["db"].daily_stats.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "2026-03-10" in text


@pytest.mark.asyncio
async def test_stats_empty():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].daily_stats.return_value = []

    await stats(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No activity" in text


# --- /weak ---


@pytest.mark.asyncio
async def test_weak_shows_words():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].weak_words.return_value = [
        WeakWord(
            word=make_word(),
            attempts=10,
            errors=7,
            error_rate=0.7,
            last_attempt=datetime.now(timezone.utc),
        ),
    ]

    await weak(update, ctx)

    ctx.bot_data["db"].weak_words.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "efimero" in text


@pytest.mark.asyncio
async def test_weak_empty():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].weak_words.return_value = []

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


# --- /lessons ---


def _lesson(
    lesson_id: int = 1, title: str = "A1 - Lesson 1",
) -> Lesson:
    return Lesson(
        id=lesson_id,
        title=title,
        language_from="es",
        language_to="es",
        word_ids=[1, 2, 3],
        word_count=3,
    )


def _lesson_progress(lesson_id: int = 1) -> LessonProgress:
    return LessonProgress(
        lesson_id=lesson_id,
        user_id=1,
        words_total=3,
        words_studied=2,
        words_mastered=1,
        completion_pct=66.7,
        mastery_pct=33.3,
    )


@pytest.mark.asyncio
async def test_lessons_shows_list():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].get_lessons.return_value = [
        _lesson(),
    ]

    with patch(
        "rembrandt_chat.session_handlers.lesson_progress",
        new_callable=AsyncMock,
        return_value=_lesson_progress(),
    ):
        await lessons(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "A1 - Lesson 1" in text
    assert "67%" in text


@pytest.mark.asyncio
async def test_lessons_empty():
    update = make_update()
    ctx = make_context()
    ctx.bot_data["db"].get_lessons.return_value = []

    await lessons(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No lessons available" in text


@pytest.mark.asyncio
async def test_lesson_callback_starts_session():
    update = make_callback_update("lesson:1")
    ctx = make_context()
    lesson = _lesson()
    ctx.bot_data["db"].get_lesson.return_value = lesson
    ex = make_exercise()

    with patch(
        "rembrandt_chat.session_handlers.Session"
    ) as MockSession:
        mock_session = MockSession.return_value
        mock_session.next_exercise = AsyncMock(
            return_value=ex
        )
        await handle_lesson_callback(update, ctx)

    assert ctx.user_data["session"] is mock_session
    assert ctx.user_data["exercise"] is ex
    MockSession.assert_called_once_with(
        db=ctx.bot_data["db"],
        user_id=1,
        language_from="es",
        language_to="es",
        word_ids=[1, 2, 3],
    )


@pytest.mark.asyncio
async def test_lesson_callback_not_found():
    update = make_callback_update("lesson:99")
    ctx = make_context()
    ctx.bot_data["db"].get_lesson.return_value = None

    await handle_lesson_callback(update, ctx)

    text = (
        update.callback_query
        .edit_message_text.call_args[0][0]
    )
    assert "not found" in text.lower()
