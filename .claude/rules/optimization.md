# Periodic Optimization

Proactively suggest performance optimization opportunities in the
following situations:

## When to Suggest

1. **Every 6-7 versions released**: Same cadence as `/refactor` —
   suggest an optimization pass alongside refactoring reviews.

2. **During long sessions**: When a session involves multiple features
   or changes across several files, suggest optimizations before
   wrapping up.

3. **When noticing performance issues**: If you spot any of the
   following while working, flag them:
   - Unbounded data structures (session dicts, caches that grow
     without limit)
   - Slow Telegram API patterns (unnecessary message edits, missing
     batching)
   - Unnecessary database queries per message

## What to Look For

- **Memory**: unbounded session/user caches, large object retention,
  missing cleanup on session end or user inactivity
- **I/O**: redundant database queries per exercise cycle, missing
  connection pooling, unnecessary Telegram API calls
- **Concurrency**: blocking calls in async handlers, missing
  `asyncio` patterns, handler contention
- **Data structures**: inefficient lookups in user/session mappings,
  repeated serialization

## How to Suggest

- Present findings as a prioritized list with file, line, and rationale
- Classify impact as HIGH / MEDIUM / LOW
- Don't auto-apply — always propose and let the user decide
- Group related findings (e.g., "DB query batching", "session cleanup")
- After each optimization proposal, add the items to `backlog.md`
  under a new section with the current date as the title (see
  `.claude/rules/backlog.md` for format)
