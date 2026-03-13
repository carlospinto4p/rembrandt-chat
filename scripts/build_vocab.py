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
    # --- ADJETIVOS ---
    {
        "title": "Adjetivos cultos I",
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
        "title": "Adjetivos cultos II",
        "description": "Más adjetivos de registro culto",
        "cefr": "C1",
        "tags": ["adjetivos", "culto"],
        "words": [
            "conspicuo", "inicuo", "ingente", "pusilánime",
            "indolente", "pertinaz", "lacónico", "falaz",
            "ecuánime", "prolijo",
        ],
    },
    {
        "title": "Adjetivos cultos III",
        "description": "Adjetivos cultos para descripciones precisas",
        "cefr": "C1",
        "tags": ["adjetivos", "culto"],
        "words": [
            "ecuestre", "coetáneo", "longevo", "inefable",
            "unívoco", "ambiguo", "pueril", "disímil",
            "subrepticio", "espurio",
        ],
    },
    {
        "title": "Adjetivos literarios I",
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
        "title": "Adjetivos literarios II",
        "description": "Más adjetivos de uso literario",
        "cefr": "C2",
        "tags": ["adjetivos", "literario"],
        "words": [
            "yermo", "álgido", "grandilocuente", "recalcitrante",
            "pródigo", "impávido", "contumaz", "ineluctable",
            "avieso", "dilecto",
        ],
    },
    # --- SUSTANTIVOS ---
    {
        "title": "Sustantivos abstractos I",
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
        "title": "Sustantivos abstractos II",
        "description": "Más conceptos abstractos de uso culto",
        "cefr": "C1",
        "tags": ["sustantivos", "abstracto"],
        "words": [
            "parsimonia", "fruición", "desavenencia", "resquemor",
            "desdén", "encono", "inquina", "lascivia",
            "probidad", "oprobio",
        ],
    },
    {
        "title": "Sustantivos abstractos III",
        "description": "Conceptos abstractos avanzados",
        "cefr": "C2",
        "tags": ["sustantivos", "abstracto"],
        "words": [
            "diletantismo", "estulticia", "vileza", "contumelia",
            "abulia", "aquiescencia", "clemencia", "ignominia",
            "inopia", "petulancia",
        ],
    },
    {
        "title": "Sustantivos formales I",
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
        "title": "Sustantivos formales II",
        "description": "Más sustantivos de registro formal",
        "cefr": "C1",
        "tags": ["sustantivos", "formal"],
        "words": [
            "subterfugio", "canon", "epítome", "paradigma",
            "prebenda", "corolario", "epílogo", "dogma",
            "estigma", "hegemonía",
        ],
    },
    {
        "title": "Sustantivos formales III",
        "description": "Sustantivos formales avanzados",
        "cefr": "C2",
        "tags": ["sustantivos", "formal"],
        "words": [
            "dádiva", "disyuntiva", "idiosincrasia", "panacea",
            "plétora", "quimera", "sinecura", "usufructo",
            "pocilga", "baluarte",
        ],
    },
    # --- VERBOS ---
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
            "vindicar", "usurpar", "desistir",
            "atenuar", "amedrentar", "avocar",
        ],
    },
    {
        "title": "Verbos precisos III",
        "description": "Verbos cultos adicionales",
        "cefr": "C1",
        "tags": ["verbos", "culto"],
        "words": [
            "coadyuvar", "concatenar", "detentar", "eludir",
            "elucidar", "infligir", "ostentar", "subyugar",
            "transgredir", "vincularse",
        ],
    },
    {
        "title": "Verbos literarios I",
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
        "title": "Verbos literarios II",
        "description": "Más verbos de uso literario",
        "cefr": "C2",
        "tags": ["verbos", "literario"],
        "words": [
            "hostigar", "cernir", "dilapidar", "exacerbar",
            "fustigar", "vilipendiar", "enajenar", "abjurar",
            "claudicar", "mancillar",
        ],
    },
    {
        "title": "Verbos literarios III",
        "description": "Verbos literarios avanzados",
        "cefr": "C2",
        "tags": ["verbos", "literario"],
        "words": [
            "apostatar", "arrogar", "colegir", "concitar",
            "diferir", "expoliar", "lucubrar", "paliar",
            "preconizar", "suscitar",
        ],
    },
    # --- RETÓRICA Y LITERATURA ---
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
        "title": "Figuras retóricas I",
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
        "title": "Figuras retóricas II",
        "description": "Más recursos literarios",
        "cefr": "C1",
        "tags": ["literatura", "retórica"],
        "words": [
            "alegoría", "ironía", "litote", "perífrasis",
            "sinestesia", "epíteto", "apóstrofe", "polisíndeton",
            "asíndeton", "aliteración",
        ],
    },
    {
        "title": "Teoría literaria",
        "description": "Términos de crítica y análisis literario",
        "cefr": "C1",
        "tags": ["literatura"],
        "words": [
            "diégesis", "verosimilitud", "soliloquio",
            "hagiografía", "exégesis", "epígrafe",
            "idilio", "panegírico", "elegía", "sátira",
        ],
    },
    # --- FILOSOFÍA ---
    {
        "title": "Filosofía y pensamiento I",
        "description": "Términos filosóficos fundamentales",
        "cefr": "C2",
        "tags": ["filosofía"],
        "words": [
            "ontología", "epistemología", "axioma", "dialéctica",
            "teleología", "hermenéutica", "nihilismo", "solipsismo",
            "empirismo", "altruismo",
        ],
    },
    {
        "title": "Filosofía y pensamiento II",
        "description": "Más conceptos filosóficos",
        "cefr": "C2",
        "tags": ["filosofía"],
        "words": [
            "escolástica", "hedonismo", "estoicismo", "determinismo",
            "utilitarismo", "relativismo", "pragmatismo",
            "racionalismo", "dogmatismo", "idealismo",
        ],
    },
    # --- DERECHO Y POLÍTICA ---
    {
        "title": "Derecho y gobierno I",
        "description": "Vocabulario jurídico y político",
        "cefr": "C1",
        "tags": ["derecho", "política"],
        "words": [
            "jurisprudencia", "potestad", "prerrogativa",
            "promulgar", "derogar", "litigio", "indulto",
            "exhorto", "fuero", "decreto",
        ],
    },
    {
        "title": "Derecho y gobierno II",
        "description": "Más vocabulario jurídico",
        "cefr": "C1",
        "tags": ["derecho", "política"],
        "words": [
            "fideicomiso", "contencioso", "desacato",
            "prescripción", "edicto", "tipificar",
            "jurisconsulto", "impugnar", "recusar", "refrendar",
        ],
    },
    # --- CIENCIA Y MEDICINA ---
    {
        "title": "Ciencia y método",
        "description": "Vocabulario del método científico",
        "cefr": "C1",
        "tags": ["ciencia"],
        "words": [
            "hipótesis", "paradigma", "postulado", "taxonomía",
            "anomalía", "variable", "correlación", "serendipia",
            "heurística", "entropía",
        ],
    },
    {
        "title": "Medicina culta",
        "description": "Términos médicos de uso culto",
        "cefr": "C1",
        "tags": ["medicina"],
        "words": [
            "etiología", "fisiopatología", "profilaxis", "iatrogenia",
            "sintomatología", "paliativo", "idiopático",
            "nosología", "asepsia", "prognosis",
        ],
    },
    # --- ARCAÍSMOS Y DESUSO ---
    {
        "title": "Palabras en desuso I",
        "description": "Arcaísmos y palabras poco frecuentes",
        "cefr": "C2",
        "tags": ["arcaísmo"],
        "words": [
            "boato", "acaecimiento", "albor", "solaz",
            "denuesto", "infundio", "procaz", "lozano",
            "donaire", "prestancia",
        ],
    },
    {
        "title": "Palabras en desuso II",
        "description": "Más arcaísmos y voces antiguas",
        "cefr": "C2",
        "tags": ["arcaísmo"],
        "words": [
            "bizarro", "gallardo", "hidalgo", "talante",
            "desaguisado", "ínclito", "preclaro", "holganza",
            "merced", "abolengo",
        ],
    },
    {
        "title": "Palabras en desuso III",
        "description": "Voces antiguas y literarias",
        "cefr": "C2",
        "tags": ["arcaísmo"],
        "words": [
            "antojadizo", "desventura", "cuita", "desaire",
            "saña", "yantar", "pesadumbre", "algarabía",
            "alborozo", "desvelo",
        ],
    },
]
# fmt: on

