# Telegram UI Design

All buttons, keyboards, and messages must be designed with
Telegram's constraints in mind. Think like a user on a small
phone screen.

## Inline Keyboard Buttons

- **Keep button labels short** (under ~30 characters). Telegram
  truncates long labels and the cutoff varies by device/screen.
- When the content is too long for a button label, move the full
  text into the message body and use short labels (numbers,
  letters, icons) on the buttons.
- Place short buttons side-by-side in a single row; use one
  button per row only when labels are medium-length.
- Paginate or nest keyboards when there are more than 4-5
  options.
- **Every keyboard must have an escape** — include a cancel or
  back button so the user is never stuck in a dead end.
- **Destructive actions** (delete, stop, reset) must have a
  confirmation step that names the item being affected
  (e.g., "Delete 'gato'?" not just "Are you sure?").
- Make confirmation button labels symmetric and action-oriented
  (e.g., "Delete" / "Keep", not "Yes" / "No").

## Message Content

- Telegram supports HTML and Markdown V2. The bot uses HTML
  (`parse_mode=HTML` set globally via `Defaults`).
- All `t()` kwargs are auto-escaped by `html.escape()`.
  Use raw HTML tags only in template strings, never in
  user-generated content.
- Keep messages concise — mobile screens show ~40-50 characters
  per line.
- Use blank lines to separate logical sections (prompt, options,
  context).
- **Next-step hints** — after completing a flow (session end,
  word added, import done, stats shown), always suggest what
  the user can do next (e.g., "Use /play for another session").
- **Empty states** — when there are no items (no words, no
  stats, no history), include a helpful prompt pointing the
  user to the right command.
- **Error messages** — explain what went wrong AND what the user
  should do to recover. Never leave the user with just
  "Something went wrong."

## Multi-Step Flows

- Every step in a conversation (addword, bulkimport, import)
  must mention `/cancel` is available.
- Acknowledge each step ("Got it, now send me...") instead of
  silently waiting.
- Set conversation timeouts so stale state doesn't persist
  indefinitely.
- Handle unexpected input (images, stickers) with a helpful
  message instead of silent ignoring.

## Internationalisation

- **All user-facing text** must go through `t()` — never
  hardcode English or Spanish strings in formatting functions.
- Use proper plural forms instead of `"word(s)"` or
  `"day(s)"`.
- Verify `lang=` is passed as a keyword argument to `t()`.
