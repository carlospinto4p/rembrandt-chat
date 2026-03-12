"""Telegram command handlers — re-export facade.

The actual implementations live in:

- `session_handlers` — `/start`, `/play`, `/stop`, `/hint`,
  `/skip`, answer handlers
- `word_handlers` — `/addword`, `/mywords`, `/deleteword`
- `stats_handlers` — `/stats`, `/weak`
"""

from rembrandt_chat.session_handlers import (
    PLAY_MODE_PREFIX,
    handle_answer_callback,
    handle_answer_text,
    handle_lesson_callback,
    handle_play_mode,
    hint,
    lessons,
    play,
    skip,
    start,
    stop,
)
from rembrandt_chat.stats_handlers import (
    AWAITING_FILE,
    export_progress,
    forecast,
    import_cancel,
    import_file,
    import_start,
    retention,
    stats,
    weak,
)
from rembrandt_chat.word_handlers import (
    AWAITING_DEFINITION,
    AWAITING_WORD,
    addword_cancel,
    addword_definition,
    addword_start,
    addword_word,
    deleteword,
    handle_deleteword_callback,
    mywords,
)

__all__ = [
    "PLAY_MODE_PREFIX",
    "start",
    "play",
    "handle_play_mode",
    "lessons",
    "handle_lesson_callback",
    "stop",
    "hint",
    "skip",
    "handle_answer_text",
    "handle_answer_callback",
    "AWAITING_WORD",
    "AWAITING_DEFINITION",
    "addword_start",
    "addword_word",
    "addword_definition",
    "addword_cancel",
    "mywords",
    "deleteword",
    "handle_deleteword_callback",
    "stats",
    "weak",
    "forecast",
    "retention",
    "export_progress",
    "AWAITING_FILE",
    "import_start",
    "import_file",
    "import_cancel",
]
