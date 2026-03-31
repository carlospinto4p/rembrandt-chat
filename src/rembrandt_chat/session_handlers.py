"""Session lifecycle and exercise handlers."""

from typing import Any

from rembrandt import Database, Session
from rembrandt.models import ExerciseType, SessionMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from rembrandt_chat._helpers import (
    EXERCISE,
    LANGUAGE,
    LAST_TOPIC,
    SESSION,
    TRANSLATION,
    TRANSLATION_MAP,
    _build_review_config,
    _clear_persisted_session,
    check_active_session,
    cleanup_session,
    get_category_topics,
    get_lang,
    get_session,
    persist_language,
    persist_session_config,
    require_callback,
    require_category,
    setup_translations,
    require_message,
    require_session,
    resolve_user,
    resolve_user_with_typing,
    send_next,
)
from rembrandt_chat.i18n import t
from rembrandt_chat.formatting import (
    CAT_CB_PREFIX,
    LANG_CB_PREFIX,
    PLAY_CAT_PREFIX,
    PLAY_LANG_PREFIX,
    CANCEL_CB,
    PLAY_BACK_PREFIX,
    STUDY_WEAK_CB,
    PLAY_MODE_PREFIX,
    PLAY_TOPIC_PREFIX,
    PLAY_TPAGE_PREFIX,
    TOPIC_CB_PREFIX,
    TPAGE_PREFIX,
    MC_PREFIX,
    QUALITY_PREFIX,
    REVEAL_CB,
    flashcard_reveal,
    format_answer,
    format_categories,
    format_exercise,
    format_hint,
    format_languages,
    format_play_categories,
    format_play_languages,
    format_play_topics,
    format_topics,
    format_summary,
)
from rembrandt_chat.topic_translations import (
    all_topics_label,
    topic_title,
)

# user_data key for topic concept_ids chosen during /play
_PLAY_CONCEPT_IDS = "_play_concept_ids"


async def _start_session(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    db: Database,
    user_id: int,
    *,
    no_words_msg: str,
    confirm_msg: str,
    **session_kwargs: Any,
) -> None:
    """Create a session, fetch the first exercise, and send it.

    :param no_words_msg: Message when no exercises available.
    :param confirm_msg: Confirmation sent via
        ``query.edit_message_text``.
    :param session_kwargs: Forwarded to `Session()` (e.g.
        ``mode`` or ``concept_ids``).
    """
    user_data = context.user_data
    query = update.callback_query
    lang = get_lang(context)
    session = Session(
        db=db,
        user_id=user_id,
        review_config=_build_review_config(),
        **session_kwargs,
    )
    user_data[SESSION] = session

    exercise = await session.next_exercise()
    if exercise is None:
        user_data.pop(SESSION, None)
        await query.edit_message_text(no_words_msg)
        return

    user_data[EXERCISE] = exercise

    # Persist session config for restart recovery
    mode = session_kwargs.get("mode", SessionMode.MIXED)
    tg_id = update.effective_user.id
    persist_session_config(
        context, tg_id, user_id,
        mode=mode.value,
        concept_ids=session_kwargs.get("concept_ids"),
    )

    await setup_translations(user_data, db, exercise)

    await query.edit_message_text(confirm_msg)
    text, keyboard = format_exercise(
        exercise,
        translation=user_data.get(TRANSLATION),
        tr_map=user_data.get(TRANSLATION_MAP),
        lang=lang,
    )
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(text, reply_markup=keyboard)


_MODE_KEYS = {
    SessionMode.MIXED: "mode_mixed",
    SessionMode.LEARN_NEW: "mode_learn_new",
    SessionMode.REVIEW_DUE: "mode_review_due",
}


@require_message
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/start` — greet the user and auto-register if new."""
    user, _ = await resolve_user(update, context)

    name = user.display_name or user.username
    lang = get_lang(context)
    await update.message.reply_text(
        t("welcome", lang, name=name)
    )


@require_message
async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/help` — list available commands."""
    lang = get_lang(context)
    await update.message.reply_text(t("help", lang))


@require_message
async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/cancel` — fallback when no conversation is active."""
    lang = get_lang(context)
    await update.message.reply_text(
        t("nothing_to_cancel", lang)
    )


