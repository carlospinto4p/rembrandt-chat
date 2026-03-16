"""Tests for rembrandt_chat.formatting."""

from datetime import datetime, timezone

from rembrandt import AnswerHistory, Hint, SessionStats, Word
from rembrandt.models import (
    AnswerResult,
    DailyStats,
    Exercise,
    ExerciseType,
    Lesson,
    LessonProgress,
    ReviewForecast,
    WeakWord,
)

from rembrandt_chat.formatting import (
    MC_PREFIX,
    QUALITY_PREFIX,
    REVEAL_CB,
    flashcard_reveal,
    format_answer,
    format_daily_stats,
    format_exercise,
    format_hint,
    format_history,
    format_summary,
    format_forecast,
    format_lessons,
    format_retention,
    format_weak_words,
)


def _word(**kw) -> Word:
    defaults = dict(
        id=1,
        language_from="es",
        language_to="es",
        word_from="efimero",
        word_to="Que dura poco tiempo",
        tags=[],
    )
    defaults.update(kw)
    return Word(**defaults)


def _exercise(
    exercise_type: ExerciseType = ExerciseType.MULTIPLE_CHOICE,
    **kw,
) -> Exercise:
    defaults = dict(
        word=_word(),
        exercise_type=exercise_type,
        options=[],
        prompt="",
        expected_answer="",
    )
    defaults.update(kw)
    return Exercise(**defaults)


# --- format_exercise: multiple choice ---


def test_multiple_choice_text():
    ex = _exercise(
        options=["Que dura poco tiempo", "perpetuo", "antiguo", "moderno"],
    )
    text, kb = format_exercise(ex)
    assert "efimero" in text
    assert kb is not None


def test_multiple_choice_keyboard_buttons():
    options = ["efimero", "perpetuo", "antiguo", "moderno"]
    ex = _exercise(options=options)
    _, kb = format_exercise(ex)
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert len(flat) == 4
    assert flat[0].text == "efimero"
    assert flat[0].callback_data == f"{MC_PREFIX}0"
    assert flat[3].callback_data == f"{MC_PREFIX}3"


def test_multiple_choice_one_per_row():
    ex = _exercise(
        options=["a", "b", "c", "d"],
    )
    _, kb = format_exercise(ex)
    assert len(kb.inline_keyboard) == 4
    assert len(kb.inline_keyboard[0]) == 1


# --- format_exercise: self-graded ---


def test_self_graded_text():
    ex = _exercise(exercise_type=ExerciseType.SELF_GRADED)
    text, kb = format_exercise(ex)
    assert "efimero" in text
    assert "Que dura poco tiempo" in text
    assert kb is not None


def test_self_graded_quality_buttons():
    ex = _exercise(exercise_type=ExerciseType.SELF_GRADED)
    _, kb = format_exercise(ex)
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert len(flat) == 6
    assert flat[0].callback_data == f"{QUALITY_PREFIX}0"
    assert flat[5].callback_data == f"{QUALITY_PREFIX}5"


# --- format_exercise: flashcard ---


def test_flashcard_prompt():
    ex = _exercise(exercise_type=ExerciseType.FLASHCARD)
    text, kb = format_exercise(ex)
    assert "efimero" in text
    assert kb is not None
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert flat[0].callback_data == REVEAL_CB


def test_flashcard_reveal():
    ex = _exercise(exercise_type=ExerciseType.FLASHCARD)
    text, kb = flashcard_reveal(ex)
    assert "efimero" in text
    assert "Que dura poco tiempo" in text
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert flat[0].callback_data == f"{QUALITY_PREFIX}0"


# --- format_exercise: typed answers ---


def test_reverse_flashcard_typed():
    ex = _exercise(
        exercise_type=ExerciseType.REVERSE_FLASHCARD,
        prompt="Que dura poco tiempo",
    )
    text, kb = format_exercise(ex)
    assert "Type your answer" in text
    assert kb is None


def test_conjugation_typed():
    ex = _exercise(
        exercise_type=ExerciseType.CONJUGATION,
        prompt="presente, yo",
    )
    text, kb = format_exercise(ex)
    assert "Conjugate" in text
    assert "presente, yo" in text
    assert kb is None


def test_cloze_typed():
    ex = _exercise(
        exercise_type=ExerciseType.CLOZE,
        prompt="El gato es muy ___",
    )
    text, kb = format_exercise(ex)
    assert "Fill in the blank" in text
    assert kb is None


# --- format_answer ---


def test_format_answer_correct():
    result = AnswerResult(
        correct=True,
        expected="efimero",
        given="efimero",
        word=_word(),
    )
    text = format_answer(result)
    assert "\u2705" in text
    assert "efimero" in text


def test_format_answer_near_miss():
    result = AnswerResult(
        correct=True,
        expected="efimero",
        given="efemero",
        word=_word(),
        near_miss=True,
    )
    text = format_answer(result)
    assert "efemero" in text


def test_format_answer_wrong():
    result = AnswerResult(
        correct=False,
        expected="efimero",
        given="perpetuo",
        word=_word(),
    )
    text = format_answer(result)
    assert "\u274c" in text
    assert "efimero" in text


