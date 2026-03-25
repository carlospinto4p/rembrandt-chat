"""Lightweight JSON persistence for user state.

Stores language preferences and active session configuration
so they survive bot restarts.  The state file is a JSON object
keyed by Telegram user ID.
"""

import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# user_data key for the serialisable session config
SESSION_CONFIG = "_session_config"


def _load_all(path: Path) -> dict[str, Any]:
    """Read the entire state file, returning ``{}`` on error."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        log.warning("Could not read state file %s", path)
        return {}


def _save_all(path: Path, data: dict[str, Any]) -> None:
    """Write the entire state file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


def save_user_state(
    path: Path,
    user_id: int,
    **kv: Any,
) -> None:
    """Merge *kv* into the stored state for *user_id*."""
    data = _load_all(path)
    key = str(user_id)
    entry = data.get(key, {})
    entry.update(kv)
    data[key] = entry
    _save_all(path, data)


def load_user_state(
    path: Path,
    user_id: int,
) -> dict[str, Any]:
    """Return the stored state for *user_id* (or ``{}``)."""
    data = _load_all(path)
    return data.get(str(user_id), {})


def clear_session_config(
    path: Path,
    user_id: int,
) -> None:
    """Remove the saved session config for *user_id*."""
    data = _load_all(path)
    key = str(user_id)
    if key in data and SESSION_CONFIG in data[key]:
        del data[key][SESSION_CONFIG]
        _save_all(path, data)
