"""Format rembrandt exercises as Telegram messages and keyboards."""

from rembrandt import AnswerHistory, Hint, SessionStats
from rembrandt.models import (
    AnswerResult,
    DailyStats,
    Exercise,
    ExerciseType,
    ReviewForecast,
    Topic,
    TopicProgress,
    WeakConcept,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Callback-data prefixes
MC_PREFIX = "mc:"
QUALITY_PREFIX = "q:"
REVEAL_CB = "reveal"
DEL_CB_PREFIX = "delw:"

# Quality labels for self-graded buttons (0–5 scale)
_QUALITY_LABELS = [
    "0 - No idea",
    "1 - Wrong",
    "2 - Almost",
    "3 - Hard",
    "4 - Good",
    "5 - Easy",
]


def format_exercise(
    exercise: Exercise,
) -> tuple[str, InlineKeyboardMarkup | None]:
    """Render an exercise as Telegram message text + optional keyboard.

    :param exercise: The exercise to format.
    :return: ``(text, keyboard)``.
    """
    et = exercise.exercise_type

    if et is ExerciseType.MULTIPLE_CHOICE:
        return _fmt_multiple_choice(exercise)
    if et is ExerciseType.SELF_GRADED:
        return _fmt_self_graded_prompt(exercise)
    return _fmt_flashcard_prompt(exercise)


# ---- exercise formatters ----


def _fmt_multiple_choice(
    ex: Exercise,
) -> tuple[str, InlineKeyboardMarkup]:
    text = (
        f"Which definition matches this word?\n\n"
        f"\u201c{ex.concept.front}\u201d"
    )
    buttons = [
        InlineKeyboardButton(opt, callback_data=f"{MC_PREFIX}{i}")
        for i, opt in enumerate(ex.options)
    ]
    # One button per row — definitions are too long for side-by-side
    rows = [[b] for b in buttons]
    return text, InlineKeyboardMarkup(rows)


def _fmt_self_graded_prompt(
    ex: Exercise,
) -> tuple[str, InlineKeyboardMarkup]:
    text = (
        f"Review this word:\n\n"
        f"{ex.concept.front} \u2014 {ex.concept.back}\n\n"
        f"How well did you know it?"
    )
    keyboard = _quality_keyboard()
    return text, keyboard


def _fmt_flashcard_prompt(
    ex: Exercise,
) -> tuple[str, InlineKeyboardMarkup]:
    text = (
        f"Do you know this word?\n\n"
        f"{ex.concept.front}"
    )
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Reveal", callback_data=REVEAL_CB)]]
    )
    return text, keyboard


def flashcard_reveal(
    ex: Exercise,
) -> tuple[str, InlineKeyboardMarkup]:
    """Show the answer and quality buttons after a flashcard reveal.

    :param ex: The current flashcard exercise.
    :return: ``(text, keyboard)`` with quality buttons.
    """
    text = (
        f"{ex.concept.front} \u2014 {ex.concept.back}\n\n"
        f"How well did you know it?"
    )
    return text, _quality_keyboard()


# ---- answer / hint / summary formatters ----


def format_answer(result: AnswerResult) -> str:
    """Render answer feedback.

    :param result: The answer evaluation from the session.
    :return: Formatted feedback text.
    """
    if result.correct:
        msg = f"\u2705 Correct! {result.expected}"
        if result.near_miss:
            msg += f" (you typed: {result.given})"
        return msg
    return (
        f"\u274c Wrong. The answer was: {result.expected}"
    )


def format_hint(hint: Hint) -> str:
    """Render a hint.

    :param hint: The hint from the session.
    :return: Formatted hint text.
    """
    lines = [f"Hint: {hint.pattern}"]
    if hint.context:
        lines.append(f"\n{hint.context}")
    return "\n".join(lines)


def format_summary(stats: SessionStats) -> str:
    """Render an end-of-session summary.

    :param stats: The session statistics.
    :return: Formatted summary text.
    """
    return (
        f"Session complete!\n\n"
        f"Total: {stats.total}\n"
        f"Correct: {stats.correct}\n"
        f"Incorrect: {stats.incorrect}\n"
        f"Accuracy: {stats.accuracy_pct:.0f}%\n"
        f"Best streak: {stats.best_streak}"
    )


