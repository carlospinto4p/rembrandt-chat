
## Changelog - Rembrandt-Chat

### v0.17.0 - 12th March 2026

- Added CEFR level badge to exercise prompts: `[A1]`, `[B2]`, etc. when the word has a CEFR level.
- Updated `/mywords`: shows CEFR level next to each word when available.
- Added `_cefr_badge()` helper in `formatting.py`.


### v0.16.0 - 12th March 2026

- Added word tags to `/addword`: after entering the definition, users can type comma-separated tags or /skip.
- Updated `/mywords`: displays tags next to each word, supports `/mywords <tag>` filtering.
- Added `addword_tags()`, `addword_skip_tags()`, `_save_word()`, and `AWAITING_TAGS` in `word_handlers.py`.
- Updated `README.md`: documented tag support in `/addword` and `/mywords`.


### v0.15.0 - 12th March 2026

- Added `get_max_new_cards()` and `get_max_review_cards()` in `config.py`: read `MAX_NEW_CARDS` / `MAX_REVIEW_CARDS` env vars.
- Updated `session_handlers.py`: pass `ReviewConfig` with daily limits to both `handle_play_mode()` and `handle_lesson_callback()`.
- Updated `README.md`: documented new env vars in the configuration table.


### v0.14.1 - 12th March 2026

- Added `send_typing()` helper in `_helpers.py`: sends `ChatAction.TYPING` before slow operations.
- Updated handlers with typing indicator:
  - `stats_handlers.py`: `/stats`, `/weak`, `/forecast`, `/retention`, `/export`, `/import`
  - `word_handlers.py`: `/mywords`, `/deleteword`
  - `session_handlers.py`: `/lessons`


### v0.14.0 - 12th March 2026

- Added `/export` command: sends progress as a JSON file.
- Added `/import` command: restores progress from a JSON file (conversational flow).
- Added `export_progress()`, `import_start()`, `import_file()`, `import_cancel()` in `stats_handlers.py`.
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
  - `_helpers.py`: shared helpers (`resolve_user`, `get_session`, `require_session`, `send_next`) and user-data key constants.
  - `session_handlers.py`: `/start`, `/play`, `/stop`, `/hint`, `/skip`, answer handlers.
  - `word_handlers.py`: `/addword`, `/mywords`, `/deleteword`.
  - `stats_handlers.py`: `/stats`, `/weak`.
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
- Updated `bot.py`: register `ConversationHandler` for `/addword`, `/mywords`, `/deleteword`, and delete callback.
- Added `test_word_handlers.py`: 10 tests for word management.


### v0.5.0 - 10th March 2026

- Added `/hint` handler: progressive hints during exercises.
- Added `/skip` handler: skip current exercise and advance.
- Updated `bot.py`: register `/hint` and `/skip` commands.
- Added tests for `/hint` and `/skip` (6 new tests).


### v0.4.0 - 10th March 2026

- Added `/play` handler: create a rembrandt `Session` and send the first exercise.
- Added `/stop` handler: end session and show summary.
- Added `handle_answer_text`: process typed answers for reverse flashcard, conjugation, cloze, etc.
- Added `handle_answer_callback`: process inline keyboard presses for multiple choice, self-graded quality, and flashcard reveal.
- Updated `bot.py`: register `/play`, `/stop`, callback query, and text message handlers; share `db` via `bot_data`.
- Added handler tests:
  - `/play`, `/stop`, text answers, callback answers, session lifecycle


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