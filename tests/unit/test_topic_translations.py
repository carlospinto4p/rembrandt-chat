"""Tests for topic title translation."""

from rembrandt_chat.topic_translations import topic_title


def test_english_translation():
    assert topic_title(2, "Adjetivos cultos I", "en") == (
        "Cultured Adjectives I"
    )


def test_spanish_returns_original():
    assert topic_title(2, "Adjetivos cultos I", "es") == (
        "Adjetivos cultos I"
    )


def test_none_lang_returns_original():
    assert topic_title(2, "Adjetivos cultos I", None) == (
        "Adjetivos cultos I"
    )


def test_unknown_id_returns_original():
    assert topic_title(999, "Custom Topic", "en") == (
        "Custom Topic"
    )