# Manual overrides for words whose Wiktionary definitions are
# broken, circular, too terse, or missing entirely.
# fmt: off
MANUAL_DEFS: dict[str, str] = {
    # Broken markup or wrong definition
    "acérrimo": "Muy firme, tenaz o extremo en su postura o sentimientos",
    "ecuestre": "Perteneciente o relativo al caballo o a la equitación",
    "escolástica": "Corriente filosófica y teológica medieval basada en la articulación entre fe y razón",
    "contencioso": "Dicho de una persona que disputa o contradice todo lo que otros afirman",
    # Wiki markup artifacts
    "acucioso": "Diligente, solícito; que hace las cosas pronto y con cuidado",
    "fruición": "Goce intenso; placer o deleite que se experimenta al disfrutar algo",
    "aliteración": "Repetición de sonidos semejantes en palabras próximas dentro de un texto",
    "procaz": "Que se comporta o habla de manera desvergonzada o atrevida",
    # Circular definitions (word ≈ definition)
    "menoscabo": "Disminución del valor, la importancia o el prestigio de algo",
    "cernir": "Separar con el cedazo la parte fina de la gruesa; amenazar algo de forma inminente",
    "litote": "Figura retórica que consiste en negar lo contrario de lo que se quiere afirmar",
    "prescripción": "Extinción de un derecho o una obligación por el transcurso del tiempo legal",
    "lucubrar": "Trabajar intelectualmente con dedicación e intensidad, especialmente de noche",
    "desvelo": "Falta de sueño; cuidado o atención solícita por algo o alguien",
    "ecuánime": "Que juzga con imparcialidad y serenidad de ánimo",
    "dilecto": "Amado con especial afecto y predilección",
    "verosimilitud": "Apariencia de verdadero o creíble; cualidad de lo que resulta posible dentro de su contexto",
    "holganza": "Ociosidad, descanso; estado de quien no trabaja",
    # Too terse or misleading
    "indolente": "Que no se afecta ni se inmuta; perezoso, apático",
    "ignoto": "Desconocido, no descubierto ni explorado",
    "iracundo": "Propenso a la ira; que se encoleriza con facilidad",
    "infligir": "Causar un daño, castigo o pena a alguien",
    "vindicar": "Defender a quien ha sido injuriado o calumniado; vengar una ofensa",
    "conminar": "Amenazar con un castigo o una sanción para obligar a cumplir algo",
    "fulminar": "Lanzar un castigo o condena de manera repentina y severa",
    "fustigar": "Azotar con un látigo o vara; criticar con dureza",
    "expoliar": "Despojar con violencia o injusticia de los bienes a alguien",
    "prestancia": "Excelencia o superioridad entre los de su especie",
    "desventura": "Suerte adversa; desgracia o infortunio",
    "suscitar": "Provocar o dar origen a un sentimiento, una reacción o un debate",
    "cariz": "Aspecto o apariencia que toma un asunto o situación",
    "pesadumbre": "Sentimiento de pesar, aflicción o disgusto",
    "ubicuo": "Que está presente en todas partes al mismo tiempo",
    "albor": "Luz del alba; comienzo o etapa inicial de algo",
    # Wrong definition (different sense)
    "anáfora": "Figura retórica que consiste en la repetición de una o varias palabras al inicio de versos o frases sucesivas",
    "sinestesia": "Figura retórica que atribuye una sensación a un sentido que no le corresponde, como 'color cálido' o 'voz dulce'",
    # Words missing from Wiktionary
    "tipificar": "Clasificar o ajustar algo a un tipo o norma; definir legalmente como delito una conducta",
    "fisiopatología": "Rama de la medicina que estudia las alteraciones funcionales del organismo causadas por enfermedades",
    "sintomatología": "Conjunto de síntomas que caracterizan una enfermedad; estudio de los síntomas",
}
# fmt: on

