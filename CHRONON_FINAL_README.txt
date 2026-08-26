================================================================================
CHRONON: DETERMINISTIC TIMETABLE GENERATION & ACADEMIC SCHEDULING SYSTEM
================================================================================
AUTHORITATIVE SPECIFICATION & ARCHITECTURAL BLUEPRINT
Version: 1.0.0
Repository: https://github.com/Mob-max30/chronon

================================================================================
1. TEAM & DOMAIN OWNERSHIP (4 DEVELOPERS)
================================================================================

There are exactly FOUR developers on this project. There is NO fifth developer.

1. PRANAV (GitHub: Mob-max30 - Repository Owner)
   - Branch: pranav
   - Primary Ownership:
     * Academic Lifecycle Management (Current Year / Old Year workflows)
     * Timetable Generation Orchestration (GenerationRun, TimetableSession)
     * Timetable Versioning & History Tracking (TimetableVersion)
     * Cross-module Integration & Master State Machine

2. UJWAL
   - Branch: ujwal
   - Primary Ownership:
     * Academic Data Ingestion & VTU Syllabus OCR / Document Parsing
     * Branch & Course Management, Student Admitted / Eligible Counts
     * Streams & First-Year Cycle Groups (Physics / Chemistry Cycles)
     * Subject Catalog (Theory, Labs, Credits, Weekly Hours)
     * Faculty Management & Department Faculty Document Ingestion (PDF/DOCX)

3. PRUTHVIK
   - Branch: pruthvik
   - Primary Ownership:
     * Deterministic Scheduling Engine (Google OR-Tools CP-SAT)
     * SchedulingInput to Solver Formulation
     * Hard Constraints (No faculty overlap, room clash, section clash)
     * Soft Constraints & Multi-objective Optimization (Workload balance, gaps)
     * Independent Timetable Validator (Decoupled from solver)
     * Scheduling Failure Analysis & Infeasibility / Conflict Diagnostics

4. NIVISH
   - Branch: nivish
   - Primary Ownership:
     * Physical Resource Management (Rooms, Capacities, Labs)
     * Physical Lab Mapping (Coinciding academic lab subjects -> Shared physical lab)
     * Section Division & Batch Partitioning (e.g. 60 students/room -> Section -> Batches)
     * Time Slots Configuration (Theory duration, Lab duration, Break slots)
     * Timetable Interactive Viewing UI, Matrix Grids & Multi-dimensional Filters

GIT BRANCHING & INTEGRATION RULES:
- `dev` is the SOLE shared integration branch.
- Standard flow: personal branch (`pranav`, `ujwal`, `pruthvik`, `nivish`) -> Commit -> Push -> PR -> `dev` -> Integration Tests -> `main`.
- Direct feature commits to `main` are strictly prohibited.

================================================================================
2. CORE USER-FACING WORKFLOW & STATE MACHINE
================================================================================

The Chronon user workflow is strictly deterministic and follows this exact sequence:

1. Choose Academic Year
   ├── If Old Year:
   │   └── View / Edit Previous Timetable Versions (Historical audit, diffs, export)
   └── If Current Year:
       └── Create New Timetable:
           ├── Step 1: Select Institution Type
           │   ├── VTU-Affiliated College (Pre-populated VTU Syllabus / Scheme)
           │   └── Autonomous University / Custom Scheme
           ├── Step 2: Choose Year & Applicable Semesters
           │   ├── 1st Year (Special handling: Physics & Chemistry Cycles, Joint Sem 1 & 2)
           │   ├── 2nd Year (Semester III & IV)
           │   ├── 3rd Year (Semester V & VI)
           │   └── 4th Year (Semester VII & VIII)
           │   └── Select Odd / Even Semester where applicable
           ├── Step 3: Branch / Course Selection & Student Counts
           │   ├── Select Branches (e.g. CSE, ECE, ISE, MECH, etc.)
           │   └── Enter Admitted / Eligible Student Count for each course
           ├── Step 4: Academic Curriculum & Faculty Setup
           │   ├── Subjects Offered (Theory: e.g. DSA, EDA, Math; Labs: e.g. OS, IDEA)
           │   └── Faculties Available:
           │       ├── Manual Input
           │       └── Ingestion via PDF / DOCX parsing
           │   └── Faculty-Subject workload mapping
           ├── Step 5: Physical Infrastructure & Section / Batch Partitioning
           │   ├── Classroom Capacity (e.g. 60 students per room) -> Generates required sections
           │   ├── Lab Allocation & Physical Mapping:
           │   │   ├── Fetch lab subjects from curriculum
           │   │   ├── Identify Coinciding Labs (e.g. DSA Lab, OS Lab -> CS Lab Resource)
           │   │   ├── Enter lab quantity and workstation capacity (C)
           │   │   └── Partition section students into batches (B1, B2, B3...) based on C
           │   └── Time Slot Definition:
           │       ├── Theory slot duration (e.g. 50 / 60 mins)
           │       ├── Lab slot duration (e.g. 100 / 120 mins continuous)
           │       └── Working days, tea breaks, lunch intervals
           ├── Step 6: Deterministic Timetable Generation
           │   └── Google OR-Tools CP-SAT Solver Execution
           ├── Step 7: Independent Validation
           │   └── Isolated Rule Engine verifies all constraints without solver bias
           └── Step 8: Versioning, Viewing, Manual Adjustments & Export
               └── Grid View (By Section, Faculty, Room, Lab), Conflict Highlighting, PDF/Excel Export

