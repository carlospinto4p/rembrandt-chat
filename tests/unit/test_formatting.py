"""Tests for rembrandt_chat.formatting."""

from datetime import datetime, timezone

from rembrandt import AnswerHistory, Hint, SessionStats
from rembrandt.models import (
    AnswerResult,
    Concept,
    DailyStats,
    Exercise,
    ExerciseType,
    ReviewForecast,
    Topic,
    TopicProgress,
    WeakConcept,
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
    format_topics,
    format_retention,
    format_weak_concepts,
)


def _concept(**kw) -> Concept:
    defaults = dict(
        id=1,
        front="efimero",
        back="Que dura poco tiempo",
        tags=[],
    )
    defaults.update(kw)
    return Concept(**defaults)


def _exercise(
    exercise_type: ExerciseType = ExerciseType.MULTIPLE_CHOICE,
    **kw,
) -> Exercise:
    defaults = dict(
        concept=_concept(),
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
        options=[
            "Que dura poco tiempo", "perpetuo",
            "antiguo", "moderno",
        ],
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


# --- format_answer ---


def test_format_answer_correct():
    result = AnswerResult(
        correct=True,
        expected="efimero",
        given="efimero",
        concept=_concept(),
    )
    text = format_answer(result)
    assert "\u2705" in text
    assert "efimero" in text


def test_format_answer_near_miss():
    result = AnswerResult(
        correct=True,
        expected="efimero",
        given="efemero",
        concept=_concept(),
        near_miss=True,
    )
    text = format_answer(result)
    assert "efemero" in text


def test_format_answer_wrong():
    result = AnswerResult(
        correct=False,
        expected="efimero",
        given="perpetuo",
        concept=_concept(),
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


def test_format_hint_with_context():
    hint = Hint(
        first_letter="e",
        word_length=7,
        pattern="e______",
        context="La belleza es ___.",
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


# --- format_weak_concepts ---


def test_format_weak_concepts():
    concepts = [
        WeakConcept(
            concept=_concept(),
            attempts=10,
            errors=7,
            error_rate=0.7,
            last_attempt=datetime.now(timezone.utc),
        ),
    ]
    text = format_weak_concepts(concepts)
    assert "efimero" in text
    assert "7/10" in text
    assert "70%" in text


def test_format_weak_concepts_empty():
    text = format_weak_concepts([])
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


# --- format_topics ---


def test_format_topics():
    ts = [
        Topic(
            id=1, title="A1 - Basics",
            concept_count=10, concept_ids=[1, 2, 3],
        ),
    ]
    prog = [
        TopicProgress(
            topic_id=1, user_id=1, concepts_total=10,
            concepts_studied=7, concepts_mastered=3,
            completion_pct=70.0, mastery_pct=30.0,
        ),
    ]
    text, kb = format_topics(ts, prog)
    assert "A1 - Basics" in text
    assert "70%" in text
    assert kb is not None
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert flat[0].callback_data == "topic:1"


def test_format_topics_empty():
    text, kb = format_topics([], [])
    assert "No topics available" in text
    assert kb is None


# --- format_history ---


def test_format_history():
    records = [
        AnswerHistory(
            user_id=1,
            concept_id=1,
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
            concept_id=2,
            exercise_type="flashcard",
            correct=False,
            quality=0,
            answered_at=datetime(
                2026, 3, 12, 14, 25,
                tzinfo=timezone.utc,
            ),
        ),
    ]
    concept_map = {1: "efimero", 2: "perpetuo"}
    text = format_history(records, concept_map)
    assert "efimero" in text
    assert "perpetuo" in text
    assert "\u2705" in text
    assert "\u274c" in text


def test_format_history_empty():
    text = format_history([], {})
    assert "No answer history" in text


def test_format_history_unknown_concept():
    records = [
        AnswerHistory(
            user_id=1,
            concept_id=99,
            exercise_type="multiple_choice",
            correct=True,
            quality=5,
        ),
    ]
    text = format_history(records, {})
    assert "#99" in text
