
## Changelog - Rembrandt-Chat

### v0.36.21 - 5th April 2026

- `.claude/`:
  - Updated `backlog` skill (v1.4.0): tables now
    always include Priority and Effort columns.


### v0.36.20 - 5th April 2026

- `.claude/hooks/`:
  - Fixed stdin consumption: all hooks now
    capture stdin before piping to python.


### v0.36.19 - 5th April 2026

- `.claude/`:
  - Updated `backlog` skill (v1.3.0): auto-cleans
    completed items before display, shows per-section
    tables when backlog has multiple sections.
  - Updated `backlog` rule: added auto-cleanup
    section.


### v0.36.18 - 5th April 2026

- `.claude/`:
  - Updated `backlog` skill (v1.1.0): auto-cleans
    completed items when 5+ accumulate.
  - Updated `backlog` rule: added auto-cleanup
    section.


### v0.36.17 - 4th April 2026

- `.claude/hooks/`:
  - Added `block-raw-python.sh`: enforces `uv run python`
    over bare `python`.


### v0.36.16 - 4th April 2026

- `.claude/rules/`:
  - Normalized `versioning.md` to enhanced canonical
    with detailed sub-bullet guidance.


### v0.36.15 - 3rd April 2026

- `.claude/rules/`:
  - Normalized `committing.md` to canonical template.


### v0.36.14 - 3rd April 2026

- `CLAUDE.md`:
  - Normalized to canonical template: added missing
    shared sections, removed low-value sections.


### v0.36.13 - 3rd April 2026

- `.claude/`:
  - Migrated `/i18n-review`, `/ux-improvements` from command to skill (v1.0.0)
    for version tracking.


### v0.36.12 - 3rd April 2026

- `.claude/`:
  - Migrated `/self-refinement` from command to skill
    (v1.0.0) for version tracking.


### v0.36.11 - 3rd April 2026

- `.claude/`:
  - Migrated `/improvements` from command to skill (v1.0.0)
    for version tracking.


### v0.36.10 - 3rd April 2026

- `.claude/`:
  - Migrated `/optimize` from command to skill (v1.0.0)
    for version tracking.


### v0.36.9 - 3rd April 2026

- `.claude/`:
  - Migrated `/refactor` from command to skill (v1.0.0)
    for version tracking.


### v0.36.8 - 3rd April 2026

- `.claude/`:
  - Updated hooks to v2: read stdin JSON instead of
    broken `$CLAUDE_TOOL_INPUT`/`$CLAUDE_FILE` env vars.
  - Added script files in `.claude/hooks/`.


### v0.36.7 - 2nd April 2026

- `.claude/settings.json`:
  - Added PreToolUse hook to block compound git commands.


### v0.36.6 - 2nd April 2026

- `CLAUDE.md`:
  - Added Shell Commands, Project Configuration, Versioning / Release,
    and Testing sections.


### v0.36.5 - 2nd April 2026

- Added `/backlog` skill in `.claude/skills/backlog/`.


### v0.36.4 - 2nd April 2026

- Added `/i18n-review` skill for auditing linguistic quality
  of all translations in `i18n.py`.


### v0.36.3 - 2nd April 2026

- Fixed Spanish translations in `i18n.py`:
  - `no_weak_words`: fixed misplaced ¡ spanning two sentences
  - `word_empty`: "estaba vacía" → "está vacía" (present tense)
  - `imported_cards`: "exitosamente" → "correctamente" (anglicism)
  - `send_file`, `json_read_error`: added missing comma after
    "Por favor"


### v0.36.2 - 1st April 2026

- Fixed Spanish `mc_prompt` translation: "¿Cuál definición
  corresponde a esta palabra?" → "¿Cuál es la definición de
  esta palabra?" for more natural phrasing.


### v0.36.1 - 1st April 2026

- Fixed inconsistent capitalization in multiple-choice options:
  all options now start with an uppercase letter regardless of
  source data.


### v0.36.0 - 31st March 2026

- Bumped `rembrandt` dependency to v6.3.0: multiple-choice
  exercises now prefer same-topic distractors, making options
  harder by keeping them within the same domain.


### v0.35.4 - 31st March 2026

- Added extra blank line between keyword and options in
  `mc_prompt` i18n template for better readability.


### v0.35.3 - 31st March 2026

- Bumped `rembrandt` dependency to v6.2.1: fixes quality-based
  evaluation for `FLASHCARD` exercises (quality was silently
  ignored, causing all flashcard answers to be recorded as
  incorrect).


### v0.35.2 - 31st March 2026

- Fixed flashcard quality feedback in `session_handlers.py`:
  self-rated quality buttons now show neutral "Recorded" instead
  of misleading "Wrong"/"Correct" messages.
- Added `quality_recorded` i18n key.


### v0.35.1 - 31st March 2026

- Updated `.claude/rules/`:
  - `ux_review.md`: added bold emphasis check to message content
    audit.
  - `telegram_design.md`: documented global HTML parse_mode and
    auto-escaping in `t()`.


### v0.35.0 - 31st March 2026

- Enabled HTML `parse_mode` globally in `bot.py` via
  `Defaults(parse_mode=ParseMode.HTML)`.
- Updated `i18n.py`:
  - Added `html.escape` auto-escaping for all `t()` kwargs.
  - Styled exercise prompts, answer feedback, hints, skipped,
    and word-added messages with `<b>` bold tags.
  - Escaped `<term>` in `search_usage` to prevent HTML parsing.
- Updated `formatting.py`: added `html.escape` for user-generated
  content in list formatters (options, concepts, history, search
  results, topics).


