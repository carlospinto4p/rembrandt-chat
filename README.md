
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

## Quick Start

1. Create a bot via [@BotFather](https://t.me/BotFather) and get your token.
2. Set environment variables:

```bash
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
export DATABASE_URL="postgresql://user:pass@localhost/rembrandt"
```

3. Run the bot:

```bash
rembrandt-chat
```

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

## Deployment

Run with Docker Compose:

```bash
docker compose up -d
```

The `docker-compose.yml` includes PostgreSQL and the bot as services.
On first run, if `BASE_VOCAB_PATH` is set and the words table is empty,
the shared vocabulary is loaded automatically.
