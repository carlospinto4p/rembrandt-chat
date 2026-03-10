
## Changelog - Rembrandt-Chat

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