
## Changelog - Rembrandt-Chat


### v0.36.67 - 24th July 2026

- Updated `.claude/rules/committing.md` from canonical: `uv.lock` is
  committed whenever it changed, and a lock-only diff takes no version
  bump or changelog entry (bumping `pyproject.toml` would push it ahead
  again and recreate the drift, so it never converges).
- Committed the pending `uv.lock` self-referential version line, per
  that same rule — it had been left dirty on disk.


### v0.36.66 - 24th July 2026

- Updated `.pre-commit-config.yaml`: the ruff hooks now run
  `uv run --no-sync ruff` instead of `uvx ruff`.
  - `uvx` resolves whatever ruff PyPI serves that day, so the commit
    gate and this project's own lock-pinned ruff were different
    versions — and any upstream ruff release could change the enforced
    rule set with no local change. `uv run` uses this project's ruff,
    so local and commit-time linting always agree.
  - `--no-sync` is required, not an optimization: a bare `uv run`
    re-syncs first, which on a version-bump commit rewrites `uv.lock`
    mid-hook and leaves pre-commit's stash/restore cycle fighting its
    own linter. Verified in programme v4.83.1.
  - `ruff format` loses its `.` argument: pre-commit already passes the
    staged files, and a literal `.` overrode that to format the whole
    tree.
  - Pushed from programme's canonical `python-base` skeleton (v4.83.1).


### v0.36.65 - 10th July 2026

- Rotated changelog: archived 2 entries to `changelog/2026.md`.


### v0.36.64 - 4th July 2026

- Rotated changelog: archived 2 entries to `changelog/2026.md`.


### v0.36.63 - 3rd July 2026

- Updated `.pre-commit-scripts/check_version_changelog.sh` to canonical:
  exclude `reservations/**` placeholder manifests from version-bump
  detection, so defensive package-name holds don't demand a changelog
  entry (programme fleet rollout).


### v0.36.62 - 1st July 2026

- Rotated changelog: archived 1 entries to `changelog/2026.md`.


### v0.36.61 - 28th June 2026

- Rotated changelog: archived 1 entries to `changelog/2026.md`.


### v0.36.60 - 25th June 2026

- Rotated changelog: archived 1 entries to `changelog/2026.md`.


### v0.36.59 - 25th June 2026

- Rotated changelog: archived 6 entries to `changelog/2026.md`.


### v0.36.58 - 20th June 2026

- Added `scripts/changelog-add.sh` (safe changelog-prepend helper) and the `check-version-changelog` pre-commit guard, distributed in the programme fleet rollout.


### v0.36.57 - 20th June 2026

- `scripts/backup_db.py`: tightened the shrink guard to refuse **any**
  snapshot smaller than the existing backup (was a >50% collapse) — a
  smaller source signals truncation/data loss. The refusal exits
  non-zero so the backup unit's `OnFailure` handler raises the alarm;
  `--allow-shrink` overrides. Added a one-byte-smaller regression test.


### v0.36.56 - 20th June 2026

- `scripts/backup_db.py`: guard `backup_one` against clobbering a good
  Dropbox backup with empty/fresh-machine data — refuse a missing or
  zero-byte source, and refuse a snapshot under 50% of the existing
  backup unless `--allow-shrink`. Added `tests/unit/test_backup_db.py`
  (5 tests). Mirrors programme's `backup_guard`.


### v0.36.55 - 20th June 2026

- Added `[tool.hatch.metadata] allow-direct-references = true` to
  `pyproject.toml`: the `rembrandt` git direct-reference dependency made
  `uv sync` fail at the editable build step (`Dependency #1 ... cannot be
  a direct reference unless ...`), blocking the venv on a fresh machine.


### v0.36.54 - 14th June 2026

- Added the `check-changelog-headers` pre-commit guard
  (`.pre-commit-scripts/check_changelog_headers.sh` + the `.pre-commit-config.yaml`
  stanza): blocks a changelog edit that overwrites an existing version
  header (the bug that silently lost manifold's `v0.1.35`).


### v0.36.53 - 13th June 2026

- Rotated changelog: archived 1 entries to `changelog/2026.md`.


### v0.36.52 - 13th June 2026

- Rotated changelog: archived 1 entries to `changelog/2026.md`.


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
