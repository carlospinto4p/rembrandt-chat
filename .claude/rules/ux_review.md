# UX Review

Audit every user-facing interaction for Telegram UX quality.
Think like a user on a small phone screen with fat fingers.

## When to Suggest

1. **On demand**: When the user runs `/ux-improvements`.
2. **When noticing UX issues**: If you spot any of the items
   below while working on other tasks, flag them.

## What to Look For

### Message content
- Wording is clear, friendly, and action-oriented
- Error messages explain what went wrong **and** what to do next
- Success confirmations are present after every destructive or
  state-changing action (delete, stop, import, settings change)
- Empty states are handled (no words yet, no sessions, no stats)
  with a helpful prompt ("Try /addword to get started")
- Numbers, dates, and stats are formatted for readability
  (e.g., "42 words" not "42", locale-aware date formatting)

### Inline keyboards
- Follow `.claude/rules/telegram_design.md` constraints
- Button labels are short, action-oriented verbs or clear nouns
- Tap targets are large enough (one button per row for actions,
  side-by-side only for very short labels like numbers/icons)
- Destructive actions (delete, stop, reset) have a confirmation
  step and are visually separated from safe actions
- Every keyboard has a cancel/back option so the user is never
  stuck
- Pagination is present when options exceed 4-5 items

### Conversation flow
- Every multi-step flow (add word, bulk import, play setup) can
  be cancelled at any point
- The bot acknowledges each step ("Got it, now send me...")
  instead of silently waiting
- After finishing a session or flow, the bot suggests what to do
  next (e.g., "Play again? /play")
- Idle timeouts: long-running conversations don't hang forever

### Navigation and discoverability
- `/help` lists all commands with one-line descriptions
- Command menu is registered via `set_my_commands()`
- Related commands are cross-referenced (e.g., `/stats` mentions
  `/weak`, `/play` mentions `/review`)
- First-time users get a welcome message that guides them

### Accessibility and i18n
- All user-facing text is translated (EN + ES)
- Language preference persists across sessions
- Emoji usage is purposeful, not decorative — aids scanning
- Messages work well in both light and dark Telegram themes

### Error handling UX
- Network/DB errors show a user-friendly message, not a
  traceback
- Invalid input is caught early with a helpful correction hint
- Rate limits or API errors suggest retrying later

## How to Audit

1. **Read every handler** — trace each command from entry to all
   possible exits (success, error, cancel, timeout).
2. **Read every `t()` call** — check wording for clarity and
   helpfulness.
3. **Read every `InlineKeyboardMarkup`** — check layout, label
   length, cancel option, pagination.
4. **Read every `edit_message_text` / `reply_text`** — check for
   missing confirmations, empty-state handling, next-step hints.
5. **Cross-check with `telegram_design.md`** — flag any
   violations.

## How to Report

- Present findings as a prioritized list sorted by impact and
  effort
- Classify impact as HIGH / MEDIUM / LOW
- Classify effort as LOW / MEDIUM / HIGH
- Group related findings (e.g., "keyboard layout", "error
  messages", "conversation flow")
- Update `telegram_design.md` if the audit reveals new
  constraints or patterns worth codifying
- Add all items to `backlog.md` under a new section with the
  current date (see `.claude/rules/backlog.md` for format)
