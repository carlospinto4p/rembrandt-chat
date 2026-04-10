
## Changelog - Rembrandt-Chat

### v0.36.27 - 11th April 2026

- `.claude/rules/`:
  - Decoupled `/refactor` rule: canonical
    `refactoring.md` is now procedural only.
  - Added `refactoring-areas.md` with
    project-specific code smells to watch.
- `.claude/skills/refactor/`:
  - Updated `SKILL.md` to read both canonical
    procedure and per-project areas.


### v0.36.26 - 11th April 2026

- `.claude/rules/`:
  - Decoupled `/optimize` rule: canonical
    `optimization.md` is now procedural only.
  - Added `optimization-areas.md` with
    project-specific performance areas.
- `.claude/skills/optimize/`:
  - Updated `SKILL.md` to read both canonical
    procedure and per-project areas.


### v0.36.25 - 10th April 2026

- `.claude/rules/`:
  - Decoupled `/improvements` rule: canonical
    `improvements.md` is now procedural only.
  - Added `improvement-areas.md` with
    project-specific areas to watch.
- `.claude/skills/improvements/`:
  - Updated `SKILL.md` to read both canonical
    procedure and per-project areas.


### v0.36.24 - 5th April 2026

- `.claude/rules/`:
  - Updated `versioning.md`: added changelog
    rotation section (30-version limit, yearly
    archives in `changelog/YYYY.md`).


### v0.36.23 - 5th April 2026

- `.claude/rules/`:
  - Updated `versioning.md`: added changelog
    rotation section (30-version limit, yearly
    archives in `changelog/YYYY.md`).


### v0.36.22 - 5th April 2026

- Rotated changelog: archived 110 old
  entries to `changelog/` yearly files.


### v0.36.21 - 5th April 2026

- `.claude/`:
  - Updated `backlog` skill (v1.4.0): tables now
    always include Priority and Effort columns.


### v0.36.20 - 5th April 2026

- `.claude/hooks/`:
  - Fixed stdin consumption: all hooks now
    capture stdin before piping to python.


### v0.36.19 - 5th April 2026

- `.claude/`:
  - Updated `backlog` skill (v1.3.0): auto-cleans
    completed items before display, shows per-section
    tables when backlog has multiple sections.
  - Updated `backlog` rule: added auto-cleanup
    section.


### v0.36.18 - 5th April 2026

- `.claude/`:
  - Updated `backlog` skill (v1.1.0): auto-cleans
    completed items when 5+ accumulate.
  - Updated `backlog` rule: added auto-cleanup
    section.


### v0.36.17 - 4th April 2026

- `.claude/hooks/`:
  - Added `block-raw-python.sh`: enforces `uv run python`
    over bare `python`.


### v0.36.16 - 4th April 2026

- `.claude/rules/`:
  - Normalized `versioning.md` to enhanced canonical
    with detailed sub-bullet guidance.


### v0.36.15 - 3rd April 2026

- `.claude/rules/`:
  - Normalized `committing.md` to canonical template.


### v0.36.14 - 3rd April 2026

- `CLAUDE.md`:
  - Normalized to canonical template: added missing
    shared sections, removed low-value sections.


### v0.36.13 - 3rd April 2026

- `.claude/`:
  - Migrated `/i18n-review`, `/ux-improvements` from command to skill (v1.0.0)
    for version tracking.


### v0.36.12 - 3rd April 2026

- `.claude/`:
  - Migrated `/self-refinement` from command to skill
    (v1.0.0) for version tracking.


### v0.36.11 - 3rd April 2026

- `.claude/`:
  - Migrated `/improvements` from command to skill (v1.0.0)
    for version tracking.


### v0.36.10 - 3rd April 2026

- `.claude/`:
  - Migrated `/optimize` from command to skill (v1.0.0)
    for version tracking.


### v0.36.9 - 3rd April 2026

- `.claude/`:
  - Migrated `/refactor` from command to skill (v1.0.0)
    for version tracking.


### v0.36.8 - 3rd April 2026

