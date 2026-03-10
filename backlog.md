
# Backlog - Rembrandt-Chat

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
