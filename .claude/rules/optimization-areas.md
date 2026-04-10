# Optimization Areas

Project-specific performance areas to watch for when
running `/optimize` or noticing issues during normal work.

## Common Signals

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