- `.claude/`:
  - Updated hooks to v2: read stdin JSON instead of
    broken `$CLAUDE_TOOL_INPUT`/`$CLAUDE_FILE` env vars.
  - Added script files in `.claude/hooks/`.


### v0.36.7 - 2nd April 2026

- `.claude/settings.json`:
  - Added PreToolUse hook to block compound git commands.


### v0.36.6 - 2nd April 2026

- `CLAUDE.md`:
  - Added Shell Commands, Project Configuration, Versioning / Release,
    and Testing sections.


### v0.36.5 - 2nd April 2026

- Added `/backlog` skill in `.claude/skills/backlog/`.


### v0.36.4 - 2nd April 2026

- Added `/i18n-review` skill for auditing linguistic quality
  of all translations in `i18n.py`.


### v0.36.3 - 2nd April 2026

- Fixed Spanish translations in `i18n.py`:
  - `no_weak_words`: fixed misplaced ¡ spanning two sentences
  - `word_empty`: "estaba vacía" → "está vacía" (present tense)
  - `imported_cards`: "exitosamente" → "correctamente" (anglicism)
  - `send_file`, `json_read_error`: added missing comma after
    "Por favor"


### v0.36.2 - 1st April 2026

- Fixed Spanish `mc_prompt` translation: "¿Cuál definición
  corresponde a esta palabra?" → "¿Cuál es la definición de
  esta palabra?" for more natural phrasing.


### v0.36.1 - 1st April 2026

- Fixed inconsistent capitalization in multiple-choice options:
  all options now start with an uppercase letter regardless of
  source data.


### v0.36.0 - 31st March 2026

- Bumped `rembrandt` dependency to v6.3.0: multiple-choice
  exercises now prefer same-topic distractors, making options
  harder by keeping them within the same domain.


### v0.35.4 - 31st March 2026

- Added extra blank line between keyword and options in
  `mc_prompt` i18n template for better readability.


### v0.35.3 - 31st March 2026

- Bumped `rembrandt` dependency to v6.2.1: fixes quality-based
  evaluation for `FLASHCARD` exercises (quality was silently
  ignored, causing all flashcard answers to be recorded as
  incorrect).


### v0.35.2 - 31st March 2026

- Fixed flashcard quality feedback in `session_handlers.py`:
  self-rated quality buttons now show neutral "Recorded" instead
  of misleading "Wrong"/"Correct" messages.
- Added `quality_recorded` i18n key.


### v0.35.1 - 31st March 2026

- Updated `.claude/rules/`:
  - `ux_review.md`: added bold emphasis check to message content
    audit.
  - `telegram_design.md`: documented global HTML parse_mode and
    auto-escaping in `t()`.


### v0.35.0 - 31st March 2026

- Enabled HTML `parse_mode` globally in `bot.py` via
  `Defaults(parse_mode=ParseMode.HTML)`.
- Updated `i18n.py`:
  - Added `html.escape` auto-escaping for all `t()` kwargs.
  - Styled exercise prompts, answer feedback, hints, skipped,
    and word-added messages with `<b>` bold tags.
  - Escaped `<term>` in `search_usage` to prevent HTML parsing.
- Updated `formatting.py`: added `html.escape` for user-generated
  content in list formatters (options, concepts, history, search
  results, topics).


### v0.34.1 - 30th March 2026

- Added catch-all callback handler in `bot.py`: unmatched
  button presses now show "This action is no longer available"
  instead of failing silently.
- Added `fallback_unknown_callback()` in `_helpers.py` and
  `action_expired` i18n key.


### v0.34.0 - 30th March 2026

- Added "Study these" button after `/weak` output: starts
  a session targeting the user's weak words.
- Added `STUDY_WEAK_CB` in `formatting.py` and
  `handle_study_weak()` in `session_handlers.py`.
- Added `study_these` i18n key.


### v0.33.28 - 30th March 2026

- Improved `/reminders` off message in `i18n.py`: replaced
  `[HH:MM]` jargon with a concrete example
  (`/reminders on 9:00`).


