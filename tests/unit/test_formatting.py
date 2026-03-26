"""Tests for rembrandt_chat.formatting."""

from datetime import date, datetime, timezone

from rembrandt import AnswerHistory, Hint, SessionStats
from rembrandt.models import (
    AnswerResult,
    Concept,
    ConceptTranslation,
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
    PLAY_TPAGE_PREFIX,
    QUALITY_PREFIX,
    REVEAL_CB,
    TPAGE_PREFIX,
    compute_streak,
    flashcard_reveal,
    format_answer,
    format_daily_stats,
    format_topic_progress,
    format_exercise,
    format_hint,
    format_history,
    format_play_topics,
    format_summary,
    format_forecast,
    format_topics,
    format_retention,
    format_weak_concepts,
)

# All tests use lang="en" so assertions match English strings.
_L = "en"


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
    text, kb = format_exercise(ex, lang=_L)
    assert "efimero" in text
    assert kb is not None


def test_multiple_choice_keyboard_buttons():
    options = ["efimero", "perpetuo", "antiguo", "moderno"]
    ex = _exercise(options=options)
    _, kb = format_exercise(ex, lang=_L)
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert len(flat) == 4
    assert flat[0].text == "efimero"
    assert flat[0].callback_data == f"{MC_PREFIX}0"
    assert flat[3].callback_data == f"{MC_PREFIX}3"


def test_multiple_choice_one_per_row():
    ex = _exercise(
        options=["a", "b", "c", "d"],
    )
    _, kb = format_exercise(ex, lang=_L)
    assert len(kb.inline_keyboard) == 4
    assert len(kb.inline_keyboard[0]) == 1


# --- format_exercise: flashcard ---


def test_flashcard_prompt():
    ex = _exercise(exercise_type=ExerciseType.FLASHCARD)
    text, kb = format_exercise(ex, lang=_L)
    assert "efimero" in text
    assert kb is not None
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert flat[0].callback_data == REVEAL_CB


def test_multiple_choice_with_context():
    ex = _exercise(options=["a", "b", "c", "d"])
    tr = ConceptTranslation(
        concept_id=1,
        language_code="en",
        front="ephemeral",
        back="short-lived",
        context="The ephemeral beauty of cherry blossoms.",
    )
    text, _ = format_exercise(ex, translation=tr, lang=_L)
    assert "Example:" in text
    assert "cherry blossoms" in text


def test_flashcard_with_context():
    ex = _exercise(exercise_type=ExerciseType.FLASHCARD)
    tr = ConceptTranslation(
        concept_id=1,
        language_code="en",
        front="ephemeral",
        back="short-lived",
        context="An ephemeral moment.",
    )
    text, _ = format_exercise(ex, translation=tr, lang=_L)
    assert "Example:" in text
    assert "ephemeral moment" in text


def test_exercise_no_context():
    ex = _exercise(options=["a", "b", "c", "d"])
    tr = ConceptTranslation(
        concept_id=1,
        language_code="en",
        front="ephemeral",
        back="short-lived",
        context="",
    )
    text, _ = format_exercise(ex, translation=tr, lang=_L)
    assert "Example:" not in text


def test_flashcard_reveal():
    ex = _exercise(exercise_type=ExerciseType.FLASHCARD)
    text, kb = flashcard_reveal(ex, lang=_L)
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
    text = format_answer(result, _L)
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
    text = format_answer(result, _L)
    assert "efemero" in text


def test_format_answer_wrong():
    result = AnswerResult(
        correct=False,
        expected="efimero",
        given="perpetuo",
        concept=_concept(),
    )
    text = format_answer(result, _L)
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
    text = format_hint(hint, _L)
    assert "ef_____" in text


def test_format_hint_with_context():
    hint = Hint(
        first_letter="e",
        word_length=7,
        pattern="e______",
        context="La belleza es ___.",
    )
    text = format_hint(hint, _L)
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
    text = format_summary(stats, _L)
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
    text = format_daily_stats(stats, lang=_L)
    assert "2026-03-10" in text
    assert "20 answers" in text
    assert "90%" in text
    assert "2026-03-09" in text


def test_format_daily_stats_empty():
    text = format_daily_stats([], lang=_L)
    assert "No activity" in text


def test_format_daily_stats_with_streak():
    day = DailyStats(
        date="2026-03-25",
        answers=10,
        correct=8,
        accuracy_pct=80.0,
    )
    text = format_daily_stats([day], streak=3, lang=_L)
    assert "streak: 3 day" in text


# --- compute_streak ---


def test_compute_streak_consecutive():
    today = date(2026, 3, 25)
    stats = [
        DailyStats(
            date="2026-03-25",
            answers=5, correct=4, accuracy_pct=80.0,
        ),
        DailyStats(
            date="2026-03-24",
            answers=3, correct=2, accuracy_pct=66.7,
        ),
        DailyStats(
            date="2026-03-23",
            answers=1, correct=1, accuracy_pct=100.0,
        ),
    ]
    assert compute_streak(stats, today=today) == 3


def test_compute_streak_gap():
    today = date(2026, 3, 25)
    stats = [
        DailyStats(
            date="2026-03-25",
            answers=5, correct=4, accuracy_pct=80.0,
        ),
        DailyStats(
            date="2026-03-23",
            answers=3, correct=2, accuracy_pct=66.7,
        ),
    ]
    assert compute_streak(stats, today=today) == 1


def test_compute_streak_no_today():
    today = date(2026, 3, 25)
    stats = [
        DailyStats(
            date="2026-03-24",
            answers=5, correct=4, accuracy_pct=80.0,
        ),
    ]
    assert compute_streak(stats, today=today) == 0


