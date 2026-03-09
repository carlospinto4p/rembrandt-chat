# Testing Guidelines

## Test Structure

Unit tests live in `tests/unit/` and run with `uv run pytest tests/unit -v`.
They are fast, isolated, and never depend on real Telegram connections,
real databases, or external services. Use fixtures, mocks, and `tmp_path`
for temporary data.

When integration tests are added, they should live in
`tests/integration/` and run separately so they don't break CI
when external services are unavailable. The `preCommit` hook currently
runs all tests under `tests/` — update it to exclude integration
tests when that directory is created.

## Style

- **No test classes.** Use plain functions with `test_` prefix.
- Group tests by module, separated by comment headers:
  ```python
  # --- Session Manager Tests ---
  ```
- Use `pytest` idioms: fixtures, parametrize, `pytest.raises`.
- Keep test files named `test_<module>.py` mirroring the source.

## Fixtures

- Define fixtures in the test file when used by that file only.
- Move shared fixtures to `conftest.py` when used across files.
- Prefer `tmp_path` (built-in) for temporary files/databases.
- Use `@pytest.fixture` without parentheses for consistency.
- Mock Telegram API calls and rembrandt dependencies in unit tests.

## Assertions

- One logical assertion per test when possible.
- Use plain `assert` — avoid `unittest`-style methods.
- For float comparisons: `assert abs(actual - expected) < 1e-9`.
- For dict key checks: `assert list(result.keys()) == [...]`.

## Naming

- Test functions: `test_<what>_<scenario>` in snake_case.
  - `test_start_registers_new_user`, `test_play_creates_session`
- Fixture functions: descriptive nouns (`mock_update`, `sample_session`).

## What to Test

- **Do test:** handlers (mocked), session manager logic, formatting
  output, user mapping, config loading, edge cases.
- **Don't test:** Telegram API internals, rembrandt library internals,
  trivial getters/setters.
