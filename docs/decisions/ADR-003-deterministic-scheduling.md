# ADR-003: Deterministic Constraint Satisfaction vs AI / LLM Generation

## Status
Accepted

## Context
Generative AI and Large Language Models (LLMs) are popular for open-ended text tasks but suffer from hallucinations, stochastic outputs, and an inability to strictly adhere to combinatorial constraints (such as zero double-bookings across hundreds of rooms and faculty).

## Decision
All timetable generation decisions in Chronon are **100% deterministic mathematical constraint programming**. No LLMs or generative AI models are permitted in the scheduling loop.

## Rationale
1. Absolute correctness: Academic institutions cannot tolerate double-booked professors or classrooms.
2. Repeatability & Explainability: Infeasible schedules provide provable conflict sets rather than random errors.
