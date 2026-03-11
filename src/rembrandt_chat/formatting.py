"""Format rembrandt exercises as Telegram messages and keyboards."""

from rembrandt import Hint, SessionStats
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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Callback-data prefixes
MC_PREFIX = "mc:"
QUALITY_PREFIX = "q:"
REVEAL_CB = "reveal"
DEL_CB_PREFIX = "delw:"

# Quality labels for self-graded buttons
_QUALITY_LABELS = ["0", "1", "2", "3", "4", "5"]


def format_exercise(
    exercise: Exercise,
) -> tuple[str, InlineKeyboardMarkup | None]:
    """Render an exercise as Telegram message text + optional keyboard.

    :param exercise: The exercise to format.
    :return: ``(text, keyboard)`` — keyboard is ``None`` when the
        user must type a free-text answer.
    """
    et = exercise.exercise_type

    if et is ExerciseType.MULTIPLE_CHOICE:
        return _fmt_multiple_choice(exercise)
    if et is ExerciseType.SELF_GRADED:
        return _fmt_self_graded_prompt(exercise)
    if et is ExerciseType.FLASHCARD:
        return _fmt_flashcard_prompt(exercise)
    # All remaining types expect a typed answer
    return _fmt_typed(exercise)


# ---- exercise formatters ----


def _fmt_multiple_choice(
    ex: Exercise,
) -> tuple[str, InlineKeyboardMarkup]:
    text = (
        f"Which word matches this definition?\n\n"
        f"\u201c{ex.prompt or ex.word.word_to}\u201d"
    )
    buttons = [
        InlineKeyboardButton(opt, callback_data=f"{MC_PREFIX}{i}")
        for i, opt in enumerate(ex.options)
    ]
    # Two buttons per row
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    return text, InlineKeyboardMarkup(rows)


def _fmt_self_graded_prompt(
    ex: Exercise,
) -> tuple[str, InlineKeyboardMarkup]:
    text = (
        f"Review this word:\n\n"
        f"{ex.word.word_from} \u2014 {ex.word.word_to}"
    )
    keyboard = _quality_keyboard()
    return text, keyboard


def _fmt_flashcard_prompt(
    ex: Exercise,
) -> tuple[str, InlineKeyboardMarkup]:
    text = (
        f"Do you know this word?\n\n"
        f"{ex.word.word_from}"
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
        f"{ex.word.word_from} \u2014 {ex.word.word_to}\n\n"
        f"How well did you know it?"
    )
    return text, _quality_keyboard()


def _fmt_typed(
    ex: Exercise,
) -> tuple[str, None]:
    et = ex.exercise_type
    if et is ExerciseType.REVERSE_FLASHCARD:
        text = (
            f"What word means:\n\n"
            f"\u201c{ex.prompt or ex.word.word_to}\u201d\n\n"
            f"Type your answer:"
        )
    elif et is ExerciseType.CONJUGATION:
        text = (
            f"Conjugate: {ex.word.word_from}\n"
            f"{ex.prompt}\n\n"
            f"Type your answer:"
        )
    elif et is ExerciseType.CLOZE:
        text = f"{ex.prompt}\n\nFill in the blank:"
    elif et is ExerciseType.TRANSLATION_CLOZE:
        text = f"{ex.prompt}\n\nType the translation:"
    elif et is ExerciseType.GENDER_MATCH:
        text = (
            f"What is the article for:\n\n"
            f"{ex.word.word_from}\n\n"
            f"Type your answer (e.g. el/la):"
        )
    elif et is ExerciseType.ADJECTIVE_AGREEMENT:
        text = f"{ex.prompt}\n\nType the agreed form:"
    elif et is ExerciseType.SENTENCE_ORDER:
        text = f"{ex.prompt}\n\nReorder the sentence:"
    else:
        text = (
            f"{ex.prompt or ex.word.word_from}\n\n"
            f"Type your answer:"
        )
    return text, None


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
    if hint.example_sentence:
        lines.append(f"\n{hint.example_sentence}")
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


def format_weak_words(words: list[WeakWord]) -> str:
    """Render the user's weakest words.

    :param words: List of weak words.
    :return: Formatted weak-words text.
    """
    if not words:
        return "No weak words found. Keep practising!"
    lines = ["Your weakest words:\n"]
    for i, w in enumerate(words, 1):
        lines.append(
            f"{i}. {w.word.word_from} \u2014 "
            f"{w.errors}/{w.attempts} errors "
            f"({w.error_rate:.0%})"
        )
    return "\n".join(lines)


LESSON_CB_PREFIX = "lesson:"


def format_lessons(
    lessons: list[Lesson],
    progress: list[LessonProgress],
) -> tuple[str, InlineKeyboardMarkup | None]:
    """Render a list of lessons with progress.

    :param lessons: Available lessons.
    :param progress: Progress for each lesson (same order).
    :return: Formatted text and inline keyboard.
    """
    if not lessons:
        return "No lessons available.", None
    prog_map = {p.lesson_id: p for p in progress}
    lines = ["Lessons:\n"]
    buttons: list[list[InlineKeyboardButton]] = []
    for lesson in lessons:
        p = prog_map.get(lesson.id)
        pct = f"{p.completion_pct:.0f}%" if p else "0%"
        lines.append(
            f"{lesson.id}. {lesson.title} ({pct} complete)"
        )
        buttons.append([
            InlineKeyboardButton(
                lesson.title,
                callback_data=(
                    f"{LESSON_CB_PREFIX}{lesson.id}"
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


# ---- shared keyboard builders ----


def _quality_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            label, callback_data=f"{QUALITY_PREFIX}{i}"
        )
        for i, label in enumerate(_QUALITY_LABELS)
    ]
    return InlineKeyboardMarkup([buttons])
