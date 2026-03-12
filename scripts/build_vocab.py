#!/usr/bin/env python3
"""Fetch Spanish definitions from Wiktionary and build vocab/lesson files.

Produces:
  data/vocab.json   — [{rank, word, definition}, ...]
  data/lessons.json — [{title, language_from, language_to, word_ranks, ...}]

Definitions are sourced from es.wiktionary.org (CC BY-SA 4.0).

Usage:
  uv run python scripts/build_vocab.py
"""

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# fmt: off
LESSONS: list[dict] = [
    {
        "title": "Adjetivos cultos",
        "description": "Adjetivos poco comunes de registro culto",
        "cefr": "C1",
        "tags": ["adjetivos", "culto"],
        "words": [
            "efímero", "ubicuo", "acérrimo", "perspicaz",
            "recóndito", "prístino", "insigne", "exiguo",
            "incólume", "acucioso",
        ],
    },
    {
        "title": "Adjetivos literarios",
        "description": "Adjetivos de uso literario y formal",
        "cefr": "C2",
        "tags": ["adjetivos", "literario"],
        "words": [
            "diáfano", "ignoto", "vetusto", "feraz",
            "sempiterno", "iracundo", "ominoso", "cruento",
            "inveterado", "execrable",
        ],
    },
    {
        "title": "Sustantivos abstractos",
        "description": "Conceptos abstractos de uso culto",
        "cefr": "C1",
        "tags": ["sustantivos", "abstracto"],
        "words": [
            "desidia", "vehemencia", "mesura", "displicencia",
            "acervo", "menoscabo", "acopio", "desazón",
            "premura", "denuedo",
        ],
    },
    {
        "title": "Sustantivos formales",
        "description": "Sustantivos de registro formal y académico",
        "cefr": "C1",
        "tags": ["sustantivos", "formal"],
        "words": [
            "resquicio", "cariz", "derrotero", "coyuntura",
            "vestigio", "diatriba", "precepto", "salvedad",
            "envergadura", "menester",
        ],
    },
    {
        "title": "Verbos precisos I",
        "description": "Verbos cultos para expresarse con precisión",
        "cefr": "C1",
        "tags": ["verbos", "culto"],
        "words": [
            "dilucidar", "esgrimir", "soslayar", "ponderar",
            "acaecer", "enmendar", "socavar", "abogar",
            "discernir", "aducir",
        ],
    },
    {
        "title": "Verbos precisos II",
        "description": "Más verbos cultos de uso formal",
        "cefr": "C1",
        "tags": ["verbos", "culto"],
        "words": [
            "dirimir", "resarcir", "escatimar", "desdeñar",
            "vindicar", "acusar", "usurpar", "desistir",
            "atenuar", "amedrentar",
        ],
    },
    {
        "title": "Verbos literarios",
        "description": "Verbos de uso literario y poético",
        "cefr": "C2",
        "tags": ["verbos", "literario"],
        "words": [
            "escindir", "holgar", "increpar", "azuzar",
            "expiar", "zaherir", "denostar", "conminar",
            "medrar", "fulminar",
        ],
    },
    {
        "title": "Retórica y argumentación",
        "description": "Vocabulario para el discurso y la persuasión",
        "cefr": "C1",
        "tags": ["retórica", "argumentación"],
        "words": [
            "falacia", "silogismo", "premisa", "paradoja",
            "retórica", "sofisma", "aforismo", "elocuencia",
            "apología", "demagogia",
        ],
    },
    {
        "title": "Filosofía y pensamiento",
        "description": "Términos filosóficos y del pensamiento crítico",
        "cefr": "C2",
        "tags": ["filosofía"],
        "words": [
            "ontología", "epistemología", "axioma", "dialéctica",
            "teleología", "hermenéutica", "nihilismo", "solipsismo",
            "empirismo", "altruismo",
        ],
    },
    {
        "title": "Figuras retóricas",
        "description": "Recursos literarios y estilísticos",
        "cefr": "C1",
        "tags": ["literatura", "retórica"],
        "words": [
            "metáfora", "metonimia", "sinécdoque", "oxímoron",
            "hipérbole", "antítesis", "prosopopeya", "elipsis",
            "anáfora", "pleonasmo",
        ],
    },
    {
        "title": "Derecho y gobierno",
        "description": "Vocabulario jurídico y político",
        "cefr": "C1",
        "tags": ["derecho", "política"],
        "words": [
            "jurisprudencia", "potestad", "prerrogativa",
            "promulgar", "derogar", "litigio", "indulto",
            "exhorto", "fuero", "aquiescencia",
        ],
    },
    {
        "title": "Palabras en desuso",
        "description": "Arcaísmos y palabras poco frecuentes",
        "cefr": "C2",
        "tags": ["arcaísmo"],
        "words": [
            "boato", "acaecimiento", "albor", "solaz",
            "denuesto", "infundio", "procaz", "lozano",
            "donaire", "prestancia",
        ],
    },
]
# fmt: on

API_URL = (
    "https://es.wiktionary.org/w/api.php"
    "?action=parse&prop=wikitext&format=json&page={word}"
)
HEADERS = {"User-Agent": "rembrandt-chat/1.0 (vocabulary builder)"}