def format_daily_stats(stats: list[DailyStats]) -> str:
    """Render daily stats for the last few days.

    :param stats: List of daily stats (most recent first).
    :return: Formatted stats text.
    """
    if not stats:
        return "No activity recorded yet."
    lines = ["Daily stats:\n"]
    for s in stats:
        lines.append(
            f"{s.date}: {s.answers} answers, "
            f"{s.correct} correct ({s.accuracy_pct:.0f}%)"
        )
    return "\n".join(lines)


def format_weak_concepts(
    concepts: list[WeakConcept],
) -> str:
    """Render the user's weakest concepts.

    :param concepts: List of weak concepts.
    :return: Formatted weak-concepts text.
    """
    if not concepts:
        return "No weak words found. Keep practising!"
    lines = ["Your weakest words:\n"]
    for i, w in enumerate(concepts, 1):
        lines.append(
            f"{i}. {w.concept.front} \u2014 "
            f"{w.errors}/{w.attempts} errors "
            f"({w.error_rate:.0%})"
        )
    return "\n".join(lines)


TOPIC_CB_PREFIX = "topic:"


def format_topics(
    topics: list[Topic],
    progress: list[TopicProgress],
) -> tuple[str, InlineKeyboardMarkup | None]:
    """Render a list of topics with progress.

    :param topics: Available topics.
    :param progress: Progress for each topic (same order).
    :return: Formatted text and inline keyboard.
    """
    if not topics:
        return "No topics available.", None
    prog_map = {p.topic_id: p for p in progress}
    lines = ["Topics:\n"]
    buttons: list[list[InlineKeyboardButton]] = []
    for topic in topics:
        p = prog_map.get(topic.id)
        pct = f"{p.completion_pct:.0f}%" if p else "0%"
        lines.append(
            f"{topic.id}. {topic.title} ({pct} complete)"
        )
        buttons.append([
            InlineKeyboardButton(
                topic.title,
                callback_data=(
                    f"{TOPIC_CB_PREFIX}{topic.id}"
                ),
            )
        ])
    text = "\n".join(lines)
    keyboard = InlineKeyboardMarkup(buttons)
    return text, keyboard


def format_retention(rate: float) -> str:
    """Render the overall retention rate.

    :param rate: Retention percentage (0.0–100.0).
    :return: Formatted retention text.
    """
    if rate == 0.0:
        return "No answers recorded yet. Start a session with /play!"
    return f"Retention rate (last 30 days): {rate:.0f}%"


def format_forecast(
    forecast: list[ReviewForecast],
) -> str:
    """Render the upcoming review workload.

    :param forecast: List of daily forecasts.
    :return: Formatted forecast text.
    """
    if not forecast:
        return "No reviews scheduled. Add words to get started!"
    lines = ["Upcoming reviews:\n"]
    for f in forecast:
        lines.append(f"{f.date}: {f.due_count} cards due")
    return "\n".join(lines)


def format_history(
    records: list[AnswerHistory],
    concept_map: dict[int, str],
) -> str:
    """Render recent answer history.

    :param records: Answer history records (newest first).
    :param concept_map: Mapping of concept id to front text.
    :return: Formatted history text.
    """
    if not records:
        return (
            "No answer history yet. "
            "Start a session with /play!"
        )
    lines = ["Recent answers:\n"]
    for r in records:
        icon = "\u2705" if r.correct else "\u274c"
        word = concept_map.get(
            r.concept_id, f"#{r.concept_id}"
        )
        date = r.answered_at.strftime("%d %b %H:%M")
        lines.append(f"{icon} {word} \u2014 {date}")
    return "\n".join(lines)


# ---- shared keyboard builders ----


def _quality_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            label, callback_data=f"{QUALITY_PREFIX}{i}"
        )
        for i, label in enumerate(_QUALITY_LABELS)
    ]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(rows)
