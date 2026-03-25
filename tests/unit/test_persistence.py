"""Tests for rembrandt_chat.persistence."""

import json

import pytest

from rembrandt_chat.persistence import (
    SESSION_CONFIG,
    clear_session_config,
    load_user_state,
    save_user_state,
)


def test_save_and_load(tmp_path):
    path = tmp_path / "state.json"
    save_user_state(path, 123, language="en")
    state = load_user_state(path, 123)
    assert state["language"] == "en"


def test_load_missing_file(tmp_path):
    path = tmp_path / "missing.json"
    state = load_user_state(path, 123)
    assert state == {}


def test_load_unknown_user(tmp_path):
    path = tmp_path / "state.json"
    save_user_state(path, 123, language="en")
    state = load_user_state(path, 999)
    assert state == {}


def test_save_merges(tmp_path):
    path = tmp_path / "state.json"
    save_user_state(path, 1, language="en")
    save_user_state(path, 1, **{SESSION_CONFIG: {"mode": "m"}})
    state = load_user_state(path, 1)
    assert state["language"] == "en"
    assert state[SESSION_CONFIG]["mode"] == "m"


def test_clear_session_config(tmp_path):
    path = tmp_path / "state.json"
    save_user_state(
        path, 1,
        language="en",
        **{SESSION_CONFIG: {"mode": "mixed"}},
    )
    clear_session_config(path, 1)
    state = load_user_state(path, 1)
    assert SESSION_CONFIG not in state
    assert state["language"] == "en"


def test_clear_session_config_noop(tmp_path):
    path = tmp_path / "state.json"
    save_user_state(path, 1, language="en")
    clear_session_config(path, 1)
    state = load_user_state(path, 1)
    assert state["language"] == "en"


def test_load_corrupt_file(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("not json")
    state = load_user_state(path, 1)
    assert state == {}
