
## Changelog - Rembrandt-Chat

### v0.36.36 - 2nd May 2026

- Rotated changelog: archived 2 entries to , keeping 30.



### v0.36.35 - 26th April 2026

- Updated `.claude/rules/committing.md`: remove SKIP workaround, ruff now runs via `uv run ruff` in all projects.



### v0.36.34 - 26th April 2026

- Updated `.claude/rules/committing.md`: add Windows `SKIP=ruff-format,ruff-fix` pattern for pre-commit hook failures when ruff is not in PATH.



### v0.36.33 - 20th April 2026

- Synced canonical `.gitignore` from programme (direnv block).


### v0.36.32 - 20th April 2026

- Synced canonical `.claude/rules/*.md` from programme.


### v0.36.31 - 19th April 2026

- Updated `scripts/pre-commit.sh`: canonical now auto-detects `tests/unit/` vs `tests/` and no-ops if neither exists. Synced from programme.


### v0.36.30 - 17th April 2026

- `.gitattributes`: Added LF line ending normalization.

### v0.36.29 - 15th April 2026

- `.claude/`: cross-project migration landed today:
  - Removed `.claude/hooks/block-raw-python.sh`; now provided globally at `~/.claude/hooks/` (PreToolUse Bash guard).
  - Removed `.claude/hooks/block-chained-commands.sh` and `.claude/skills/{refactor,improvements,optimize,self-refinement,backlog}/`; the hook and the five periodic-review skills are now provided globally under `~/.claude/`.
  - Removed `.claude/hooks/format-python.sh`; the ruff auto-format PostToolUse hook is now provided globally at `~/.claude/hooks/`.
  - Removed `.claude/hooks/pre-commit-tests.sh`; replaced by a global dispatcher at `~/.claude/hooks/pre-commit-tests.sh` that invokes `scripts/pre-commit.sh` on `git commit`. Added `scripts/pre-commit.sh` with the project-local test command.


### v0.36.28 - 12th April 2026

- Updated `.claude/hooks/block-chained-commands.sh`:
  propagated newline-chaining block from the
  programme canonical.


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


