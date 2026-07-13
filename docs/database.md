# Database Documentation

## Overview

The application uses **SQLite** as its database engine. The database file (`hiring.db`) is created automatically in the project root directory when the application starts.

## Schema

### Table: `candidates`

This is the only table in the database.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `name` | `TEXT` | PRIMARY KEY | Candidate's full name (case-insensitive matching) |
| `resume_score` | `REAL` | | Resume-JD match score (0–100) |
| `interview_score` | `REAL` | NULLABLE | Final interview score; NULL if not yet interviewed |

### DDL

```sql
CREATE TABLE IF NOT EXISTS candidates (
    name TEXT PRIMARY KEY,
    resume_score REAL,
    interview_score REAL
);
```

## Operations

All database operations are defined in `database.py`.

### `init_db()`

Creates the `candidates` table if it doesn't exist. Called once at application startup.

### `add_candidate(name, resume_score)`

- Strips whitespace from the name.
- Performs a case-insensitive lookup (`LOWER(name)`).
- If the candidate does not exist: inserts a new row with `interview_score = NULL`.
- If the candidate exists: updates only the `resume_score`. The existing `interview_score` is preserved (not reset).

### `update_interview_score(name, interview_score)`

- Strips whitespace from the name.
- Updates the `interview_score` for the matching candidate using case-insensitive matching.
- This is called after the candidate completes all 5 interview questions.

### `get_candidate(name)`

- Returns `(name, resume_score, interview_score)` as a tuple.
- Returns `None` if no matching candidate is found.
- Used by the Candidate Portal to verify login and check if the assessment was already completed.

### `get_all_candidates()`

- Returns all rows: `[(name, resume_score, interview_score), ...]`.
- Used by the Recruiter dashboard to populate KPIs, charts, and lists.

## Data Flow Diagram

```
┌──────────────┐     add_candidate()     ┌──────────────┐
│  Resume      │ ──────────────────────▶  │              │
│  Screening   │                          │   SQLite     │
│  (Recruiter) │                          │  hiring.db   │
└──────────────┘                          │              │
                                          │  candidates  │
┌──────────────┐     update_interview     │  ┌────────┐  │
│  Interview   │     _score()             │  │ name   │  │
│  (Candidate) │ ──────────────────────▶  │  │ resume │  │
└──────────────┘                          │  │ _score │  │
                                          │  │ inter- │  │
┌──────────────┐     get_all_candidates() │  │ view_  │  │
│  Recruiter   │ ◀──────────────────────  │  │ score  │  │
│  Dashboard   │                          │  └────────┘  │
└──────────────┘                          └──────────────┘
```

## Notes

- The database has **no indexes** beyond the implicit PRIMARY KEY index on `name`.
- The `LOWER()` function is used for case-insensitive matching, which prevents index usage on large datasets. For production, consider using `COLLATE NOCASE` or a PostgreSQL migration.
- There is **no migration system**. Schema changes require manual SQL execution or application code changes.
- The database file (`hiring.db`) is listed in `.gitignore` and should not be committed to version control.
