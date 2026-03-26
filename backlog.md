
# Backlog - Rembrandt-Chat

### 2026.03.25 (improvements pass)

- [x] `/help` command — list all available commands with brief descriptions (HIGH impact, LOW effort)
- [x] Telegram bot menu — register commands via `set_my_commands()` in `_post_init()` so `/` shows the command list (HIGH impact, LOW effort)
- [x] Global error handler — log unhandled exceptions and send user-friendly error message (HIGH impact, LOW effort)
- [x] Daily review reminders — notify users when reviews are due, configurable via `/reminders on|off` (HIGH impact, MEDIUM effort)
- [x] Session persistence — persist session state so bot restarts don't lose in-progress sessions (HIGH impact, MEDIUM effort)
- [x] Streak tracking — track consecutive study days, show in `/stats`, congratulate milestones (HIGH impact, MEDIUM effort)
- [x] `/search <term>` command — search vocabulary by front/back text match (MEDIUM impact, LOW effort)
- [x] Topic progress in `/stats` — show per-topic completion percentages alongside daily activity (MEDIUM impact, LOW effort)
- [x] `/review` shortcut — start review-only session for last-used topic, skipping the full selection flow (MEDIUM impact, LOW effort)
- [x] Example sentences in exercises — display `ConceptTranslation.context` field during exercise prompts (MEDIUM impact, MEDIUM effort)
- [x] Bulk word import via file — upload CSV/text to add multiple words at once (MEDIUM impact, MEDIUM effort)
- [x] ~~Quiz mode with timer~~ — discarded
- [x] `/cancel` global command — universal escape from any active conversation state (LOW impact, LOW effort)
- [x] Confirm before `/deleteword` — add confirmation step to prevent accidental deletion (LOW impact, LOW effort)

### 2026.03.26 (v0.33.0 refactor review)

- [x] Extract `_lang()` to `_helpers.py` — identical 3-line function defined in `session_handlers.py`, `word_handlers.py`, and `stats_handlers.py`
- [x] Extract `_cleanup_session()` helper in `_helpers.py` — deduplicate 5-line session cleanup pattern (2 occurrences: `stop()` and `send_next()`)
- [x] Extract `_extract_command_arg()` helper in `_helpers.py` — deduplicate 3-line command argument parsing pattern (3 occurrences across `word_handlers.py` and `stats_handlers.py`)
- [x] Extract `_require_category()` helper — deduplicate category lookup + "not found" error pattern (4 occurrences in `session_handlers.py`)
- [x] Move formatting logic out of `word_handlers.py` — `mywords` and `search` build message text inline; extract to `format_concepts_list()` and `format_search_results()` in `formatting.py`
- [x] Centralise callback-data prefixes — `PLAY_MODE_PREFIX`, `PLAY_TOPIC_PREFIX`, `PLAY_LANG_PREFIX` are defined in `session_handlers.py` while the rest live in `formatting.py`; move all to one module
- [x] Split `handle_answer_callback` into sub-functions — 3 separate branches (reveal, quality, MC) each ~10 lines; extract to `_handle_reveal()`, `_handle_quality()`, `_handle_mc()`

### 2026.03.26 (UX feedback)

- [x] Paginate topic selection keyboard — when a category has more than 5 topics, group them into pages (or sub-groups) instead of showing a flat list of buttons (HIGH impact, MEDIUM effort)

### 2026.03.25 (v0.31.2 refactor review)

- [x] Fix `send_next` indentation in `handle_answer_callback` — args at lines 589-592 and 600-603 are misaligned (BUG)
- [x] Extract `_check_active_session` helper in `_helpers.py` — deduplicate active-session guard (7 occurrences in `session_handlers.py`)
- [x] Extract `_setup_translations` helper in `_helpers.py` — deduplicate translation lookup + cache pattern (3 occurrences across `session_handlers.py` and `_helpers.py`)
- [x] Extract `_get_category_topics` helper — deduplicate category filtering + progress gathering (2 occurrences in `session_handlers.py`)
- [x] Consolidate `format_play_topics` and `format_topics` in `formatting.py` — near-identical functions differing only in button prefix and "All topics" option
- [x] Move test factory helpers (`_language`, `_translation`, `_topic`, `_topic_progress`) from `test_handlers.py` to `conftest.py`
- [x] Add `all_topics_label()` to `topic_translations.py` — deduplicate hardcoded "All topics" / "Todos los temas" strings (2 occurrences)
- [x] Add `WordEntry` type alias in `word_handlers.py` — replace verbose `tuple[str, str, list[str]]` return type (4 occurrences)

### 2026.03.25 (v0.31.10 optimization review)

- [x] Batch `/search` queries with `asyncio.gather()` — two sequential `db.get_concepts()` calls in `word_handlers.py` (MEDIUM impact, LOW effort)
- [x] Batch `/bulkimport` word creation with `asyncio.gather()` — sequential `db.add_concept()` loop in `word_handlers.py` (MEDIUM impact, LOW effort)
- [x] Cache quality keyboard as module constant in `formatting.py` — same 6 buttons rebuilt on every flashcard reveal (LOW impact, TRIVIAL effort)

