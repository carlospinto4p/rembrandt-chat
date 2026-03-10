"""Format rembrandt exercises as Telegram messages and keyboards."""

from rembrandt import Hint, SessionStats
from rembrandt.models import (
    AnswerResult,
    Exercise,
    ExerciseType,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Callback-data prefixes
MC_PREFIX = "mc:"
QUALITY_PREFIX = "q:"
REVEAL_CB = "reveal"

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


# ---- shared keyboard builders ----


def _quality_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            label, callback_data=f"{QUALITY_PREFIX}{i}"
        )
        for i, label in enumerate(_QUALITY_LABELS)
    ]
    return InlineKeyboardMarkup([buttons])
