"""Format rembrandt exercises as Telegram messages and keyboards."""

from datetime import date, timedelta

from rembrandt import AnswerHistory, Hint, SessionStats
from rembrandt.models import (
    AnswerResult,
    ConceptTranslation,
    DailyStats,
    Exercise,
    ExerciseType,
    Language,
    ReviewForecast,
    Topic,
    TopicProgress,
    WeakConcept,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from rembrandt_chat.topic_translations import (
    CATEGORIES,
    all_topics_label,
    category_name,
    topic_title,
)

# Callback-data prefixes
MC_PREFIX = "mc:"
QUALITY_PREFIX = "q:"
REVEAL_CB = "reveal"
DEL_CB_PREFIX = "delw:"
DEL_CONFIRM_PREFIX = "delconfirm:"
DEL_CANCEL_CB = "delcancel"

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
    *,
    translation: ConceptTranslation | None = None,
    tr_map: dict[str, str] | None = None,
) -> tuple[str, InlineKeyboardMarkup | None]:
    """Render an exercise as Telegram message text + optional keyboard.

    :param exercise: The exercise to format.
    :param translation: Optional translation for the main
        concept.
    :param tr_map: Optional mapping of original text to
        translated text, used for MC option translation.
    :return: ``(text, keyboard)``.
    """
    et = exercise.exercise_type

    if et is ExerciseType.MULTIPLE_CHOICE:
        return _fmt_multiple_choice(
            exercise, translation, tr_map
        )
    return _fmt_flashcard_prompt(exercise, translation)


# ---- exercise formatters ----


def _context_line(
    translation: ConceptTranslation | None,
) -> str:
    """Return a context/example line, or empty string."""
    if translation and translation.context:
        return f"\n\nExample: {translation.context}"
    return ""


def _fmt_multiple_choice(
    ex: Exercise,
    translation: ConceptTranslation | None = None,
    tr_map: dict[str, str] | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    front = translation.front if translation else ex.concept.front
    text = (
        f"Which definition matches this word?\n\n"
        f"\u201c{front}\u201d"
    )
    text += _context_line(translation)
    options = ex.options
    if tr_map:
        options = [tr_map.get(o, o) for o in options]
    buttons = [
        InlineKeyboardButton(
            opt, callback_data=f"{MC_PREFIX}{i}"
        )
        for i, opt in enumerate(options)
    ]
    # One button per row — definitions are too long for side-by-side
    rows = [[b] for b in buttons]
    return text, InlineKeyboardMarkup(rows)


def _fmt_flashcard_prompt(
    ex: Exercise,
    translation: ConceptTranslation | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    front = translation.front if translation else ex.concept.front
    text = (
        f"Do you know this word?\n\n"
        f"{front}"
    )
    text += _context_line(translation)
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            "Reveal", callback_data=REVEAL_CB
        )]]
    )
    return text, keyboard