================================================================================
3. SYSTEM ARCHITECTURE & MODULE BOUNDARIES
================================================================================

Chronon is built as a modular monorepo:

  [ Next.js 14+ Frontend (React, TypeScript, Tailwind CSS, shadcn/ui) ]
                                 │ REST API (JSON)
                                 ▼
       [ FastAPI Backend (Python 3.12, Pydantic v2, SQLAlchemy 2.x) ]
         ├── Ingestion Service (OCR / PDF / DOCX -> Normalized Data)
         ├── Academic Service (Years, Schemes, Branches, Subjects, Faculty)
         ├── Resource Service (Rooms, Labs, Sections, Batches, Time Slots)
         ├── Scheduling Service (OR-Tools CP-SAT Engine)
         ├── Independent Validation Service (Zero solver dependency)
         └── Versioning & Persistence Service
                                 │
                     [ PostgreSQL Database ]

KEY ARCHITECTURAL CONSTRAINTS:
- ZERO AI / LLM IN TIMETABLE GENERATION: Timetable construction is 100% mathematical constraint satisfaction using Google OR-Tools CP-SAT.
- INDEPENDENT VALIDATOR: Validation must be completely decoupled from the solver.
- OCR PROVIDER ABSTRACTION: Ingestion interfaces allow pluggable OCR engines (defaulting to Tesseract). OCR output requires user confirmation before persisting to the DB.
- PHYSICAL VS ACADEMIC LAB DECOUPLING: Academic Lab Subjects (curriculum) are distinct from Physical Lab Resources (hardware).

================================================================================
4. DATABASE SCHEMA SPECIFICATION
================================================================================

The database utilizes SQLAlchemy 2.0 and PostgreSQL:

1. AcademicYear: id, name (e.g. '2026-2027'), is_current (bool), start_date, end_date.
2. Institution: id, name, code, type ('VTU_AFFILIATED' | 'AUTONOMOUS_UNIVERSITY').
3. Scheme: id, institution_id, name (e.g. '2022 Scheme'), year.
4. Branch: id, institution_id, name, code (e.g. 'CSE', 'ECE').
5. Stream: id, branch_id, name, code.
6. Semester: id, scheme_id, number (1-8), term_type ('ODD' | 'EVEN').
7. Subject: id, semester_id, branch_id, code, name, subject_type ('THEORY' | 'LAB' | 'INTEGRATED'), weekly_hours, credits.
8. Faculty: id, institution_id, name, employee_code, email, max_weekly_hours.
9. FacultySubject: id, faculty_id, subject_id, preference_rank, is_primary.
10. Room: id, institution_id, name, building, capacity, is_active.
11. Lab: id, institution_id, name, building, capacity (workstations), lab_type.
12. LabSubjectMapping: id, subject_id, lab_id.
13. Section: id, branch_id, semester_id, name (e.g. 'A', 'B'), student_count, room_id.
14. Batch: id, section_id, name (e.g. 'B1', 'B2', 'B3'), student_count.
15. TimeSlot: id, day_of_week (0-5), period_index, start_time, end_time, slot_type ('THEORY' | 'LAB' | 'BREAK').
16. Timetable: id, academic_year_id, name, status ('DRAFT' | 'PUBLISHED' | 'ARCHIVED').
17. TimetableVersion: id, timetable_id, version_number, is_active, notes.
18. TimetableSession: id, version_id, subject_id, faculty_id, section_id, batch_id, room_id, lab_id, time_slot_id.
19. GenerationRun: id, timetable_id, triggered_by, status ('RUNNING' | 'SUCCESS' | 'FAILED' | 'INFEASIBLE'), solver_time_seconds, conflict_summary.
20. Document: id, file_name, file_type ('PDF' | 'DOCX' | 'IMAGE'), status ('UPLOADED' | 'PARSED' | 'CONFIRMED'), parsed_data.

================================================================================
5. SCHEDULING CONTRACTS & CP-SAT FORMULATION
================================================================================

- Hard Constraints:
  1. Room Clash: No room scheduled for multiple theory sessions at the same time slot.
  2. Faculty Clash: No faculty scheduled for multiple sessions simultaneously.
  3. Section Clash: No section scheduled for multiple theory sessions simultaneously.
  4. Batch Clash: Batches of a single section cannot have lab clashes.
  5. Capacity Constraint: Assigned room/lab capacity >= section/batch student count.
  6. Lab Contiguity: Lab sessions must occupy 2 or 3 contiguous periods.

- First-Year Joint Support:
  - First-year streams alternate Physics and Chemistry cycles between Semesters 1 and 2.
  - Scheduler supports both `generate_single(semester)` and `generate_joint(sem1, sem2)`.

================================================================================
6. VERIFICATION CRITERIA
================================================================================
- Frontend Next.js build passes without TypeScript errors.
- Backend FastAPI starts with `GET /health` returning `{"status": "ok", "service": "chronon-backend"}`.
- Google OR-Tools CP-SAT solves a basic constraint model.
- Alembic database configuration initialized.
- Docker compose services defined.
- Complete CI workflows configured.
================================================================================