API_URL = (
    "https://es.wiktionary.org/w/api.php"
    "?action=parse&prop=wikitext&format=json&page={word}"
)
HEADERS = {"User-Agent": "rembrandt-chat/1.0 (vocabulary builder)"}

# Delay between API requests (seconds)
REQUEST_DELAY = 1.0
# Max retries on 429 errors
MAX_RETRIES = 3


def _fetch_wikitext(word: str) -> str | None:
    """Fetch the raw wikitext for a word from es.wiktionary.org."""
    url = API_URL.format(word=urllib.request.quote(word))
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < MAX_RETRIES - 1:
                wait = 5 * (attempt + 1)
                print(f"429, waiting {wait}s...", end=" ")
                time.sleep(wait)
                continue
            print(f"  WARN: failed to fetch '{word}': {exc}")
            return None
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

        # Use manual override if available
        if word in MANUAL_DEFS:
            definition = MANUAL_DEFS[word]
            print(f"MANUAL: {definition[:60]}")
        else:
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

            print(f"OK: {definition[:60]}")
            time.sleep(REQUEST_DELAY)

        # In load_lessons(): definition → word_from, word → word_to
        # For ES-ES: word_from = the word, word_to = the definition
        # So: "definition" field = the word, "word" field = the def
        vocab.append({
            "rank": i,
            "definition": word,
            "word": definition,
        })

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
