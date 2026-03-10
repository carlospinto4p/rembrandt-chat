
# Backlog - Rembrandt-Chat

### 2026.03.09 (initial implementation)

- [x] User mapping — `/start` handler, auto-registration, telegram-to-rembrandt user mapping
- [x] Exercise flow — `/play`, `/stop`, answer handling, inline keyboards for multiple choice and self-graded
- [x] Formatting — `formatting.py` to render each exercise type as Telegram messages with appropriate keyboards
- [x] Hints and skip — `/hint`, `/skip` handlers
- [ ] Word management — `/addword` conversational handler, `/mywords`, `/deleteword`
- [ ] Stats — `/stats`, `/weak` handlers
- [ ] Deployment — `Dockerfile`, `docker-compose.yml`, base vocab loading on first run
