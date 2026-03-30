"""Internationalisation \u2014 all user-facing strings."""

_STRINGS: dict[str, dict[str, str]] = {
    # ---- general ----
    "welcome": {
        "en": (
            "Welcome, {name}!\n\n"
            "I help you learn vocabulary with spaced "
            "repetition exercises.\n\n"
            "/play \u2014 Start a practice session\n"
            "/addword \u2014 Add your own words\n"
            "/help \u2014 See all commands"
        ),
        "es": (
            "\u00a1Bienvenido, {name}!\n\n"
            "Te ayudo a aprender vocabulario con "
            "ejercicios de repetici\u00f3n espaciada.\n\n"
            "/play \u2014 Iniciar una sesi\u00f3n\n"
            "/addword \u2014 Agregar tus palabras\n"
            "/help \u2014 Ver todos los comandos"
        ),
    },
    "nothing_to_cancel": {
        "en": "Nothing to cancel.",
        "es": "Nada que cancelar.",
    },
    "cancelled": {
        "en": "Cancelled.",
        "es": "Cancelado.",
    },
    "error_generic": {
        "en": (
            "Something went wrong. "
            "Use /cancel to reset, then try again."
        ),
        "es": (
            "Algo sali\u00f3 mal. "
            "Usa /cancel para reiniciar e "
            "intenta de nuevo."
        ),
    },
    "expected_text": {
        "en": "Please send a text message.",
        "es": "Por favor, env\u00eda un mensaje de texto.",
    },
    "expected_file": {
        "en": "Please send a file, not text.",
        "es": "Por favor, env\u00eda un archivo, no texto.",
    },
    "conversation_timeout": {
        "en": "Session timed out. Please start again.",
        "es": (
            "La sesi\u00f3n expir\u00f3. "
            "Por favor, intenta de nuevo."
        ),
    },

    # ---- help ----
    "help": {
        "en": (
            "Available commands:\n\n"
            "Learning:\n"
            "/play \u2014 Start an exercise session\n"
            "/review \u2014 Quick review of last topic\n"
            "/stop \u2014 End session and show summary\n"
            "/hint \u2014 Get a hint\n"
            "/skip \u2014 Skip current exercise\n\n"
            "Words:\n"
            "/addword \u2014 Add a new word\n"
            "/mywords \u2014 List your words\n"
            "/deleteword \u2014 Delete a word\n"
            "/search \u2014 Search vocabulary\n"
            "/bulkimport \u2014 Import from file\n\n"
            "Progress:\n"
            "/stats \u2014 Daily stats\n"
            "/weak \u2014 Weakest words\n"
            "/forecast \u2014 Review workload (7 days)\n"
            "/retention \u2014 Retention rate (30 days)\n"
            "/history \u2014 Recent answers\n\n"
            "Settings:\n"
            "/language \u2014 Set preferred language\n"
            "/topics \u2014 Browse topics\n"
            "/reminders \u2014 Daily reminders\n"
            "/export \u2014 Export progress\n"
            "/import \u2014 Import progress\n"
            "/cancel \u2014 Cancel current operation\n"
            "/help \u2014 Show this message"
        ),
        "es": (
            "Comandos disponibles:\n\n"
            "Aprendizaje:\n"
            "/play \u2014 Iniciar sesi\u00f3n de ejercicios\n"
            "/review \u2014 Repaso r\u00e1pido\n"
            "/stop \u2014 Finalizar sesi\u00f3n\n"
            "/hint \u2014 Obtener una pista\n"
            "/skip \u2014 Saltar ejercicio\n\n"
            "Palabras:\n"
            "/addword \u2014 Agregar una palabra\n"
            "/mywords \u2014 Listar tus palabras\n"
            "/deleteword \u2014 Eliminar una palabra\n"
            "/search \u2014 Buscar vocabulario\n"
            "/bulkimport \u2014 Importar desde archivo\n\n"
            "Progreso:\n"
            "/stats \u2014 Estad\u00edsticas diarias\n"
            "/weak \u2014 Palabras m\u00e1s d\u00e9biles\n"
            "/forecast \u2014 Repasos pendientes (7 d\u00edas)\n"
            "/retention \u2014 Retenci\u00f3n (30 d\u00edas)\n"
            "/history \u2014 Historial de respuestas\n\n"
            "Ajustes:\n"
            "/language \u2014 Idioma preferido\n"
            "/topics \u2014 Explorar temas\n"
            "/reminders \u2014 Recordatorios diarios\n"
            "/export \u2014 Exportar progreso\n"
            "/import \u2014 Importar progreso\n"
            "/cancel \u2014 Cancelar operaci\u00f3n\n"
            "/help \u2014 Mostrar este mensaje"
        ),
    },

    # ---- session ----
    "active_session": {
        "en": (
            "You already have an active session. "
            "Use /stop to end it first."
        ),
        "es": (
            "Ya tienes una sesi\u00f3n activa. "
            "Usa /stop para finalizarla primero."
        ),
    },
    "no_active_session": {
        "en": "No active session.",
        "es": "No hay sesi\u00f3n activa.",
    },
    "no_active_exercise": {
        "en": "No active exercise.",
        "es": "No hay ejercicio activo.",
    },
    "no_previous_topic": {
        "en": (
            "No previous topic found. "
            "Use /play to start a session first."
        ),
        "es": (
            "No se encontr\u00f3 un tema anterior. "
            "Usa /play para iniciar una sesi\u00f3n primero."
        ),
    },
    "no_reviews_due": {
        "en": "No reviews due right now!",
        "es": "\u00a1No hay repasos pendientes!",
    },
    "review_started": {
        "en": "Review session started.",
        "es": "Sesi\u00f3n de repaso iniciada.",
    },
    "session_started": {
        "en": "Session started ({label}).",
        "es": "Sesi\u00f3n iniciada ({label}).",
    },
    "no_words_available": {
        "en": (
            "No words available. "
            "Add words first with /addword."
        ),
        "es": (
            "No hay palabras disponibles. "
            "Agrega palabras primero con /addword."
        ),
    },
    "no_words_in_topic": {
        "en": "No words available in this topic.",
        "es": "No hay palabras disponibles en este tema.",
    },
    "skipped": {
        "en": "Skipped: {front}",
        "es": "Saltado: {front}",
    },

    # ---- selection prompts ----
    "choose_language": {
        "en": "Choose a language:",
        "es": "Elige un idioma:",
    },
    "choose_your_language": {
        "en": "Choose your language:",
        "es": "Elige tu idioma:",
    },
    "choose_category": {
        "en": "Choose a category:",
        "es": "Elige una categor\u00eda:",
    },
    "choose_topic": {
        "en": "Choose a topic:",
        "es": "Elige un tema:",
    },
    "choose_session_mode": {
        "en": "Topic: {topic}\n\nChoose a session mode:",
        "es": "Tema: {topic}\n\nElige un modo de sesi\u00f3n:",
    },
    "language_set": {
        "en": "Language set to {name}.",
        "es": "Idioma establecido: {name}.",
    },
    "category_not_found": {
        "en": "Category not found.",
        "es": "Categor\u00eda no encontrada.",
    },
    "topic_not_found": {
        "en": "Topic not found.",
        "es": "Tema no encontrado.",
    },
    "topics_header": {
        "en": "Topics:",
        "es": "Temas:",
    },
    "no_topics": {
        "en": "No topics available.",
        "es": "No hay temas disponibles.",
    },

    # ---- mode labels ----
    "mode_mixed": {
        "en": "Mixed",
        "es": "Mixto",
    },
    "mode_learn_new": {
        "en": "Learn new",
        "es": "Aprender nuevas",
    },
    "mode_review_due": {
        "en": "Review due",
        "es": "Repasar pendientes",
    },

    # ---- exercise ----
    "mc_prompt": {
        "en": (
            "Which definition matches this word?\n\n"
            "\u201c{front}\u201d"
        ),
        "es": (
            "\u00bfCu\u00e1l definici\u00f3n corresponde "
            "a esta palabra?\n\n"
            "\u201c{front}\u201d"
        ),
    },
    "flashcard_prompt": {
        "en": "Do you know this word?\n\n{front}",
        "es": "\u00bfConoces esta palabra?\n\n{front}",
    },
    "reveal": {
        "en": "Reveal",
        "es": "Revelar",
    },
    "flashcard_reveal": {
        "en": (
            "{front} \u2014 {back}\n\n"
            "How well did you know it?"
        ),
        "es": (
            "{front} \u2014 {back}\n\n"
            "\u00bfQu\u00e9 tan bien la conoc\u00edas?"
        ),
    },
    "example": {
        "en": "\n\nExample: {context}",
        "es": "\n\nEjemplo: {context}",
    },

    # ---- quality labels ----
    "quality_0": {
        "en": "0 - No idea", "es": "0 - Ni idea",
    },
    "quality_1": {
        "en": "1 - Wrong", "es": "1 - Mal",
    },
    "quality_2": {
        "en": "2 - Almost", "es": "2 - Casi",
    },
    "quality_3": {
        "en": "3 - Hard", "es": "3 - Dif\u00edcil",
    },
    "quality_4": {
        "en": "4 - Good", "es": "4 - Bien",
    },
    "quality_5": {
        "en": "5 - Easy", "es": "5 - F\u00e1cil",
    },

    # ---- answer feedback ----
    "correct": {
        "en": "\u2705 Correct! {expected}",
        "es": "\u2705 \u00a1Correcto! {expected}",
    },
    "correct_near_miss": {
        "en": (
            "\u2705 Correct! {expected} "
            "(you typed: {given})"
        ),
        "es": (
            "\u2705 \u00a1Correcto! {expected} "
            "(escribiste: {given})"
        ),
    },
    "wrong": {
        "en": "\u274c Wrong. The answer was: {expected}",
        "es": (
            "\u274c Incorrecto. "
            "La respuesta era: {expected}"
        ),
    },

    # ---- hint ----
    "hint": {
        "en": "Hint: {pattern}",
        "es": "Pista: {pattern}",
    },

    # ---- summary ----
    "session_complete": {
        "en": (
            "Session complete!\n\n"
            "Total: {total}\n"
            "Correct: {correct}\n"
            "Incorrect: {incorrect}\n"
            "Accuracy: {accuracy}%\n"
            "Best streak: {streak}\n\n"
            "Use /play for another session "
            "or /stats to see your progress."
        ),
        "es": (
            "\u00a1Sesi\u00f3n completada!\n\n"
            "Total: {total}\n"
            "Correctas: {correct}\n"
            "Incorrectas: {incorrect}\n"
            "Precisi\u00f3n: {accuracy}%\n"
            "Mejor racha: {streak}\n\n"
            "Usa /play para otra sesi\u00f3n "
            "o /stats para ver tu progreso."
        ),
    },

    # ---- stats ----
    "no_activity": {
        "en": "No activity recorded yet.",
        "es": "No hay actividad registrada a\u00fan.",
    },
    "daily_stats_header": {
        "en": "Daily stats:\n",
        "es": "Estad\u00edsticas diarias:\n",
    },
    "study_streak": {
        "en": "\nStudy streak: {streak} days",
        "es": "\nRacha de estudio: {streak} d\u00edas",
    },
    "no_weak_words": {
        "en": "No weak words found. Keep practising!",
        "es": (
            "\u00a1No se encontraron palabras d\u00e9biles. "
            "Sigue practicando!"
        ),
    },
    "weakest_words_header": {
        "en": "Your weakest words:\n",
        "es": "Tus palabras m\u00e1s d\u00e9biles:\n",
    },
    "errors": {
        "en": "errors",
        "es": "errores",
    },
    "topic_progress_header": {
        "en": "Topic progress:\n",
        "es": "Progreso por tema:\n",
    },

    "stats_hint": {
        "en": (
            "\n\nUse /play to practice "
            "or /weak to review difficult words."
        ),
        "es": (
            "\n\nUsa /play para practicar "
            "o /weak para repasar palabras dif\u00edciles."
        ),
    },

    # ---- retention / forecast / history ----
    "no_answers_yet": {
        "en": (
            "No answers recorded yet. "
            "Start a session with /play!"
        ),
        "es": (
            "No hay respuestas registradas a\u00fan. "
            "\u00a1Inicia una sesi\u00f3n con /play!"
        ),
    },
    "retention_rate": {
        "en": "Retention rate (last 30 days): {rate}%",
        "es": (
            "Tasa de retenci\u00f3n "
            "(\u00faltimos 30 d\u00edas): {rate}%"
        ),
    },
    "no_reviews_scheduled": {
        "en": (
            "No reviews scheduled. "
            "Add words to get started!"
        ),
        "es": (
            "No hay repasos programados. "
            "\u00a1Agrega palabras para comenzar!"
        ),
    },
    "upcoming_reviews_header": {
        "en": "Upcoming reviews:\n",
        "es": "Pr\u00f3ximos repasos:\n",
    },
    "forecast_line": {
        "en": "{date}: {count} cards due",
        "es": "{date}: {count} tarjetas pendientes",
    },
    "no_history": {
        "en": (
            "No answer history yet. "
            "Start a session with /play!"
        ),
        "es": (
            "No hay historial de respuestas a\u00fan. "
            "\u00a1Inicia una sesi\u00f3n con /play!"
        ),
    },
    "recent_answers_header": {
        "en": "Recent answers:\n",
        "es": "Respuestas recientes:\n",
    },

    # ---- word management ----
    "send_word": {
        "en": "Send the word (/cancel to abort):",
        "es": "Env\u00eda la palabra (/cancel para salir):",
    },
    "send_definition": {
        "en": "Send the definition (/cancel to abort):",
        "es": (
            "Env\u00eda la definici\u00f3n "
            "(/cancel para salir):"
        ),
    },
    "word_empty": {
        "en": (
            "Word or definition was empty. "
            "Try /addword again."
        ),
        "es": (
            "La palabra o definici\u00f3n estaba vac\u00eda. "
            "Intenta /addword de nuevo."
        ),
    },
    "send_tags": {
        "en": (
            "Send tags (comma-separated), "
            "/skip, or /cancel:"
        ),
        "es": (
            "Env\u00eda etiquetas "
            "(separadas por coma), "
            "/skip o /cancel:"
        ),
    },
    "word_added": {
        "en": 'Added "{front}" \u2014 {back}',
        "es": 'Agregada "{front}" \u2014 {back}',
    },
    "word_added_tags": {
        "en": (
            'Added "{front}" \u2014 {back}\n'
            'Tags: {tags}'
        ),
        "es": (
            'Agregada "{front}" \u2014 {back}\n'
            'Etiquetas: {tags}'
        ),
    },
    "bulkimport_prompt": {
        "en": (
            "Send a file with words to import "
            "(/cancel to abort).\n\n"
            "Supported formats:\n\n"
            "CSV:\n"
            "apple,manzana\n"
            "book,libro,nouns\n\n"
            "Text:\n"
            "apple \u2014 manzana\n"
            "book \u2014 libro"
        ),
        "es": (
            "Env\u00eda un archivo con palabras "
            "para importar "
            "(/cancel para salir).\n\n"
            "Formatos soportados:\n\n"
            "CSV:\n"
            "apple,manzana\n"
            "book,libro,sustantivos\n\n"
            "Texto:\n"
            "apple \u2014 manzana\n"
            "book \u2014 libro"
        ),
    },
    "send_file": {
        "en": "Please send a file.",
        "es": "Por favor env\u00eda un archivo.",
    },
    "file_read_error": {
        "en": (
            "Could not read the file. "
            "Please send a UTF-8 text file."
        ),
        "es": (
            "No se pudo leer el archivo. "
            "Por favor env\u00eda un archivo de texto UTF-8."
        ),
    },
    "no_valid_words": {
        "en": "No valid words found in the file.",
        "es": (
            "No se encontraron palabras v\u00e1lidas "
            "en el archivo."
        ),
    },
    "imported_words": {
        "en": "Imported {count} words.",
        "es": "{count} palabras importadas.",
    },
    "no_words_with_tag": {
        "en": 'No words with tag "{tag}".',
        "es": (
            'No hay palabras con '
            'la etiqueta "{tag}".'
        ),
    },
    "no_private_words": {
        "en": (
            "You have no private words yet. "
            "Use /addword to add one."
        ),
        "es": (
            "A\u00fan no tienes palabras propias. "
            "Usa /addword para agregar una."
        ),
    },
    "search_usage": {
        "en": "Usage: /search <term>",
        "es": "Uso: /search <t\u00e9rmino>",
    },
    "search_no_results": {
        "en": 'No results for "{term}".',
        "es": 'No hay resultados para "{term}".',
    },
    "search_results_header": {
        "en": 'Results for "{term}" ({count}):\n\n',
        "es": (
            'Resultados para "{term}" '
            '({count}):\n\n'
        ),
    },
    "no_words_to_delete": {
        "en": "You have no private words to delete.",
        "es": (
            "No tienes palabras propias "
            "para eliminar."
        ),
    },
    "tap_to_delete": {
        "en": "Tap a word to delete it:",
        "es": "Toca una palabra para eliminarla:",
    },
    "confirm_delete": {
        "en": "Delete \u201c{word}\u201d?",
        "es": "\u00bfEliminar \u201c{word}\u201d?",
    },
    "yes_delete": {
        "en": "Yes, delete",
        "es": "S\u00ed, eliminar",
    },
    "no_keep": {
        "en": "No",
        "es": "No",
    },
    "word_deleted": {
        "en": "Word deleted.",
        "es": "Palabra eliminada.",
    },
    "deletion_cancelled": {
        "en": "Deletion cancelled.",
        "es": "Eliminaci\u00f3n cancelada.",
    },

    # ---- export / import ----
    "no_progress_to_export": {
        "en": (
            "No progress to export yet. "
            "Start a session with /play!"
        ),
        "es": (
            "No hay progreso para exportar a\u00fan. "
            "\u00a1Inicia una sesi\u00f3n con /play!"
        ),
    },
    "exported_cards": {
        "en": "Exported {count} cards.",
        "es": "{count} tarjetas exportadas.",
    },
    "import_prompt": {
        "en": (
            "Send the JSON file exported "
            "with /export (/cancel to abort)."
        ),
        "es": (
            "Env\u00eda el archivo JSON exportado "
            "con /export (/cancel para salir)."
        ),
    },
    "send_json_file": {
        "en": "Please send a JSON file.",
        "es": (
            "Por favor env\u00eda un archivo JSON."
        ),
    },
    "json_read_error": {
        "en": (
            "Could not read the file. "
            "Please send a valid JSON file."
        ),
        "es": (
            "No se pudo leer el archivo. "
            "Por favor env\u00eda un archivo JSON "
            "v\u00e1lido."
        ),
    },
    "json_invalid_format": {
        "en": "Invalid format: expected a JSON array.",
        "es": (
            "Formato inv\u00e1lido: "
            "se esperaba un array JSON."
        ),
    },
    "imported_cards": {
        "en": "Imported {count} cards successfully.",
        "es": (
            "{count} tarjetas importadas "
            "exitosamente."
        ),
    },

    # ---- reminders ----
    "reminder_due": {
        "en": (
            "You have {due} reviews due today! "
            "Use /play to start."
        ),
        "es": (
            "\u00a1Tienes {due} repasos "
            "pendientes hoy! "
            "Usa /play para comenzar."
        ),
    },
    "reminders_disabled": {
        "en": "Daily reminders disabled.",
        "es": "Recordatorios diarios desactivados.",
    },
    "reminders_on": {
        "en": (
            "Reminders are ON.\n"
            "Use /reminders off to disable."
        ),
        "es": (
            "Los recordatorios est\u00e1n activados.\n"
            "Usa /reminders off para desactivar."
        ),
    },
    "reminders_off": {
        "en": (
            "Reminders are OFF.\n"
            "Use /reminders on [HH:MM] to enable "
            "(default 09:00 UTC)."
        ),
        "es": (
            "Los recordatorios est\u00e1n "
            "desactivados.\n"
            "Usa /reminders on [HH:MM] para activar "
            "(por defecto 09:00 UTC)."
        ),
    },
    "reminders_enabled": {
        "en": (
            "Daily reminders enabled "
            "at {time} UTC."
        ),
        "es": (
            "Recordatorios diarios activados "
            "a las {time} UTC."
        ),
    },

    # ---- pagination ----
    "back": {
        "en": "\u25c0 Back",
        "es": "\u25c0 Volver",
    },
    "cancel_btn": {
        "en": "Cancel",
        "es": "Cancelar",
    },
    "prev": {
        "en": "\u25c0 Previous",
        "es": "\u25c0 Anterior",
    },
    "next": {
        "en": "Next \u25b6",
        "es": "Siguiente \u25b6",
    },
}


def t(
    key: str,
    lang: str | None = None,
    **kwargs: object,
) -> str:
    """Look up a translated string.

    :param key: Translation key.
    :param lang: Language code (``"en"`` or ``"es"``).
        Defaults to English when ``None``.
    :param kwargs: Format parameters interpolated into the
        string via `str.format()`.
    :return: The translated, formatted string.
    """
    entry = _STRINGS.get(key, {})
    code = "es" if lang == "es" else "en"
    text = entry.get(code, entry.get("en", key))
    if kwargs:
        text = text.format(**kwargs)
    return text
