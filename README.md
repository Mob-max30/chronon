<div align="center">

# ⏱️ CHRONON
### *Deterministic Academic Timetable Generation & Scheduling System*

[![Branch](https://img.shields.io/badge/integration_branch-dev-blue.svg)](https://github.com/Mob-max30/chronon/tree/dev)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org)
[![Constraint Solver](https://img.shields.io/badge/Solver-Google_OR--Tools_CP--SAT-FF6F00.svg)](https://developers.google.com/optimization)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_16-336791.svg)](https://www.postgresql.org)

<p align="center">
  A high-performance, 100% deterministic constraint-satisfaction platform built to generate clash-free academic schedules for <b>VTU-affiliated engineering colleges</b> and <b>autonomous universities</b>.
</p>

</div>

---

## 📌 Executive Overview

Unlike heuristic or generative AI approaches that suffer from hallucinations and double-booking errors, **Chronon** utilizes mathematical constraint programming via **Google OR-Tools CP-SAT**. It guarantees mathematical proof of feasibility and zero hard-constraint clashes across faculty, classrooms, laboratory hardware, and student batches.

---

## 👥 Team & Parallel Domain Ownership

Chronon is developed by a balanced 4-developer engineering team working across isolated domain boundaries:

| Developer | Branch | Primary Subsystem Ownership |
| :--- | :---: | :--- |
| **Pranav** *(Lead)* | `pranav` | **Academic Lifecycle & Orchestration**: Academic Year switching (Current vs Historical), `GenerationRun` state machine, `TimetableVersion` snapshotting & diffs, system integration. |
| **Ujwal** | `ujwal` | **Curriculum, OCR & Faculty**: VTU syllabus PDF parser, Subject catalogs, First-Year Stream/Cycle Groups (Physics/Chemistry), Faculty document ingestion (PDF/DOCX) & workload limits. |
| **Pruthvik** | `pruthvik` | **CP-SAT Solver & Independent Validator**: OR-Tools mathematical formulation, Hard/Soft constraint modeling, multi-objective optimization, decoupled rule validator, conflict diagnostics. |
| **Nivish** | `nivish` | **Physical Resources & Timetable Grid UI**: Classrooms, Physical Lab Hardware Mappings, Section partitioning, Batching ($C$), Time slots, Interactive Multi-Filter Matrix Grid UI. |

### 🌿 Git Branching Rule
* `dev` is the **sole integration branch**.
* Normal flow: `feature-branch` $\rightarrow$ Push $\rightarrow$ Pull Request $\rightarrow$ `dev` $\rightarrow$ Integration Testing $\rightarrow$ `main`.

---

## 🔄 Core User Workflow

```
Choose Academic Year
        │
        ├── [Old Year] ─────► View / Audit Historical Timetable Versions & Diff
        │
        └── [Current Year] ──► Create New Timetable:
                                  │
                                  ▼
                     Institution Scheme Selection (VTU / Autonomous)
                                  │
                                  ▼
                     Year & Applicable Semesters (Odd / Even / 1st Year P&C Cycle)
                                  │
                                  ▼
                     Branches & Admitted / Eligible Student Counts
                                  │
                                  ▼
                     Curriculum (Theory & Labs) + Faculty Availability (Manual / Ingest)
                                  │
                                  ▼
                     Classrooms + Physical Lab Mappings + Section/Batch Division
                                  │
                                  ▼
                     Time Slot Intervals & Break Structure
                                  │
                                  ▼
                     Deterministic Google OR-Tools CP-SAT Engine
                                  │
                                  ▼
                     Independent Decoupled Constraint Validator
                                  │
                                  ▼
                     Interactive Grid Matrix View, Versioning & Export
```

---

## 🏛️ Key Architectural Guarantees

1. **Zero AI / LLMs in Scheduling**: 100% deterministic mathematical constraint satisfaction. No probabilistic guessing or hallucinated schedules.
2. **Independent Validator**: A completely isolated rule engine verifies every generated or manually modified timetable without solver bias.
3. **Physical vs Academic Lab Decoupling**: Academic lab subjects (e.g. *DSA Lab*, *OS Lab*, *IDEA Lab*) map to physical hardware spaces (e.g. *Computer Science Lab*).
4. **First-Year Cycle Support**: Dual-stream Physics / Chemistry cycle support with joint multi-cohort optimization via `generate_joint(sem1, sem2)`.
5. **Staged OCR Review**: Ingested syllabi and faculty documents are staged for user confirmation before writing to the database catalog.

---

## 🛠️ Technology Stack

- **Frontend**: Next.js 14+ (App Router), React, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, React Hook Form, Zod.
- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic.
- **Solver**: Google OR-Tools CP-SAT.
- **Document Parsing**: Tesseract OCR (with pluggable `OCRProvider` abstraction), PyMuPDF, python-docx.
- **Database**: PostgreSQL 16+.
- **DevOps**: Docker, Docker Compose.

---

## 📂 Repository Structure

```
chronon/
├── frontend/               # Next.js 14 application shell & grid viewer
│   ├── src/app/            # App router pages, layouts & health indicators
│   ├── src/components/     # Navigation shell, timeline & UI components
│   └── src/lib/            # API client & utilities
├── backend/                # FastAPI backend service
│   ├── app/api/            # 10 Domain REST API route modules
│   ├── app/core/           # Settings & environment configuration
│   ├── app/db/             # SQLAlchemy 2.0 database engine & session
│   ├── app/models/         # 20 SQLAlchemy declarative database models
│   ├── app/schemas/        # Pydantic v2 schemas & shared contracts
│   ├── app/scheduling/     # Google OR-Tools CP-SAT solver & generators
│   ├── app/validation/     # Independent decoupled timetable validator
│   ├── app/ingestion/      # Pluggable OCR & document parsing pipeline
│   └── tests/              # Pytest test suite (all passing)
├── docs/                   # Architectural guides, API conventions & ADRs
│   ├── architecture/       # System overview & module boundaries
│   ├── api/                # REST conventions & schema definitions
│   ├── scheduling/         # CP-SAT mathematical model overview
│   └── decisions/          # Architectural Decision Records (ADRs 001-004)
├── docker/                 # Container Dockerfiles (Frontend & Backend)
├── docker-compose.yml      # Local multi-service orchestration
├── .env.example            # Environment variables template
├── CHRONON_FINAL_README.txt# Authoritative comprehensive specification
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Node.js**: v20+ & npm
- **Python**: v3.12+
- **PostgreSQL**: v16+ (or run via Docker)

### 2. Environment Setup
```bash
cp .env.example .env
```

### 3. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API Health Check: `http://localhost:8000/health`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:3000`

### 5. Running with Docker Compose
```bash
docker-compose up --build
```

---

## 📄 Full Specification Reference

For the comprehensive, unabridged product specification, see [CHRONON_FINAL_README.txt](file:///e:/My%20Projects/chronon/CHRONON_FINAL_README.txt).