### v0.34.1 - 30th March 2026

- Added catch-all callback handler in `bot.py`: unmatched
  button presses now show "This action is no longer available"
  instead of failing silently.
- Added `fallback_unknown_callback()` in `_helpers.py` and
  `action_expired` i18n key.


### v0.34.0 - 30th March 2026

- Added "Study these" button after `/weak` output: starts
  a session targeting the user's weak words.
- Added `STUDY_WEAK_CB` in `formatting.py` and
  `handle_study_weak()` in `session_handlers.py`.
- Added `study_these` i18n key.


### v0.33.28 - 30th March 2026

- Improved `/reminders` off message in `i18n.py`: replaced
  `[HH:MM]` jargon with a concrete example
  (`/reminders on 9:00`).


### v0.33.27 - 30th March 2026

- Improved `/search` usage message in `i18n.py`: added
  example (`/search hello`).


### v0.33.26 - 30th March 2026

- Simplified weak words display in `formatting.py`:
  `"4/10 errors (40%)"` → `"40% ❌"`.


### v0.33.25 - 30th March 2026

- Added emoji to quality button labels in `i18n.py` for
  faster visual scanning on mobile.


### v0.33.24 - 30th March 2026

- Improved delete confirmation button labels in `i18n.py`:
  "Yes, delete" / "No" → "Delete" / "Keep".


### v0.33.23 - 30th March 2026

- Allow retry on `/bulkimport` file errors in
  `word_handlers.py`: file read errors and "no valid words"
  now return to `AWAITING_BULK_FILE` instead of ending the
  conversation.
- Updated `file_read_error` and `no_valid_words` i18n keys
  to suggest retrying or `/cancel`.


### v0.33.22 - 30th March 2026

- Improved `/bulkimport` prompt in `i18n.py`: replaced
  format descriptions with inline examples showing CSV
  and text formats.


### v0.33.21 - 30th March 2026

- Added topic count to category buttons in `formatting.py`:
  both `/play` and `/topics` now show e.g. "Vocabulary (5)"
  instead of just "Vocabulary".


### v0.33.20 - 30th March 2026

- Improved global error handler in `bot.py`: now translated
  via `error_generic` i18n key and suggests `/cancel` to
  reset state.


### v0.33.19 - 30th March 2026

- Grouped `/help` commands into four categories in `i18n.py`:
  Learning, Words, Progress, and Settings.


### v0.33.18 - 30th March 2026

- Added fallback handlers for unexpected input in all
  conversation states in `bot.py`:
  - Text-expecting states (`/addword`): replies "Please send
    a text message" when user sends images, stickers, etc.
  - File-expecting states (`/bulkimport`, `/import`): replies
    "Please send a file, not text" when user sends text.
- Added `fallback_expected_text()` and
  `fallback_expected_file()` in `_helpers.py`.
- Added `expected_text` and `expected_file` i18n keys.


### v0.33.17 - 30th March 2026

- Added 5-minute conversation timeouts to all
  `ConversationHandler` instances (`/addword`, `/bulkimport`,
  `/import`) in `bot.py`.
- Added `CONVERSATION_TIMEOUT` constant and
  `conversation_timeout()` handler in `_helpers.py`.
- Added `conversation_timeout` i18n key.


### v0.33.16 - 30th March 2026

- Added next-step hint footer to all stats commands in
  `stats_handlers.py`:
  - `/stats`
  - `/weak`
  - `/forecast`
  - `/retention`
  - `/history`
- Added `stats_hint` i18n key.


### v0.33.15 - 30th March 2026

- Added `/cancel` hints to all multi-step flow prompts in
  `i18n.py`:
  - `send_word`
  - `send_definition`
  - `send_tags`
  - `bulkimport_prompt`
  - `import_prompt`


### v0.33.14 - 30th March 2026

- Fixed awkward `(s)` plurals in `i18n.py`: replaced with
  plain plural forms in:
  - `study_streak`
  - `imported_words`
  - `exported_cards`
  - `imported_cards`
  - `reminder_due`


### v0.33.13 - 30th March 2026

- Updated delete confirmation to show the word name:
  `"Delete \u201cgato\u201d?"` instead of `"Are you sure?"`.
- Updated `confirm_delete` i18n key to accept `{word}` param.
- Updated `handle_deleteword_callback` in `word_handlers.py`
  to fetch the concept before confirming.


### v0.33.12 - 30th March 2026

- Added cancel button to both language selection keyboards
  (`format_play_languages` and `format_languages` in
  `formatting.py`).
- Added `CANCEL_CB` constant and `handle_cancel_action()`
  handler for dismissing inline keyboards.
- Added `cancel_btn` i18n key.


### v0.33.11 - 30th March 2026

- Added back button to `/play` mode selection keyboard so
  users can return to the category list instead of being
  forced to pick a mode.
- Added `PLAY_BACK_PREFIX` in `formatting.py` and
  `handle_play_back()` in `session_handlers.py`.
- Added `back` i18n key.


### v0.33.10 - 30th March 2026

- Improved welcome message in `i18n.py`: explains the bot's
  purpose and lists key commands (`/play`, `/addword`, `/help`).


### v0.33.9 - 30th March 2026