# Delay between API requests (seconds)
REQUEST_DELAY = 0.5


def _fetch_wikitext(word: str) -> str | None:
    """Fetch the raw wikitext for a word from es.wiktionary.org."""
    url = API_URL.format(word=urllib.request.quote(word))
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"  WARN: failed to fetch '{word}': {exc}")
        return None

    parse = data.get("parse")
    if parse is None:
        print(f"  WARN: no parse result for '{word}'")
        return None

    wikitext = parse.get("wikitext", {})
    return wikitext.get("*")


def _clean_markup(text: str) -> str:
    """Remove wikitext markup, keeping plain text."""
    # Remove {{plm|word}} → word
    text = re.sub(r"\{\{plm\|([^}]*)\}\}", r"\1", text)
    # Remove {{csem|category}}: → empty (category prefix)
    text = re.sub(r"\{\{csem\|[^}]*\}\}:\s*", "", text)
    # Remove {{ucf|word}} → Word (capitalize)
    text = re.sub(
        r"\{\{ucf\|([^}]*)\}\}",
        lambda m: m.group(1).capitalize(),
        text,
    )
    # Remove {{l|es|word}} → word
    text = re.sub(r"\{\{l\|[^|]*\|([^}]*)\}\}", r"\1", text)
    # Remove remaining {{template|...}} → last arg
    text = re.sub(
        r"\{\{[^}]*\|([^|}]*)\}\}",
        r"\1",
        text,
    )
    # Remove remaining {{template}} with no args
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    # Remove [[link|display]] → display
    text = re.sub(r"\[\[[^|\]]*\|([^\]]*)\]\]", r"\1", text)
    # Remove [[link]] → link
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    # Remove <ref>...</ref>
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text)
    # Remove remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove trailing period if present, we'll add our own
    text = text.rstrip(".")
    return text


def _extract_first_definition(wikitext: str) -> str | None:
    """Extract the first Spanish definition from wikitext."""
    in_spanish = False
    for line in wikitext.split("\n"):
        stripped = line.strip()
        # Detect Spanish language section
        if re.match(r"==\s*\{\{lengua\|es\}\}\s*==", stripped):
            in_spanish = True
            continue
        # Detect next language section — stop
        if in_spanish and re.match(r"==\s*\{\{lengua\|", stripped):
            break
        if not in_spanish:
            continue
        # Match definition line: ;1 or ;1: or ;1 {{csem|...}}:
        m = re.match(r"^;1\b[^:]*:\s*(.+)", stripped)
        if m:
            raw = m.group(1)
            cleaned = _clean_markup(raw)
            if cleaned:
                return cleaned
    return None


def build() -> None:
    """Build vocab.json and lessons.json from Wiktionary."""
    # Collect all unique words with their rank
    all_words: list[str] = []
    for lesson in LESSONS:
        for w in lesson["words"]:
            if w not in all_words:
                all_words.append(w)

    print(f"Fetching definitions for {len(all_words)} words...")

    vocab: list[dict] = []
    failed: list[str] = []

    for i, word in enumerate(all_words, 1):
        print(f"  [{i}/{len(all_words)}] {word}...", end=" ")
        wikitext = _fetch_wikitext(word)
        if wikitext is None:
            failed.append(word)
            print("FAILED (no wikitext)")
            time.sleep(REQUEST_DELAY)
            continue

        definition = _extract_first_definition(wikitext)
        if definition is None:
            failed.append(word)
            print("FAILED (no definition found)")
            time.sleep(REQUEST_DELAY)
            continue

        # In load_lessons(): definition → word_from, word → word_to
        # For ES-ES: word_from = the word, word_to = the definition
        # So: "definition" field = the word, "word" field = the def
        vocab.append({
            "rank": i,
            "definition": word,
            "word": definition,
        })
        print(f"OK: {definition[:60]}")
        time.sleep(REQUEST_DELAY)

    if failed:
        print(f"\n{len(failed)} words failed:")
        for w in failed:
            print(f"  - {w}")

    # Build word-to-rank mapping
    word_to_rank: dict[str, int] = {}
    for entry in vocab:
        word_to_rank[entry["definition"]] = entry["rank"]

    # Build lessons JSON
    lessons_out: list[dict] = []
    for lesson in LESSONS:
        ranks = []
        for w in lesson["words"]:
            rank = word_to_rank.get(w)
            if rank is not None:
                ranks.append(rank)
        lessons_out.append({
            "title": lesson["title"],
            "description": lesson["description"],
            "language_from": "es",
            "language_to": "es",
            "cefr": lesson.get("cefr"),
            "tags": lesson.get("tags", []),
            "word_ranks": ranks,
        })

    # Write files
    DATA_DIR.mkdir(exist_ok=True)

    vocab_path = DATA_DIR / "vocab.json"
    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {len(vocab)} entries to {vocab_path}")

    lessons_path = DATA_DIR / "lessons.json"
    with open(lessons_path, "w", encoding="utf-8") as f:
        json.dump(lessons_out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(lessons_out)} lessons to {lessons_path}")

    if failed:
        print(
            f"\nWARN: {len(failed)} words need manual definitions."
        )
        sys.exit(1)


if __name__ == "__main__":
    build()
