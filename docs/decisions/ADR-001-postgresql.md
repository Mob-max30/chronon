# ADR-001: Selection of PostgreSQL as Primary Database

## Status
Accepted

## Context
Chronon manages relational academic structures: Institutions, Schemes, Semesters, Branches, Subjects, Faculty, Rooms, Labs, Sections, Batches, TimeSlots, and Timetable Versions.

## Decision
We choose **PostgreSQL** with SQLAlchemy 2.x (asyncpg) and Alembic migrations.

## Rationale
1. Strong relational integrity, foreign key cascading, and strict typing.
2. JSONB support for OCR document extraction staging and flexible configuration parameters.
3. Proven reliability, standard ACID compliance, and compatibility with enterprise academic systems.