# --- format_hint ---


def test_format_hint_pattern():
    hint = Hint(
        first_letter="e",
        word_length=7,
        pattern="ef_____",
        reveal_count=2,
    )
    text = format_hint(hint)
    assert "ef_____" in text


def test_format_hint_with_sentence():
    hint = Hint(
        first_letter="e",
        word_length=7,
        pattern="e______",
        example_sentence="La belleza es ___.",
    )
    text = format_hint(hint)
    assert "La belleza es ___." in text


# --- format_summary ---


def test_format_summary():
    stats = SessionStats(
        total=10,
        correct=8,
        incorrect=2,
        streak=3,
        best_streak=5,
        accuracy_pct=80.0,
    )
    text = format_summary(stats)
    assert "Total: 10" in text
    assert "Correct: 8" in text
    assert "80%" in text
    assert "Best streak: 5" in text


# --- format_daily_stats ---


def test_format_daily_stats():
    stats = [
        DailyStats(
            date="2026-03-10", answers=20,
            correct=18, accuracy_pct=90.0,
        ),
        DailyStats(
            date="2026-03-09", answers=15,
            correct=12, accuracy_pct=80.0,
        ),
    ]
    text = format_daily_stats(stats)
    assert "2026-03-10" in text
    assert "20 answers" in text
    assert "90%" in text
    assert "2026-03-09" in text


def test_format_daily_stats_empty():
    text = format_daily_stats([])
    assert "No activity" in text


# --- format_weak_words ---


def test_format_weak_words():
    words = [
        WeakWord(
            word=_word(),
            attempts=10,
            errors=7,
            error_rate=0.7,
            last_attempt=datetime.now(timezone.utc),
        ),
    ]
    text = format_weak_words(words)
    assert "efimero" in text
    assert "7/10" in text
    assert "70%" in text


def test_format_weak_words_empty():
    text = format_weak_words([])
    assert "No weak words" in text


# --- format_forecast ---


def test_format_forecast():
    data = [
        ReviewForecast(date="2026-03-11", due_count=15),
        ReviewForecast(date="2026-03-12", due_count=8),
    ]
    text = format_forecast(data)
    assert "2026-03-11" in text
    assert "15 cards due" in text
    assert "2026-03-12" in text


def test_format_forecast_empty():
    text = format_forecast([])
    assert "No reviews scheduled" in text


# --- format_retention ---


def test_format_retention():
    text = format_retention(85.0)
    assert "85%" in text
    assert "Retention" in text


def test_format_retention_zero():
    text = format_retention(0.0)
    assert "No answers recorded" in text


# --- format_lessons ---


def test_format_lessons():
    ls = [
        Lesson(
            id=1, title="A1 - Basics",
            language_from="es", language_to="es",
            word_count=10, word_ids=[1, 2, 3],
        ),
    ]
    prog = [
        LessonProgress(
            lesson_id=1, user_id=1, words_total=10,
            words_studied=7, words_mastered=3,
            completion_pct=70.0, mastery_pct=30.0,
        ),
    ]
    text, kb = format_lessons(ls, prog)
    assert "A1 - Basics" in text
    assert "70%" in text
    assert kb is not None
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert flat[0].callback_data == "lesson:1"


def test_format_lessons_empty():
    text, kb = format_lessons([], [])
    assert "No lessons available" in text
    assert kb is None


# --- CEFR badge ---


def test_exercise_shows_cefr_badge():
    w = _word(cefr="B1")
    ex = _exercise(
        word=w,
        exercise_type=ExerciseType.REVERSE_FLASHCARD,
        prompt="Que dura poco tiempo",
    )
    text, _ = format_exercise(ex)
    assert "[B1]" in text


def test_exercise_no_cefr_no_badge():
    ex = _exercise(
        exercise_type=ExerciseType.REVERSE_FLASHCARD,
        prompt="Que dura poco tiempo",
    )
    text, _ = format_exercise(ex)
    assert "[" not in text.split("\n")[0]


# --- format_history ---


def test_format_history():
    records = [
        AnswerHistory(
            user_id=1,
            word_id=1,
            exercise_type="multiple_choice",
            correct=True,
            quality=5,
            answered_at=datetime(
                2026, 3, 12, 14, 30,
                tzinfo=timezone.utc,
            ),
        ),
        AnswerHistory(
            user_id=1,
            word_id=2,
            exercise_type="reverse_flashcard",
            correct=False,
            quality=0,
            answered_at=datetime(
                2026, 3, 12, 14, 25,
                tzinfo=timezone.utc,
            ),
        ),
    ]
    word_map = {1: "efimero", 2: "perpetuo"}
    text = format_history(records, word_map)
    assert "efimero" in text
    assert "perpetuo" in text
    assert "\u2705" in text
    assert "\u274c" in text


def test_format_history_empty():
    text = format_history([], {})
    assert "No answer history" in text


def test_format_history_unknown_word():
    records = [
        AnswerHistory(
            user_id=1,
            word_id=99,
            exercise_type="multiple_choice",
            correct=True,
            quality=5,
        ),
    ]
    text = format_history(records, {})
    assert "#99" in text
