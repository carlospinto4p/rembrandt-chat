
# Rembrandt Chat

A Telegram bot client for the [rembrandt](https://github.com/carlospinto4p/rembrandt)
library — learn Spanish vocabulary through chat-based exercises.

## Overview

Users interact with a Telegram bot to practice Spanish vocabulary using
definition-mode exercises (ES-ES: word + definition/synonyms). The bot
handles user identity via Telegram accounts, runs exercise sessions with
spaced-repetition scheduling, and lets users add their own private words.

## Installation

```bash
pip install rembrandt-chat
```

## Bot Setup: New vs Existing

End users just open a chat with the bot in Telegram and send `/start`
— no setup on their part. The sections below are for **deployers**
choosing between creating a fresh bot or reusing an existing one.

### Creating a new bot

If you don't have a Telegram bot yet:

1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot` and follow the prompts to choose a name and username.
3. BotFather will give you a token — set it as `TELEGRAM_BOT_TOKEN`.
4. Optionally, send `/setcommands` to BotFather to register the
   command list (see [Bot Commands](#bot-commands) below) so users
   get autocomplete when typing `/`.

With a new bot you start with an empty database — no users, no
words, no history. Set `BASE_VOCAB_PATH` to preload a shared
vocabulary on first run.

### Using an existing bot

If you already have a bot token from a previous deployment:

1. Set the same `TELEGRAM_BOT_TOKEN` in your environment.
2. Point `DATABASE_URL` to the existing database to preserve all
   users, words, scores, and session history.
3. The bot resumes exactly where it left off — no re-registration
   needed.

If you reuse the token but connect to a **new** database, the bot
will work but all users will appear as new (they just need to send
`/start` again). Their Telegram accounts are re-registered
automatically, but previous scores and words are lost.

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message, auto-register if new |
| `/play` | Start an exercise session |
| `/stop` | End session and show summary |
| `/hint` | Get a hint for the current exercise |
| `/skip` | Skip the current exercise |
| `/addword` | Add a new word (conversational) |
| `/mywords` | List your private words |
| `/deleteword` | Delete one of your words |
| `/stats` | Show daily stats and accuracy |
| `/weak` | Show your weakest words |

## Exercise Types

Definition mode generates three exercise types:

### Multiple choice

The bot shows a definition and four inline keyboard buttons:

```
Which word matches this definition?

"Que dura poco tiempo"

[efimero] [perpetuo] [antiguo] [moderno]
```

### Reverse flashcard

The bot shows a definition and the user types the answer:

```
What word means:

"Que dura poco tiempo"

Type your answer:
```

### Self-graded

The bot shows word + definition, user rates recall quality:

```
Review this word:

efimero — Que dura poco tiempo

How well did you know it?
[0 ] [1 ] [2 ] [3 ] [4 ] [5 ]
```

## Adding Words

Users can add private words via a conversational flow:

```
User: /addword
Bot:  Send the word:
User: efimero
Bot:  Send the definition:
User: Que dura poco tiempo
Bot:  Added "efimero" — Que dura poco tiempo
```

Private words are visible only to the user who added them.

## Configuration

Environment variables (loaded via `config.py`):

| Variable | Description | Example |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | `123456:ABC-DEF...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/rembrandt` |
| `BASE_VOCAB_PATH` | Path to shared vocabulary JSON (optional) | `data/spanish_10000.json` |

## Deployment (Docker Compose)

1. Copy the example environment file and fill in your bot token:

```bash
cp .env.example .env
```

2. Edit `.env` and set `TELEGRAM_BOT_TOKEN` to the token from
   [@BotFather](https://t.me/BotFather). Optionally set
   `BASE_VOCAB_PATH` to a vocabulary CSV file to preload on first run.

3. Start the services:

```bash
docker compose up -d
```

This spins up PostgreSQL and the bot. The database connection is
handled internally — no need to set `DATABASE_URL` when using
Docker Compose.

On first run, if `BASE_VOCAB_PATH` is set and the words table is
empty, the shared vocabulary is loaded automatically.

To view logs:

```bash
docker compose logs -f bot
```

To stop:

```bash
docker compose stop
```
