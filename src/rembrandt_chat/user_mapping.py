"""Map Telegram users to rembrandt users.

Each Telegram user is mapped to a rembrandt user with username
``tg_<telegram_id>``.  On first contact the rembrandt user is
auto-registered; subsequent calls return the existing user.
"""

import secrets

from rembrandt import PostgresDatabase, User
from telegram import User as TelegramUser


def _make_username(telegram_id: int) -> str:
    """Build the rembrandt username for a Telegram user ID."""
    return f"tg_{telegram_id}"


def _display_name(tg_user: TelegramUser) -> str:
    """Build a display name from the Telegram profile."""
    parts: list[str] = []
    if tg_user.first_name:
        parts.append(tg_user.first_name)
    if tg_user.last_name:
        parts.append(tg_user.last_name)
    return " ".join(parts) or _make_username(tg_user.id)


class UserMapper:
    """Resolve a Telegram user to a rembrandt `User`.

    :param db: An initialised `PostgresDatabase` instance.
    """

    def __init__(self, db: PostgresDatabase) -> None:
        self._db = db

    def ensure_user(self, tg_user: TelegramUser) -> User:
        """Return the rembrandt user for `tg_user`, creating one
        if it does not exist yet.

        :param tg_user: The Telegram user object from the update.
        :return: The corresponding rembrandt `User`.
        """
        username = _make_username(tg_user.id)
        user = self._db.get_user(username)
        if user is not None:
            return user
        password = secrets.token_urlsafe(32)
        return self._db.register_user(
            username,
            password,
            display_name=_display_name(tg_user),
        )
