"""Tests for rembrandt_chat.handlers."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from rembrandt import Hint, SessionStats, User, Word
from rembrandt.models import (
    AnswerResult,
    DailyStats,
    Exercise,
    ExerciseType,
    WeakWord,
)

from rembrandt_chat.formatting import MC_PREFIX, QUALITY_PREFIX, REVEAL_CB
from rembrandt_chat.handlers import (
    handle_answer_callback,
    handle_answer_text,
    hint,
    play,
    skip,
    start,
    stats,
    stop,
    weak,
)
from rembrandt_chat.user_mapping import UserMapper


# --- Helpers ---


def _user(display_name: str = "Alice") -> User:
    return User(
        id=1,
        username="tg_12345",
        display_name=display_name,
        password_hash="",
        created_at=datetime.now(timezone.utc),
    )


def _word() -> Word:
    return Word(
        id=1,
        language_from="es",
        language_to="es",
        word_from="efimero",
        word_to="Que dura poco tiempo",
        tags=[],
    )


def _exercise(
    exercise_type: ExerciseType = ExerciseType.MULTIPLE_CHOICE,
    **kw,
) -> Exercise:
    defaults = dict(
        word=_word(),
        exercise_type=exercise_type,
        options=["efimero", "perpetuo", "antiguo", "moderno"],
        prompt="Que dura poco tiempo",
        expected_answer="efimero",
    )
    defaults.update(kw)
    return Exercise(**defaults)


def _answer_result(correct: bool = True) -> AnswerResult:
    return AnswerResult(
        correct=correct,
        expected="efimero",
        given="efimero" if correct else "perpetuo",
        word=_word(),
    )


def _context(
    *,
    user: User | None = None,
    session: MagicMock | None = None,
    exercise: Exercise | None = None,
) -> MagicMock:
    mapper = MagicMock(spec=UserMapper)
    mapper.ensure_user.return_value = user or _user()

    ctx = MagicMock()
    ctx.bot_data = {
        "user_mapper": mapper,
        "db": MagicMock(),
    }
    ctx.user_data = {}
    if session is not None:
        ctx.user_data["session"] = session
    if exercise is not None:
        ctx.user_data["exercise"] = exercise
    return ctx


def _update(
    *,
    has_user: bool = True,
    has_message: bool = True,
    text: str = "",
) -> MagicMock:
    update = MagicMock()
    if has_user:
        update.effective_user = MagicMock()
        update.effective_user.id = 12345
    else:
        update.effective_user = None

    if has_message:
        update.message = AsyncMock()
        update.message.text = text
    else:
        update.message = None

    update.effective_chat = AsyncMock()
    return update


def _callback_update(data: str) -> MagicMock:
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_chat = AsyncMock()
    update.callback_query = AsyncMock()
    update.callback_query.data = data
    return update


# --- /start ---


@pytest.mark.asyncio
async def test_start_greets_user():
    update = _update()
    ctx = _context()
    await start(update, ctx)
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Alice" in text


@pytest.mark.asyncio
async def test_start_no_effective_user():
    update = _update(has_user=False)
    ctx = _context()
    await start(update, ctx)
    update.message.reply_text.assert_not_called()


# --- /play ---


@pytest.mark.asyncio
async def test_play_creates_session():
    update = _update()
    ctx = _context()
    ex = _exercise()

    with patch(
        "rembrandt_chat.handlers.Session"
    ) as MockSession:
        mock_session = MockSession.return_value
        mock_session.next_exercise.return_value = ex
        await play(update, ctx)

    assert ctx.user_data["session"] is mock_session
    assert ctx.user_data["exercise"] is ex
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_play_rejects_when_session_active():
    update = _update()
    ctx = _context(session=MagicMock())
    await play(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "already have an active session" in text


@pytest.mark.asyncio
async def test_play_no_words_available():
    update = _update()
    ctx = _context()

    with patch(
        "rembrandt_chat.handlers.Session"
    ) as MockSession:
        MockSession.return_value.next_exercise.return_value = None
        await play(update, ctx)

    assert "session" not in ctx.user_data
    text = update.message.reply_text.call_args[0][0]
    assert "No words available" in text


# --- /stop ---


@pytest.mark.asyncio
async def test_stop_shows_summary():
    session = MagicMock()
    session.summary.return_value = SessionStats(
        total=5, correct=4, incorrect=1,
        streak=2, best_streak=3, accuracy_pct=80.0,
    )
    update = _update()
    ctx = _context(session=session)

    await stop(update, ctx)

    assert "session" not in ctx.user_data
    text = update.message.reply_text.call_args[0][0]
    assert "80%" in text


@pytest.mark.asyncio
async def test_stop_no_session():
    update = _update()
    ctx = _context()
    await stop(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No active session" in text


# --- handle_answer_text ---


@pytest.mark.asyncio
async def test_answer_text_correct():
    session = MagicMock()
    session.answer.return_value = _answer_result(correct=True)
    session.next_exercise.return_value = _exercise()
    ex = _exercise(exercise_type=ExerciseType.REVERSE_FLASHCARD)

    update = _update(text="efimero")
    ctx = _context(session=session, exercise=ex)

    await handle_answer_text(update, ctx)

    session.answer.assert_called_once_with(text="efimero")
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_answer_text_no_session():
    update = _update(text="hello")
    ctx = _context()
    await handle_answer_text(update, ctx)
    update.message.reply_text.assert_not_called()


# --- handle_answer_callback: multiple choice ---


@pytest.mark.asyncio
async def test_callback_multiple_choice():
    session = MagicMock()
    session.answer.return_value = _answer_result(correct=True)
    session.next_exercise.return_value = _exercise()
    ex = _exercise()

    update = _callback_update(f"{MC_PREFIX}0")
    ctx = _context(session=session, exercise=ex)

    await handle_answer_callback(update, ctx)

    session.answer.assert_called_once_with(text="efimero")
    update.callback_query.edit_message_text.assert_called_once()


# --- handle_answer_callback: quality ---


@pytest.mark.asyncio
async def test_callback_quality():
    session = MagicMock()
    session.answer.return_value = _answer_result(correct=True)
    session.next_exercise.return_value = _exercise()
    ex = _exercise(exercise_type=ExerciseType.SELF_GRADED)

    update = _callback_update(f"{QUALITY_PREFIX}4")
    ctx = _context(session=session, exercise=ex)

    await handle_answer_callback(update, ctx)

    session.answer.assert_called_once_with(quality=4)


# --- handle_answer_callback: reveal ---


@pytest.mark.asyncio
async def test_callback_reveal():
    session = MagicMock()
    ex = _exercise(exercise_type=ExerciseType.FLASHCARD)

    update = _callback_update(REVEAL_CB)
    ctx = _context(session=session, exercise=ex)

    await handle_answer_callback(update, ctx)

    # Reveal edits message but does NOT call session.answer
    session.answer.assert_not_called()
    update.callback_query.edit_message_text.assert_called_once()


# --- session ends when no more exercises ---


@pytest.mark.asyncio
async def test_session_ends_on_last_exercise():
    session = MagicMock()
    session.answer.return_value = _answer_result(correct=True)
    session.next_exercise.return_value = None
    session.summary.return_value = SessionStats(
        total=1, correct=1, incorrect=0,
        streak=1, best_streak=1, accuracy_pct=100.0,
    )
    ex = _exercise(exercise_type=ExerciseType.REVERSE_FLASHCARD)

    update = _update(text="efimero")
    ctx = _context(session=session, exercise=ex)

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
    ex = _exercise(exercise_type=ExerciseType.REVERSE_FLASHCARD)
    update = _update()
    ctx = _context(session=session, exercise=ex)

    await hint(update, ctx)

    session.hint.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "ef_____" in text


@pytest.mark.asyncio
async def test_hint_no_session():
    update = _update()
    ctx = _context()
    await hint(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No active session" in text


@pytest.mark.asyncio
async def test_hint_no_exercise():
    update = _update()
    ctx = _context(session=MagicMock())
    await hint(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No active exercise" in text


# --- /skip ---


@pytest.mark.asyncio
async def test_skip_advances_to_next():
    session = MagicMock()
    skipped_ex = _exercise()
    session.skip.return_value = skipped_ex
    session.next_exercise.return_value = _exercise()

    update = _update()
    ctx = _context(session=session, exercise=skipped_ex)

    await skip(update, ctx)

    session.skip.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Skipped" in text
    assert "efimero" in text


@pytest.mark.asyncio
async def test_skip_no_session():
    update = _update()
    ctx = _context()
    await skip(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No active session" in text


@pytest.mark.asyncio
async def test_skip_no_exercise():
    update = _update()
    ctx = _context(session=MagicMock())
    await skip(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No active exercise" in text


# --- /stats ---


@pytest.mark.asyncio
async def test_stats_shows_daily():
    update = _update()
    ctx = _context()
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
    update = _update()
    ctx = _context()
    ctx.bot_data["db"].daily_stats.return_value = []

    await stats(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No activity" in text


# --- /weak ---


@pytest.mark.asyncio
async def test_weak_shows_words():
    update = _update()
    ctx = _context()
    ctx.bot_data["db"].weak_words.return_value = [
        WeakWord(
            word=_word(),
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
    update = _update()
    ctx = _context()
    ctx.bot_data["db"].weak_words.return_value = []

    await weak(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "No weak words" in text
