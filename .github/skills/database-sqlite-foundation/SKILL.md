---
name: database-sqlite-foundation
description: 'Create a production-sensible SQLite foundation for FastAPI projects with SQLAlchemy, migrations, test DB isolation, and operational safeguards.'
argument-hint: 'Optional focus such as schema design, migrations, or test database setup'
user-invocable: true
---

# Database SQLite Foundation

Use this skill when you need to implement SQLite correctly in a FastAPI codebase and avoid common anti-patterns.

This skill is optimized for BuildAThon speed while preserving upgrade paths to PostgreSQL.

## Outcomes

By the end of this skill, you should have:

1. SQLAlchemy engine/session wiring
2. ORM models with clear keys and indexes
3. Alembic migrations initialized and first revision created
4. Deterministic local and test database behavior
5. A safe path to future Postgres migration

## Recommended Stack

- SQLAlchemy 2.x ORM
- Alembic for migrations
- SQLite for local/dev and optionally tests
- FastAPI dependency-injected DB session

## SQLite Design Rules

1. Keep schema explicit and normalized
- Use stable primary keys
- Add foreign keys for relationships
- Add indexes on query/filter columns

2. Treat SQLite as relational, not key-value
- Do not store core entities in serialized blobs
- Avoid ad-hoc JSON payload persistence for transactional rows

3. Use UTC timestamps
- Store timezone-aware UTC datetimes
- Convert for display at API/UI boundary

4. Keep business logic out of ORM models
- Place behavior in repositories/services
- Keep models focused on schema

## Engine and Session Best Practices

Use one engine per process and one session per request.

SQLite engine guidance:

- For file DB: `sqlite:///./app.db`
- For test DB file: `sqlite:///./test.db`
- For in-memory tests with shared connection: use `StaticPool`
- Set `connect_args={"check_same_thread": False}` when using FastAPI

Minimal pattern:

```python
engine = create_engine(url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Schema and Migration Workflow (Alembic)

1. Initialize Alembic once in backend root
- `alembic init alembic`

2. Configure Alembic URL
- Read from `DATABASE_URL`
- Ensure local default is SQLite file

3. Point Alembic metadata at SQLAlchemy Base
- `target_metadata = Base.metadata`

4. Create first migration
- `alembic revision --autogenerate -m "initial schema"`

5. Apply migration
- `alembic upgrade head`

6. Commit both model changes and migration files together

## Repository Pattern Guidance

For each aggregate (employee, shift, leave), add repository functions for:

1. Create
2. Query by identity
3. Query list with filters and limit
4. Update state transitions

Rules:

- Validate input before write
- Keep transactions small
- Use explicit commits where state changes occur

## FastAPI Integration Guidance

1. Inject DB session via dependency in endpoints
2. Use repository/service layer for reads/writes
3. Return dict/DTO payloads, not raw ORM objects
4. Raise explicit HTTP errors for validation and missing records

## Test Database Best Practices

1. Use dedicated test DB URL
- Example: `sqlite:///./test.db`

2. Recreate schema per test session
- Apply migrations or create/drop metadata

3. Isolate test state per test
- Transaction rollback fixture or table cleanup fixture

4. Seed deterministic fixtures
- Seed required employees/reference rows in fixture setup

5. Avoid mutating module-level globals
- Tests should not rely on in-memory app state

## SQLite Operational Best Practices

1. Enable WAL mode for concurrent local reads when useful
- `PRAGMA journal_mode=WAL;`

2. Set foreign key enforcement on
- `PRAGMA foreign_keys=ON;`

3. Backup strategy
- For demo/dev, snapshot the SQLite file before destructive migration work

4. Keep DB file path explicit
- Use env var `DATABASE_URL`
- Do not hide DB under temp dirs unless intentional

## Migration Hygiene

1. One logical change per migration
2. Name revisions clearly
3. Never edit applied migration history in shared branches
4. Add downgrade steps when feasible

## Common Mistakes To Avoid

1. Creating tables at runtime without migrations for non-test environments
2. Mixing autogenerate and manual schema edits without review
3. Reusing one long-lived session across requests
4. Returning ORM entities directly from API
5. Writing tests that patch internals instead of using DB fixtures

## Upgrade Path To PostgreSQL

Design now so DB switch is easy later:

1. Avoid SQLite-only SQL in business logic
2. Keep timestamps/timezone handling consistent
3. Use Alembic migrations from day one
4. Isolate DB URL/config in one place

Then migration is mainly:

1. Change `DATABASE_URL`
2. Apply migrations
3. Run test suite

## Definition Of Done

SQLite foundation is complete when:

1. App starts with DB-backed endpoints
2. `alembic upgrade head` succeeds
3. Tests run against DB-backed state
4. No core workflow depends on module-level in-memory stores
5. Roadmap/traceability references DB-backed implementation evidence
