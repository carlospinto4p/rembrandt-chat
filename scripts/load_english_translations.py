"""Load English translations for the bundled Spanish vocabulary."""

import asyncio

from rembrandt import Database, import_concepts_csv

# (spanish_front, english_front, english_back)
TRANSLATIONS: list[tuple[str, str, str]] = [
    # Adjectives I (1-10)
    ("efímero", "ephemeral",
     "Lasting for a very short time"),
    ("ubicuo", "ubiquitous",
     "Present, appearing, or found everywhere"),
    ("acérrimo", "staunch",
     "Very firm and unyielding in one's ideas or attitudes"),
    ("perspicaz", "perspicacious",
     "Having keen mental perception and understanding"),
    ("recóndito", "recondite",
     "Very hidden, reserved, and secluded"),
    ("prístino", "pristine",
     "Retaining its original nature without any change"),
    ("insigne", "illustrious",
     "Famous and distinguished for outstanding merits"),
    ("exiguo", "meagre",
     "Very scarce in quantity or size"),
    ("incólume", "unscathed",
     "Healthy, without injury or damage"),
    ("acucioso", "diligent",
     "Prompt and careful in doing things"),
    # Adjectives II (11-20)
    ("diáfano", "diaphanous",
     "Allowing light to pass through almost entirely"),
    ("ignoto", "unknown",
     "Not known, not discovered or explored"),
    ("vetusto", "ancient",
     "Very old or of great age"),
    ("feraz", "fertile",
     "Extremely productive, abundant in fruit"),
    ("sempiterno", "everlasting",
     "Of infinite duration"),
    ("iracundo", "irascible",
     "Prone to anger, easily enraged"),
    ("ominoso", "ominous",
     "Causing fear or repulsion due to danger or bad luck"),
    ("cruento", "bloody",
     "Involving or causing great bloodshed"),
    ("inveterado", "inveterate",
     "Long-established and difficult to change"),
    ("execrable", "execrable",
     "Deserving severe condemnation or criticism"),
    # Abstract nouns I (21-30)
    ("desidia", "indolence",
     "Lack of effort or dedication to necessary tasks"),
    ("vehemencia", "vehemence",
     "Great intensity of feeling or expression"),
    ("mesura", "moderation",
     "Restraint and composure in behaviour or words"),
    ("displicencia", "disdain",
     "Displeasure or indifference in manner"),
    ("acervo", "collection",
     "An accumulation of small items piled together"),
    ("menoscabo", "detriment",
     "Diminishment of value, importance, or prestige"),
    ("acopio", "stockpile",
     "The act of gathering provisions or materials"),
    ("desazón", "unease",
     "A feeling of malaise, restlessness, or displeasure"),
    ("premura", "urgency",
     "Pressure, haste, or pressing need"),
    ("denuedo", "determination",
     "Vigorous effort to achieve something"),
    # Abstract nouns II (31-40)
    ("resquicio", "crack",
     "An opening between a door and its frame"),
    ("cariz", "aspect",
     "The appearance a matter or situation presents"),
    ("derrotero", "course",
     "The path or direction taken to reach a goal"),
    ("coyuntura", "juncture",
     "A combination of circumstances at a given moment"),
    ("vestigio", "vestige",
     "A trace left in a place where someone has been"),
    ("diatriba", "diatribe",
     "A violent and injurious speech against someone"),
    ("precepto", "precept",
     "A commandment given by an authorised person"),
    ("salvedad", "caveat",
     "A qualification or exception to what is said"),
    ("envergadura", "wingspan",
     "The distance between the tips of outstretched wings"),
    ("menester", "occupation",
     "A person's habitual work or activity"),
    # Verbs I (41-50)
    ("dilucidar", "elucidate",
     "To explain or clarify a matter"),
    ("esgrimir", "wield",
     "To use something, especially an argument, as a weapon"),
    ("soslayar", "sidestep",
     "To avoid a difficulty or topic"),
    ("ponderar", "ponder",
     "To examine something carefully, weighing pros and cons"),
    ("acaecer", "occur",
     "To happen, to take place"),
    ("enmendar", "amend",
     "To fix or correct faults or defects"),
    ("socavar", "undermine",
     "To dig underneath, weakening support"),
    ("abogar", "advocate",
     "To defend or counsel someone in a legal matter"),
    ("discernir", "discern",
     "To differentiate one thing from another"),
    ("aducir", "adduce",
     "To present reasons or evidence in support"),
    # Verbs II (51-60)
    ("dirimir", "settle",
     "To resolve or put an end to a dispute"),
    ("resarcir", "compensate",
     "To repair damage through payment or action"),
    ("escatimar", "skimp",
     "To give or use as little as possible"),
    ("desdeñar", "disdain",
     "To treat someone or something with contempt"),
    ("vindicar", "vindicate",
     "To defend someone unjustly attacked or despised"),
    ("acusar", "accuse",
     "To assign blame for something illegal or immoral"),
    ("usurpar", "usurp",
     "To seize property or a right by force"),
    ("desistir", "desist",
     "To stop insisting or cease an effort"),
    ("atenuar", "attenuate",
     "To reduce the force or intensity of something"),
    ("amedrentar", "intimidate",
     "To instil fear or apprehension"),
    # Verbs III (61-71)
    ("escindir", "split",
     "To separate or divide into parts"),
    ("holgar", "rest",
     "To take a break after exertion"),
    ("increpar", "rebuke",
     "To reprimand someone harshly"),
    ("azuzar", "incite",
     "To urge a dog to bark or attack"),
    ("expiar", "expiate",
     "To atone for guilt through punishment"),
    ("zaherir", "wound",
     "To say something causing humiliation or moral pain"),
    ("denostar", "revile",
     "To verbally attack with grave insults"),
    ("conminar", "threaten",
     "To warn someone of punishment for disobedience"),
    ("medrar", "thrive",
     "To improve one's position or prosper"),
    ("fulminar", "annihilate",
     "To destroy suddenly and violently"),
    # Logic & rhetoric (72-80)
    ("falacia", "fallacy",
     "A deception or lie intended to harm another"),
    ("silogismo", "syllogism",
     "A deductive argument with three propositions"),
    ("premisa", "premise",
     "A principle from which inferences are drawn"),
    ("paradoja", "paradox",
     "A statement contrary to common belief"),
    ("retórica", "rhetoric",
     "The art of effective and persuasive language"),
    ("sofisma", "sophism",
     "An apparently valid argument used to defend a lie"),
    ("aforismo", "aphorism",
     "A concise statement expressing a principle"),
    ("elocuencia", "eloquence",
     "The ability to express oneself fluently and "
     "persuasively"),
    ("apología", "apologia",
     "A speech or writing in defence or praise"),
    # Philosophy (81-91)
    ("demagogia", "demagoguery",
     "The political practice of gaining popular favour "
     "through flattery"),
    ("ontología", "ontology",
     "The branch of metaphysics studying being and "
     "existence"),
    ("epistemología", "epistemology",
     "The field studying the foundations of scientific "
     "knowledge"),
    ("axioma", "axiom",
     "A self-evident truth requiring no proof"),
    ("dialéctica", "dialectics",
     "Formal reasoning through dialogue and logical "
     "arguments"),
    ("teleología", "teleology",
     "The doctrine explaining the universe through "
     "purposeful causes"),
    ("hermenéutica", "hermeneutics",
     "The theory and method of text interpretation"),
    ("nihilismo", "nihilism",
     "The denial of all principles or dogmas"),
    ("solipsismo", "solipsism",
     "The theory that only one's own mind is certain "
     "to exist"),
    ("empirismo", "empiricism",
     "The doctrine that knowledge is founded on "
     "experience"),
    ("altruismo", "altruism",
     "Selfless concern for the well-being of others"),
    # Literary figures (92-101)
    ("metáfora", "metaphor",
     "A figure of speech equating two unlike things"),
    ("metonimia", "metonymy",
     "A figure substituting a name with a related one"),
    ("sinécdoque", "synecdoche",
     "A figure where a part represents the whole or "
     "vice versa"),
    ("oxímoron", "oxymoron",
     "An expression combining contradictory terms"),
    ("hipérbole", "hyperbole",
     "Deliberate exaggeration for emphasis"),
    ("antítesis", "antithesis",
     "The opposition of two contrasting ideas"),
    ("prosopopeya", "prosopopoeia",
     "A literary device attributing speech to a "
     "character"),
    ("elipsis", "ellipsis",
     "The omission of a word without affecting meaning"),
    ("anáfora", "anaphora",
     "Repetition of words at the start of successive "
     "clauses"),
    ("pleonasmo", "pleonasm",
     "The use of more words than necessary for "
     "emphasis"),
    # Legal terms (102-111)
    ("jurisprudencia", "jurisprudence",
     "The body of judicial decisions interpreting the "
     "law"),
    ("potestad", "authority",
     "Dominion or power held over something"),
    ("prerrogativa", "prerogative",
     "A privilege granted to someone by virtue of "
     "rank"),
    ("promulgar", "promulgate",
     "To publish or announce something officially"),
    ("derogar", "repeal",
     "To abolish or revoke a law or regulation"),
    ("litigio", "litigation",
     "A legal dispute or lawsuit"),
    ("indulto", "pardon",
     "A grace or privilege exempting someone from "
     "punishment"),
    ("exhorto", "rogatory letter",
     "A written request from one court to another"),
    ("fuero", "charter",
     "A particular law or statute of a region"),
    ("aquiescencia", "acquiescence",
     "Passive agreement to a decision made by another"),
    # Miscellaneous (112-121)
    ("boato", "pomp",
     "A public display of magnificence"),
    ("acaecimiento", "occurrence",
     "Something that happens or takes place"),
    ("albor", "dawn",
     "The light of daybreak; the beginning of "
     "something"),
    ("solaz", "solace",
     "Rest or recreation of body or spirit"),
    ("denuesto", "affront",
     "A grave insult, spoken or written"),
    ("infundio", "canard",
     "A false or baseless rumour spread to harm"),
    ("procaz", "impudent",
     "Shameless or brazen, especially in a sexual "
     "manner"),
    ("lozano", "lush",
     "Abounding in leaves and shoots, showing vigour"),
    ("donaire", "wit",
     "The ability to express oneself with elegance "
     "and ingenuity"),
    ("prestancia", "excellence",
     "The quality of being distinguished or superior"),
]


async def main() -> None:
    db = await Database.connect("data/rembrandt.db")

    # Load Spanish vocab if not already present
    concepts = await db.get_concepts()
    es_fronts = {c.front for c in concepts}
    sample_word = TRANSLATIONS[0][0]  # "efímero"
    if sample_word not in es_fronts:
        new = await import_concepts_csv(db, "data/vocab.csv")
        print(f"Loaded {len(new)} Spanish vocab words")
        concepts = await db.get_concepts()

    # Ensure English language exists
    lang = await db.get_language("en")
    if lang is None:
        await db.add_language("en", "English")
        print("Registered language: English (en)")

    front_map = {c.front: c for c in concepts}

    added = 0
    skipped = 0
    missing = 0

    for es_front, en_front, en_back in TRANSLATIONS:
        concept = front_map.get(es_front)
        if concept is None:
            print(f"  MISSING concept: {es_front}")
            missing += 1
            continue

        existing = await db.get_translation(
            concept.id, "en"
        )
        if existing is not None:
            skipped += 1
            continue

        await db.add_translation(
            concept.id, "en",
            front=en_front,
            back=en_back,
        )
        added += 1

    print(
        f"Done: {added} added, {skipped} skipped "
        f"(already exist), {missing} missing concepts"
    )
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
