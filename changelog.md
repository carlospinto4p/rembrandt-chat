
## Changelog - Rembrandt-Chat

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