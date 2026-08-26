# Generation Orchestration Architecture

## 1. Role & Architectural Boundaries
The **Generation Orchestration Layer** (owned by Pranav) coordinates the complete scheduling execution pipeline. It acts as the bridge connecting:
- Academic Curriculum & Ingestion Data (Ujwal)
- Physical Resources, Rooms, Labs, Sections & Time Slots (Nivish)
- Mathematical CP-SAT Solver & Independent Validator (Pruthvik)
- Timetable Versioning & History Storage (Pranav)

---

## 2. End-to-End Generation Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Request (Year, Semester, Joint 1st Year Flag, Limit)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Create GenerationRun in DB (State: QUEUED)               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Pipeline Service: Assemble Normalized SchedulingInput    │
│    (State: Transitions to RUNNING)                          │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            │                                     │
   [1st Year Joint pass]                [2nd-4th Year pass]
            │                                     │
            ▼                                     ▼
   generate_joint(sem1, sem2)             generate_single(sem)
            │                                     │
            └──────────────────┬──────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. OR-Tools CP-SAT Solver Execution                         │
│    -> Returns Candidate Timetable + Status (OPTIMAL/FEASIBLE)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Independent Validator Verification                        │
│    - Faculty Collision Checks                                │
│    - Section / Batch Collision Checks                        │
│    - Physical Lab & Room Capacity Checks                     │
│    - Paired-Slot Constraint Verification (1st Year)          │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
     [Validation PASS]                     [Validation FAIL]
            │                                     │
            ▼                                     ▼
┌──────────────────────────────┐       ┌──────────────────────┐
│ 6. Persist TimetableVersion  │       │ GenerationStatus =   │
│    Snapshot + Sessions       │       │ FAILED / INFEASIBLE  │
│    GenerationStatus = SUCCESS│       │ Store Conflict Errors│
└──────────────────────────────┘       └──────────────────────┘
```

---

## 3. Joint vs Single Semester Routing
- **2nd, 3rd, 4th Year**: Evaluated one semester at a time (`generate_single(semester)`).
- **1st Year**: Evaluated jointly across Semester 1 and Semester 2 (`generate_joint(sem1, sem2)`).
  This is required because Physics and Chemistry cycle groups mirror their subject allocations across semesters and share constrained laboratory facilities (e.g., Physics Lab, Chemistry Lab, CAED Lab).
