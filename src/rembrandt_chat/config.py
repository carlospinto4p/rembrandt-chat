"""Bot configuration loaded from environment variables."""

import os


def get_bot_token() -> str:
    """Return the Telegram bot token.

    :raises RuntimeError: If ``TELEGRAM_BOT_TOKEN`` is not set.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is not set"
        )
    return token


def get_database_path() -> str:
    """Return the SQLite database file path.

    Defaults to ``data/rembrandt.db`` relative to the working
    directory when ``DATABASE_PATH`` is not set.
    """
    return os.environ.get("DATABASE_PATH", "") or "data/rembrandt.db"


def get_base_vocab_path() -> str | None:
    """Return the optional base vocabulary CSV path.

    :return: The path string, or ``None`` if not set.
    """
    return os.environ.get("BASE_VOCAB_PATH") or None


def get_bundled_vocab_dir() -> str:
    """Return the bundled vocabulary data directory.

    Defaults to ``data/`` relative to the working directory
    when ``BUNDLED_VOCAB_DIR`` is not set.
    """
    return os.environ.get("BUNDLED_VOCAB_DIR", "") or "data"


def get_state_path() -> str:
    """Return the user-state JSON file path.

    Defaults to ``data/user_state.json`` relative to the
    working directory when ``STATE_PATH`` is not set.
    """
    return (
        os.environ.get("STATE_PATH", "")
        or "data/user_state.json"
    )


def get_max_new_cards() -> int:
    """Return the maximum new cards per session.

    :return: ``0`` (unlimited) if not set.
    """
    return int(os.environ.get("MAX_NEW_CARDS", "0"))


def get_max_review_cards() -> int:
    """Return the maximum review cards per session.

    :return: ``0`` (unlimited) if not set.
    """
    return int(os.environ.get("MAX_REVIEW_CARDS", "0"))
