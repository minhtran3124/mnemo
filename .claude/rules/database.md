---
paths:
  - "**/{store,storage,db,database,repository,repositories,models,schema,migrations}/**"
  - "**/{store,storage,db,database,repository,models,schema}*.py"
  - "**/*.sql"
  - "data/**"
---

# Data and storage rules

## Access
- All reads and writes go through one data-access module. No other code opens data files or the database directly.
- The data-access module exposes a small, named set of functions (add, get, list, update, delete). Callers never build file paths or SQL themselves.
- The storage engine (files, SQLite, Postgres) is a detail of that module. Changing it must not change any caller.

## Integrity
- Validate every record against a schema before writing. Reject invalid records; never write a partially valid one.
- Writes are atomic. For files: write to a temp file in the same directory, `fsync`, then rename over the original. For databases: use a transaction.
- IDs are unique and never reused, even after a delete.
- Store timestamps in UTC, ISO 8601, set by the server, never by the client.
- Use `null` for "unknown" and keep it distinct from an empty string or zero.

## Schema changes
- Version the schema. Every change ships with a migration that upgrades existing data, and the migration is tested on a copy of real data.
- Additive changes first (new optional field), removals later. Never rename a field in one step.
- Never edit a migration that has already run; add a new one.

## Queries and performance
- Use parameterized queries only. Never build SQL with string formatting.
- Add an index for every field used in a frequent filter or lookup. Check the query plan for slow queries.
- Paginate list endpoints. Never load an unbounded table or file into one response.

## Safety
- Back up data before a migration and on a schedule. Test that a backup restores.
- Keep data and backups out of git when they contain user content.
- On a corrupt or unreadable store, stop with a clear error. Do not overwrite it with an empty store.
- Concurrent writers need a lock, a single writer process, or database-level transactions.
