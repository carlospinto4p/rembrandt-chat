"""Shared test fixtures and helpers."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from rembrandt import User
from rembrandt.models import (
    AnswerResult,
    Concept,
    ConceptTranslation,
    Exercise,
    ExerciseType,
    Language,
    Topic,
    TopicProgress,
)

from rembrandt_chat.user_mapping import UserMapper


def make_user(display_name: str = "Alice") -> User:
    return User(
        id=1,
        username="tg_12345",
        display_name=display_name,
        password_hash="",
        created_at=datetime.now(timezone.utc),
    )


def make_concept(
    concept_id: int = 1,
    front: str = "efimero",
    **kw,
) -> Concept:
    defaults = dict(
        id=concept_id,
        front=front,
        back="Que dura poco tiempo",
        tags=[],
    )
    defaults.update(kw)
    return Concept(**defaults)


def make_exercise(
    exercise_type: ExerciseType = ExerciseType.MULTIPLE_CHOICE,
    **kw,
) -> Exercise:
    defaults = dict(
        concept=make_concept(),
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
        concept=make_concept(),
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

    update.callback_query = None
    update.effective_chat = AsyncMock()
    return update


def make_callback_update(data: str) -> MagicMock:
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_chat = AsyncMock()
    update.callback_query = AsyncMock()
    update.callback_query.data = data
    return update


def make_language(
    code: str = "es", name: str = "Spanish",
) -> Language:
    return Language(code=code, name=name)


def make_languages() -> list[Language]:
    return [
        make_language("es", "Spanish"),
        make_language("en", "English"),
    ]


def make_translation(
    concept_id: int = 1,
    language_code: str = "en",
    front: str = "ephemeral",
    back: str = "Lasting for a very short time",
    context: str = "",
) -> ConceptTranslation:
    return ConceptTranslation(
        concept_id=concept_id,
        language_code=language_code,
        front=front,
        back=back,
        context=context,
    )


def make_topic(
    topic_id: int = 1, title: str = "A1 - Topic 1",
) -> Topic:
    return Topic(
        id=topic_id,
        title=title,
        concept_ids=[1, 2, 3],
        concept_count=3,
    )


def make_topic_progress(
    topic_id: int = 1,
) -> TopicProgress:
    return TopicProgress(
        topic_id=topic_id,
        user_id=1,
        concepts_total=3,
        concepts_studied=2,
        concepts_mastered=1,
        completion_pct=66.7,
        mastery_pct=33.3,
    )