@require_message
async def play(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/play` — pick language, topic, then session mode."""
    if await check_active_session(update, context):
        return

    _, db = await resolve_user_with_typing(update, context)
    lang = get_lang(context)
    languages = await db.get_languages()
    text, keyboard = format_play_languages(languages, lang)
    await update.message.reply_text(
        text, reply_markup=keyboard
    )


@require_message
async def review(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/review` — quick review-due session for last topic."""
    if await check_active_session(update, context):
        return

    user, db = await resolve_user_with_typing(update, context)
    lang = get_lang(context)

    last = context.user_data.get(LAST_TOPIC)
    if last is None:
        await update.message.reply_text(
            t("no_previous_topic", lang)
        )
        return

    concept_ids = last.get("concept_ids")
    session = Session(
        db=db,
        user_id=user.id,
        mode=SessionMode.REVIEW_DUE,
        concept_ids=concept_ids,
        review_config=_build_review_config(),
    )
    user_data = context.user_data
    user_data[SESSION] = session

    exercise = await session.next_exercise()
    if exercise is None:
        user_data.pop(SESSION, None)
        await update.message.reply_text(
            t("no_reviews_due", lang)
        )
        return

    user_data[EXERCISE] = exercise
    tg_id = update.effective_user.id
    persist_session_config(
        context, tg_id, user.id,
        mode=SessionMode.REVIEW_DUE.value,
        concept_ids=concept_ids,
    )

    await setup_translations(user_data, db, exercise)

    await update.message.reply_text(
        t("review_started", lang)
    )
    text, keyboard = format_exercise(
        exercise,
        translation=user_data.get(TRANSLATION),
        tr_map=user_data.get(TRANSLATION_MAP),
        lang=lang,
    )
    chat = update.effective_chat
    if chat is not None:
        await chat.send_message(
            text, reply_markup=keyboard
        )


@require_callback
async def handle_play_language(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle language selection from `/play`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(PLAY_LANG_PREFIX):
        return

    user_data = context.user_data
    if await check_active_session(update, context):
        return

    lang_code = data[len(PLAY_LANG_PREFIX):]
    user_data[LANGUAGE] = lang_code
    persist_language(
        context, update.effective_user.id, lang_code,
    )

    text, keyboard = format_play_categories(lang=lang_code)
    await query.edit_message_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_play_category(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle category selection from `/play`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(PLAY_CAT_PREFIX):
        return

    user_data = context.user_data
    if await check_active_session(update, context):
        return

    cat_key = data[len(PLAY_CAT_PREFIX):]
    lang = get_lang(context)
    cat = await require_category(query, cat_key, lang)
    if cat is None:
        return

    user, db = await resolve_user(update, context)
    filtered, progress = await get_category_topics(
        db, user.id, cat.topic_ids,
    )
    text, keyboard = format_play_topics(
        filtered, progress, lang=lang, cat_key=cat_key,
    )
    await query.edit_message_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_play_topic(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle topic selection from `/play`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(PLAY_TOPIC_PREFIX):
        return

    user_data = context.user_data
    if await check_active_session(update, context):
        return

    lang = get_lang(context)
    topic_value = data[len(PLAY_TOPIC_PREFIX):]
    if topic_value == "all":
        user_data.pop(_PLAY_CONCEPT_IDS, None)
        topic_label = all_topics_label(lang)
    else:
        topic_id = int(topic_value)
        _, db = await resolve_user(update, context)
        topic = await db.get_topic(topic_id)
        if topic is None:
            await query.edit_message_text(
                t("topic_not_found", lang)
            )
            return
        user_data[_PLAY_CONCEPT_IDS] = topic.concept_ids
        topic_label = topic_title(
            topic.id, topic.title, lang
        )

    buttons = [
        InlineKeyboardButton(
            t(key, lang),
            callback_data=f"{PLAY_MODE_PREFIX}{mode.value}",
        )
        for mode, key in _MODE_KEYS.items()
    ]
    back_btn = InlineKeyboardButton(
        t("back", lang),
        callback_data=f"{PLAY_BACK_PREFIX}cat",
    )
    rows = [[b] for b in buttons] + [[back_btn]]
    await query.edit_message_text(
        t(
            "choose_session_mode", lang,
            topic=topic_label,
        ),
        reply_markup=InlineKeyboardMarkup(rows),
    )


@require_callback
async def handle_play_topic_page(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle page navigation in `/play` topic list."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(PLAY_TPAGE_PREFIX):
        return

    payload = data[len(PLAY_TPAGE_PREFIX):]
    cat_key, page_str = payload.rsplit(":", 1)
    page = int(page_str)

    lang = get_lang(context)
    cat = await require_category(query, cat_key, lang)
    if cat is None:
        return

    user, db = await resolve_user(update, context)
    filtered, progress = await get_category_topics(
        db, user.id, cat.topic_ids,
    )
    text, keyboard = format_play_topics(
        filtered, progress, lang=lang,
        page=page, cat_key=cat_key,
    )
    await query.edit_message_text(
        text, reply_markup=keyboard,
    )


@require_callback
async def handle_cancel_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Dismiss the current inline keyboard."""
    query = update.callback_query
    lang = get_lang(context)
    await query.edit_message_text(t("cancelled", lang))


@require_callback
async def handle_study_weak(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Start a session targeting weak words."""
    query = update.callback_query
    user_data = context.user_data

    if await check_active_session(update, context):
        return

    lang = get_lang(context)
    concept_ids = user_data.pop("_weak_concept_ids", None)
    if not concept_ids:
        await query.edit_message_text(
            t("cancelled", lang)
        )
        return

    user_data[_PLAY_CONCEPT_IDS] = concept_ids
    buttons = [
        InlineKeyboardButton(
            t(key, lang),
            callback_data=f"{PLAY_MODE_PREFIX}{mode.value}",
        )
        for mode, key in _MODE_KEYS.items()
    ]
    back_btn = InlineKeyboardButton(
        t("back", lang),
        callback_data=f"{PLAY_BACK_PREFIX}cat",
    )
    rows = [[b] for b in buttons] + [[back_btn]]
    await query.edit_message_text(
        t(
            "choose_session_mode", lang,
            topic=t("weakest_words_header", lang).strip(),
        ),
        reply_markup=InlineKeyboardMarkup(rows),
    )


@require_callback
async def handle_play_back(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle back button press from mode selection."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(PLAY_BACK_PREFIX):
        return

    lang = get_lang(context)
    text, keyboard = format_play_categories(lang=lang)
    await query.edit_message_text(
        text, reply_markup=keyboard,
    )


@require_callback
async def handle_play_mode(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle session-mode button press from `/play`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(PLAY_MODE_PREFIX):
        return

    mode_value = data[len(PLAY_MODE_PREFIX):]
    mode = SessionMode(mode_value)

    user_data = context.user_data
    if await check_active_session(update, context):
        return

    lang = get_lang(context)
    user, db = await resolve_user(update, context)
    label = t(_MODE_KEYS[mode], lang)

    concept_ids = user_data.pop(_PLAY_CONCEPT_IDS, None)
    session_kwargs: dict[str, Any] = {"mode": mode}
    if concept_ids is not None:
        session_kwargs["concept_ids"] = concept_ids

    await _start_session(
        update, context, db, user.id,
        no_words_msg=t("no_words_available", lang),
        confirm_msg=t(
            "session_started", lang, label=label,
        ),
        **session_kwargs,
    )


@require_message
async def stop(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/stop` — end the current session and show summary."""
    session, user_data = get_session(context)
    lang = get_lang(context)
    if session is None:
        await update.message.reply_text(
            t("no_active_session", lang)
        )
        return

    summary = session.summary()
    cleanup_session(user_data)
    _clear_persisted_session(update, context)
    await update.message.reply_text(
        format_summary(summary, lang)
    )


async def _require_active_exercise(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[Session, dict] | None:
    """Return ``(session, user_data)`` or send an error and
    return ``None``.
    """
    result = await require_session(context)
    if result is not None:
        return result
    lang = get_lang(context)
    session, _ = get_session(context)
    key = (
        "no_active_exercise"
        if session is not None
        else "no_active_session"
    )
    await update.message.reply_text(t(key, lang))
    return None


@require_message
async def hint(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/hint` — get a progressive hint for the current exercise."""
    result = await _require_active_exercise(update, context)
    if result is None:
        return

    session, _ = result
    lang = get_lang(context)
    h = session.hint()
    await update.message.reply_text(format_hint(h, lang))


@require_message
async def skip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/skip` — skip the current exercise."""
    result = await _require_active_exercise(update, context)
    if result is None:
        return

    session, user_data = result
    lang = get_lang(context)
    skipped = session.skip()
    tr = user_data.get(TRANSLATION)
    front = tr.front if tr else skipped.concept.front
    await update.message.reply_text(
        t("skipped", lang, front=front)
    )

    db: Database = context.bot_data["db"]
    await send_next(
        session, user_data, update, db=db,
        context=context,
    )


@require_message
async def handle_answer_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle a typed answer."""
    result = await require_session(context)
    if result is None:
        return

    session, user_data = result
    lang = get_lang(context)
    answer = await session.answer(
        text=update.message.text or ""
    )
    await update.message.reply_text(
        format_answer(answer, lang)
    )

    db: Database = context.bot_data["db"]
    await send_next(
        session, user_data, update, db=db,
        context=context,
    )


async def _handle_reveal(query, exercise, user_data, lang):
    """Show the flashcard answer and quality buttons."""
    tr = user_data.get(TRANSLATION)
    text, keyboard = flashcard_reveal(
        exercise, translation=tr, lang=lang,
    )
    await query.edit_message_text(
        text, reply_markup=keyboard
    )


async def _handle_quality(
    query, data, session, user_data, update, db, lang,
    *, context,
):
    """Process a self-graded quality rating."""
    quality = int(data[len(QUALITY_PREFIX):])
    answer = await session.answer(quality=quality)
    await query.edit_message_text(
        t("quality_recorded", lang)
    )
    await send_next(
        session, user_data, update, db=db,
        context=context,
    )


async def _handle_mc(
    query, data, exercise, session, user_data, update,
    db, lang, *, context,
):
    """Process a multiple-choice button press."""
    idx = int(data[len(MC_PREFIX):])
    chosen = exercise.options[idx]
    answer = await session.answer(text=chosen)
    await query.edit_message_text(
        format_answer(answer, lang)
    )
    await send_next(
        session, user_data, update, db=db,
        context=context,
    )


@require_callback
async def handle_answer_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle inline-keyboard button presses."""
    result = await require_session(context)
    if result is None:
        return

    query = update.callback_query
    session, user_data = result
    exercise = user_data[EXERCISE]
    data = query.data or ""
    lang = get_lang(context)
    db: Database = context.bot_data["db"]

    if data == REVEAL_CB:
        await _handle_reveal(
            query, exercise, user_data, lang,
        )
    elif data.startswith(QUALITY_PREFIX):
        await _handle_quality(
            query, data, session, user_data,
            update, db, lang, context=context,
        )
    elif data.startswith(MC_PREFIX):
        await _handle_mc(
            query, data, exercise, session,
            user_data, update, db, lang,
            context=context,
        )


@require_message
async def topics(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/topics` — list categories, then topics."""
    lang = get_lang(context)
    text, keyboard = format_categories(lang=lang)
    await update.message.reply_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_category_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show topics in a category from `/topics`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(CAT_CB_PREFIX):
        return

    cat_key = data[len(CAT_CB_PREFIX):]
    lang = get_lang(context)
    cat = await require_category(query, cat_key, lang)
    if cat is None:
        return

    user, db = await resolve_user(update, context)
    filtered, progress = await get_category_topics(
        db, user.id, cat.topic_ids,
    )
    text, keyboard = format_topics(
        filtered, progress, lang=lang, cat_key=cat_key,
    )
    await query.edit_message_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_topic_page(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle page navigation in `/topics` topic list."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(TPAGE_PREFIX):
        return

    payload = data[len(TPAGE_PREFIX):]
    cat_key, page_str = payload.rsplit(":", 1)
    page = int(page_str)

    lang = get_lang(context)
    cat = await require_category(query, cat_key, lang)
    if cat is None:
        return

    user, db = await resolve_user(update, context)
    filtered, progress = await get_category_topics(
        db, user.id, cat.topic_ids,
    )
    text, keyboard = format_topics(
        filtered, progress, lang=lang,
        page=page, cat_key=cat_key,
    )
    await query.edit_message_text(
        text, reply_markup=keyboard,
    )


@require_callback
async def handle_topic_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Start a session scoped to a topic's concepts."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(TOPIC_CB_PREFIX):
        return

    if await check_active_session(update, context):
        return

    lang = get_lang(context)
    topic_id = int(data[len(TOPIC_CB_PREFIX):])
    user, db = await resolve_user(update, context)

    topic = await db.get_topic(topic_id)
    if topic is None:
        await query.edit_message_text(
            t("topic_not_found", lang)
        )
        return

    topic_label = topic_title(topic.id, topic.title, lang)
    await _start_session(
        update, context, db, user.id,
        no_words_msg=t("no_words_in_topic", lang),
        confirm_msg=f"Topic: {topic_label}",
        concept_ids=topic.concept_ids,
    )


@require_message
async def language(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """`/language` — set preferred language."""
    _, db = await resolve_user_with_typing(update, context)
    lang = get_lang(context)
    languages = await db.get_languages()
    text, keyboard = format_languages(languages, lang)
    await update.message.reply_text(
        text, reply_markup=keyboard
    )


@require_callback
async def handle_language_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle language selection from `/language`."""
    query = update.callback_query
    data = query.data or ""
    if not data.startswith(LANG_CB_PREFIX):
        return

    lang_code = data[len(LANG_CB_PREFIX):]
    context.user_data[LANGUAGE] = lang_code
    persist_language(
        context, update.effective_user.id, lang_code,
    )

    _, db = await resolve_user(update, context)
    lang_obj = await db.get_language(lang_code)
    name = lang_obj.name if lang_obj else lang_code
    await query.edit_message_text(
        t("language_set", lang=lang_code, name=name)
    )
