"""One-time migration: load missing vocab and create topics.

Adds the remaining Spanish words (ranks 121-529) from
vocab.json, creates a "Data Science - Basics" topic for
the existing DS/ML/NLP concepts (IDs 1-60), and creates
all 53 Spanish vocabulary topics from lessons.json.

Usage:
    uv run python scripts/migrate_topics.py
"""

import asyncio
import json
from pathlib import Path

from rembrandt import Database
from rembrandt.models import Topic

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "rembrandt.db"
VOCAB_JSON = DATA_DIR / "vocab.json"
LESSONS_JSON = DATA_DIR / "lessons.json"

# The first 60 concept IDs are data science terms.
DS_CONCEPT_IDS = list(range(1, 61))

# Spanish vocab starts at concept ID 61 in the current DB,
# corresponding to vocab rank 1.  120 words are already
# loaded (ranks 1-120, IDs 61-180).
SPANISH_ID_OFFSET = 60
EXISTING_SPANISH_RANKS = 120


async def main() -> None:
    db = await Database.connect(str(DB_PATH))

    # -- 1. Load missing Spanish words (ranks 121-529) --
    with open(VOCAB_JSON, encoding="utf-8") as f:
        all_words = json.load(f)

    # rank -> concept_id mapping for existing words
    rank_to_id: dict[int, int] = {
        r: r + SPANISH_ID_OFFSET
        for r in range(1, EXISTING_SPANISH_RANKS + 1)
    }

    new_count = 0
    for entry in all_words:
        rank = entry["rank"]
        if rank <= EXISTING_SPANISH_RANKS:
            continue
        # vocab.json: "definition" = front, "word" = back
        concept = await db.add_concept(
            front=entry["definition"],
            back=entry["word"],
        )
        rank_to_id[rank] = concept.id
        new_count += 1

    print(f"Added {new_count} new Spanish concepts")

    # -- 2. Create "Data Science - Basics" topic --
    ds_topic = Topic(
        title="Data Science - Basics",
        description="Fundamental data science, ML, and NLP "
        "terminology",
        tags=["data-science", "ml", "nlp"],
        concept_count=len(DS_CONCEPT_IDS),
        concept_ids=DS_CONCEPT_IDS,
    )
    saved_ds = await db.add_topic(ds_topic)
    print(
        f"Created topic '{saved_ds.title}' "
        f"(id={saved_ds.id}, {saved_ds.concept_count} "
        f"concepts)"
    )

    # -- 3. Create Spanish vocabulary topics --
    with open(LESSONS_JSON, encoding="utf-8") as f:
        lessons = json.load(f)

    spanish_topics: list[Topic] = []
    for lesson in lessons:
        concept_ids = [
            rank_to_id[r]
            for r in lesson["word_ranks"]
            if r in rank_to_id
        ]
        if not concept_ids:
            print(
                f"  SKIP: {lesson['title']} "
                f"(no matching concepts)"
            )
            continue
        spanish_topics.append(
            Topic(
                title=lesson["title"],
                description=lesson.get("description", ""),
                tags=lesson.get("tags", []),
                concept_count=len(concept_ids),
                concept_ids=concept_ids,
            )
        )

    saved = await db.add_topics(spanish_topics)
    print(f"Created {len(saved)} Spanish topics")

    await db.close()
    print("Migration complete.")


if __name__ == "__main__":
    asyncio.run(main())
