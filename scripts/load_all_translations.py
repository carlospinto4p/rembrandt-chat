"""Load English translations for all concepts missing them.

Covers 60 data science terms (English definitions) and
409 Spanish vocabulary words (English equivalents).

Usage:
    uv run python scripts/load_all_translations.py
"""

import asyncio

from rembrandt import Database

# (concept_id, english_front, english_back)
TRANSLATIONS: list[tuple[int, str, str]] = [
    # --- Data Science (1-20) ---
    (1, "dataset",
     "A structured collection of data organised for analysis"),
    (2, "dataframe",
     "A tabular data structure of rows and columns used for "
     "data manipulation"),
    (3, "feature",
     "An individual variable or attribute used as model input"),
    (4, "outlier",
     "A data point that deviates significantly from the rest"),
    (5, "missing value",
     "An absent or unrecorded datum in a dataset"),
    (6, "data wrangling",
     "The process of cleaning and transforming raw data into "
     "a usable format"),
    (7, "exploratory data analysis",
     "Initial analysis of data to discover patterns and "
     "anomalies"),
    (8, "correlation",
     "A statistical relationship between two variables"),
    (9, "distribution",
     "A function describing the probability of possible "
     "values of a variable"),
    (10, "standard deviation",
     "A measure of dispersion indicating how far values "
     "deviate from the mean"),
    (11, "normalization",
     "Scaling data to a common range, typically 0 to 1"),
    (12, "data pipeline",
     "An automated sequence of steps for moving and "
     "transforming data"),
    (13, "ETL",
     "Extract, Transform, Load — a process for integrating "
     "data from multiple sources"),
    (14, "hypothesis testing",
     "A statistical method to determine whether a hypothesis "
     "about a population is supported by data"),
    (15, "p-value",
     "The probability of obtaining a result at least as "
     "extreme as observed, assuming the null hypothesis"),
    (16, "confidence interval",
     "A range of values likely to contain the true population "
     "parameter"),
    (17, "sampling bias",
     "Systematic error caused by a non-representative sample "
     "selection"),
    (18, "dimensionality reduction",
     "A technique to reduce the number of variables while "
     "retaining essential information"),
    (19, "cross-validation",
     "An evaluation method that partitions data into subsets "
     "for training and testing"),
    (20, "A/B testing",
     "A controlled experiment comparing two variants to "
     "determine which performs better"),
    # --- Machine Learning (21-40) ---
    (21, "supervised learning",
     "Learning where the model trains on labelled data"),
    (22, "unsupervised learning",
     "Learning where the model finds patterns in unlabelled "
     "data"),
    (23, "reinforcement learning",
     "Learning where an agent learns to make decisions by "
     "receiving rewards or penalties"),
    (24, "overfitting",
     "When a model fits training data too closely, losing "
     "generalisation ability"),
    (25, "underfitting",
     "When a model is too simple to capture the underlying "
     "patterns in data"),
    (26, "gradient descent",
     "An optimisation algorithm that adjusts parameters by "
     "moving in the direction of steepest descent"),
    (27, "learning rate",
     "A hyperparameter controlling the step size during "
     "gradient descent"),
    (28, "loss function",
     "A function measuring the difference between predicted "
     "and actual values"),
    (29, "epoch",
     "One complete pass of the training algorithm through "
     "the entire dataset"),
    (30, "batch size",
     "The number of samples processed before updating model "
     "parameters"),
    (31, "regularization",
     "A technique that penalises model complexity to prevent "
     "overfitting"),
    (32, "hyperparameter",
     "A parameter set before training begins, not learned "
     "from data"),
    (33, "decision tree",
     "A model that makes decisions by splitting data along "
     "feature thresholds"),
    (34, "random forest",
     "An ensemble of decision trees that combines their "
     "predictions"),
    (35, "neural network",
     "A computational model inspired by the brain, composed "
     "of interconnected layers of nodes"),
    (36, "backpropagation",
     "An algorithm that computes the error gradient and "
     "propagates it backwards to update weights"),
    (37, "activation function",
     "A function introducing non-linearity into a neuron's "
     "output"),
    (38, "convolutional neural network",
     "A neural network specialised in processing data with "
     "spatial structure, such as images"),
    (39, "transfer learning",
     "A technique that reuses a pre-trained model for a "
     "different but related task"),
    (40, "ensemble method",
     "A technique combining multiple models to achieve "
     "better predictions"),
    # --- NLP (41-60) ---
    (41, "tokenization",
     "Splitting text into smaller units such as words or "
     "subwords"),
    (42, "stemming",
     "Reducing words to their root by removing suffixes"),
    (43, "lemmatization",
     "Reducing a word to its base or dictionary form"),
    (44, "stop words",
     "Very frequent words typically removed during text "
     "preprocessing"),
    (45, "bag of words",
     "A text representation as a set of words disregarding "
     "order"),
    (46, "TF-IDF",
     "A statistic evaluating the importance of a word in a "
     "document relative to a corpus"),
    (47, "word embedding",
     "A dense vector representation of words capturing "
     "semantic relationships"),
    (48, "named entity recognition",
     "The task of identifying and classifying entities such "
     "as people, places, and organisations"),
    (49, "sentiment analysis",
     "Determining the attitude or emotion expressed in a "
     "text"),
    (50, "part-of-speech tagging",
     "Assigning grammatical categories to each word in a "
     "sentence"),
    (51, "language model",
     "A probabilistic model that predicts the next word in "
     "a sequence"),
    (52, "attention mechanism",
     "A mechanism allowing a model to focus on the most "
     "relevant parts of the input"),
    (53, "transformer",
     "A neural network architecture based on attention "
     "mechanisms for sequence processing"),
    (54, "sequence-to-sequence",
     "A model that transforms an input sequence into an "
     "output sequence"),
    (55, "text classification",
     "Assigning predefined categories to text fragments"),
    (56, "machine translation",
     "Automatic translation of text from one language to "
     "another"),
    (57, "corpus",
     "A large, structured collection of texts used for "
     "linguistic or computational research"),
    (58, "perplexity",
     "A metric measuring how well a language model predicts "
     "a sample"),
    (59, "fine-tuning",
     "Adjusting a pre-trained model with task-specific data"),
    (60, "hallucination",
     "Generation of text that appears plausible but is "
     "factually incorrect"),
    # --- Spanish: Verbs II remainder (181-200) ---
    (181, "settle",
     "To resolve or put an end to a dispute"),
    (182, "compensate",
     "To repair damage through payment or action"),
    (183, "skimp",
     "To give or use as little as possible"),
    (184, "disdain",
     "To treat someone or something with contempt"),
    (185, "vindicate",
     "To defend someone unjustly attacked or despised"),
    (186, "usurp",
     "To seize property or a right by force"),
    (187, "desist",
     "To stop insisting or cease an effort"),
    (188, "attenuate",
     "To reduce the force or intensity of something"),
    (189, "intimidate",
     "To instil fear or apprehension"),
    (190, "take over a case",
     "For a higher court to assume jurisdiction of a lower "
     "court's case"),
    (191, "contribute",
     "To help achieve or accomplish an activity"),
    (192, "concatenate",
     "To join or connect things in a sequence or chain"),
    (193, "hold illegitimately",
     "To exercise a position of power or responsibility "
     "without rightful claim"),
    (194, "elude",
     "To avoid a difficulty by means of some artifice"),
    (195, "elucidate",
     "To clarify or make something plain"),
    (196, "inflict",
     "To cause damage, punishment, or suffering to someone"),
    (197, "flaunt",
     "To display something conspicuously"),
    (198, "subjugate",
     "To force into obedience"),
    (199, "transgress",
     "To violate or break an established norm or law"),
    (200, "bond",
     "To establish a connection or tie with others"),
    # --- Spanish: Verbs III (201-210) ---
    (201, "split",
     "To separate or divide into parts"),
    (202, "rest",
     "To take a break after exertion"),
    (203, "rebuke",
     "To reprimand someone harshly"),
    (204, "incite",
     "To urge a dog to bark or attack"),
    (205, "expiate",
     "To atone for guilt through punishment"),
    (206, "wound",
     "To say something causing humiliation or moral pain"),
    (207, "revile",
     "To verbally attack with grave insults"),
    (208, "threaten",
     "To warn someone of punishment for disobedience"),
    (209, "thrive",
     "To improve one's position or prosper"),
    (210, "annihilate",
     "To destroy suddenly and violently"),
    # --- Spanish: Literary verbs I (211-220) ---
    (211, "harass",
     "To whip or punish with a lash or rod"),
    (212, "sift",
     "To separate fine from coarse with a sieve; to loom "
     "imminently"),
    (213, "squander",
     "To waste or misuse one's own patrimony"),
    (214, "exacerbate",
     "To cause intense anger or irritation"),
    (215, "castigate",
     "To whip or lash; to criticise harshly"),
    (216, "vilify",
     "To treat someone with contempt or despise something"),
    (217, "alienate",
     "To transfer ownership of a property or right to "
     "another person"),
    (218, "abjure",
     "To solemnly retract an error under oath"),
    (219, "capitulate",
     "To eventually yield to pressure or temptation"),
    (220, "sully",
     "To stain or tarnish something's appearance or "
     "reputation"),
    # --- Spanish: Literary verbs II (221-230) ---
    (221, "apostatise",
     "To renounce a faith one was baptised into"),
    (222, "arrogate",
     "To assign or attribute something to oneself"),
    (223, "gather",
     "To collect scattered things or people in one place"),
    (224, "stir up",
     "To excite unrest and sedition"),
    (225, "defer",
     "To postpone or delay the completion of something"),
    (226, "despoil",
     "To strip someone of their possessions by violence"),
    (227, "lucubrate",
     "To work intellectually with dedication, especially "
     "at night"),
    (228, "palliate",
     "To mitigate or lessen something negative"),
    (229, "extol",
     "To praise publicly and enthusiastically"),
    (230, "provoke",
     "To give rise to a feeling, reaction, or debate"),
    # --- Spanish: Rhetoric (231-240) ---
    (231, "fallacy",
     "A deception or lie intended to harm another"),
    (232, "syllogism",
     "A deductive argument with three propositions"),
    (233, "premise",
     "A principle from which inferences are drawn"),
    (234, "paradox",
     "A statement contrary to common belief"),
    (235, "rhetoric",
     "The art of effective and persuasive language"),
    (236, "sophism",
     "An apparently valid argument used to defend a lie"),
    (237, "aphorism",
     "A concise statement expressing a principle"),
    (238, "eloquence",
     "The ability to express oneself fluently and "
     "persuasively"),
    (239, "apologia",
     "A speech or writing in defence or praise"),
    (240, "demagoguery",
     "The political practice of gaining popular favour "
     "through flattery"),
    # --- Spanish: Figures of speech I (241-250) ---
    (241, "metaphor",
     "A figure of speech equating two unlike things"),
    (242, "metonymy",
     "A figure substituting a name with a related one"),
    (243, "synecdoche",
     "A figure where a part represents the whole or "
     "vice versa"),
    (244, "oxymoron",
     "An expression combining contradictory terms"),
    (245, "hyperbole",
     "Deliberate exaggeration for emphasis"),
    (246, "antithesis",
     "The opposition of two contrasting ideas"),
    (247, "prosopopoeia",
     "A literary device attributing speech to a character"),
    (248, "ellipsis",
     "The omission of a word without affecting meaning"),
    (249, "anaphora",
     "Repetition of words at the start of successive "
     "clauses"),
    (250, "pleonasm",
     "The use of more words than necessary for emphasis"),
    # --- Spanish: Figures of speech II (251-260) ---
    (251, "allegory",
     "A fictional creation with hidden or symbolic "
     "meaning"),
    (252, "irony",
     "Delicate and feigned mockery or jest"),
    (253, "litotes",
     "A figure of speech that affirms by negating the "
     "opposite"),
    (254, "periphrasis",
     "A roundabout way of saying something using multiple "
     "words"),
    (255, "synaesthesia",
     "A figure attributing a sensation to a different "
     "sense, as in 'warm colour'"),
    (256, "epithet",
     "An adjective that characterises rather than "
     "specifies"),
    (257, "apostrophe",
     "A figure where the speaker addresses an absent "
     "or imaginary person"),
    (258, "polysyndeton",
     "Repeated use of conjunctions for emphasis"),
    (259, "asyndeton",
     "Omission of conjunctions to quicken rhythm"),
    (260, "alliteration",
     "Repetition of similar sounds in nearby words"),
    # --- Spanish: Literary theory (261-270) ---
    (261, "diegesis",
     "The fictional world in which a narrative takes "
     "place"),
    (262, "verisimilitude",
     "The appearance of being true or credible"),
    (263, "soliloquy",
     "A theatrical speech in which an actor talks to "
     "themselves"),
    (264, "hagiography",
     "The biography or study of saints' lives"),
    (265, "exegesis",
     "Critical explanation or interpretation of a text"),
    (266, "epigraph",
     "A descriptive phrase heading a written work or "
     "chapter"),
    (267, "idyll",
     "A short pastoral poem of tender and delicate "
     "character"),
    (268, "panegyric",
     "A speech or writing of elaborate praise"),
    (269, "elegy",
     "A short lyric poem reflecting loss, grief, or "
     "sorrow"),
    (270, "satire",
     "A literary form using irony to criticise or "
     "ridicule"),
    # --- Spanish: Philosophy I (271-280) ---
    (271, "ontology",
     "The branch of metaphysics studying being and "
     "existence"),
    (272, "epistemology",
     "The field studying the foundations of knowledge"),
    (273, "axiom",
     "A self-evident truth requiring no proof"),
    (274, "dialectics",
     "Formal reasoning through dialogue and logical "
     "arguments"),
    (275, "teleology",
     "The doctrine explaining the universe through "
     "purposeful causes"),
    (276, "hermeneutics",
     "The theory and method of text interpretation"),
    (277, "nihilism",
     "The denial of all principles or dogmas"),
    (278, "solipsism",
     "The theory that only one's own mind is certain "
     "to exist"),
    (279, "empiricism",
     "The doctrine that knowledge is founded on "
     "experience"),
    (280, "altruism",
     "Selfless concern for the well-being of others"),
    # --- Spanish: Philosophy II (281-290) ---
    (281, "scholasticism",
     "A medieval philosophical and theological tradition "
     "based on Aristotelian logic"),
    (282, "hedonism",
     "A philosophical doctrine seeking a life full of "
     "pleasure"),
    (283, "stoicism",
     "Strength or control over one's own emotions"),
    (284, "determinism",
     "The view that a system's evolution depends solely "
     "on its initial conditions"),
    (285, "utilitarianism",
     "A moral doctrine judging actions by their overall "
     "usefulness"),
    (286, "relativism",
     "The theory that aspects of experience are relative "
     "to perspective"),
    (287, "pragmatism",
     "A doctrine that adopts practical utility as the "
     "criterion of truth"),
    (288, "rationalism",
     "A system of thought prioritising reason in "
     "acquiring knowledge"),
    (289, "dogmatism",
     "The presumption that one's own doctrine is "
     "unquestionable"),
    (290, "idealism",
     "A doctrine considering ideas and ideals as the "
     "foundation of reality"),
    # --- Spanish: Law and government I (291-300) ---
    (291, "jurisprudence",
     "The body of judicial decisions interpreting the "
     "law"),
    (292, "authority",
     "Dominion or power held over something"),
    (293, "prerogative",
     "A privilege granted by virtue of rank"),
    (294, "promulgate",
     "To publish or announce something officially"),
    (295, "repeal",
     "To abolish or revoke a law or regulation"),
    (296, "litigation",
     "A legal dispute or lawsuit"),
    (297, "pardon",
     "A grace exempting someone from punishment"),
    (298, "rogatory letter",
     "A written request from one court to another"),
    (299, "charter",
     "A particular law or statute of a region"),
    (300, "decree",
     "An official order or decision issued by an "
     "authority"),
    # --- Spanish: Law and government II (301-310) ---
    (301, "trust",
     "A legal arrangement where assets are held by one "
     "party for another's benefit"),
    (302, "contentious",
     "Given to disputing or contradicting everything"),
    (303, "contempt of court",
     "Disrespect towards the administration of justice"),
    (304, "prescription",
     "The extinction of a right or obligation through "
     "the passage of time"),
    (305, "edict",
     "A legal order or decree issued by a ruler"),
    (306, "classify",
     "To adjust or define something according to a type "
     "or legal norm"),
    (307, "jurist",
     "A person devoted to the study and interpretation "
     "of law"),
    (308, "challenge",
     "To oppose and refute something with reasoned "
     "arguments"),
    (309, "recuse",
     "To reject or disqualify something or someone"),
    (310, "countersign",
     "To authorise a document with an additional "
     "signature"),
    # --- Spanish: Science and method (311-320) ---
    (311, "hypothesis",
     "A provisional proposition serving as a basis for "
     "investigation"),
    (312, "postulate",
     "A proposition accepted without proof as a starting "
     "point"),
    (313, "taxonomy",
     "The science of classification according to "
     "systematic principles"),
    (314, "anomaly",
     "A deviation or irregularity from what is normal"),
    (315, "variable",
     "A quantity that can change or take different "
     "values"),
    (316, "correlation",
     "A reciprocal correspondence or influence between "
     "two things"),
    (317, "serendipity",
     "A fortunate and unexpected discovery made by "
     "accident"),
    (318, "heuristic",
     "A method of discovery and investigation through "
     "trial and experience"),
    (319, "entropy",
     "A measure of disorder or unavailable energy in a "
     "system"),
    (320, "aetiology",
     "The study of the fundamental origin or cause of "
     "things"),
    # --- Spanish: Medicine (321-329) ---
    (321, "pathophysiology",
     "The study of functional alterations caused by "
     "disease"),
    (322, "prophylaxis",
     "Prevention of disease through hygienic or "
     "therapeutic measures"),
    (323, "iatrogenesis",
     "Unintended harm to health caused by medical "
     "intervention"),
    (324, "symptomatology",
     "The set of symptoms characterising a disease"),
    (325, "palliative",
     "Something that reduces pain or a problem without "
     "eliminating it"),
    (326, "idiopathic",
     "Of a disease with no known cause or origin"),
    (327, "nosology",
     "The branch of medicine that describes and "
     "classifies diseases"),
    (328, "asepsis",
     "The absence of germs or infection-causing matter"),
    (329, "prognosis",
     "A forecast of the probable course of a disease"),
    # --- Spanish: Archaic words I (330-339) ---
    (330, "pomp",
     "A public display of magnificence"),
    (331, "occurrence",
     "Something that happens or takes place"),
    (332, "dawn",
     "The light of daybreak; the beginning of something"),
    (333, "solace",
     "Rest or recreation of body or spirit"),
    (334, "affront",
     "A grave insult, spoken or written"),
    (335, "canard",
     "A false or baseless rumour spread to harm"),
    (336, "impudent",
     "Shameless or brazen in manner"),
    (337, "lush",
     "Abounding in leaves and vigour"),
    (338, "wit",
     "The ability to express oneself with elegance and "
     "ingenuity"),
    (339, "excellence",
     "The quality of being distinguished or superior"),
    # --- Spanish: Archaic words II (340-349) ---
    (340, "gallant",
     "Showing valour or bravery; dashing and handsome"),
    (341, "graceful",
     "Having an elegant and poised bearing"),
    (342, "noble",
     "Of the nobility, especially the lesser gentry"),
    (343, "disposition",
     "One's manner or mood when doing something"),
    (344, "blunder",
     "A reckless or harmful action; a mess"),
    (345, "illustrious",
     "Famous for outstanding achievements or qualities"),
    (346, "eminent",
     "Distinguished, famous, and worthy of admiration"),
    (347, "idleness",
     "Leisure or rest; the state of not working"),
    (348, "grace",
     "A reward or favour given for service"),
    (349, "lineage",
     "Ancestry of grandparents or forebears; noble "
     "descent"),
    # --- Spanish: Archaic words III (350-359) ---
    (350, "capricious",
     "Constantly having passing whims or fancies"),
    (351, "misfortune",
     "Adverse luck; calamity or hardship"),
    (352, "grief",
     "Affliction, worry, or anguish of the spirit"),
    (353, "slight",
     "A lack of courtesy; a dismissive snub"),
    (354, "fury",
     "Blind rage; a sudden and violent burst of anger"),
    (355, "dine",
     "To eat a midday meal; to eat heartily"),
    (356, "sorrow",
     "A feeling of sadness, affliction, or displeasure"),
    (357, "hubbub",
     "Noise made by many people talking at once"),
    (358, "elation",
     "Extraordinary joy, pleasure, or delight"),
    (359, "vigilance",
     "Lack of sleep; careful attention to something"),
    # --- Spanish: Phenomena and states I (360-369) ---
    (360, "stagnation",
     "Extreme paralysis of activity or spirit"),
    (361, "lethargy",
     "A state of deep and prolonged drowsiness; "
     "persistent inactivity"),
    (362, "ecstasy",
     "A state of intense rapture suspending the senses"),
    (363, "maelstrom",
     "An impetuous whirlpool; a chaotic and absorbing "
     "situation"),
    (364, "cataclysm",
     "A great disturbance of the earth; a major "
     "catastrophe"),
    (365, "debacle",
     "A sudden and resounding disaster or defeat"),
    (366, "hecatomb",
     "A disaster with a great number of victims"),
    (367, "paroxysm",
     "An extreme intensification of a feeling or "
     "symptoms"),
    (368, "stupor",
     "Amazement leaving one unable to react"),
    (369, "torpor",
     "Drowsiness; a heavy sleepiness dulling the "
     "senses"),
    # --- Spanish: Phenomena and states II (370-379) ---
    (370, "jumble",
     "A disordered confusion of things or people"),
    (371, "tumult",
     "A disorderly commotion of a crowd"),
    (372, "commotion",
     "Great noise and confusion produced by many "
     "people"),
    (373, "din",
     "A very loud and resounding noise"),
    (374, "roar",
     "A thunderous, prolonged noise"),
    (375, "clatter",
     "A loud and violent noise causing alarm"),
    (376, "clamour",
     "A collective cry expressing intense feeling"),
    (377, "bustle",
     "Noise and agitation produced by a crowd in "
     "motion"),
    (378, "uproar",
     "A tumultuous outcry by a mob"),
    (379, "fracas",
     "A confused fight or scuffle; general disorder"),
    # --- Spanish: People and types I (380-389) ---
    (380, "upstart",
     "A person arriving at a place or position without "
     "belonging to it"),
    (381, "acolyte",
     "A faithful follower or attendant"),
    (382, "epigone",
     "A follower or imitator of a school or style, "
     "usually without originality"),
    (383, "philanthropist",
     "A person who loves humanity and works for its "
     "welfare"),
    (384, "misanthrope",
     "A person who feels aversion towards social "
     "interaction"),
    (385, "dignitary",
     "An illustrious and eminent person, especially in "
     "public life"),
    (386, "patron",
     "A wealthy person who sponsors the arts or "
     "sciences"),
    (387, "neophyte",
     "A person newly admitted to an activity or belief"),
    (388, "dilettante",
     "An amateur who dabbles in an art or science "
     "without deep commitment"),
    (389, "rival",
     "A person who attempts to equal or surpass another"),
    # --- Spanish: People and types II (390-399) ---
    (390, "sidekick",
     "A person who constantly accompanies another as "
     "an assistant"),
    (391, "confidant",
     "A person entrusted with secrets or intimate "
     "matters"),
    (392, "accomplice",
     "A person who participates with another in "
     "committing a crime"),
    (393, "detractor",
     "A person who criticises or speaks ill of "
     "someone"),
    (394, "benefactor",
     "A person who does good to others or provides "
     "generous help"),
    (395, "benefactor",
     "A person who habitually and selflessly does "
     "good to others"),
    (396, "patrician",
     "A person of the noble or aristocratic class"),
    (397, "plebeian",
     "A person of the common people, not of the "
     "nobility"),
    (398, "proselyte",
     "A recent convert to a doctrine or cause"),
    (399, "apostate",
     "A person who publicly abandons their religion "
     "or doctrine"),
    # --- Spanish: Feelings I (400-409) ---
    (400, "anguish",
     "Deep distress and affliction of the soul"),
    (401, "anxiety",
     "Unease or dread before danger or uncertainty"),
    (402, "restlessness",
     "Persistent unease or disquiet"),
    (403, "longing",
     "Sadness for the absence of something or someone "
     "cherished"),
    (404, "rapture",
     "A state of deep ecstasy or admiration"),
    (405, "enchantment",
     "Intense pleasure that captivates and absorbs "
     "attention"),
    (406, "consternation",
     "Dismay and shock caused by something unexpected"),
    (407, "perturbation",
     "An alteration of mood producing confusion or "
     "embarrassment"),
    (408, "disconsolation",
     "Deep grief from the lack of comfort or hope"),
    (409, "affliction",
     "Intense moral pain or suffering of the soul"),
    # --- Spanish: Feelings II (410-419) ---
    (410, "glee",
     "Intense and boisterous joy"),
    (411, "outburst",
     "A sudden, violent impulse of feeling or passion"),
    (412, "nightmare",
     "An agonising dream; an oppressive situation"),
    (413, "chill",
     "A sudden cold sensation caused by fear, fever, "
     "or emotion"),
    (414, "shudder",
     "An involuntary trembling caused by intense "
     "emotion"),
    (415, "awe",
     "Amazement mixed with fear or reverence"),
    (416, "fascination",
     "A state of rapture caused by something beautiful"),
    (417, "entrancement",
     "A suspension of the senses through admiration "
     "or delight"),
    (418, "tribulation",
     "Anguish, grief, or torment afflicting the soul"),
    (419, "heartbreak",
     "A grave loss of health or strength; great "
     "sorrow"),
    # --- Spanish: Conflicts and stratagems (420-429) ---
    (420, "struggle",
     "A fight or clash between people, groups, or "
     "ideas"),
    (421, "strife",
     "A confrontation or dispute between two or more "
     "parties"),
    (422, "skirmish",
     "A brief, minor combat between small forces"),
    (423, "conflagration",
     "A large-scale military conflict; a devastating "
     "fire"),
    (424, "flattery",
     "Exaggerated and usually self-interested praise"),
    (425, "quibble",
     "A subtle and deceitful argument used to "
     "mislead"),
    (426, "ruse",
     "A clever stratagem to achieve an end"),
    (427, "trick",
     "An ingenious manoeuvre to deceive or obtain "
     "something"),
    (428, "wile",
     "A cunning and disguised trap to achieve a "
     "purpose"),
    (429, "stratagem",
     "An astute plan devised to achieve a goal, "
     "especially military"),
    # --- Spanish: Places (430-439) ---
    (430, "pinnacle",
     "The highest or culminating point of something"),
    (431, "zenith",
     "The highest point in the sky; the peak or apex"),
    (432, "nadir",
     "The lowest point; the most unfavourable moment"),
    (433, "moor",
     "A barren, exposed upland plain"),
    (434, "wasteland",
     "Uncultivated, abandoned, and unproductive land"),
    (435, "alcazar",
     "A fortress or fortified palace of Moorish "
     "origin"),
    (436, "watchtower",
     "A raised tower for surveying the surrounding "
     "territory"),
    (437, "redoubt",
     "A last stronghold of resistance or refuge"),
    (438, "bastion",
     "A fortified point of defence; a main support"),
    (439, "citadel",
     "A fortified enclosure within a fortified city"),
    # --- Spanish: Health and remedies (440-449) ---
    (440, "ailment",
     "An illness or indisposition, especially chronic"),
    (441, "suffering",
     "An illness endured over a long time"),
    (442, "convalescence",
     "A period of recovery after illness or surgery"),
    (443, "prostration",
     "A state of extreme physical or moral "
     "exhaustion"),
    (444, "potion",
     "A medicinal drink prepared with herbs or other "
     "substances"),
    (445, "ointment",
     "A greasy medicinal substance applied to the "
     "skin"),
    (446, "balm",
     "An aromatic and healing substance; relief from "
     "pain"),
    (447, "elixir",
     "A marvellous medicinal preparation; an ideal "
     "solution"),
    (448, "antidote",
     "A substance counteracting the effects of a "
     "poison"),
    (449, "poultice",
     "A soft, moist medicinal plaster applied to the "
     "skin"),
    # --- Spanish: Character adjectives I (450-459) ---
    (450, "sagacious",
     "Showing keen judgement and foresight"),
    (451, "tenacious",
     "Holding firmly to one's purposes with great "
     "perseverance"),
    (452, "loquacious",
     "Talking a great deal or with great ease"),
    (453, "magnanimous",
     "Having greatness of spirit and generosity in "
     "forgiving"),
    (454, "benevolent",
     "Having goodwill towards others; kind"),
    (455, "circumspect",
     "Acting with prudence and seriousness, weighing "
     "words carefully"),
    (456, "taciturn",
     "Quiet and silent; of a melancholic temperament"),
    (457, "phlegmatic",
     "Acting with imperturbable calm"),
    (458, "affable",
     "Pleasant, kind, and courteous in manner"),
    (459, "parsimonious",
     "Acting with excessive slowness and calm"),
    # --- Spanish: Character adjectives II (460-469) ---
    (460, "mendacious",
     "Given to lying; false and deceitful"),
    (461, "suspicious",
     "Inclined to distrust everyone and everything"),
    (462, "mordant",
     "Criticising with biting sharpness and sarcasm"),
    (463, "voracious",
     "Eating with excessive greed; consuming "
     "ravenously"),
    (464, "rogue",
     "Cunning, roguish, and ill-intentioned"),
    (465, "crafty",
     "Acting with guile and cunning to deceive"),
    (466, "sly",
     "Cunning and concealing one's true intentions"),
    (467, "wily",
     "Shrewd and astute, especially at deception"),
    (468, "underhand",
     "Maliciously concealing one's feelings or "
     "intentions"),
    (469, "insidious",
     "Laying traps or snares in a covert manner"),
    # --- Spanish: Physical appearance (470-479) ---
    (470, "gaunt",
     "Thin, emaciated, and sickly in appearance"),
    (471, "lean",
     "Thin, dry, and having little flesh"),
    (472, "famished",
     "Extremely hungry; very thin from lack of food"),
    (473, "languid",
     "Showing weakness or lack of vital energy"),
    (474, "haggard",
     "With a face worn by illness, fatigue, or "
     "suffering"),
    (475, "scrawny",
     "Extremely thin, dirty, and unkempt"),
    (476, "austere",
     "Stern-faced, dry, and unfriendly"),
    (477, "sallow",
     "Of a yellowish-green complexion; melancholic"),
    (478, "ruddy",
     "Of a reddish colour, especially of the face"),
    (479, "burly",
     "Of a robust, strong, and stout build"),
    # --- Spanish: Condition adjectives (480-489) ---
    (480, "peremptory",
     "Urgent, conclusive, and admitting no delay"),
    (481, "ill-fated",
     "Of bad omen; bringing misfortune"),
    (482, "disastrous",
     "Causing grief or misfortune; mournful"),
    (483, "inexorable",
     "That cannot be avoided or stopped; implacable"),
    (484, "untimely",
     "Occurring at an inopportune or unsuitable time"),
    (485, "unusual",
     "Not habitual; occurring rarely or surprisingly"),
    (486, "unwonted",
     "Rare, unaccustomed, and out of the ordinary"),
    (487, "primeval",
     "Original, primitive; existing from the "
     "beginning"),
    (488, "atavistic",
     "Stemming from remote ancestors or ancestral "
     "instincts"),
    (489, "customary",
     "Done by custom or established tradition"),
    # --- Spanish: Communication verbs (490-499) ---
    (490, "harangue",
     "To deliver an impassioned speech to rouse "
     "spirits"),
    (491, "argue",
     "To present arguments against something; to "
     "deduce"),
    (492, "rebut",
     "To reject or contradict an argument with "
     "reasons"),
    (493, "refute",
     "To demonstrate the falsity of an argument"),
    (494, "discourse",
     "To expound a topic at length before an "
     "audience"),
    (495, "orate",
     "To deliver a long, often tedious or emphatic "
     "speech"),
    (496, "annotate",
     "To add brief notes or comments to a text"),
    (497, "interpellate",
     "To demand explanations from someone about their "
     "conduct"),
    (498, "murmur",
     "To speak in a very low voice, almost in a "
     "whisper"),
    (499, "vociferate",
     "To shout vehemently or cry out loudly"),
    # --- Spanish: Perception verbs (500-509) ---
    (500, "ponder",
     "To reflect insistently and deeply on something"),
    (501, "ruminate",
     "To think carefully and repeatedly about "
     "something"),
    (502, "scan",
     "To observe attentively to discover something "
     "hidden"),
    (503, "glimpse",
     "To perceive something faintly or confusedly; "
     "to intuit"),
    (504, "espy",
     "To look cautiously and stealthily; to perceive "
     "signs"),
    (505, "scrutinise",
     "To examine with close and careful attention"),
    (506, "survey",
     "To look from a high place to observe the "
     "surroundings"),
    (507, "descry",
     "To catch sight of something in the distance"),
    (508, "conjecture",
     "To form a judgement from incomplete evidence"),
    (509, "suspect",
     "To sense or foresee something from signs or "
     "clues"),
    # --- Spanish: Domination verbs (510-519) ---
    (510, "subjugate",
     "To subdue with violence; to dominate by force"),
    (511, "overpower",
     "To subdue or overwhelm someone, imposing "
     "obedience"),
    (512, "subdue",
     "To make someone yield in will or resistance"),
    (513, "daunt",
     "To make someone retreat through fear"),
    (514, "dishearten",
     "To cause fear or discouragement that paralyses "
     "action"),
    (515, "overwhelm",
     "To crush or bewilder someone, leaving them "
     "speechless"),
    (516, "silence",
     "To make someone or something quiet; to suppress "
     "protest"),
    (517, "coerce",
     "To exert pressure or force on someone to "
     "compel action"),
    (518, "curtail",
     "To limit or restrict someone's freedom or "
     "rights"),
    (519, "constrain",
     "To compel someone to do something; to oppress"),
    # --- Spanish: Movement verbs (520-529) ---
    (520, "wander",
     "To walk without a fixed direction or "
     "destination"),
    (521, "lurk",
     "To loiter around a place with suspicious "
     "intent"),
    (522, "stalk",
     "To watch or spy cautiously with hostile "
     "purpose"),
    (523, "plough",
     "To sail the sea; to cross an open space"),
    (524, "decant",
     "To move things from one place to another; to "
     "drink excessively"),
    (525, "pilgrimage",
     "To travel to a sacred place; to wander"),
    (526, "digress",
     "To stray from the main topic; to think or "
     "speak without order"),
    (527, "slip away",
     "To escape or leave a place stealthily"),
    (528, "retreat",
     "To withdraw in an orderly fashion before an "
     "adversary"),
    (529, "congregate",
     "To gather or assemble in a place"),
    # --- Spanish: Psychology (530-539) ---
    (530, "catharsis",
     "A release of repressed emotions bringing inner "
     "relief"),
    (531, "narcissism",
     "Excessive and unhealthy admiration of oneself"),
    (532, "megalomania",
     "A delusion of grandeur; an exaggerated belief "
     "in one's own power"),
    (533, "paranoia",
     "A disorder marked by extreme distrust and "
     "delusions of persecution"),
    (534, "sublimation",
     "The transformation of instinctive impulses into "
     "socially valued activities"),
    (535, "phobia",
     "An intense and irrational fear of something "
     "specific"),
    (536, "psychosis",
     "A severe mental disorder with loss of contact "
     "with reality"),
    (537, "delirium",
     "A mental disturbance with incoherent ideas and "
     "false perceptions"),
    (538, "hysteria",
     "A state of extreme nervous excitement with "
     "uncontrolled reactions"),
    (539, "hallucination",
     "A false sensory perception without an external "
     "stimulus"),
    # --- Spanish: Sociology and power (540-549) ---
    (540, "anomie",
     "The absence of social norms or breakdown of "
     "moral order"),
    (541, "plutocracy",
     "A system of government where power is held by "
     "the wealthiest"),
    (542, "oligarchy",
     "Government by a small, privileged group"),
    (543, "autocracy",
     "A system where a single person holds absolute "
     "power"),
    (544, "theocracy",
     "Government exercised directly by God or by "
     "priests"),
    (545, "nepotism",
     "Favouritism towards relatives in granting "
     "positions"),
    (546, "bossism",
     "The abusive domination of a local boss over a "
     "community"),
    (547, "clientelism",
     "A political system based on the exchange of "
     "favours for votes"),
    (548, "stratification",
     "The division of society into hierarchical "
     "layers"),
    (549, "endogamy",
     "The practice of marrying within one's own "
     "social group"),
    # --- Spanish: Religion and beliefs (550-559) ---
    (550, "heresy",
     "A doctrine contrary to the dogmas of an "
     "established religion"),
    (551, "schism",
     "A division or split within a church or "
     "community"),
    (552, "blasphemy",
     "An injurious word or expression against God "
     "or the sacred"),
    (553, "sacrilege",
     "The profanation of something considered sacred"),
    (554, "iconoclast",
     "One who rejects or destroys established "
     "traditions or values"),
    (555, "heterodox",
     "Departing from accepted doctrine or norms"),
    (556, "orthodox",
     "Faithfully adhering to established doctrine"),
    (557, "proselytism",
     "The zeal to win followers for a cause or "
     "doctrine"),
    (558, "syncretism",
     "The fusion of elements from different "
     "doctrines or cultures"),
    (559, "pantheism",
     "The doctrine identifying God with the universe "
     "and nature"),
    # --- Spanish: Nature and geography (560-569) ---
    (560, "steppe",
     "A vast, arid plain with sparse herbaceous "
     "vegetation"),
    (561, "gorge",
     "A narrow mountain pass allowing only single-"
     "file passage"),
    (562, "hillock",
     "A gentle depression between two neighbouring "
     "heights"),
    (563, "knoll",
     "An isolated hill commanding a plain"),
    (564, "glen",
     "A narrow, elongated valley between mountains"),
    (565, "meadow",
     "A low, flat, fertile stretch of land by a "
     "river"),
    (566, "hilltop",
     "A low hill or rise"),
    (567, "crag",
     "A large, elevated rock protruding from the "
     "terrain"),
    (568, "cliff",
     "A high, steep, and difficult-to-access rocky "
     "formation"),
    (569, "ravine",
     "A narrow, rugged opening between mountains"),
    # --- Spanish: Economy and finance (570-579) ---
    (570, "treasury",
     "The public funds of a state; government "
     "revenues"),
    (571, "savings",
     "A person's own money or modest capital"),
    (572, "stipend",
     "Remuneration given for a service rendered"),
    (573, "emolument",
     "Supplementary pay received for holding office"),
    (574, "encumbrance",
     "A charge or obligation upon a property or "
     "person"),
    (575, "capital gain",
     "An increase in the value of an asset due to "
     "external causes"),
    (576, "tariff",
     "An official duty on imports or exports"),
    (577, "usury",
     "The charging of excessive interest on a loan"),
    (578, "insolvency",
     "Inability to pay one's debts"),
    (579, "oligopoly",
     "A market dominated by a few sellers"),
    # --- Spanish: Virtues and vices (580-589) ---
    (580, "temperance",
     "Moderation and sobriety in appetites and "
     "pleasures"),
    (581, "magnanimity",
     "Greatness of spirit in undertaking noble deeds "
     "and forgiving"),
    (582, "munificence",
     "Splendid generosity in giving"),
    (583, "continence",
     "The virtue of restraining passions and "
     "appetites"),
    (584, "prodigality",
     "A tendency to spend or give excessively"),
    (585, "pusillanimity",
     "Lack of courage to face difficulties"),
    (586, "concupiscence",
     "A disordered desire for pleasures, especially "
     "carnal"),
    (587, "intemperance",
     "Lack of moderation; excess in appetites"),
    (588, "abjection",
     "A state of extreme moral degradation"),
    (589, "negligence",
     "Carelessness in fulfilling one's obligations"),
]


async def main() -> None:
    db = await Database.connect("data/rembrandt.db")

    # Ensure English language exists
    lang = await db.get_language("en")
    if lang is None:
        await db.add_language("en", "English")
        print("Registered language: English (en)")

    added = 0
    skipped = 0

    for concept_id, en_front, en_back in TRANSLATIONS:
        existing = await db.get_translation(
            concept_id, "en"
        )
        if existing is not None:
            skipped += 1
            continue

        await db.add_translation(
            concept_id, "en",
            front=en_front,
            back=en_back,
        )
        added += 1

    print(
        f"Done: {added} added, {skipped} skipped "
        f"(already exist)"
    )
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
