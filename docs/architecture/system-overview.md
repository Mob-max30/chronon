# Chronon System Architecture Overview

## 1. Mission & Philosophy
Chronon is an automated, **deterministic**, constraint-driven academic timetable scheduling platform designed specifically for engineering colleges and universities (with deep first-class support for VTU schemes and autonomous semester frameworks).

Unlike probabilistic or stochastic approaches (or generative AI models which can hallucinate conflicting schedules), Chronon utilizes mathematical constraint programming via **Google OR-Tools CP-SAT** to guarantee 100% clash-free, valid timetables.

## 2. High-Level Architecture

```mermaid
graph TD
    Client["Next.js 14+ Frontend (React / TS / Tailwind)"] -->|REST API| Gateway["FastAPI Backend Layer"]
    
    subgraph Backend Core
        Gateway --> Ingestion["Document Ingestion (OCR / PDF / DOCX)"]
        Gateway --> Academic["Academic Lifecycle & Catalog Service"]
        Gateway --> Resource["Physical Resource & Batching Service"]
        Gateway --> Orchestration["Generation & Versioning Orchestration"]
        
        Orchestration --> Solver["CP-SAT Scheduling Engine (OR-Tools)"]
        Orchestration --> Validator["Independent Constraint Validator"]
    end
    
    Backend Core --> DB[(PostgreSQL Database)]
```

## 3. Core Principles
1. **Zero AI/LLM for Scheduling**: Generation is 100% deterministic constraint satisfaction.
2. **Independent Validator**: Timetable validity is checked by a decoupled validator with zero solver bias.
3. **Physical vs Academic Decoupling**: Academic lab subjects are mapped to physical hardware laboratories.
4. **First-Year Cycle Support**: Dual-stream Physics / Chemistry cycle support with joint optimization capabilities (`generate_joint(sem1, sem2)`).
5. **Strict Data Review**: Ingested OCR data requires explicit user review before persisting.
