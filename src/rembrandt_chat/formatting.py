"""Format rembrandt exercises as Telegram messages and keyboards."""

from datetime import date, timedelta

from rembrandt import AnswerHistory, Hint, SessionStats
from rembrandt.models import (
    AnswerResult,
    Concept,
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

from rembrandt_chat.i18n import t
from rembrandt_chat.topic_translations import (
    CATEGORIES,
    Category,
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


def format_exercise(
    exercise: Exercise,
    *,
    translation: ConceptTranslation | None = None,
    tr_map: dict[str, str] | None = None,
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup | None]:
    """Render an exercise as Telegram message text + optional keyboard.

    :param exercise: The exercise to format.
    :param translation: Optional translation for the main
        concept.
    :param tr_map: Optional mapping of original text to
        translated text, used for MC option translation.
    :param lang: User language code.
    :return: ``(text, keyboard)``.
    """
    et = exercise.exercise_type

    if et is ExerciseType.MULTIPLE_CHOICE:
        return _fmt_multiple_choice(
            exercise, translation, tr_map, lang
        )
    return _fmt_flashcard_prompt(exercise, translation, lang)


# ---- exercise formatters ----


def _context_line(
    translation: ConceptTranslation | None,
    lang: str | None = None,
) -> str:
    """Return a context/example line, or empty string."""
    if translation and translation.context:
        return t("example", lang, context=translation.context)
    return ""


def _fmt_multiple_choice(
    ex: Exercise,
    translation: ConceptTranslation | None = None,
    tr_map: dict[str, str] | None = None,
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    front = (
        translation.front if translation
        else ex.concept.front
    )
    text = t("mc_prompt", lang, front=front)
    text += _context_line(translation, lang)
    options = ex.options
    if tr_map:
        options = [tr_map.get(o, o) for o in options]
    for i, opt in enumerate(options, 1):
        text += f"\n{i}. {opt}"
    buttons = [
        InlineKeyboardButton(
            str(i), callback_data=f"{MC_PREFIX}{i - 1}"
        )
        for i in range(1, len(options) + 1)
    ]
    # Compact numbered buttons fit side-by-side
    return text, InlineKeyboardMarkup([buttons])


def _fmt_flashcard_prompt(
    ex: Exercise,
    translation: ConceptTranslation | None = None,
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    front = (
        translation.front if translation
        else ex.concept.front
    )
    text = t("flashcard_prompt", lang, front=front)
    text += _context_line(translation, lang)
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            t("reveal", lang), callback_data=REVEAL_CB
        )]]
    )
    return text, keyboard


