# ADR-002: Use of Google OR-Tools CP-SAT Solver

## Status
Accepted

## Context
Academic timetable generation is an NP-hard combinatorial problem requiring strict satisfaction of physical and organizational constraints along with weighted soft-preference optimization.

## Decision
We select **Google OR-Tools CP-SAT** (Constraint Programming - Satisfiability) as the core scheduling engine.

## Rationale
1. High performance, native multi-threaded search.
2. Formulates exact boolean and integer constraints cleanly.
3. Supports soft-constraint objective penalties and provable optimal/feasible solutions.
4. Robust Python bindings with zero cloud/vendor lock-in.
