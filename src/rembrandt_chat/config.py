"""Bot configuration loaded from environment variables."""

import os

# Default language pair for exercises and word storage.
LANG_FROM = "es"
LANG_TO = "es"


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

    :raises RuntimeError: If ``DATABASE_PATH`` is not set.
    """
    path = os.environ.get("DATABASE_PATH", "")
    if not path:
        raise RuntimeError(
            "DATABASE_PATH environment variable is not set"
        )
    return path


def get_base_vocab_path() -> str | None:
    """Return the optional base vocabulary CSV path.

    :return: The path string, or ``None`` if not set.
    """
    return os.environ.get("BASE_VOCAB_PATH") or None


def get_bundled_vocab_dir() -> str | None:
    """Return the optional bundled vocabulary data directory.

    :return: The directory path string, or ``None`` if not set.
    """
    return os.environ.get("BUNDLED_VOCAB_DIR") or None


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
