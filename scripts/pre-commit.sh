#!/bin/bash
# Project-local pre-commit checks. Invoked by the global
# ~/.claude/hooks/pre-commit-tests.sh when a Bash tool runs
# `git commit`. Exit non-zero to block the commit.
set -e
uv run pytest tests/unit/ --tb=short -q
