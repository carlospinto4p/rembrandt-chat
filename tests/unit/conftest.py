"""Shared test fixtures and helpers."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from rembrandt import User, Word
from rembrandt.models import AnswerResult, Exercise, ExerciseType

from rembrandt_chat.user_mapping import UserMapper


def make_user(display_name: str = "Alice") -> User:
    return User(
        id=1,
        username="tg_12345",
        display_name=display_name,
        password_hash="",
        created_at=datetime.now(timezone.utc),
    )


def make_word(
    word_id: int = 1,
    word_from: str = "efimero",
    **kw,
) -> Word:
    defaults = dict(
        id=word_id,
        language_from="es",
        language_to="es",
        word_from=word_from,
        word_to="Que dura poco tiempo",
        tags=[],
    )
    defaults.update(kw)
    return Word(**defaults)


def make_exercise(
    exercise_type: ExerciseType = ExerciseType.MULTIPLE_CHOICE,
    **kw,
) -> Exercise:
    defaults = dict(
        word=make_word(),
        exercise_type=exercise_type,
        options=["efimero", "perpetuo", "antiguo", "moderno"],
        prompt="Que dura poco tiempo",
        expected_answer="efimero",
    )
    defaults.update(kw)
    return Exercise(**defaults)


def make_answer_result(correct: bool = True) -> AnswerResult:
    return AnswerResult(
        correct=correct,
        expected="efimero",
        given="efimero" if correct else "perpetuo",
        word=make_word(),
    )


def make_context(
    *,
    user: User | None = None,
    session: MagicMock | None = None,
    exercise: Exercise | None = None,
) -> MagicMock:
    mapper = MagicMock(spec=UserMapper)
    mapper.ensure_user = AsyncMock(
        return_value=user or make_user()
    )

    ctx = MagicMock()
    ctx.bot_data = {
        "user_mapper": mapper,
        "db": AsyncMock(),
    }
    ctx.user_data = {}
    if session is not None:
        ctx.user_data["session"] = session
    if exercise is not None:
        ctx.user_data["exercise"] = exercise
    return ctx


def make_update(
    *,
    has_user: bool = True,
    has_message: bool = True,
    text: str = "",
) -> MagicMock:
    update = MagicMock()
    if has_user:
        update.effective_user = MagicMock()
        update.effective_user.id = 12345
    else:
        update.effective_user = None

    if has_message:
        update.message = AsyncMock()
        update.message.text = text
    else:
        update.message = None

    update.effective_chat = AsyncMock()
    return update


def make_callback_update(data: str) -> MagicMock:
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_chat = AsyncMock()
    update.callback_query = AsyncMock()
    update.callback_query.data = data
    return update