def flashcard_reveal(
    ex: Exercise,
    translation: ConceptTranslation | None = None,
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    """Show the answer and quality buttons after a flashcard
    reveal.

    :param ex: The current flashcard exercise.
    :param translation: Optional translation override.
    :param lang: User language code.
    :return: ``(text, keyboard)`` with quality buttons.
    """
    front = (
        translation.front if translation
        else ex.concept.front
    )
    back = (
        translation.back if translation
        else ex.concept.back
    )
    text = t(
        "flashcard_reveal", lang, front=front, back=back,
    )
    return text, _quality_keyboard(lang)


# ---- answer / hint / summary formatters ----


def format_answer(
    result: AnswerResult,
    lang: str | None = None,
) -> str:
    """Render answer feedback.

    :param result: The answer evaluation from the session.
    :param lang: User language code.
    :return: Formatted feedback text.
    """
    if result.correct:
        if result.near_miss:
            return t(
                "correct_near_miss", lang,
                expected=result.expected,
                given=result.given,
            )
        return t("correct", lang, expected=result.expected)
    return t("wrong", lang, expected=result.expected)


def format_hint(
    hint: Hint,
    lang: str | None = None,
) -> str:
    """Render a hint.

    :param hint: The hint from the session.
    :param lang: User language code.
    :return: Formatted hint text.
    """
    lines = [t("hint", lang, pattern=hint.pattern)]
    if hint.context:
        lines.append(f"\n{hint.context}")
    return "\n".join(lines)


def format_summary(
    stats: SessionStats,
    lang: str | None = None,
) -> str:
    """Render an end-of-session summary.

    :param stats: The session statistics.
    :param lang: User language code.
    :return: Formatted summary text.
    """
    return t(
        "session_complete", lang,
        total=stats.total,
        correct=stats.correct,
        incorrect=stats.incorrect,
        accuracy=f"{stats.accuracy_pct:.0f}",
        streak=stats.best_streak,
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
    lang: str | None = None,
) -> str:
    """Render daily stats for the last few days.

    :param stats: List of daily stats (most recent first).
    :param streak: Current consecutive study-day streak.
    :param lang: User language code.
    :return: Formatted stats text.
    """
    if not stats:
        return t("no_activity", lang)
    lines = [t("daily_stats_header", lang)]
    for s in stats:
        lines.append(
            f"{s.date}: {s.answers} answers, "
            f"{s.correct} correct ({s.accuracy_pct:.0f}%)"
        )
    if streak > 0:
        lines.append(t("study_streak", lang, streak=streak))
    return "\n".join(lines)


def format_weak_concepts(
    concepts: list[WeakConcept],
    lang: str | None = None,
) -> str:
    """Render the user's weakest concepts.

    :param concepts: List of weak concepts.
    :param lang: User language code.
    :return: Formatted weak-concepts text.
    """
    if not concepts:
        return t("no_weak_words", lang)
    lines = [t("weakest_words_header", lang)]
    for i, w in enumerate(concepts, 1):
        lines.append(
            f"{i}. {w.concept.front} \u2014 "
            f"{w.error_rate:.0%} \u274c"
        )
    return "\n".join(lines)


TOPIC_CB_PREFIX = "topic:"
PLAY_TOPIC_PREFIX = "play_topic:"
PLAY_LANG_PREFIX = "play_lang:"
PLAY_CAT_PREFIX = "play_cat:"
PLAY_TPAGE_PREFIX = "play_tpage:"
PLAY_MODE_PREFIX = "play_mode:"
PLAY_BACK_PREFIX = "play_back:"
CANCEL_CB = "cancel_action"
CAT_CB_PREFIX = "cat:"
TPAGE_PREFIX = "tpage:"
LANG_CB_PREFIX = "lang:"

_TOPIC_PAGE_SIZE = 5


def format_play_languages(
    languages: list[Language],
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    """Render language selection for `/play`.

    :param languages: Available languages.
    :param lang: User language code.
    :return: Formatted text and inline keyboard.
    """
    buttons = [
        [InlineKeyboardButton(
            lg.name,
            callback_data=f"{PLAY_LANG_PREFIX}{lg.code}",
        )]
        for lg in languages
    ]
    buttons.append([InlineKeyboardButton(
        t("cancel_btn", lang),
        callback_data=CANCEL_CB,
    )])
    return t("choose_language", lang), InlineKeyboardMarkup(
        buttons,
    )


def format_languages(
    languages: list[Language],
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    """Render language selection for `/language`.

    :param languages: Available languages.
    :param lang: User language code.
    :return: Formatted text and inline keyboard.
    """
    buttons = [
        [InlineKeyboardButton(
            lg.name,
            callback_data=f"{LANG_CB_PREFIX}{lg.code}",
        )]
        for lg in languages
    ]
    buttons.append([InlineKeyboardButton(
        t("cancel_btn", lang),
        callback_data=CANCEL_CB,
    )])
    return t("choose_your_language", lang), (
        InlineKeyboardMarkup(buttons)
    )


def _cat_label(cat: Category, lang: str | None) -> str:
    count = len(cat.topic_ids)
    return f"{category_name(cat, lang)} ({count})"


def format_play_categories(
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    """Render category selection for `/play`.

    :param lang: User language code.
    :return: Formatted text and inline keyboard.
    """
    buttons = [
        [InlineKeyboardButton(
            _cat_label(cat, lang),
            callback_data=f"{PLAY_CAT_PREFIX}{cat.key}",
        )]
        for cat in CATEGORIES
    ]
    return t("choose_category", lang), InlineKeyboardMarkup(
        buttons,
    )


def format_categories(
    lang: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    """Render category selection for `/topics`.

    :param lang: User language code.
    :return: Formatted text and inline keyboard.
    """
    buttons = [
        [InlineKeyboardButton(
            _cat_label(cat, lang),
            callback_data=f"{CAT_CB_PREFIX}{cat.key}",
        )]
        for cat in CATEGORIES
    ]
    return t("choose_category", lang), InlineKeyboardMarkup(
        buttons,
    )


def _format_topic_list(
    topics: list[Topic],
    progress: list[TopicProgress],
    *,
    header: str,
    button_prefix: str,
    lang: str | None = None,
    include_all: bool = False,
    page: int = 0,
    page_prefix: str = "",
    cat_key: str = "",
) -> tuple[str, InlineKeyboardMarkup]:
    """Render a topic list with progress and buttons.

    :param header: First line of the message.
    :param button_prefix: Callback-data prefix for buttons.
    :param include_all: Prepend an "All topics" button.
    :param page: Zero-based page index for pagination.
    :param page_prefix: Callback-data prefix for page
        navigation buttons.
    :param cat_key: Category key encoded in page callbacks.
    """
    total = len(topics)
    needs_paging = total > _TOPIC_PAGE_SIZE
    if needs_paging:
        start = page * _TOPIC_PAGE_SIZE
        end = start + _TOPIC_PAGE_SIZE
        page_topics = topics[start:end]
        total_pages = (
            (total + _TOPIC_PAGE_SIZE - 1)
            // _TOPIC_PAGE_SIZE
        )
    else:
        page_topics = topics
        total_pages = 1

    prog_map = {p.topic_id: p for p in progress}
    page_label = (
        f" ({page + 1}/{total_pages})"
        if needs_paging else ""
    )
    lines = [f"{header}{page_label}\n"]
    buttons: list[list[InlineKeyboardButton]] = []
    if include_all and page == 0:
        all_label = all_topics_label(lang)
        buttons.append([InlineKeyboardButton(
            all_label,
            callback_data=f"{button_prefix}all",
        )])
    for topic in page_topics:
        p = prog_map.get(topic.id)
        pct = f"{p.completion_pct:.0f}%" if p else "0%"
        name = topic_title(topic.id, topic.title, lang)
        lines.append(
            f"{topic.id}. {name} ({pct})"
        )
        buttons.append([
            InlineKeyboardButton(
                name,
                callback_data=(
                    f"{button_prefix}{topic.id}"
                ),
            )
        ])
    if needs_paging and page_prefix:
        nav: list[InlineKeyboardButton] = []
        if page > 0:
            nav.append(InlineKeyboardButton(
                t("prev", lang),
                callback_data=(
                    f"{page_prefix}{cat_key}:{page - 1}"
                ),
            ))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton(
                t("next", lang),
                callback_data=(
                    f"{page_prefix}{cat_key}:{page + 1}"
                ),
            ))
        if nav:
            buttons.append(nav)
    return "\n".join(lines), InlineKeyboardMarkup(buttons)


def format_play_topics(
    topics: list[Topic],
    progress: list[TopicProgress],
    lang: str | None = None,
    *,
    page: int = 0,
    cat_key: str = "",
) -> tuple[str, InlineKeyboardMarkup]:
    """Render topic selection for `/play` with an
    "All topics" option.
    """
    return _format_topic_list(
        topics, progress,
        header=t("choose_topic", lang),
        button_prefix=PLAY_TOPIC_PREFIX,
        lang=lang,
        include_all=True,
        page=page,
        page_prefix=PLAY_TPAGE_PREFIX,
        cat_key=cat_key,
    )


def format_topics(
    topics: list[Topic],
    progress: list[TopicProgress],
    lang: str | None = None,
    *,
    page: int = 0,
    cat_key: str = "",
) -> tuple[str, InlineKeyboardMarkup | None]:
    """Render a list of topics with progress."""
    if not topics:
        return t("no_topics", lang), None
    return _format_topic_list(
        topics, progress,
        header=t("topics_header", lang),
        button_prefix=TOPIC_CB_PREFIX,
        lang=lang,
        page=page,
        page_prefix=TPAGE_PREFIX,
        cat_key=cat_key,
    )


def format_retention(
    rate: float,
    lang: str | None = None,
) -> str:
    """Render the overall retention rate.

    :param rate: Retention percentage (0.0-100.0).
    :param lang: User language code.
    :return: Formatted retention text.
    """
    if rate == 0.0:
        return t("no_answers_yet", lang)
    return t("retention_rate", lang, rate=f"{rate:.0f}")


def format_topic_progress(
    topics: list[Topic],
    progress: list[TopicProgress],
    lang: str | None = None,
) -> str:
    """Render per-topic completion percentages.

    :param topics: List of topics.
    :param progress: Matching list of progress objects.
    :param lang: User language code.
    :return: Formatted text, or empty string if no topics.
    """
    if not topics:
        return ""
    lines = [t("topic_progress_header", lang)]
    for tp, p in zip(topics, progress):
        lines.append(
            f"{tp.title}: {p.completion_pct:.0f}%"
        )
    return "\n".join(lines)


def format_forecast(
    forecast: list[ReviewForecast],
    lang: str | None = None,
) -> str:
    """Render the upcoming review workload.

    :param forecast: List of daily forecasts.
    :param lang: User language code.
    :return: Formatted forecast text.
    """
    if not forecast:
        return t("no_reviews_scheduled", lang)
    lines = [t("upcoming_reviews_header", lang)]
    for f in forecast:
        lines.append(
            t("forecast_line", lang,
              date=f.date, count=f.due_count)
        )
    return "\n".join(lines)


def format_history(
    records: list[AnswerHistory],
    concept_map: dict[int, str],
    lang: str | None = None,
) -> str:
    """Render recent answer history.

    :param records: Answer history records (newest first).
    :param concept_map: Mapping of concept id to front text.
    :param lang: User language code.
    :return: Formatted history text.
    """
    if not records:
        return t("no_history", lang)
    lines = [t("recent_answers_header", lang)]
    for r in records:
        icon = "\u2705" if r.correct else "\u274c"
        word = concept_map.get(
            r.concept_id, f"#{r.concept_id}"
        )
        dt = r.answered_at.strftime("%d %b %H:%M")
        lines.append(f"{icon} {word} \u2014 {dt}")
    return "\n".join(lines)


# ---- concept list formatters ----


def format_concepts_list(
    concepts: list[Concept],
) -> str:
    """Render a numbered list of concepts with tags.

    :param concepts: List of concepts.
    :return: Formatted text.
    """
    lines = []
    for i, c in enumerate(concepts, 1):
        line = f"{i}. {c.front} \u2014 {c.back}"
        if c.tags:
            line += f" [{', '.join(c.tags)}]"
        lines.append(line)
    return "\n".join(lines)


def format_search_results(
    matches: list[Concept],
    term: str,
    lang: str | None = None,
) -> str:
    """Render search results with a header.

    :param matches: Matching concepts (may be truncated).
    :param term: The search term.
    :param lang: User language code.
    :return: Formatted text.
    """
    header = t(
        "search_results_header", lang,
        term=term, count=len(matches),
    )
    lines = []
    for i, c in enumerate(matches[:20], 1):
        lines.append(f"{i}. {c.front} \u2014 {c.back}")
    return header + "\n".join(lines)


# ---- shared keyboard builders ----


def _quality_keyboard(
    lang: str | None = None,
) -> InlineKeyboardMarkup:
    """Build the quality rating keyboard.

    :param lang: User language code.
    :return: Inline keyboard with 6 quality buttons.
    """
    labels = [t(f"quality_{i}", lang) for i in range(6)]
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                labels[j + k],
                callback_data=f"{QUALITY_PREFIX}{j + k}",
            )
            for k in range(2)
        ]
        for j in range(0, 6, 2)
    ])
