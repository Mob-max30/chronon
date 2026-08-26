# ADR-004: Independent Validator Architecture

## Status
Accepted

## Context
When a solver outputs a timetable or when an administrator manually edits a timetable grid, the timetable must be thoroughly checked for hard and soft constraint violations without relying on the solver's internal state.

## Decision
Create an **Independent Timetable Validator** (`app.validation`) that is completely isolated from Google OR-Tools.

## Rationale
1. Verifies manually edited timetable grids via the same unified rule engine.
2. Acts as a double-check against formulation bugs in the CP-SAT solver.
3. Provides structured diagnostic reports (`ValidationError`, `ValidationResult`) directly to the frontend.
