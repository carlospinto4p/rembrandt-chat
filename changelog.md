
## Changelog - Rembrandt-Chat


### v0.36.86 - 27th September 2026

- `.claude/rules/committing.md`/`versioning.md`: pulled programme's
  canonical trim (2026-09-27 context-budget pass) — shorter
  Concurrent-Sessions wording, one fewer commit-message example, and
  the stale PEP-735 `uv pip install -e ".[dev]"` wording fixed. No
  behavior change.


### v0.36.85 - 25th September 2026

- Rotated changelog: archived 2 entries to `changelog/2026.md`.


### v0.36.84 - 23rd September 2026

- Gave the backup's temporary file a per-process name, so two runs
  snapshotting the same database can no longer write the same file.
  Fleet-wide change following the failure this caused in
  `knowledge_graph_news` on 2026-09-22, where a retired systemd unit
  was left installed beside its replacement and both ran the identical
  command at 02:00.
  - `scripts/backup_db.py`:
    - Added `_tmp_sibling`: writes `<dest>.<pid>.tmp` instead of the
      shared `<dest>.tmp`.
    - Added `_sweep_stale_tmp`: deletes temp siblings untouched for a
      day, including the older fixed `<dest>.tmp` form, which nothing
      reclaims once every run writes a pid-suffixed name. Errors are
      swallowed, since a concurrent run may sweep the same file and
      cleanup must not fail the backup it precedes.
    - Added `_STALE_TMP_AGE_S`.
- Added `tests/unit/test_backup_db.py` coverage: 6 tests — no temp file
  left behind, the pid in the name, a stale sibling and a stale legacy
  `.tmp` both swept, and a fresh sibling and the destination both left
  alone.


### v0.36.83 - 10th August 2026

- Rotated changelog: archived 2 entries to `changelog/2026.md`.


### v0.36.82 - 9th August 2026

- **Documented the Dropbox backup restore procedure.** Added a
  `## Restoring from backup` section to `README.md` — the plain `cp`
  step to copy `rembrandt.db` back from
  `~/Dropbox/home/development/db/rembrandt-chat/` after
  `scripts/backup_db.py` has snapshotted it.


### v0.36.81 - 4th August 2026

- Rotated changelog: archived 2 entries to `changelog/2026.md`.


### v0.36.80 - 1st August 2026

- Moved dev tooling from `[project.optional-dependencies]` to PEP 735
  `[dependency-groups]` in `pyproject.toml` — a bare `uv run`/`uv sync`
  no longer uninstalls pytest/ruff/pre-commit, since extras are
  opt-in per invocation but groups are not. Added `[tool.uv]
  default-groups = ["dev"]`.
- Updated `CLAUDE.md` and `.claude/rules/committing.md` install
  instructions from `uv sync --all-extras` to a bare `uv sync`.


### v0.36.79 - 31st July 2026

- Rotated changelog: archived 2 entries to `changelog/2026.md`.


### v0.36.78 - 30th July 2026

- Pruned the stale `Read(credentials/**)` deny from `.claude/settings.json`
  (superseded by the git-aware `block-read-secrets` hook, fleet-wide
  `push_to_projects.py --types projectperms` sync).


### v0.36.77 - 28th July 2026

- Rotated changelog: archived 7 entries to `changelog/2026.md`.


### v0.36.76 - 27th July 2026

- Updated `.claude/rules/committing.md` from canonical: added a
  "Concurrent Sessions" section covering the cross-session
  commit-pollution hazard (check `git status --porcelain`
  immediately before every commit, stage by name, diff before
  re-shipping a change another session already committed).


### v0.36.75 - 27th July 2026

- Fixed `scripts/backup_db.py`: `DEFAULT_DEST` now resolves to
  `~/Dropbox/home/development/db/rembrandt-chat` (was the stale
  `rembrandt_chat` underscore slug from before the project's registry
  rename). The old default had been silently writing nightly snapshots
  into a parallel directory instead of the project's real backup
  location. Added `test_default_dest_uses_hyphenated_project_slug`
  regression test.


### v0.36.74 - 26th July 2026

- Redeployed the hardened `scripts/changelog-add.sh`: guards against
  the CWD-relative wrong-repo footgun (comparing the target
  changelog's version against the wrong repo's manifest when invoked
  from outside its own directory).


### v0.36.73 - 25th July 2026

- Fixed 19 pre-existing `ruff check` errors (backlog item):
  - `bot.py`: moved `load_dotenv()` inside `create_app()` so config
    imports sit at the top of the file (10 `E402` errors — env vars
    are only read lazily inside functions, never at import time).
  - `_helpers.py`: imported `Exercise` from `rembrandt.models`
    instead of an unresolvable forward-reference string (`F821`).
  - `session_handlers.py`: removed the unused `ExerciseType` import
    and a dead `user_data` assignment; dropped the unused `answer`
    result from `_handle_quality` (self-graded flashcards don't get
    correct/wrong feedback, so the value was never meant to be used);
    re-exported `CANCEL_CB`/`STUDY_WEAK_CB` explicitly (`as`-aliased)
    since `handlers.py` re-imports them from this module.
  - `test_handlers.py`, `test_persistence.py`: removed unused
    `make_topic_progress`, `json`, `pytest` imports.


### v0.36.72 - 25th July 2026

- Updated `.claude/rules/committing.md` from canonical: clarifies that
  a lock file's self-referential version drifting by a patch after a
  non-code bump is expected and harmless — not something to chase
  across repos.


### v0.36.71 - 25th July 2026

- Added `[tool.ruff.lint] select = ["E4", "E7", "E9", "F"]` to
  `pyproject.toml`, pinning ruff's default rule set explicitly
  (verified via `ruff check --show-settings` against the project's
  locked 0.15.5 — identical enabled-rule list before and after). A
  future ruff release can no longer silently turn on new default
  rules underneath the project. Part of a fleet-wide pass; see
  programme's backlog and v4.91.1/v4.92.0.


### v0.36.70 - 25th July 2026

- Rotated changelog: archived 5 entries to `changelog/2026.md`.


### v0.36.69 - 24th July 2026

- `CLAUDE.md`: replaced the superseded **Core Rules** periodic-review
  trigger with the backlog-depth rule — when `/backlog` shows fewer
  than 5 open items, propose `/scan`, `/improvements`, and `/prune`.
  The old "Every 6-7 versions" cadence also named `/refactor` and
  `/optimize`, neither of which is a real skill. Pushed from the
  programme registry via `sync-config --types section`.


### v0.36.68 - 24th July 2026

- Updated `.claude/rules/committing.md`: adds the canonical
  `Pull First — Before Any Work` section — `git pull` is the first step
  of every session, run before reading, planning, or editing, not just
  before pushing. Synced from the programme registry (rule v1.4).


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