def flashcard_reveal(
    ex: Exercise,
    translation: ConceptTranslation | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    """Show the answer and quality buttons after a flashcard
    reveal.

    :param ex: The current flashcard exercise.
    :param translation: Optional translation override.
    :return: ``(text, keyboard)`` with quality buttons.
    """
    front = translation.front if translation else ex.concept.front
    back = translation.back if translation else ex.concept.back
    text = (
        f"{front} \u2014 {back}\n\n"
        f"How well did you know it?"
    )
    return text, _QUALITY_KEYBOARD


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


def compute_streak(
    stats: list[DailyStats],
    today: date | None = None,
) -> int:
    """Count consecutive study days ending today.

    :param stats: Daily stats sorted most-recent first.
        The `date` field may be a string (``"YYYY-MM-DD"``)
        or a `date` object.
    :param today: Override for testability (defaults to
        ``date.today()``).
    :return: Number of consecutive days with activity.
    """
    if not stats:
        return 0
    if today is None:
        today = date.today()
    active_dates: set[date] = set()
    for s in stats:
        if s.answers > 0:
            d = s.date
            if isinstance(d, str):
                d = date.fromisoformat(d)
            active_dates.add(d)
    streak = 0
    day = today
    while day in active_dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


def format_daily_stats(
    stats: list[DailyStats],
    *,
    streak: int = 0,
) -> str:
    """Render daily stats for the last few days.

    :param stats: List of daily stats (most recent first).
    :param streak: Current consecutive study-day streak.
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
    if streak > 0:
        lines.append(f"\nStudy streak: {streak} day(s)")
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
PLAY_TOPIC_PREFIX = "play_topic:"
PLAY_LANG_PREFIX = "play_lang:"
PLAY_CAT_PREFIX = "play_cat:"
CAT_CB_PREFIX = "cat:"
LANG_CB_PREFIX = "lang:"


def format_play_languages(
    languages: list[Language],
) -> tuple[str, InlineKeyboardMarkup]:
    """Render language selection for `/play`.

    :param languages: Available languages.
    :return: Formatted text and inline keyboard.
    """
    buttons = [
        [InlineKeyboardButton(
            lang.name,
            callback_data=f"{PLAY_LANG_PREFIX}{lang.code}",
        )]
        for lang in languages
    ]
    return "Choose a language:", InlineKeyboardMarkup(buttons)


def format_languages(
    languages: list[Language],
) -> tuple[str, InlineKeyboardMarkup]:
    """Render language selection for `/language`.

    :param languages: Available languages.
    :return: Formatted text and inline keyboard.
    """
    buttons = [
        [InlineKeyboardButton(
            lang.name,
            callback_data=f"{LANG_CB_PREFIX}{lang.code}",
        )]
        for lang in languages
    ]
    return "Choose your language:", InlineKeyboardMarkup(
        buttons
    )


def format_play_categories(
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    """Render category selection for `/play`.

    :param lang: User language code.
    :return: Formatted text and inline keyboard.
    """
    prompt = (
        "Choose a category:"
        if lang == "en"
        else "Elige una categoría:"
    )
    buttons = [
        [InlineKeyboardButton(
            category_name(cat, lang),
            callback_data=f"{PLAY_CAT_PREFIX}{cat.key}",
        )]
        for cat in CATEGORIES
    ]
    return prompt, InlineKeyboardMarkup(buttons)


def format_categories(
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    """Render category selection for `/topics`.

    :param lang: User language code.
    :return: Formatted text and inline keyboard.
    """
    prompt = (
        "Choose a category:"
        if lang == "en"
        else "Elige una categoría:"
    )
    buttons = [
        [InlineKeyboardButton(
            category_name(cat, lang),
            callback_data=f"{CAT_CB_PREFIX}{cat.key}",
        )]
        for cat in CATEGORIES
    ]
    return prompt, InlineKeyboardMarkup(buttons)


def _format_topic_list(
    topics: list[Topic],
    progress: list[TopicProgress],
    *,
    header: str,
    button_prefix: str,
    lang: str | None = None,
    include_all: bool = False,
) -> tuple[str, InlineKeyboardMarkup]:
    """Render a topic list with progress and buttons.

    :param header: First line of the message.
    :param button_prefix: Callback-data prefix for buttons.
    :param include_all: Prepend an "All topics" button.
    """
    prog_map = {p.topic_id: p for p in progress}
    lines = [f"{header}\n"]
    buttons: list[list[InlineKeyboardButton]] = []
    if include_all:
        all_label = all_topics_label(lang)
        buttons.append([InlineKeyboardButton(
            all_label,
            callback_data=f"{button_prefix}all",
        )])
    for topic in topics:
        p = prog_map.get(topic.id)
        pct = f"{p.completion_pct:.0f}%" if p else "0%"
        name = topic_title(topic.id, topic.title, lang)
        lines.append(
            f"{topic.id}. {name} ({pct} complete)"
        )
        buttons.append([
            InlineKeyboardButton(
                name,
                callback_data=(
                    f"{button_prefix}{topic.id}"
                ),
            )
        ])
    return "\n".join(lines), InlineKeyboardMarkup(buttons)


def format_play_topics(
    topics: list[Topic],
    progress: list[TopicProgress],
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    """Render topic selection for `/play` with an
    "All topics" option.
    """
    return _format_topic_list(
        topics, progress,
        header="Choose a topic:",
        button_prefix=PLAY_TOPIC_PREFIX,
        lang=lang,
        include_all=True,
    )


def format_topics(
    topics: list[Topic],
    progress: list[TopicProgress],
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup | None]:
    """Render a list of topics with progress."""
    if not topics:
        return "No topics available.", None
    return _format_topic_list(
        topics, progress,
        header="Topics:",
        button_prefix=TOPIC_CB_PREFIX,
        lang=lang,
    )


def format_retention(rate: float) -> str:
    """Render the overall retention rate.

    :param rate: Retention percentage (0.0–100.0).
    :return: Formatted retention text.
    """
    if rate == 0.0:
        return "No answers recorded yet. Start a session with /play!"
    return f"Retention rate (last 30 days): {rate:.0f}%"


def format_topic_progress(
    topics: list[Topic],
    progress: list[TopicProgress],
) -> str:
    """Render per-topic completion percentages.

    :param topics: List of topics.
    :param progress: Matching list of progress objects.
    :return: Formatted text, or empty string if no topics.
    """
    if not topics:
        return ""
    lines = ["Topic progress:\n"]
    for t, p in zip(topics, progress):
        lines.append(
            f"{t.title}: {p.completion_pct:.0f}%"
        )
    return "\n".join(lines)


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


_QUALITY_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            label, callback_data=f"{QUALITY_PREFIX}{i}"
        )
        for i, label in enumerate(_QUALITY_LABELS[j : j + 2], j)
    ]
    for j in range(0, len(_QUALITY_LABELS), 2)
])
