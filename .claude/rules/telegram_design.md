# Telegram UI Design

All buttons, keyboards, and messages must be designed with
Telegram's constraints in mind.

## Inline Keyboard Buttons

- **Keep button labels short** (under ~30 characters). Telegram
  truncates long labels and the cutoff varies by device/screen.
- When the content is too long for a button label, move the full
  text into the message body and use short labels (numbers,
  letters, icons) on the buttons.
- Place short buttons side-by-side in a single row; use one
  button per row only when labels are medium-length.
- Paginate or nest keyboards when there are more than 4-5
  options (see `feedback_long_option_lists` memory).

## Message Formatting

- Telegram supports HTML and Markdown V2. The bot uses HTML
  (`parse_mode=HTML`).
- Keep messages concise — mobile screens show ~40-50 characters
  per line.
- Use blank lines to separate logical sections (prompt, options,
  context).
