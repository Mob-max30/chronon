# Chronon

> **Deterministic Academic Timetable Generation & Scheduling System**

Chronon is a modern, high-performance, deterministic constraint-satisfaction platform built to generate 100% clash-free academic timetables for VTU-affiliated colleges and universities.

---

## 👥 Core Team & Domain Ownership

| Developer | Branch | Primary Ownership Area |
| :--- | :--- | :--- |
| **Pranav** (*Lead / Owner*) | `pranav` | Academic Lifecycle, Orchestration (`GenerationRun`, `TimetableSession`), Versioning (`TimetableVersion`), Master State Machine |
| **Ujwal** | `ujwal` | VTU Syllabus OCR, Academic Catalog, Branch/Student Counts, Streams & Cycles, Faculty Management & Doc Ingestion |
| **Pruthvik** | `pruthvik` | OR-Tools CP-SAT Solver, Constraint Formulation, Optimization, Independent Validator, Conflict Diagnostics |
| **Nivish** | `nivish` | Rooms, Labs, Physical Lab Mappings, Section Partitioning, Batching, Time Slots, Matrix Grid Viewer UI |

---

## 🛠️ Technology Stack

- **Frontend**: Next.js 14+ (App Router), React, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, React Hook Form, Zod.
- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (asyncpg), Alembic.
- **Scheduling**: Google OR-Tools CP-SAT (100% Deterministic, No LLMs).
- **Document Ingestion**: Tesseract OCR, PyMuPDF, python-docx (with pluggable `OCRProvider`).
- **Database**: PostgreSQL 16+.
- **DevOps**: Docker, Docker Compose, GitHub Actions CI.

---

## 🔄 Chronon Workflow

```
Choose Academic Year
        ↓
Current Year / Old Year
        ├── Old Year ──> View / Edit Previous Timetable Versions
        └── Current Year:
                 ↓
      VTU-Affiliated / University Scheme
                 ↓
      Choose Year & Applicable Semesters (Odd / Even, 1st Year P/C Cycle)
                 ↓
      Branch / Course Selection & Student Counts
                 ↓
      Curriculum (Theory & Lab Subjects) & Faculty Availability (Manual / Ingestion)
                 ↓
      Rooms, Physical Labs, Section Partitioning & Batch Generation
                 ↓
      Time Slot Matrix & Duration Definition
                 ↓
      Deterministic CP-SAT Timetable Generation
                 ↓
      Independent Constraint Validation
                 ↓
      Timetable Grid Matrix, Versioning & Export
```

---

## 🚀 Quickstart (Local Development)

### 1. Prerequisites
- Node.js 20+ & npm
- Python 3.12+
- Docker & Docker Compose (Optional for containerized run)
- PostgreSQL 16+

### 2. Setup Environment
```bash
cp .env.example .env
```

### 3. Running with Docker Compose
```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API & Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 4. Running Backend Directly
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 5. Running Frontend Directly
```bash
cd frontend
npm install
npm run dev
```

---

## 📖 Specifications & Architectural Documentation

For full architectural blueprints, see:
- [CHRONON_FINAL_README.txt](file:///e:/My%20Projects/chronon/CHRONON_FINAL_README.txt) - Authoritative Specification
- [docs/architecture/system-overview.md](file:///e:/My%20Projects/chronon/docs/architecture/system-overview.md)
- [docs/architecture/module-boundaries.md](file:///e:/My%20Projects/chronon/docs/architecture/module-boundaries.md)
- [docs/api/api-conventions.md](file:///e:/My%20Projects/chronon/docs/api/api-conventions.md)
- [docs/scheduling/scheduling-overview.md](file:///e:/My%20Projects/chronon/docs/scheduling/scheduling-overview.md)
