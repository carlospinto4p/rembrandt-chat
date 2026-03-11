
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

### 2026.03.10

- [x] Upgrade rembrandt client version to v3.2.0

### 2026.03.11 (improvements pass)

- [x] `/forecast` command — show upcoming review workload per day using `db.forecast()`
- [x] `/retention` command — show overall retention rate using `db.retention_rate()`
- [ ] Session mode selection — inline keyboard on `/play` to pick learn-new, review-due, or mixed
- [ ] Tests for `stats_handlers.py` — `/stats` and `/weak` have zero coverage
- [ ] Lesson system — `/lessons` (list) and `/lesson <name>` (practice a word group) using rembrandt's lesson management
- [ ] Progress export/import — `/export` sends JSON with full SR state, `/import` restores it
- [ ] Typing indicator — send `ChatAction.TYPING` before slow operations
- [ ] Configurable daily limits — expose `max_new_cards` / `max_review_cards` via env vars or `/settings`
- [ ] Word tags — use rembrandt's `tags` field in `/addword`, display in `/mywords`, allow filtering by tag
- [ ] CEFR level display — show word difficulty (A1–C2) in exercise prompts and `/mywords`
- [ ] `/history` command — show recent answers with date filtering using `db.get_answer_history()`
