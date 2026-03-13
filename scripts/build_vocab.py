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
    # --- FENÓMENOS Y ESTADOS ---
    {
        "title": "Fenómenos y estados I",
        "description": "Sustantivos cultos para fenómenos y estados",
        "cefr": "C1",
        "tags": ["sustantivos", "fenómenos"],
        "words": [
            "marasmo", "letargo", "éxtasis", "vorágine",
            "cataclismo", "debacle", "hecatombe", "paroxismo",
            "estupor", "sopor",
        ],
    },
    {
        "title": "Fenómenos y estados II",
        "description": "Más sustantivos de fenómenos y estados",
        "cefr": "C1",
        "tags": ["sustantivos", "fenómenos"],
        "words": [
            "maremágnum", "tumulto", "barahúnda", "estruendo",
            "fragor", "estrépito", "clamor", "bullicio",
            "algarada", "zafarrancho",
        ],
    },
    # --- PERSONAS Y ROLES ---
    {
        "title": "Personas y tipos I",
        "description": "Sustantivos para tipos de personas",
        "cefr": "C1",
        "tags": ["sustantivos", "personas"],
        "words": [
            "advenedizo", "acólito", "epígono", "filántropo",
            "misántropo", "prócer", "mecenas", "neófito",
            "diletante", "émulo",
        ],
    },
    {
        "title": "Personas y tipos II",
        "description": "Más sustantivos para tipos de personas",
        "cefr": "C2",
        "tags": ["sustantivos", "personas"],
        "words": [
            "adlátere", "confidente", "cómplice", "detractor",
            "benefactor", "bienhechor", "patricio", "plebeyo",
            "prosélito", "apóstata",
        ],
    },
    # --- SENTIMIENTOS ---
    {
        "title": "Sentimientos y emociones I",
        "description": "Sustantivos cultos de sentimientos",
        "cefr": "C1",
        "tags": ["sustantivos", "sentimientos"],
        "words": [
            "congoja", "zozobra", "desasosiego", "añoranza",
            "arrobo", "embeleso", "consternación", "turbación",
            "desconsuelo", "aflicción",
        ],
    },
    {
        "title": "Sentimientos y emociones II",
        "description": "Más sustantivos de sentimientos",
        "cefr": "C1",
        "tags": ["sustantivos", "sentimientos"],
        "words": [
            "regocijo", "arrebato", "pesadilla", "escalofrío",
            "estremecimiento", "sobrecogimiento", "embelesamiento",
            "arrobamiento", "tribulación", "quebranto",
        ],
    },
    # --- CONFLICTOS Y ESTRATAGEMAS ---
    {
        "title": "Conflictos y estratagemas",
        "description": "Vocabulario de conflictos y engaños",
        "cefr": "C1",
        "tags": ["sustantivos", "conflicto"],
        "words": [
            "pugna", "contienda", "escaramuza", "conflagración",
            "lisonja", "argucia", "ardid", "treta",
            "artimaña", "estratagema",
        ],
    },
    # --- ESPACIOS Y LUGARES ---
    {
        "title": "Espacios y lugares cultos",
        "description": "Sustantivos cultos de lugares y espacios",
        "cefr": "C2",
        "tags": ["sustantivos", "lugares"],
        "words": [
            "pináculo", "cénit", "nadir", "páramo",
            "erial", "alcázar", "atalaya", "reducto",
            "bastión", "ciudadela",
        ],
    },
    # --- SALUD ---
    {
        "title": "Salud y remedios",
        "description": "Vocabulario culto de salud y remedios",
        "cefr": "C1",
        "tags": ["sustantivos", "salud"],
        "words": [
            "dolencia", "padecimiento", "convalecencia",
            "postración", "pócima", "ungüento", "bálsamo",
            "elixir", "antídoto", "cataplasma",
        ],
    },
    # --- ADJETIVOS: CARÁCTER ---
    {
        "title": "Adjetivos de carácter I",
        "description": "Adjetivos positivos de carácter",
        "cefr": "C1",
        "tags": ["adjetivos", "carácter"],
        "words": [
            "sagaz", "tenaz", "locuaz", "magnánimo",
            "benévolo", "circunspecto", "taciturno", "flemático",
            "afable", "parsimonioso",
        ],
    },
    {
        "title": "Adjetivos de carácter II",
        "description": "Adjetivos negativos de carácter",
        "cefr": "C1",
        "tags": ["adjetivos", "carácter"],
        "words": [
            "mendaz", "suspicaz", "mordaz", "voraz",
            "bellaco", "artero", "taimado", "ladino",
            "solapado", "insidioso",
        ],
    },
    # --- ADJETIVOS: ASPECTO Y CONDICIÓN ---
    {
        "title": "Adjetivos de aspecto físico",
        "description": "Adjetivos cultos de apariencia",
        "cefr": "C1",
        "tags": ["adjetivos", "aspecto"],
        "words": [
            "macilento", "enjuto", "famélico", "lánguido",
            "demacrado", "escuálido", "adusto", "cetrino",
            "rubicundo", "fornido",
        ],
    },
    {
        "title": "Adjetivos de condición",
        "description": "Adjetivos cultos de estados y condiciones",
        "cefr": "C1",
        "tags": ["adjetivos", "condición"],
        "words": [
            "perentorio", "aciago", "funesto", "inexorable",
            "intempestivo", "inusitado", "insólito", "primigenio",
            "atávico", "consuetudinario",
        ],
    },
    # --- VERBOS: COMUNICACIÓN ---
    {
        "title": "Verbos de comunicación",
        "description": "Verbos cultos para hablar y debatir",
        "cefr": "C1",
        "tags": ["verbos", "comunicación"],
        "words": [
            "arengar", "argüir", "rebatir", "refutar",
            "disertar", "perorar", "apostillar", "interpelar",
            "musitar", "vociferar",
        ],
    },
    # --- VERBOS: PERCEPCIÓN ---
    {
        "title": "Verbos de percepción y pensamiento",
        "description": "Verbos cultos de observar y pensar",
        "cefr": "C1",
        "tags": ["verbos", "percepción"],
        "words": [
            "cavilar", "rumiar", "avizorar", "vislumbrar",
            "atisbar", "escrutar", "otear", "columbrar",
            "conjeturar", "barruntar",
        ],
    },
    # --- VERBOS: DOMINIO ---
    {
        "title": "Verbos de dominio y sometimiento",
        "description": "Verbos cultos de poder y control",
        "cefr": "C2",
        "tags": ["verbos", "dominio"],
        "words": [
            "sojuzgar", "avasallar", "doblegar", "arredrar",
            "amilanar", "apabullar", "acallar", "coaccionar",
            "coartar", "constreñir",
        ],
    },
    # --- VERBOS: MOVIMIENTO ---
    {
        "title": "Verbos de movimiento",
        "description": "Verbos cultos de desplazamiento",
        "cefr": "C1",
        "tags": ["verbos", "movimiento"],
        "words": [
            "deambular", "merodear", "acechar", "surcar",
            "trasegar", "peregrinar", "divagar", "escabullirse",
            "replegarse", "congregarse",
        ],
    },
    # --- PSICOLOGÍA ---
    {
        "title": "Psicología y mente",
        "description": "Términos psicológicos cultos",
        "cefr": "C1",
        "tags": ["psicología"],
        "words": [
            "catarsis", "narcisismo", "megalomanía", "paranoia",
            "sublimación", "fobia", "psicosis", "delirio",
            "histeria", "alucinación",
        ],
    },
    # --- SOCIOLOGÍA ---
    {
        "title": "Sociología y poder",
        "description": "Vocabulario de sociología y sistemas de poder",
        "cefr": "C1",
        "tags": ["sociología", "política"],
        "words": [
            "anomia", "plutocracia", "oligarquía", "autocracia",
            "teocracia", "nepotismo", "caciquismo", "clientelismo",
            "estratificación", "endogamia",
        ],
    },
    # --- RELIGIÓN ---
    {
        "title": "Religión y creencias",
        "description": "Vocabulario de religión y doctrinas",
        "cefr": "C2",
        "tags": ["religión"],
        "words": [
            "herejía", "cisma", "blasfemia", "sacrilegio",
            "iconoclasta", "heterodoxo", "ortodoxo", "proselitismo",
            "sincretismo", "panteísmo",
        ],
    },
    # --- NATURALEZA ---
    {
        "title": "Naturaleza y geografía",
        "description": "Vocabulario culto de paisajes y terrenos",
        "cefr": "C1",
        "tags": ["naturaleza", "geografía"],
        "words": [
            "estepa", "desfiladero", "collado", "otero",
            "cañada", "vega", "alcor", "peñasco",
            "risco", "quebrada",
        ],
    },
    # --- ECONOMÍA ---
    {
        "title": "Economía y hacienda",
        "description": "Vocabulario culto de economía y finanzas",
        "cefr": "C1",
        "tags": ["economía"],
        "words": [
            "erario", "peculio", "estipendio", "emolumento",
            "gravamen", "plusvalía", "arancel", "usura",
            "insolvencia", "oligopolio",
        ],
    },
    # --- VIRTUDES Y VICIOS ---
    {
        "title": "Virtudes y vicios",
        "description": "Vocabulario de virtudes y vicios morales",
        "cefr": "C2",
        "tags": ["sustantivos", "moral"],
        "words": [
            "templanza", "magnanimidad", "munificencia",
            "continencia", "prodigalidad", "pusilanimidad",
            "concupiscencia", "intemperancia", "abyección",
            "incuria",
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
    # --- Existing words: Adjetivos cultos I ---
    "efímero": "Que dura un solo día; pasajero, de corta duración",
    "perspicaz": "Que tiene percepción mental aguda y penetrante",
    "recóndito": "Muy escondido, reservado y oculto",
    "prístino": "Que mantiene sin cambio alguno su naturaleza original",
    "insigne": "Célebre, distinguido y notable por sus méritos",
    "exiguo": "Muy escaso en cantidad o dimensión",
    "incólume": "Que no ha sufrido lesión ni menoscabo; ileso",
    "conspicuo": "Notable, sobresaliente e ilustre",
    # --- Existing words that fail intermittently on Wiktionary ---
    "hipótesis": "Proposición que se establece provisionalmente como base de una investigación",
    "postulado": "Proposición cuya veracidad se admite sin demostración",
    "taxonomía": "Ciencia de la clasificación según principios sistemáticos",
    "anomalía": "Desviación o irregularidad respecto de lo normal o esperado",
    "variable": "Que varía o puede variar; magnitud que puede tomar distintos valores",
    "correlación": "Correspondencia o influencia recíproca entre dos o más cosas",
    "serendipia": "Descubrimiento o hallazgo afortunado e inesperado que se produce por accidente",
    "heurística": "Disciplina que estudia los métodos de descubrimiento e investigación",
    "entropía": "Magnitud de la energía de un sistema que no puede convertirse en trabajo útil",
    "etiología": "Estudio sobre el origen fundamental o causa de las cosas, especialmente enfermedades",
    "profilaxis": "Prevención de enfermedades mediante medidas higiénicas o terapéuticas",
    "iatrogenia": "Daño no deseado en la salud causado por una intervención médica",
    "paliativo": "Que reduce o frena el dolor o un problema sin eliminarlo de raíz",
    "idiopático": "Dicho de una enfermedad que no tiene causa u origen conocido",
    "nosología": "Parte de la medicina que describe y clasifica las enfermedades",
    "asepsia": "Ausencia de gérmenes o materia productora de infecciones",
    "prognosis": "Pronóstico; estimación del desarrollo probable de una enfermedad o situación",
    "boato": "Exhibición pública de magnificencia y ostentación",
    "acaecimiento": "Algo que sucede u ocurre; acontecimiento",
    "solaz": "Descanso o recreo del cuerpo o del espíritu",
    "denuesto": "Injuria grave, de palabra o por escrito",
    "infundio": "Mentira o información falsa que se difunde con intención de dañar",
    "lozano": "Que abunda en verdor y frescura; que muestra vigor y salud",
    "donaire": "Capacidad de expresarse con elegancia e ingenio; gracia en el porte",
    "bizarro": "Que muestra valor o bravura; gallardo y apuesto",
    "gallardo": "Desembarazado, airoso y de porte elegante",
    "hidalgo": "Perteneciente a la nobleza, especialmente a la baja nobleza castellana",
    "talante": "Modo o manera de ejecutar una cosa; disposición del ánimo",
    "desaguisado": "Destrozo, desafuero; acción desatinada o perjudicial",
    "ínclito": "Famoso por su sobresaliente logro o aptitudes; ilustre",
    "preclaro": "Esclarecido, ilustre, famoso y digno de admiración y respeto",
    "merced": "Premio o galardón que se da por el trabajo; gracia o favor",
    "abolengo": "Ascendencia de abuelos o antepasados; linaje noble",
    "antojadizo": "Que constantemente tiene antojos o caprichos pasajeros",
    "cuita": "Aflicción, preocupación o angustia del ánimo",
    "desaire": "Falta de amabilidad o cortesía; desatención despectiva",
    "saña": "Enojo ciego; acceso súbito y violento de ira",
    "yantar": "Tomar la comida de mediodía; comer, especialmente con apetito",
    "algarabía": "Ruido generado por mucha gente que habla al mismo tiempo",
    "alborozo": "Extraordinario regocijo, placer o alegría",
    # --- New words: Fenómenos y estados I ---
    "marasmo": "Paralización o estancamiento extremo de la actividad o el ánimo",
    "letargo": "Estado de somnolencia profunda y prolongada; inactividad persistente",
    "éxtasis": "Estado de arrobamiento o admiración intensa que suspende los sentidos",
    "vorágine": "Remolino impetuoso; situación caótica y absorbente",
    "cataclismo": "Trastorno grave del globo terráqueo; gran desastre o catástrofe",
    "debacle": "Desastre, hundimiento o derrota repentina y estrepitosa",
    "hecatombe": "Desastre con gran número de víctimas; catástrofe de grandes proporciones",
    "paroxismo": "Exaltación extrema de un sentimiento o de los síntomas de una enfermedad",
    "estupor": "Asombro o pasmo que deja sin capacidad de reacción",
    "sopor": "Adormecimiento; somnolencia pesada que embota los sentidos",
    # --- New words: Fenómenos y estados II ---
    "maremágnum": "Confusión o abundancia desordenada de cosas o personas",
    "tumulto": "Alboroto o agitación desordenada de una multitud",
    "barahúnda": "Ruido y confusión grandes producidos por mucha gente",
    "estruendo": "Ruido muy fuerte y estrepitoso; gran conmoción",
    "fragor": "Ruido estruendoso y prolongado, como el de un trueno o batalla",
    "estrépito": "Ruido fuerte y violento que causa alarma o sobresalto",
    "clamor": "Grito o voz colectiva que expresa un sentimiento intenso",
    "bullicio": "Ruido y agitación producidos por mucha gente en movimiento",
    "algarada": "Vocerío tumultuoso; alboroto provocado por una multitud",
    "zafarrancho": "Riña o pelea confusa; desorden y limpieza general",
    # --- New words: Personas y tipos I ---
    "advenedizo": "Persona que llega a un lugar o posición sin pertenecer a él por origen o mérito",
    "acólito": "Seguidor o acompañante fiel de alguien; ayudante en ceremonias",
    "epígono": "Seguidor o imitador de una escuela o estilo, generalmente sin originalidad",
    "filántropo": "Persona que ama al género humano y trabaja por su bienestar",
    "misántropo": "Persona que siente aversión o rechazo hacia el trato con otros",
    "prócer": "Persona ilustre y eminente, especialmente en la vida pública de un país",
    "mecenas": "Persona adinerada que patrocina las artes o las ciencias",
    "neófito": "Persona recién incorporada a una actividad, grupo o creencia",
    "diletante": "Persona que cultiva un arte o una ciencia como aficionado, sin profundidad",
    "émulo": "Persona que intenta igualar o superar a otra en méritos o logros",
    # --- New words: Personas y tipos II ---
    "adlátere": "Persona que acompaña constantemente a otra como auxiliar o subordinado",
    "confidente": "Persona a quien se confían secretos o asuntos íntimos",
    "cómplice": "Persona que participa junto con otra en la comisión de un delito o acción reprobable",
    "detractor": "Persona que critica, desacredita o habla mal de alguien o algo",
    "benefactor": "Persona que hace bien a otra o le presta ayuda generosa",
    "bienhechor": "Persona que hace el bien a otros de manera habitual y desinteresada",
    "patricio": "Persona perteneciente a la clase noble o aristocrática de una sociedad",
    "plebeyo": "Persona del pueblo llano, no perteneciente a la nobleza",
    "prosélito": "Persona que se ha convertido recientemente a una doctrina o causa",
    "apóstata": "Persona que abandona públicamente su religión, doctrina o partido",
    # --- New words: Sentimientos I ---
    "congoja": "Angustia y aflicción profundas del ánimo",
    "zozobra": "Inquietud, desasosiego o temor ante un peligro o incertidumbre",
    "desasosiego": "Falta de sosiego; inquietud o intranquilidad persistente",
    "añoranza": "Sentimiento de tristeza por la ausencia de algo o alguien querido",
    "arrobo": "Estado de éxtasis o admiración profunda que suspende los sentidos",
    "embeleso": "Placer intenso que cautiva y absorbe la atención por completo",
    "consternación": "Abatimiento y sorpresa causados por algo inesperado y grave",
    "turbación": "Alteración del ánimo que produce confusión o vergüenza",
    "desconsuelo": "Aflicción profunda por la falta de consuelo o esperanza",
    "aflicción": "Pena, dolor moral o sufrimiento intenso del ánimo",
    # --- New words: Sentimientos II ---
    "regocijo": "Alegría intensa y bulliciosa; júbilo manifiesto",
    "arrebato": "Impulso violento y súbito de un sentimiento o pasión",
    "pesadilla": "Sueño angustioso; situación opresiva y difícil de soportar",
    "escalofrío": "Sensación de frío repentino causada por miedo, fiebre o emoción",
    "estremecimiento": "Temblor involuntario del cuerpo causado por una emoción intensa",
    "sobrecogimiento": "Sensación de asombro mezclada con temor o respeto reverencial",
    "embelesamiento": "Estado de arrobamiento causado por algo bello o cautivador",
    "arrobamiento": "Enajenación de los sentidos por efecto de la admiración o el éxtasis",
    "tribulación": "Congoja, pena o tormento que aflige el ánimo",
    "quebranto": "Pérdida grave de la salud o de las fuerzas; gran pesar o aflicción",
    # --- New words: Conflictos y estratagemas ---
    "pugna": "Lucha o enfrentamiento entre personas, grupos o ideas",
    "contienda": "Enfrentamiento o disputa entre dos o más partes",
    "escaramuza": "Combate breve y de poca importancia entre fuerzas menores",
    "conflagración": "Conflicto bélico de grandes proporciones; incendio devastador",
    "lisonja": "Alabanza exagerada y generalmente interesada para ganar el favor de alguien",
    "argucia": "Argumento sutil y engañoso usado para confundir o persuadir",
    "ardid": "Estratagema o medio hábil para lograr un fin, especialmente engañoso",
    "treta": "Artificio o maniobra ingeniosa para engañar o conseguir algo",
    "artimaña": "Trampa o engaño hábil y disimulado para conseguir un propósito",
    "estratagema": "Plan astuto ideado para lograr un objetivo, especialmente militar",
    # --- New words: Espacios y lugares ---
    "pináculo": "Punto más alto o culminante de algo; remate puntiagudo de un edificio",
    "cénit": "Punto más alto del cielo sobre un observador; apogeo o cumbre de algo",
    "nadir": "Punto opuesto al cénit; momento más bajo o desfavorable",
    "páramo": "Terreno yermo, raso y desabrigado, generalmente elevado",
    "erial": "Tierra sin cultivar ni labrar; lugar abandonado e improductivo",
    "alcázar": "Fortaleza o palacio fortificado de origen árabe",
    "atalaya": "Torre elevada desde la que se vigila el territorio circundante",
    "reducto": "Último lugar de resistencia o refugio; fortín",
    "bastión": "Baluarte o punto fuerte de defensa; apoyo principal de algo",
    "ciudadela": "Recinto fortificado en el interior de una plaza de armas",
    # --- New words: Salud y remedios ---
    "dolencia": "Enfermedad o indisposición, especialmente crónica o leve",
    "padecimiento": "Sufrimiento o enfermedad que se soporta durante largo tiempo",
    "convalecencia": "Período de recuperación tras una enfermedad o intervención",
    "postración": "Estado de abatimiento extremo, físico o moral",
    "pócima": "Bebida medicinal preparada con hierbas u otras sustancias",
    "ungüento": "Sustancia grasa medicinal que se aplica sobre la piel",
    "bálsamo": "Sustancia aromática y curativa; alivio para el dolor o la pena",
    "elixir": "Preparado medicinal prodigioso; solución ideal para un problema",
    "antídoto": "Sustancia que contrarresta los efectos de un veneno o un mal",
    "cataplasma": "Emplasto medicinal blando y húmedo que se aplica sobre la piel como remedio",
    # --- New words: Adjetivos de carácter I ---
    "sagaz": "Que muestra agudeza y previsión para entender las cosas",
    "tenaz": "Que se mantiene firme en sus propósitos con gran perseverancia",
    "locuaz": "Que habla mucho o con gran facilidad",
    "magnánimo": "Que tiene grandeza de ánimo y generosidad para perdonar ofensas",
    "benévolo": "Que tiene buena voluntad hacia los demás; bondadoso",
    "circunspecto": "Que actúa con prudencia y seriedad, midiendo sus palabras y actos",
    "taciturno": "Callado, silencioso; de temperamento melancólico",
    "flemático": "Que actúa con calma imperturbable y sin alterarse",
    "afable": "De trato agradable, amable y cortés",
    "parsimonioso": "Que actúa con lentitud y calma excesivas",
    # --- New words: Adjetivos de carácter II ---
    "mendaz": "Que tiene costumbre de mentir; falso, engañoso",
    "suspicaz": "Inclinado a desconfiar o sospechar de todo y de todos",
    "mordaz": "Que critica con agudeza hiriente y sarcasmo",
    "voraz": "Que come con ansia desmedida; que consume o destruye con rapidez",
    "bellaco": "Astuto, pícaro y de malas intenciones",
    "artero": "Que actúa con maña y astucia para engañar",
    "taimado": "Astuto, disimulado y que oculta sus verdaderas intenciones",
    "ladino": "Sagaz y astuto, especialmente para engañar o salir de apuros",
    "solapado": "Que oculta maliciosamente sus intenciones o sentimientos",
    "insidioso": "Que prepara asechanzas o trampas de manera encubierta",
    # --- New words: Aspecto físico ---
    "macilento": "Flaco, demacrado y de aspecto enfermizo",
    "enjuto": "Delgado, seco y de pocas carnes",
    "famélico": "Extremadamente hambriento; muy flaco por falta de alimento",
    "lánguido": "Que muestra debilidad, desgana o falta de energía vital",
    "demacrado": "Con el rostro deteriorado por enfermedad, cansancio o sufrimiento",
    "escuálido": "Sumamente flaco, sucio y desaliñado",
    "adusto": "De semblante severo, seco y poco amable",
    "cetrino": "De tez de color amarillento verdoso; de aspecto melancólico",
    "rubicundo": "De color rojizo, especialmente aplicado al rostro o la tez",
    "fornido": "De complexión robusta, fuerte y corpulenta",
    # --- New words: Condiciones ---
    "perentorio": "Que es urgente, concluyente y no admite dilación",
    "aciago": "De mal agüero; que trae desgracia o infortunio",
    "funesto": "Que es origen de pesares o desgracias; luctuoso",
    "inexorable": "Que no se puede evitar ni detener; implacable",
    "intempestivo": "Que ocurre fuera del tiempo oportuno o conveniente",
    "inusitado": "No habitual; que ocurre rara vez o resulta sorprendente",
    "insólito": "Raro, desacostumbrado y fuera de lo común",
    "primigenio": "Originario, primitivo; que existe desde el principio",
    "atávico": "Que procede de antepasados remotos o de instintos ancestrales",
    "consuetudinario": "Que se hace por costumbre o tradición establecida",
    # --- New words: Verbos de comunicación ---
    "arengar": "Dirigir un discurso enérgico para enardecer los ánimos",
    "argüir": "Presentar argumentos contra algo; deducir o inferir",
    "rebatir": "Rechazar o contradecir un argumento con razones",
    "refutar": "Demostrar la falsedad de un argumento o afirmación",
    "disertar": "Exponer con amplitud y método un tema ante un auditorio",
    "perorar": "Pronunciar un discurso largo, a menudo tedioso o enfático",
    "apostillar": "Añadir notas o comentarios breves a un texto o discurso",
    "interpelar": "Dirigirse a alguien para exigirle explicaciones sobre su conducta",
    "musitar": "Hablar en voz muy baja, casi en susurro",
    "vociferar": "Gritar con vehemencia o dar grandes voces",
    # --- New words: Percepción y pensamiento ---
    "cavilar": "Reflexionar con insistencia y profundidad sobre algo",
    "rumiar": "Pensar detenida y repetidamente sobre algo; darle vueltas a una idea",
    "avizorar": "Observar con atención para descubrir algo oculto o lejano",
    "vislumbrar": "Percibir algo de manera confusa o tenue; intuir",
    "atisbar": "Mirar con cautela y disimulo; percibir indicios de algo",
    "escrutar": "Examinar con atención y minuciosidad algo para descubrir lo oculto",
    "otear": "Mirar desde un lugar alto para observar lo que hay a lo lejos",
    "columbrar": "Divisar algo a lo lejos de manera imprecisa; conjeturar",
    "conjeturar": "Formar juicio u opinión a partir de indicios o datos incompletos",
    "barruntar": "Presentir o sospechar algo por indicios o señales",
    # --- New words: Dominio y sometimiento ---
    "sojuzgar": "Someter con violencia; dominar por la fuerza",
    "avasallar": "Someter o subyugar a alguien imponiéndole obediencia",
    "doblegar": "Hacer ceder a alguien en su voluntad o resistencia",
    "arredrar": "Hacer retroceder a alguien por miedo o temor; amedrentar",
    "amilanar": "Causar miedo o desánimo que paraliza la acción",
    "apabullar": "Abrumar o desconcertar a alguien dejándolo sin respuesta",
    "acallar": "Hacer callar a alguien o algo; silenciar protestas u opiniones",
    "coaccionar": "Ejercer presión o fuerza sobre alguien para obligarlo a actuar",
    "coartar": "Limitar o restringir la libertad o los derechos de alguien",
    "constreñir": "Obligar o compeler a alguien a hacer algo; oprimir",
    # --- New words: Movimiento ---
    "deambular": "Andar sin rumbo fijo ni destino determinado",
    "merodear": "Rondar un lugar con intención sospechosa o a la espera",
    "acechar": "Observar o espiar cautelosamente con un propósito hostil",
    "surcar": "Navegar por el mar; atravesar un espacio abierto",
    "trasegar": "Mudar cosas de un lugar a otro; beber con exceso",
    "peregrinar": "Viajar a un lugar sagrado por devoción; andar errante",
    "divagar": "Apartarse del tema principal; hablar o pensar sin orden ni concierto",
    "escabullirse": "Escapar o irse de un lugar con disimulo y rapidez",
    "replegarse": "Retirarse ordenadamente ante el adversario; recogerse sobre sí mismo",
    "congregarse": "Reunirse o juntarse varias personas en un lugar",
    # --- New words: Psicología ---
    "catarsis": "Liberación de emociones reprimidas que produce alivio interior",
    "narcisismo": "Admiración excesiva y enfermiza de uno mismo",
    "megalomanía": "Delirio de grandeza; creencia exagerada en el propio poder",
    "paranoia": "Trastorno caracterizado por desconfianza extrema y delirios de persecución",
    "sublimación": "Transformación de impulsos instintivos en actividades socialmente valoradas",
    "fobia": "Temor intenso e irracional hacia algo específico",
    "psicosis": "Trastorno mental grave con pérdida del contacto con la realidad",
    "delirio": "Perturbación mental con ideas incoherentes y percepciones falsas",
    "histeria": "Estado de excitación nerviosa extrema con reacciones descontroladas",
    "alucinación": "Percepción sensorial falsa sin estímulo externo real",
    # --- New words: Sociología y poder ---
    "anomia": "Ausencia de normas sociales o desintegración del orden moral",
    "plutocracia": "Sistema de gobierno en que el poder lo ejercen los más ricos",
    "oligarquía": "Gobierno ejercido por un grupo reducido y privilegiado",
    "autocracia": "Sistema de gobierno en que una sola persona ejerce el poder absoluto",
    "teocracia": "Gobierno ejercido directamente por Dios o por los sacerdotes",
    "nepotismo": "Favoritismo hacia familiares o amigos en la concesión de cargos",
    "caciquismo": "Dominio abusivo de un cacique o jefe local sobre una comunidad",
    "clientelismo": "Sistema de relaciones políticas basado en el intercambio de favores",
    "estratificación": "División de la sociedad en capas o niveles jerárquicos",
    "endogamia": "Práctica de contraer matrimonio dentro del propio grupo social",
    # --- New words: Religión ---
    "herejía": "Doctrina contraria a los dogmas de una religión establecida",
    "cisma": "División o separación en el seno de una iglesia o comunidad",
    "blasfemia": "Palabra o expresión injuriosa contra Dios o lo sagrado",
    "sacrilegio": "Profanación de algo considerado sagrado o digno de respeto",
    "iconoclasta": "Que rechaza o destruye tradiciones, imágenes o valores establecidos",
    "heterodoxo": "Que se aparta de la doctrina o las normas aceptadas",
    "ortodoxo": "Que se ajusta fielmente a la doctrina o normas establecidas",
    "proselitismo": "Afán de ganar seguidores para una causa, doctrina o partido",
    "sincretismo": "Fusión de elementos de distintas doctrinas, religiones o culturas",
    "panteísmo": "Doctrina que identifica a Dios con el universo y la naturaleza",
    # --- New words: Naturaleza ---
    "estepa": "Llanura extensa y árida con escasa vegetación herbácea",
    "desfiladero": "Paso estrecho entre montañas por donde solo se puede ir en fila",
    "collado": "Depresión suave entre dos alturas contiguas de un terreno montañoso",
    "otero": "Cerro aislado que domina un llano",
    "cañada": "Valle estrecho y alargado entre montañas o lomas",
    "vega": "Extensión de tierra baja, llana y fértil junto a un río",
    "alcor": "Colina o cerro de poca altura",
    "peñasco": "Roca grande y elevada que sobresale en un terreno",
    "risco": "Peñasco alto, escarpado y de difícil acceso",
    "quebrada": "Abertura estrecha y áspera entre montañas; barranco",
    # --- New words: Economía ---
    "erario": "Tesoro público de un Estado; conjunto de rentas del Estado",
    "peculio": "Dinero o bienes propios de una persona; caudal modesto",
    "estipendio": "Remuneración que se da a una persona por un servicio prestado",
    "emolumento": "Retribución complementaria que se recibe por un cargo o empleo",
    "gravamen": "Carga u obligación que pesa sobre una propiedad o persona",
    "plusvalía": "Aumento del valor de un bien por causas externas al propietario",
    "arancel": "Tarifa oficial que grava la importación o exportación de mercancías",
    "usura": "Cobro de intereses excesivos por un préstamo de dinero",
    "insolvencia": "Incapacidad de pagar las deudas contraídas",
    "oligopolio": "Situación de mercado en la que unos pocos vendedores controlan la oferta",
    # --- New words: Virtudes y vicios ---
    "templanza": "Moderación y sobriedad en los apetitos y en el uso de los sentidos",
    "magnanimidad": "Grandeza de ánimo para emprender grandes obras y perdonar ofensas",
    "munificencia": "Generosidad espléndida en dar o conceder",
    "continencia": "Virtud de moderar y refrenar las pasiones y apetitos",
    "prodigalidad": "Tendencia a gastar o dar con exceso y sin medida",
    "pusilanimidad": "Falta de valor y ánimo para afrontar dificultades o emprender grandes cosas",
    "concupiscencia": "Deseo desordenado de placeres, especialmente carnales",
    "intemperancia": "Falta de templanza o moderación; exceso en los apetitos",
    "abyección": "Estado de degradación moral extrema; bajeza y envilecimiento",
    "incuria": "Negligencia y descuido en el cumplimiento de las obligaciones",
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