def test_compute_streak_empty():
    assert compute_streak([]) == 0


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
    text = format_weak_concepts(concepts, _L)
    assert "efimero" in text
    assert "7/10" in text
    assert "70%" in text


def test_format_weak_concepts_empty():
    text = format_weak_concepts([], _L)
    assert "No weak words" in text


# --- format_forecast ---


def test_format_forecast():
    data = [
        ReviewForecast(date="2026-03-11", due_count=15),
        ReviewForecast(date="2026-03-12", due_count=8),
    ]
    text = format_forecast(data, _L)
    assert "2026-03-11" in text
    assert "15 cards due" in text
    assert "2026-03-12" in text


def test_format_forecast_empty():
    text = format_forecast([], _L)
    assert "No reviews scheduled" in text


# --- format_retention ---


def test_format_retention():
    text = format_retention(85.0, _L)
    assert "85%" in text
    assert "Retention" in text


def test_format_retention_zero():
    text = format_retention(0.0, _L)
    assert "No answers recorded" in text


# --- format_topic_progress ---


def test_format_topic_progress():
    ts = [
        Topic(
            id=1, title="A1 - Basics",
            concept_count=10, concept_ids=[1, 2, 3],
        ),
    ]
    prog = [
        TopicProgress(
            topic_id=1, user_id=1,
            concepts_total=10, concepts_studied=7,
            concepts_mastered=3,
            completion_pct=70.0, mastery_pct=30.0,
        ),
    ]
    text = format_topic_progress(ts, prog, _L)
    assert "A1 - Basics" in text
    assert "70%" in text


def test_format_topic_progress_empty():
    assert format_topic_progress([], []) == ""


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
    text, kb = format_topics(ts, prog, _L)
    # topic_id=1 maps to "Data Science - Basics" in EN
    assert "Data Science - Basics" in text
    assert "70%" in text
    assert kb is not None
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert flat[0].callback_data == "topic:1"


def test_format_topics_empty():
    text, kb = format_topics([], [], _L)
    assert "No topics available" in text
    assert kb is None


def _make_topics(n):
    """Create *n* topics with matching progress."""
    topics = [
        Topic(
            id=i, title=f"Topic {i}",
            concept_count=10, concept_ids=[i],
        )
        for i in range(1, n + 1)
    ]
    progress = [
        TopicProgress(
            topic_id=i, user_id=1, concepts_total=10,
            concepts_studied=5, concepts_mastered=2,
            completion_pct=50.0, mastery_pct=20.0,
        )
        for i in range(1, n + 1)
    ]
    return topics, progress


def test_format_topics_no_pagination_when_small():
    ts, prog = _make_topics(4)
    text, kb = format_topics(
        ts, prog, _L, cat_key="vocab",
    )
    assert "(1/" not in text
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert len(flat) == 4
    assert all(
        not btn.callback_data.startswith(TPAGE_PREFIX)
        for btn in flat
    )


def test_format_topics_paginated_first_page():
    ts, prog = _make_topics(8)
    text, kb = format_topics(
        ts, prog, _L, page=0, cat_key="vocab",
    )
    assert "(1/2)" in text
    rows = kb.inline_keyboard
    topic_btns = [
        btn for row in rows for btn in row
        if btn.callback_data.startswith("topic:")
    ]
    assert len(topic_btns) == 5
    nav = rows[-1]
    assert len(nav) == 1
    assert nav[0].callback_data == f"{TPAGE_PREFIX}vocab:1"


def test_format_topics_paginated_last_page():
    ts, prog = _make_topics(8)
    text, kb = format_topics(
        ts, prog, _L, page=1, cat_key="vocab",
    )
    assert "(2/2)" in text
    rows = kb.inline_keyboard
    topic_btns = [
        btn for row in rows for btn in row
        if btn.callback_data.startswith("topic:")
    ]
    assert len(topic_btns) == 3
    nav = rows[-1]
    assert len(nav) == 1
    assert nav[0].callback_data == f"{TPAGE_PREFIX}vocab:0"


def test_format_play_topics_first_page_has_all():
    ts, prog = _make_topics(7)
    text, kb = format_play_topics(
        ts, prog, _L, page=0, cat_key="vocab",
    )
    assert "(1/2)" in text
    rows = kb.inline_keyboard
    assert rows[0][0].callback_data == "play_topic:all"
    nav = rows[-1]
    assert any(
        btn.callback_data == f"{PLAY_TPAGE_PREFIX}vocab:1"
        for btn in nav
    )


def test_format_play_topics_page_two_no_all():
    ts, prog = _make_topics(7)
    _, kb = format_play_topics(
        ts, prog, _L, page=1, cat_key="vocab",
    )
    flat = [btn for row in kb.inline_keyboard for btn in row]
    assert all(
        btn.callback_data != "play_topic:all"
        for btn in flat
    )


def test_format_topics_middle_page_has_both_nav():
    ts, prog = _make_topics(12)
    _, kb = format_topics(
        ts, prog, _L, page=1, cat_key="c",
    )
    nav = kb.inline_keyboard[-1]
    assert len(nav) == 2
    assert nav[0].callback_data == f"{TPAGE_PREFIX}c:0"
    assert nav[1].callback_data == f"{TPAGE_PREFIX}c:2"


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
    text = format_history(records, concept_map, _L)
    assert "efimero" in text
    assert "perpetuo" in text
    assert "\u2705" in text
    assert "\u274c" in text


def test_format_history_empty():
    text = format_history([], {}, _L)
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
    text = format_history(records, {}, _L)
    assert "#99" in text
