"""English translations for topic titles and categories."""

from dataclasses import dataclass


@dataclass
class Category:
    """A topic category with bilingual names."""

    key: str
    name_es: str
    name_en: str
    topic_ids: list[int]


CATEGORIES: list[Category] = [
    Category(
        key="ds",
        name_es="Data Science",
        name_en="Data Science",
        topic_ids=[1],
    ),
    Category(
        key="vocab",
        name_es="Vocabulario",
        name_en="Vocabulary",
        topic_ids=[
            *range(2, 19), *range(29, 49),
        ],
    ),
    Category(
        key="culture",
        name_es="Cultura",
        name_en="Culture",
        topic_ids=[
            *range(19, 29), *range(49, 55),
        ],
    ),
]

_CAT_BY_KEY: dict[str, Category] = {
    c.key: c for c in CATEGORIES
}


def get_category(key: str) -> Category | None:
    """Look up a category by its key.

    :param key: Category key (e.g. ``"vocab"``).
    :return: The `Category`, or ``None``.
    """
    return _CAT_BY_KEY.get(key)


def category_name(cat: Category, lang: str | None) -> str:
    """Return the category name in the user's language.

    :param cat: The category.
    :param lang: Language code.
    :return: Translated name.
    """
    return cat.name_en if lang == "en" else cat.name_es


_EN: dict[int, str] = {
    1: "Data Science - Basics",
    2: "Cultured Adjectives I",
    3: "Cultured Adjectives II",
    4: "Cultured Adjectives III",
    5: "Literary Adjectives I",
    6: "Literary Adjectives II",
    7: "Abstract Nouns I",
    8: "Abstract Nouns II",
    9: "Abstract Nouns III",
    10: "Formal Nouns I",
    11: "Formal Nouns II",
    12: "Formal Nouns III",
    13: "Precise Verbs I",
    14: "Precise Verbs II",
    15: "Precise Verbs III",
    16: "Literary Verbs I",
    17: "Literary Verbs II",
    18: "Literary Verbs III",
    19: "Rhetoric and Argumentation",
    20: "Figures of Speech I",
    21: "Figures of Speech II",
    22: "Literary Theory",
    23: "Philosophy and Thought I",
    24: "Philosophy and Thought II",
    25: "Law and Government I",
    26: "Law and Government II",
    27: "Science and Method",
    28: "Formal Medical Terms",
    29: "Archaic Words I",
    30: "Archaic Words II",
    31: "Archaic Words III",
    32: "Phenomena and States I",
    33: "Phenomena and States II",
    34: "People and Types I",
    35: "People and Types II",
    36: "Feelings and Emotions I",
    37: "Feelings and Emotions II",
    38: "Conflicts and Stratagems",
    39: "Formal Places and Spaces",
    40: "Health and Remedies",
    41: "Character Adjectives I",
    42: "Character Adjectives II",
    43: "Physical Appearance Adjectives",
    44: "Condition Adjectives",
    45: "Communication Verbs",
    46: "Perception and Thought Verbs",
    47: "Domination and Subjugation Verbs",
    48: "Movement Verbs",
    49: "Psychology and Mind",
    50: "Sociology and Power",
    51: "Religion and Beliefs",
    52: "Nature and Geography",
    53: "Economy and Finance",
    54: "Virtues and Vices",
}


def all_topics_label(lang: str | None) -> str:
    """Return the "All topics" label in the user's language."""
    return "All topics" if lang == "en" else "Todos los temas"


def topic_title(
    topic_id: int,
    title: str,
    lang: str | None,
) -> str:
    """Return a translated topic title.

    :param topic_id: Database topic ID.
    :param title: Original title (fallback).
    :param lang: Language code (e.g. ``"en"``).
    :return: Translated title, or `title` if no
        translation exists.
    """
    if lang == "en":
        return _EN.get(topic_id, title)
    return title
