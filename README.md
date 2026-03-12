
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

## Getting a Bot Token

You need a Telegram bot token to run rembrandt-chat. If you already
have one from a previous deployment, skip to [Configuration](#configuration).

To create a new bot:

1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot` and follow the prompts to choose a name and username.
3. Copy the token BotFather gives you.
4. Optionally, send `/setcommands` to register the command list
   (see [Bot Commands](#bot-commands)) so users get autocomplete
   when typing `/`.

## Configuration

Set the following environment variables:

| Variable | Description | Required |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `BASE_VOCAB_PATH` | Path to shared vocabulary JSON | No |
| `MAX_NEW_CARDS` | Max new cards per session (0 = unlimited) | No |
| `MAX_REVIEW_CARDS` | Max review cards per session (0 = unlimited) | No |
| `BUNDLED_VOCAB_DIR` | Path to directory with bundled vocab/lesson files | No |

If `BASE_VOCAB_PATH` is set and the words table is empty on first
run, the shared vocabulary is loaded automatically.

If `BUNDLED_VOCAB_DIR` is set, the bot loads bundled vocabulary
and lessons on first run. Includes 120 advanced Spanish words
(C1–C2) for native speakers, across 12 thematic lessons:
adjetivos cultos, verbos precisos, retórica, filosofía, figuras
retóricas, derecho, and more. Set it to the `data/` directory
included in this repository.

## Running the Bot

```bash
rembrandt-chat
```

That's it. End users just open a chat with the bot in Telegram and
send `/start`.

### New bot vs existing database

With a **new bot and empty database**, you start fresh — no users,
no words, no history. Use `BASE_VOCAB_PATH` to preload vocabulary.

If you **reuse a token with the same database**, the bot resumes
exactly where it left off — all users, words, and scores are
preserved.

If you reuse a token but point to a **new database**, the bot works
but all users appear as new. They just send `/start` again to
re-register, but previous scores and words are lost.

## Deployment (Docker Compose)

1. Copy the example environment file and fill in your bot token:

```bash
cp .env.example .env
```

2. Edit `.env` and set `TELEGRAM_BOT_TOKEN`. Optionally set
   `BASE_VOCAB_PATH` to a vocabulary CSV file to preload.

3. Start the services:

```bash
docker compose up -d
```

This spins up PostgreSQL and the bot. No need to set `DATABASE_URL`
— Docker Compose handles the database connection internally.

To view logs:

```bash
docker compose logs -f bot
```

To stop:

```bash
docker compose stop
```

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message, auto-register if new |
| `/play` | Start an exercise session |
| `/stop` | End session and show summary |
| `/hint` | Get a hint for the current exercise |
| `/skip` | Skip the current exercise |
| `/addword` | Add a new word with optional tags |
| `/mywords [tag]` | List your private words, optionally filtered by tag |
| `/deleteword` | Delete one of your words |
| `/stats` | Show daily stats and accuracy |
| `/weak` | Show your weakest words |
| `/forecast` | Show upcoming review workload (7 days) |
| `/retention` | Show overall retention rate (30 days) |
| `/lessons` | List lessons and start a lesson session |
| `/history [1d\|3d\|7d\|30d]` | Show recent answer history |
| `/export` | Export your progress as a JSON file |
| `/import` | Import progress from a JSON file |

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
