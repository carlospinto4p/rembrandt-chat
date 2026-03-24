"""English translations for topic titles."""

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