- Updated `session_complete` i18n strings to include next-step
  hints ("Use /play for another session or /stats to see your
  progress") in both EN and ES.


### v0.33.8 - 30th March 2026

- Fixed `t("language_set", lang_code, ...)` in
  `session_handlers.py`: passed `lang_code` as keyword
  `lang=lang_code` so the confirmation shows in the
  correct language.


### v0.33.7 - 30th March 2026

- Translated hardcoded English in `formatting.py`:
  - `"errors"` (weak words list) → `t("errors", lang)`
  - `"cards due"` (forecast) → `t("forecast_line", lang)`
- Added i18n keys in `i18n.py`:
  - `errors`
  - `forecast_line`


### v0.33.6 - 30th March 2026

- Added `/ux-improvements` command:
  - `.claude/commands/ux-improvements.md`
  - `.claude/rules/ux_review.md`


### v0.33.5 - 30th March 2026

- Changed session mode buttons (Mixed, Learn new, Review due)
  to one per row in `session_handlers.py` for better tap
  targets on mobile.


### v0.33.4 - 30th March 2026

- Redesigned multiple-choice exercise layout in
  `formatting.py`: options now appear as a numbered list in
  the message body with compact `1 2 3 4` buttons in a
  single row, preventing Telegram from truncating long
  definitions.
- Added `.claude/rules/telegram_design.md`: guidelines for
  Telegram-friendly button and message design.


### v0.33.3 - 30th March 2026

- Changed default UI language from Spanish to English in
  `i18n.py`: when no user language is set, the bot now
  shows English text instead of Spanish.


### v0.33.2 - 26th March 2026

- Moved formatting logic out of `word_handlers.py`:
  - Added `format_concepts_list()` in `formatting.py`
  - Added `format_search_results()` in `formatting.py`
- Centralised callback-data prefixes: moved
  `PLAY_MODE_PREFIX` from `session_handlers.py` to
  `formatting.py` (joining the other prefixes already there).
- Split `handle_answer_callback` into sub-functions:
  - `_handle_reveal()`
  - `_handle_quality()`
  - `_handle_mc()`


### v0.33.1 - 26th March 2026

- Added shared helpers in `_helpers.py`:
  - `get_lang()`: replaces 3 identical `_lang()` definitions
  - `cleanup_session()`: deduplicates 5-line session teardown
    (was in `stop()` and `send_next()`)
  - `extract_command_arg()`: deduplicates 3-line argument
    parsing (was in `mywords`, `search`, `history`)
  - `require_category()`: deduplicates category lookup +
    error pattern (4 occurrences in `session_handlers.py`)
- Updated `session_handlers.py`, `word_handlers.py`,
  `stats_handlers.py` to use the new shared helpers.


### v0.33.0 - 26th March 2026

- Added `i18n.py` module with centralised translation system
  (`t()` function) supporting English and Spanish for all
  user-facing strings (68+ strings translated).
- Updated `formatting.py`: all format functions now accept a
  `lang` parameter; removed hardcoded English strings.
- Updated `session_handlers.py`: all handler messages use
  `t()` with the user's selected language.
- Updated `word_handlers.py`: all prompts, errors, and
  confirmation messages use `t()`.
- Updated `stats_handlers.py`: all stats, export/import, and
  reminder messages use `t()`.
- Updated `_helpers.py`: `check_active_session()` and
  `send_next()` use translated messages.


### v0.32.1 - 26th March 2026

- Fixed pagination nav buttons to use the user's selected
  language (Spanish by default, English when `lang == "en"`).


### v0.32.0 - 26th March 2026

- Added topic list pagination: when a category has more than
  5 topics, the keyboard is split into pages with Prev/Next
  navigation buttons instead of showing a flat list.
- Added new callback prefixes:
  - `PLAY_TPAGE_PREFIX` for `/play` topic page navigation
  - `TPAGE_PREFIX` for `/topics` topic page navigation
- Added handlers:
  - `handle_play_topic_page`
  - `handle_topic_page`
- Updated `format_play_topics()` and `format_topics()` with
  `page` and `cat_key` parameters.


### v0.31.11 - 26th March 2026

- Optimized `/search`: batched two sequential
  `db.get_concepts()` calls with `asyncio.gather()`.
- Optimized `/bulkimport`: batched sequential
  `db.add_concept()` calls with `asyncio.gather()`.
- Optimized flashcard reveal: replaced per-call
  `_quality_keyboard()` function with a pre-built
  `_QUALITY_KEYBOARD` module constant.


### v0.31.10 - 25th March 2026

- Added `WordEntry` type alias in `word_handlers.py` —
  replaces verbose `tuple[str, str, list[str]]` return type
  across 5 occurrences in file parsing functions.


### v0.31.9 - 25th March 2026

- Added `all_topics_label()` to `topic_translations.py` —
  deduplicates hardcoded "All topics" / "Todos los temas"
  strings in `formatting.py` and `session_handlers.py`.


### v0.31.8 - 25th March 2026

- Moved test factory helpers to `conftest.py`:
  - `make_language()`, `make_languages()`
  - `make_translation()`
  - `make_topic()`, `make_topic_progress()`
- Removed duplicate definitions from `test_handlers.py`.


### v0.31.7 - 25th March 2026

- Consolidated `format_play_topics()` and `format_topics()`
  into a shared `_format_topic_list()` helper in
  `formatting.py`. Both public functions are now thin
  wrappers.


### v0.31.6 - 25th March 2026

- Extracted `get_category_topics()` helper in `_helpers.py`
  — deduplicates category filtering + progress gathering
  in `handle_play_category()` and `handle_category_callback()`
  (2 occurrences).
- Removed unused `asyncio` and `topic_progress` imports from
  `session_handlers.py`.


### v0.31.5 - 25th March 2026

- Extracted `setup_translations()` helper in `_helpers.py`
  — deduplicates translation lookup + cache pattern across
  `_start_session()`, `review()`, and `require_session()`
  restoration (3 occurrences).
- Removed unused `_lookup_translation` and
  `_build_translation_map` imports from `session_handlers.py`.


### v0.31.4 - 25th March 2026

- Extracted `check_active_session()` helper in `_helpers.py`
  — deduplicates the active-session guard across 7 call sites
  in `session_handlers.py`.
- Removed `_ACTIVE_SESSION_MSG` constant from
  `session_handlers.py` (moved to `_helpers.py`).


### v0.31.3 - 25th March 2026

- Fixed `send_next()` call indentation in
  `handle_answer_callback()` — arguments were misaligned
  at two call sites (quality and MC branches).


### v0.31.2 - 25th March 2026

- Added confirmation step to `/deleteword`: tapping a word
  now shows "Are you sure? [Yes, delete / No]" before
  actually deleting.
- Updated `formatting.py`: added `DEL_CONFIRM_PREFIX` and
  `DEL_CANCEL_CB` callback-data constants.
- Updated `word_handlers.py`:
  - `handle_deleteword_callback()`: now shows confirmation
    instead of deleting immediately.
  - `handle_deleteword_confirm()`: performs the actual
    deletion.
  - `handle_deleteword_cancel()`: cancels the deletion.
- Updated `bot.py`: registered confirmation and cancel
  callback handlers.


### v0.31.1 - 25th March 2026

- Added `/cancel` global command: cancels any active
  conversation (addword, import, bulkimport). When no
  conversation is active, replies "Nothing to cancel."
- Updated `session_handlers.py`: added `cancel()` handler
  and `/cancel` in help text.
- Updated `bot.py`: registered global `/cancel` handler
  after conversation handlers and added bot menu entry.


### v0.31.0 - 25th March 2026

- Added `/bulkimport` command: upload a file to add multiple
  words at once. Supported formats:
  - CSV with `front,back` columns (optional `tags` column,
    semicolon-separated).
  - Text with one `word — definition` per line (em-dash,
    en-dash, or hyphen separator).
- Updated `word_handlers.py`:
  - `bulkimport_start()`, `bulkimport_file()`,
    `bulkimport_cancel()` conversation handlers.
  - `_parse_bulk_file()`, `_parse_csv()`, `_parse_text()`
    parsers.
- Updated `bot.py`: registered `/bulkimport` conversation
  handler and bot menu entry.
- Updated `session_handlers.py`: added `/bulkimport` to help
  text.


### v0.30.1 - 25th March 2026

- Added example sentences in exercises: when a
  `ConceptTranslation` has a non-empty `context` field,
  it is shown below the prompt as "Example: ...".
- Updated `formatting.py`:
  - `_context_line()` helper.
  - `_fmt_multiple_choice()`: appends context line.
  - `_fmt_flashcard_prompt()`: appends context line.


### v0.30.0 - 25th March 2026

- Added `/review` shortcut: starts a review-due session for
  the last-used topic, skipping the full selection flow.
- Updated `_helpers.py`:
  - `LAST_TOPIC` key: persists the last topic's concept IDs.
  - `persist_session_config()`: now also saves `_last_topic`.
  - `_restore_user_state()`: restores both language and last
    topic from the state file (renamed from `_restore_language`).
- Updated `session_handlers.py`: added `review()` handler.
- Updated `bot.py`: registered `/review` command and bot menu
  entry.


### v0.29.3 - 25th March 2026

- Added per-topic completion percentages to `/stats`: shows
  progress for all topics the user has studied.
- Updated `formatting.py`: added `format_topic_progress()`.
- Updated `stats_handlers.py`: `/stats` fetches topic progress
  via `asyncio.gather()` and appends it to the output.


### v0.29.2 - 25th March 2026

- Added `/search <term>` command: search shared and user-owned
  vocabulary by front/back text match (case-insensitive,
  up to 20 results).
- Updated `word_handlers.py`: added `search()` handler.
- Updated `bot.py`: registered `/search` command and bot menu
  entry.
- Updated `session_handlers.py`: added `/search` to help text.


### v0.29.1 - 25th March 2026

- Added study streak tracking: `/stats` now shows the number
  of consecutive days with at least one answer.
- Updated `formatting.py`:
  - `compute_streak()`: counts consecutive study days.
  - `format_daily_stats()`: added `streak` parameter.
- Updated `stats_handlers.py`: `/stats` computes and displays
  the streak.


### v0.29.0 - 25th March 2026

- Added session and language persistence: user state survives
  bot restarts via a JSON file (`data/user_state.json`).
- Added `persistence.py`:
  - `save_user_state()`, `load_user_state()`,
    `clear_session_config()`.
- Updated `config.py`: added `get_state_path()`.
- Updated `_helpers.py`:
  - `require_session()` is now async and auto-restores
    sessions from persisted config after a restart.
  - `persist_session_config()`, `persist_language()` helpers.
  - `_build_review_config()` and `_build_translation_map()`
    moved from `session_handlers.py`.
  - `send_next()` clears persisted config on session end.
- Updated `session_handlers.py`:
  - `_start_session()` persists session config on creation.
  - `stop()` clears persisted session config.
  - `handle_play_language()`, `handle_language_callback()`
    persist language preference.
- Updated `bot.py`: stores state file path in `bot_data`.


### v0.28.0 - 25th March 2026

- Added `/reminders` command: daily review notifications via
  Telegram's `JobQueue`.
  - `/reminders on [HH:MM]` — enable at given time (default
    09:00 UTC).
  - `/reminders off` — disable.
  - `/reminders` — show current status.
  - Sends a message when reviews are due.
- Updated `stats_handlers.py`:
  - `reminders()` handler.
  - `_reminder_callback()` job callback.
  - `_parse_reminder_args()` argument parser.
- Updated `bot.py`: registered `/reminders` command and bot menu
  entry.
- Updated `session_handlers.py`: added `/reminders` to help text.


### v0.27.3 - 25th March 2026

- Added global error handler: logs unhandled exceptions and
  sends a user-friendly message.
- Updated `bot.py`: added `_error_handler()` and registered it
  via `add_error_handler()`.


### v0.27.2 - 25th March 2026

- Added Telegram bot menu: registers all commands via
  `set_my_commands()` on startup so users see autocomplete
  when typing `/`.
- Updated `bot.py`:
  - `_BOT_COMMANDS` list with 17 command descriptions.
  - `_post_init()`: calls `set_my_commands()` during startup.


### v0.27.1 - 25th March 2026

- Added `/help` command: lists all available bot commands with
  descriptions.
- Updated `session_handlers.py`: added `help_command()` handler.
- Updated `bot.py`: registered `/help` command handler.


### v0.27.0 - 25th March 2026

- Added nested topic selection: users pick a category first
  (Data Science, Vocabulary, Culture), then a topic within it.
- Added `topic_translations.py`:
  - `Category` dataclass with bilingual names.
  - `CATEGORIES` list grouping 54 topics into 3 categories.
  - `get_category()` and `category_name()` helpers.
- Updated `formatting.py`:
  - `format_play_categories()`: category keyboard for `/play`.
  - `format_categories()`: category keyboard for `/topics`.
- Updated `session_handlers.py`:
  - `handle_play_category()`: new handler for `/play` flow.
  - `handle_category_callback()`: new handler for `/topics` flow.
  - `handle_play_language()`: now shows categories instead of
    the full topic list.
  - `topics()`: now shows categories instead of the full
    topic list.
- Updated `bot.py`: registered new callback handlers.


### v0.26.0 - 25th March 2026

- Added `topic_translations.py`: English translations for
  all 54 topic titles.
- Updated `formatting.py`:
  - `format_play_topics()`: added `lang` parameter, translates
    topic titles and "All topics" / "Todos los temas" label.
  - `format_topics()`: added `lang` parameter, translates
    topic titles.
- Updated `session_handlers.py`: passes user language to
  topic formatting and direct title displays.


### v0.25.1 - 24th March 2026

- Added `scripts/load_all_translations.py`: English translations
  for all 589 concepts (60 data science + 529 Spanish).
- Updated `data/rembrandt.db`: all concepts now have English
  translations.


### v0.25.0 - 24th March 2026

- Added `scripts/migrate_topics.py`: one-time migration to create
  topics for the existing database.
- Updated `data/vocab.csv`: expanded from 120 to 589 words
  (60 data science + 529 Spanish).
- Added `data/topics.json`: 54 topics with `concept_ids`
  (replaces `lessons.json` format with `word_ranks`):
  - "Data Science - Basics" (60 concepts)
  - 53 Spanish vocabulary topics
- Updated `data/rembrandt.db`: migrated with 409 new Spanish
  concepts and all 54 topics.


### v0.24.2 - 24th March 2026

- Removed `SELF_GRADED` exercise type support: only `FLASHCARD`
  (with reveal step) is used for recall-based exercises.


### v0.24.1 - 23rd March 2026

- Added `scripts/load_english_translations.py`: loads 120
  English translations for the bundled Spanish vocabulary.
- Fixed `data/vocab.csv` headers: `word_from,word_to` →
  `front,back` (required by rembrandt v6.2.0).


### v0.24.0 - 23rd March 2026

- Updated `rembrandt` dependency to v6.2.0.
- Added language support to `/play` flow: language → topic → mode.
- Added `/language` command to set preferred language.
- Added `handle_play_language()` and `handle_language_callback()`
  handlers.
- Added `format_play_languages()` and `format_languages()`
  formatters.
- Updated exercise formatters to accept optional
  `ConceptTranslation` for translated display.
- Updated `send_next()` to look up translations when a
  language is set.
- Added `_build_translation_map()` for MC option translation.
- Registered default languages (Spanish, English) on first run.


### v0.23.0 - 23rd March 2026

- Added topic-first flow to `/play`: user now picks a topic (or
  "All topics") before selecting session mode.
- Added `handle_play_topic()` handler and `format_play_topics()`
  formatter.
- Added `PLAY_TOPIC_PREFIX` callback prefix.


### v0.22.2 - 23rd March 2026

- Updated `.claude/rules/committing.md`: added explicit rule against
  compound git commands (one command per Bash call).


### v0.22.1 - 19th March 2026

- Updated `rembrandt` dependency to v6.0.0.
- Removed `REVERSE_FLASHCARD` exercise type (dropped in rembrandt v6).
- Removed `_fmt_typed` formatter and typed-answer formatting branch.


### v0.22.0 - 19th March 2026

- Updated `rembrandt` dependency to v5.0.2.
- Adapted all source and test files to rembrandt v5 API:
  - `Word` → `Concept` (`word_from`/`word_to` → `front`/`back`)
  - `Lesson` → `Topic`, `LessonProgress` → `TopicProgress`
  - `WeakWord` → `WeakConcept`
  - `import_words_csv` → `import_concepts_csv`
  - `load_lessons` → `load_topics`, `lesson_progress` → `topic_progress`
  - DB methods: `get_words` → `get_concepts`, `add_word` → `add_concept`,
    `delete_word` → `delete_concept`, `weak_words` → `weak_concepts`,
    `get_lessons` → `get_topics`, `get_lesson` → `get_topic`
- Renamed `/lessons` command to `/topics`.
- Removed `LANG_FROM`/`LANG_TO` config constants (no longer needed
  by rembrandt v5).
- Removed CEFR badge display (field no longer in `Concept` model).
- Removed exercise types no longer in rembrandt v5:
  - `CONJUGATION`
  - `CLOZE`
  - `TRANSLATION_CLOZE`
  - `GENDER_MATCH`
  - `ADJECTIVE_AGREEMENT`
  - `SENTENCE_ORDER`


### v0.21.9 - 17th March 2026

- Updated `rembrandt` dependency to v3.2.2: definition mode now 95%
  multiple choice / 5% self-graded.


### v0.21.8 - 17th March 2026

- Updated `rembrandt` dependency to v3.2.1: removes reverse flashcard
  from definition mode (synonyms made typing exact words too difficult).


### v0.21.7 - 16th March 2026

- Fixed WAL mode setup crashing on startup when database is temporarily locked.


### v0.21.6 - 16th March 2026

- Improved self-graded exercise UX: added descriptive labels to quality
  buttons (e.g. "0 - No idea", "5 - Easy") and "How well did you know it?"
  prompt. Changed layout to two buttons per row.


### v0.21.5 - 16th March 2026

- Fixed "database is locked" errors by enabling SQLite WAL mode on startup.


### v0.21.4 - 16th March 2026

- Fixed multiple choice formatting: show the word as the prompt and
  definitions as options (was showing definition as both prompt and option).
- Changed multiple choice layout to one button per row for long definitions.


### v0.21.3 - 16th March 2026

- Added `python-dotenv` dependency to load `.env` file on startup.


### v0.21.2 - 16th March 2026

- Updated `get_bundled_vocab_dir()`: defaults to `data/` so bundled
  vocabulary and lessons load automatically on first run.


### v0.21.1 - 16th March 2026

- Updated `get_database_path()`: defaults to `data/rembrandt.db` when
  `DATABASE_PATH` is not set.
- Added `*.db` to `.gitignore`.


### v0.21.0 - 16th March 2026

- Switched database backend from PostgreSQL to SQLite:
  - Replaced `PostgresDatabase` with `Database` across all modules.
  - Renamed `DATABASE_URL` env var to `DATABASE_PATH`.
  - Updated `docker-compose.yml` to remove the `db` service.
- Updated `README.md` with new env var and Docker instructions.


### v0.20.1 - 16th March 2026

- Added `__version__` to `rembrandt_chat.__init__` via `importlib.metadata`.


### v0.20.0 - 13th March 2026

- Expanded bundled vocabulary from 299 to 529 words across 53 lessons.
- Added 23 new thematic lessons:
  - Fenómenos y estados I & II
  - Personas y tipos I & II
  - Sentimientos y emociones I & II
  - Conflictos y estratagemas
  - Espacios y lugares cultos
  - Salud y remedios
  - Adjetivos de carácter I & II
  - Adjetivos de aspecto físico
  - Adjetivos de condición
  - Verbos de comunicación
  - Verbos de percepción y pensamiento
  - Verbos de dominio y sometimiento
  - Verbos de movimiento
  - Psicología y mente
  - Sociología y poder
  - Religión y creencias
  - Naturaleza y geografía
  - Economía y hacienda
  - Virtudes y vicios
- Updated `scripts/build_vocab.py`: added ~280 manual definitions to eliminate dependency on Wiktionary API availability.


### v0.19.2 - 13th March 2026

- Expanded bundled vocabulary from 203 to 299 words across 30 thematic lessons (all lessons now fully populated).
- Updated `scripts/build_vocab.py`: added `MANUAL_DEFS` override dict with 40 manual definitions for words with broken, circular, or missing Wiktionary entries.
- Fixed 3 words missing from Wiktionary:
  - `tipificar`
  - `fisiopatología`
  - `sintomatología`


### v0.19.1 - 12th March 2026

- Fixed bundled vocabulary: replaced basic A1–B2 words with 120 advanced words (C1–C2) aimed at Spanish native speakers expanding their vocabulary.
- Updated `scripts/build_vocab.py`: new word list with 12 thematic lessons (adjetivos cultos, verbos precisos, retórica, filosofía, figuras retóricas, derecho, arcaísmos).
- Fixed ~20 low-quality Wiktionary definitions with manual replacements.


### v0.19.0 - 12th March 2026

- Added bundled Spanish vocabulary: 120 words in 12 thematic lessons, definitions sourced from es.wiktionary.org (CC BY-SA 4.0).
- Added `scripts/build_vocab.py`: fetches definitions from the Wiktionary API and generates data files.
- Added in `data/`:
  - `vocab.json`: vocabulary entries with rank, word, and definition.
  - `vocab.csv`: CSV format for `import_words_csv()`.
  - `lessons.json`: 12 lessons grouped by theme and CEFR level.
- Added `_load_bundled_lessons()` in `bot.py`: loads bundled vocabulary and lessons on first run via `BUNDLED_VOCAB_DIR` env var.
- Added `get_bundled_vocab_dir()` in `config.py`.
- Updated `README.md`: documented `BUNDLED_VOCAB_DIR` env var and bundled lessons.


### v0.18.4 - 12th March 2026

- Fixed `changelog.md`: grouped same-file changes under file-level bullets (v0.18.1, v0.18.2).
- Updated `versioning.md`: added "group by file" rule for 3+ changes to the same file.


### v0.18.3 - 12th March 2026

- Updated `stats_handlers.py`: `/history` now runs all 3 DB queries concurrently via `asyncio.gather()`.
- Updated `session_handlers.py`: `/lessons` now fetches all lesson progress concurrently via `asyncio.gather()`.
- Updated `word_handlers.py`: `/addword` clears leftover `_addword_*` keys on entry to prevent accumulation from abandoned conversations.


### v0.18.2 - 12th March 2026

- Added in `session_handlers.py`:
  - `_start_session()` helper: deduplicated session creation + first exercise fetch + error handling from `handle_play_mode` and `handle_lesson_callback`.
  - `_require_active_exercise()` helper: deduplicated no-session/no-exercise error logic from `/hint` and `/skip`.
- Added `require_message_conv()` decorator in `_helpers.py`: like `require_message` but returns `ConversationHandler.END` for conversation handlers (7 occurrences across 2 files).


### v0.18.1 - 12th March 2026

- Added in `_helpers.py`:
  - `require_message()` decorator: eliminates `effective_user`/`message` None guards from 15 handler functions.
  - `require_callback()` decorator: eliminates callback query None check + `query.answer()` boilerplate from 4 callback handlers.
  - `resolve_user_with_typing()`: combines `send_typing()` + `resolve_user()` (8 call sites).
- Added `_ACTIVE_SESSION_MSG` constant in `session_handlers.py`: deduplicated "already have active session" message (3 occurrences).


### v0.18.0 - 12th March 2026

- Added `/history` command: shows recent answers with word name, result icon, and timestamp.
- Added `history()` handler in `stats_handlers.py`: supports optional date filter (`/history 1d`, `3d`, `7d`, `30d`).
- Added `format_history()` in `formatting.py`.
- Updated `README.md`: added `/history` to the command table.


### v0.17.1 - 12th March 2026

- Fixed `changelog.md`: applied sub-bullet formatting for all entries listing 3+ items (per `versioning.md` rules).


### v0.17.0 - 12th March 2026

- Added CEFR level badge to exercise prompts: `[A1]`, `[B2]`, etc. when the word has a CEFR level.
- Updated `/mywords`: shows CEFR level next to each word when available.
- Added `_cefr_badge()` helper in `formatting.py`.


### v0.16.0 - 12th March 2026

- Added word tags to `/addword`: after entering the definition, users can type comma-separated tags or /skip.
- Updated `/mywords`: displays tags next to each word, supports `/mywords <tag>` filtering.
- Added in `word_handlers.py`:
  - `addword_tags()`
  - `addword_skip_tags()`
  - `_save_word()`
  - `AWAITING_TAGS`
- Updated `README.md`: documented tag support in `/addword` and `/mywords`.


### v0.15.0 - 12th March 2026

- Added `get_max_new_cards()` and `get_max_review_cards()` in `config.py`: read `MAX_NEW_CARDS` / `MAX_REVIEW_CARDS` env vars.
- Updated `session_handlers.py`: pass `ReviewConfig` with daily limits to both `handle_play_mode()` and `handle_lesson_callback()`.
- Updated `README.md`: documented new env vars in the configuration table.


### v0.14.1 - 12th March 2026

- Added `send_typing()` helper in `_helpers.py`: sends `ChatAction.TYPING` before slow operations.
- Updated `stats_handlers.py` with typing indicator:
  - `/stats`
  - `/weak`
  - `/forecast`
  - `/retention`
  - `/export`
  - `/import`
- Updated `word_handlers.py` with typing indicator:
  - `/mywords`
  - `/deleteword`
- Updated `session_handlers.py` with typing indicator for `/lessons`.


### v0.14.0 - 12th March 2026

- Added `/export` command: sends progress as a JSON file.
- Added `/import` command: restores progress from a JSON file (conversational flow).
- Added in `stats_handlers.py`:
  - `export_progress()`
  - `import_start()`
  - `import_file()`
  - `import_cancel()`
- Updated `README.md`: added `/export` and `/import` to the command table.


### v0.13.0 - 11th March 2026

- Added `/lessons` command: lists available lessons with completion progress, tap to start a lesson session.
- Added `handle_lesson_callback()` in `session_handlers.py`: creates a session scoped to a lesson's word set.
- Added `format_lessons()` and `LESSON_CB_PREFIX` in `formatting.py`.
- Updated `README.md`: added `/lessons` to the command table.


### v0.12.0 - 11th March 2026

- Added session mode selection: `/play` now shows an inline keyboard to pick Mixed, Learn new, or Review due.
- Added `handle_play_mode()` callback handler in `session_handlers.py`.


### v0.11.0 - 11th March 2026

- Added `/retention` command: shows overall retention rate over the last 30 days.
- Added `format_retention()` in `formatting.py`.
- Updated `README.md`: added `/retention` to the command table.


### v0.10.0 - 11th March 2026

- Added `/forecast` command: shows upcoming review workload per day (7-day lookahead).
- Added `format_forecast()` in `formatting.py`.
- Updated `README.md`: added `/forecast` to the command table.


### v0.9.0 - 11th March 2026

- Upgraded rembrandt dependency from v2.6.0 to v3.2.0.
- Migrated to async database API: `PostgresDatabase.connect()`, all DB calls and `Session.next_exercise()`/`Session.answer()` now use `await`.
- Updated `bot.py`: database init moved to `post_init` callback for async lifecycle.
- Updated `user_mapping.py`: `ensure_user()` is now async.
- Updated `_helpers.py`: `resolve_user()` and `send_next()` now await async calls.
- Updated all handler modules to await async DB and session methods.
- Updated all test mocks to use `AsyncMock` for async methods.


### v0.8.7 - 11th March 2026

- Restructured `README.md`: clearer flow from token to configuration to running the bot, with a dedicated "Running the Bot" section.


### v0.8.6 - 11th March 2026

- Removed redundant "Quick Start" section from `README.md` (covered by "Bot Setup" and "Deployment").


### v0.8.5 - 11th March 2026

- Updated `README.md`: clarified that the bot setup section is for deployers, not end users.


### v0.8.4 - 11th March 2026

- Updated `README.md`: added "Bot Setup: New vs Existing" section explaining the differences between creating a new bot and reusing an existing one.


### v0.8.3 - 10th March 2026

- Added `.env.example` with documented environment variables.
- Updated `README.md`: expanded deployment section with step-by-step Docker Compose instructions.


### v0.8.2 - 10th March 2026

- Split `handlers.py` into separate modules:
  - `_helpers.py`: shared helpers and user-data key constants:
    - `resolve_user()`
    - `get_session()`
    - `require_session()`
    - `send_next()`
  - `session_handlers.py`:
    - `/start`
    - `/play`
    - `/stop`
    - `/hint`
    - `/skip`
    - answer handlers
  - `word_handlers.py`:
    - `/addword`
    - `/mywords`
    - `/deleteword`
  - `stats_handlers.py`:
    - `/stats`
    - `/weak`
- Converted `handlers.py` into a re-export facade for backward compatibility.
- Updated `test_handlers.py`: patched `Session` in `session_handlers` module.


### v0.8.1 - 10th March 2026

- Refactored `handlers.py`:
  - Extracted `_resolve_user()` helper (deduplicated 7 call sites).
  - Extracted `_require_session()` / `_get_session()` guards (deduplicated session+exercise checks).
  - Replaced hardcoded `"es", "es"` with `LANG_FROM` / `LANG_TO` constants from `config.py`.
  - Moved inline import to top level in `deleteword`.
- Updated `config.py`: added `LANG_FROM` and `LANG_TO` constants.
- Updated `bot.py`: import `DEL_CB_PREFIX` from `formatting` and use language constants.
- Moved `DEL_CB_PREFIX` to `formatting.py` with other callback-data constants.
- Moved shared test helpers to `conftest.py`, removed duplication from:
  - `test_handlers.py`
  - `test_word_handlers.py`


### v0.8.0 - 10th March 2026

- Added `Dockerfile` and `docker-compose.yml` with PostgreSQL and bot services.
- Added `rembrandt-chat` console script entry point.
- Added base vocabulary loading on first run via `BASE_VOCAB_PATH` env var.
- Updated `bot.py`: logging setup and `_load_base_vocab()` on startup.
- Updated `config.py`: added `get_base_vocab_path()`.
- Added tests:
  - `test_bot.py`: 3 tests for base vocab loading logic.
  - `test_config.py`: 3 tests for `get_base_vocab_path()`.


### v0.7.0 - 10th March 2026

- Added `/stats` handler: show daily stats for the last 7 days.
- Added `/weak` handler: show the user's 10 weakest words.
- Added `format_daily_stats()` and `format_weak_words()` to `formatting.py`.
- Added 8 new tests (4 formatting + 4 handler).


### v0.6.0 - 10th March 2026

- Added `/addword` conversational handler: two-step flow (word, then definition) to add private words.
- Added `/mywords` handler: list user's private words.
- Added `/deleteword` handler: show private words as inline buttons, tap to delete.
- Updated `bot.py`: registered handlers:
  - `ConversationHandler` for `/addword`
  - `/mywords`
  - `/deleteword`
  - delete callback
- Added `test_word_handlers.py`: 10 tests for word management.


### v0.5.0 - 10th March 2026

- Added `/hint` handler: progressive hints during exercises.
- Added `/skip` handler: skip current exercise and advance.
- Updated `bot.py`: register `/hint` and `/skip` commands.
- Added tests for `/hint` and `/skip` (6 new tests).


### v0.4.0 - 10th March 2026

- Added `/play` handler: create a rembrandt `Session` and send the first exercise.
- Added `/stop` handler: end session and show summary.
- Added `handle_answer_text`: process typed answers for:
  - reverse flashcard
  - conjugation
  - cloze
- Added `handle_answer_callback`: process inline keyboard presses for:
  - multiple choice
  - self-graded quality
  - flashcard reveal
- Updated `bot.py`: registered handlers:
  - `/play`
  - `/stop`
  - callback query
  - text message
- Added handler tests:
  - `/play`
  - `/stop`
  - text answers
  - callback answers
  - session lifecycle


### v0.3.0 - 10th March 2026

- Added `formatting.py`: render exercises, answers, hints, and session summaries as Telegram messages with inline keyboards.
- Added `test_formatting.py`: 16 tests covering all exercise types and formatters.


### v0.2.0 - 10th March 2026

- Added `config.py`: load `TELEGRAM_BOT_TOKEN` and `DATABASE_URL` from env.
- Added `user_mapping.py`: `UserMapper` maps Telegram users to rembrandt users via `tg_<id>` convention, auto-registering on first contact.
- Added `handlers.py`: `/start` command handler with greeting and auto-registration.
- Added `bot.py`: application factory with polling entry point.
- Added `pytest-asyncio` dev dependency.
- Added unit tests:
  - `test_config.py`
  - `test_user_mapping.py`
  - `test_handlers.py`


### v0.1.1 - 9th March 2026

- Added `rembrandt` (v2.6.0) and `python-telegram-bot` (v21+) as dependencies.
- Added implementation backlog.


### v0.1.0 - 9th March 2026

- Initial commit.