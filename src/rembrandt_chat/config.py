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


def get_database_url() -> str:
    """Return the PostgreSQL connection URL.

    :raises RuntimeError: If ``DATABASE_URL`` is not set.
    """
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set"
        )
    return url


def get_base_vocab_path() -> str | None:
    """Return the optional base vocabulary CSV path.

    :return: The path string, or ``None`` if not set.
    """
    return os.environ.get("BASE_VOCAB_PATH") or None


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