### 2026.03.09 (initial implementation)

- [x] User mapping — `/start` handler, auto-registration, telegram-to-rembrandt user mapping
- [x] Exercise flow — `/play`, `/stop`, answer handling, inline keyboards for multiple choice and self-graded
- [x] Formatting — `formatting.py` to render each exercise type as Telegram messages with appropriate keyboards
- [x] Hints and skip — `/hint`, `/skip` handlers
- [x] Word management — `/addword` conversational handler, `/mywords`, `/deleteword`
- [x] Stats — `/stats`, `/weak` handlers
- [x] Deployment — `Dockerfile`, `docker-compose.yml`, base vocab loading on first run

### 2026.03.10 (v0.8.0 refactor review)

- [x] Extract `_resolve_user()` helper in `handlers.py` to deduplicate mapper/db lookup (7 call sites)
- [x] Extract `_require_session()` guard in `handlers.py` to deduplicate session+exercise checks
- [x] Extract hardcoded `"es", "es"` language pair into a config constant
- [x] Move shared test helpers (`_user`, `_word`, `_context`, `_update`, `_callback_update`) to `conftest.py`
- [x] Move inline import to top level in `deleteword`
- [x] Consolidate callback-data constants (`DEL_CB_PREFIX` → `formatting.py`)
- [x] Split `handlers.py` into `session_handlers.py`, `word_handlers.py`, `stats_handlers.py`

### 2026.03.10

- [x] Upgrade rembrandt client version to v3.2.0

### 2026.03.11 (improvements pass)

- [x] `/forecast` command — show upcoming review workload per day using `db.forecast()`
- [x] `/retention` command — show overall retention rate using `db.retention_rate()`
- [x] Session mode selection — inline keyboard on `/play` to pick learn-new, review-due, or mixed
- [x] Tests for `stats_handlers.py` — `/stats` and `/weak` have zero coverage
- [x] Lesson system — `/lessons` (list) and `/lesson <name>` (practice a word group) using rembrandt's lesson management
- [x] Progress export/import — `/export` sends JSON with full SR state, `/import` restores it
- [x] Typing indicator — send `ChatAction.TYPING` before slow operations
- [x] Configurable daily limits — expose `max_new_cards` / `max_review_cards` via env vars or `/settings`
- [x] Word tags — use rembrandt's `tags` field in `/addword`, display in `/mywords`, allow filtering by tag
- [x] CEFR level display — show word difficulty (A1–C2) in exercise prompts and `/mywords`
- [x] `/history` command — show recent answers with date filtering using `db.get_answer_history()`

### 2026.03.12 (v0.18.0 refactor review)

- [x] Extract `@require_message` decorator in `_helpers.py` — deduplicate `effective_user`/`message` None guard (13 occurrences across 3 handler files)
- [x] Extract `@require_callback` decorator in `_helpers.py` — deduplicate callback query None check + `query.answer()` boilerplate (4 occurrences across 2 files)
- [x] Extract `resolve_user_with_typing()` helper in `_helpers.py` — combine `send_typing()` + `resolve_user()` calls (8 occurrences across 2 files)
- [x] Extract `_check_no_active_session()` helper in `session_handlers.py` — deduplicate "already have session" guard (3 occurrences)
- [x] Extract `_create_and_start_session()` helper in `session_handlers.py` — deduplicate session creation + first exercise fetch + error handling (2 occurrences)
- [x] Extract `_require_active_exercise()` helper in `session_handlers.py` — deduplicate no-session/no-exercise error logic in `/hint` and `/skip` (2 occurrences)
- [x] Standardise conversation handler early returns — unify `ConversationHandler.END` guard pattern with message decorator (5 occurrences across 2 files)

### 2026.03.12 (v0.18.2 optimization review)

- [x] Use `asyncio.gather()` for parallel DB queries in `/history` — `get_answer_history`, `get_words` (shared), and `get_words` (user) are independent but run sequentially (`stats_handlers.py`)
- [x] Use `asyncio.gather()` for parallel lesson progress in `/lessons` — N sequential `lesson_progress()` calls could run concurrently (`session_handlers.py`)
- [x] Clean up `_addword_*` conversation keys on all exit paths — `_addword_word` and `_addword_def` may linger in `user_data` if the conversation ends abnormally (`word_handlers.py`)

### 2026.03.12

- [x] Expand bundled vocabulary to ~300 words — re-run `scripts/build_vocab.py` with retry logic (already updated), fix remaining bad definitions, regenerate CSV, update changelog (v0.19.2)
- [x] Bundled Spanish vocabulary — curate ES-ES word definitions from Wiktionary (CC BY-SA), create vocabulary CSV and lesson JSON files, load on first run via `load_lessons()`

### 2026.03.20

- [x] Review `SELF_GRADED` and `FLASHCARD` exercise types — evaluate whether both are needed and if the UX flow makes sense (SELF_GRADED shows the answer immediately with no challenge)
- [x] Ask for topic before starting a session — `/play` should prompt the user to pick a topic first, then select the session mode
