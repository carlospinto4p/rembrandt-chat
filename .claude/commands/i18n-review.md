Audit every user-facing string in `src/rembrandt_chat/i18n.py`
for linguistic quality in both English and Spanish. Read the
entire file and check each translation for:

## Grammar and punctuation

- Correct use of Spanish punctuation marks (paired inverted
  marks: `¡...!`, `¿...?` — each must wrap only its own
  clause, not span multiple sentences)
- Consistent comma usage (e.g., comma after "Por favor," and
  "Sin embargo,")
- Correct verb tense (present for current state, not past)
- Subject-verb agreement and gender/number agreement

## Natural phrasing

- Awkward calques from English (e.g., "exitosamente" →
  "correctamente", "corresponde a" → "es la ... de")
- Overly literal translations that a native speaker wouldn't
  say
- Register consistency (the bot uses informal "tú" — verify
  all imperatives and possessives match)

## Consistency across strings

- Same concept translated the same way everywhere (e.g.,
  "abort" always as "cancelar" or always as "salir", not
  mixed)
- Parallel structure between English and Spanish (if English
  uses a verb, Spanish should too)
- Consistent punctuation style (periods, exclamation marks)

## What to fix immediately

- Clear grammatical errors
- Misplaced or missing punctuation marks
- Anglicisms with obvious natural alternatives

## What to flag but not fix

- Style preferences that are debatable — present them as
  suggestions and let the user decide

Present findings as a numbered list sorted by severity.
Fix clear errors directly, then commit following the workflow
in `.claude/rules/committing.md`.
