
## Changelog - Rembrandt-Chat




### v0.36.51 - 10th June 2026

- Rotated changelog: archived 2 entries to `changelog/2026.md`.

### v0.36.50 - 8th June 2026

- Synced from programme: reworded `versioning.md` changelog-prepend guidance (insert a new entry above the top header, never replace it) and added universal `.gitignore` entries (`*.bak.*`, `*.tmp.*`, etc.).


### v0.36.49 - 7th June 2026

- Rotated changelog: archived 1 entries to `changelog/2026.md`.

### v0.36.48 - 4th June 2026

- Rotated changelog: archived 7 entries to `changelog/2026.md`.

### v0.36.47 - 4th June 2026

- Synced `.claude/rules/committing.md` from the programme registry: step 6 now scopes `uv.lock` regeneration to code-related bumps only — non-code patch bumps (`.claude/` config, docs, changelog, rule syncs) skip `uv lock`.

### v0.36.46 - 3rd June 2026

- Synced `.claude/rules/testing.md` from the programme registry: added the SQLite-backed fixtures pointer to the session-scoped template pattern (see the shared `testing-python` rule).

### v0.36.45 - 3rd June 2026

- Updated `.gitignore`: ignore SQLite WAL-mode sidecars
  (`*.db-shm`, `*.db-wal`, `*.db-journal`) so transient files
  stop appearing as untracked.


### v0.36.44 - 1st June 2026

- Updated `.claude/rules/committing.md`: no-parallel-git-command rule and `-m` flag guidance.


### v0.36.43 - 31st May 2026

- Added `[build-system]` to `pyproject.toml`; `uv sync --all-extras` now handles the editable install automatically.


### v0.36.42 - 31st May 2026

- Added `scripts/backup_db.py`: snapshots `data/rembrandt.db` to
  `~/Dropbox/home/development/db/rembrandt_chat/` using the SQLite
  online backup API (atomic write; source opened read-only). Destination
  overridable via `REMBRANDT_CHAT_BACKUP_DEST` env var or `--dest` flag.


### v0.36.41 - 17th May 2026

- Rotated changelog: archived 5 old entries to `changelog/2026.md`.



### v0.36.40 - 9th May 2026

- Added `When to Skip Tests` section to `.claude/rules/committing.md`: explicit allowlist (markdown, version bump, lock file, `.claude/` config, `CLAUDE.md`) of diffs where tests can be safely skipped.



### v0.36.39 - 9th May 2026

- Regrouped 1 historical changelog entry flagged by `/changelog-review` (programme v2.52.143):
  - `changelog/2026.md` v0.25.0: 3 top-level bullets touching `data/` collapsed under one parent.


### v0.36.38 - 9th May 2026

- Updated `.claude/rules/versioning.md` (1.0 → 1.1): rewrote changelog-format section to fix rule/example contradiction; threshold now stated as "3+ top-level bullets touching the same module → group under a parent"; sub-bullet patterns reorganised; added "When NOT to group" section. Synced from programme v2.52.144.



### v0.36.37 - 8th May 2026

- Synced canonical rules from `programme` v2.52.139/v2.52.140: `backlog`, `refactoring`, `optimization`, `improvements` rules promoted to global (`~/.claude/rules/`) and removed locally; `versioning.md` updated with depth-based-cadence batch exception.



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


