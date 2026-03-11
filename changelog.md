
## Changelog - Rembrandt-Chat

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