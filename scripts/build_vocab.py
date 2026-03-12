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
        "title": "La casa",
        "description": "Objetos y partes de la casa",
        "cefr": "A1",
        "tags": ["hogar"],
        "words": [
            "mesa", "silla", "cama", "puerta", "ventana",
            "cocina", "espejo", "lámpara", "alfombra", "escalera",
        ],
    },
    {
        "title": "Alimentos",
        "description": "Comida y bebida cotidiana",
        "cefr": "A1",
        "tags": ["comida"],
        "words": [
            "pan", "leche", "agua", "arroz", "carne",
            "fruta", "verdura", "queso", "huevo", "sal",
        ],
    },
    {
        "title": "La familia",
        "description": "Miembros de la familia",
        "cefr": "A1",
        "tags": ["familia"],
        "words": [
            "madre", "padre", "hermano", "hermana", "abuelo",
            "abuela", "hijo", "hija", "primo", "sobrino",
        ],
    },
    {
        "title": "El cuerpo",
        "description": "Partes del cuerpo humano",
        "cefr": "A1",
        "tags": ["cuerpo"],
        "words": [
            "cabeza", "mano", "pie", "ojo", "boca",
            "nariz", "oreja", "brazo", "pierna", "dedo",
        ],
    },
    {
        "title": "Ropa y accesorios",
        "description": "Prendas de vestir",
        "cefr": "A2",
        "tags": ["ropa"],
        "words": [
            "camisa", "falda", "zapato", "sombrero", "pantalón",
            "cinturón", "abrigo", "bufanda", "guante", "bolsillo",
        ],
    },
    {
        "title": "La ciudad",
        "description": "Lugares y elementos urbanos",
        "cefr": "A2",
        "tags": ["ciudad"],
        "words": [
            "calle", "plaza", "parque", "puente", "iglesia",
            "mercado", "hospital", "escuela", "biblioteca", "estación",
        ],
    },
    {
        "title": "La naturaleza",
        "description": "Elementos del mundo natural",
        "cefr": "A2",
        "tags": ["naturaleza"],
        "words": [
            "árbol", "flor", "río", "montaña", "bosque",
            "playa", "piedra", "nube", "lluvia", "tierra",
        ],
    },
    {
        "title": "Animales",
        "description": "Animales comunes",
        "cefr": "A2",
        "tags": ["animales"],
        "words": [
            "perro", "gato", "caballo", "pájaro", "pez",
            "vaca", "oveja", "gallina", "conejo", "tortuga",
        ],
    },
    {
        "title": "Profesiones",
        "description": "Oficios y profesiones",
        "cefr": "B1",
        "tags": ["trabajo"],
        "words": [
            "médico", "maestro", "abogado", "ingeniero", "enfermero",
            "bombero", "carpintero", "cocinero", "periodista", "soldado",
        ],
    },
    {
        "title": "Emociones",
        "description": "Sentimientos y estados de ánimo",
        "cefr": "B1",
        "tags": ["emociones"],
        "words": [
            "alegría", "tristeza", "miedo", "amor", "odio",
            "vergüenza", "orgullo", "esperanza", "envidia", "ternura",
        ],
    },
    {
        "title": "Viajes",
        "description": "Vocabulario de viaje y transporte",
        "cefr": "B1",
        "tags": ["viajes"],
        "words": [
            "equipaje", "pasaporte", "billete", "aduana", "maleta",
            "destino", "frontera", "vuelo", "andén", "brújula",
        ],
    },
    {
        "title": "Cultura y sociedad",
        "description": "Conceptos culturales y sociales",
        "cefr": "B2",
        "tags": ["cultura"],
        "words": [
            "costumbre", "herencia", "ciudadano", "igualdad", "libertad",
            "democracia", "prejuicio", "convivencia", "identidad",
            "solidaridad",
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
