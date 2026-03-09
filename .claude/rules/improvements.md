# Periodic Improvements

Proactively suggest new capabilities, features, and design
improvements for the bot.

## When to Suggest

1. **When the backlog runs low**: If the backlog has fewer than
   3-4 open items, suggest an `/improvements` pass to replenish
   it with fresh ideas. Check the backlog after completing tasks.

2. **During long sessions**: When wrapping up a session with
   multiple completed tasks, suggest improvements before finishing.

3. **When noticing gaps**: If you spot any of the following while
   working, flag them:
   - Missing bot features that users of similar bots would expect
   - UX improvements (better message formatting, richer keyboards)
   - New chat platform integrations (WhatsApp, Discord, etc.)
   - Missing convenience commands or shortcuts
   - Developer experience improvements (better errors, logging,
     debugging tools)

## What to Look For

- **Chat UX**: message formatting, inline keyboards, conversation
  flow improvements, emoji/sticker feedback, media support
- **New platforms**: WhatsApp, Discord, Slack adapters
- **Session features**: adaptive difficulty, streaks/gamification,
  progress visualisation in chat, daily reminders
- **Word management**: bulk import, sharing words between users,
  word categories/tags
- **Admin tools**: broadcast messages, usage analytics, vocabulary
  management commands
- **Deployment**: health checks, monitoring, auto-scaling, backup
- **Developer experience**: better logging, error reporting,
  debug mode, test utilities

## How to Suggest

- Present suggestions as a prioritized list with clear rationale
- Classify by impact (HIGH / MEDIUM / LOW) and effort
- Don't auto-apply — always propose and let the user decide
- Group related suggestions (e.g., "UX improvements",
  "new platforms", "admin tools")
- After each proposal, add the items to `backlog.md` under a new
  section with the current date as the title (see
  `.claude/rules/backlog.md` for format)
