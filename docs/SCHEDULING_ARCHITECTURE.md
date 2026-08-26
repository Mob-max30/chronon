# Chronon Deterministic Scheduling & Independent Validation Architecture
**Domain Ownership:** PRUTHVIK (Branch: `pruthvik`)

---

## Architecture Overview

```
                      +-----------------------------+
                      |       SchedulingInput       |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |     ChrononCPSATSolver      |
                      |   (Google OR-Tools CP-SAT)  |
                      +-----------------------------+
                                     |
             +-----------------------+-----------------------+
             |                                               |
             v                                               v
+-------------------------+                     +-------------------------+
|   Hard Constraints      |                     |    Soft Objectives      |
|  - Faculty/Room Clash   |                     |  - Distribute Subj Days |
|  - Section/Lab Clash    |                     |  - Minimize Idle Gaps   |
|  - Room/Lab Capacity    |                     |  - Balance Workload     |
|  - Faculty Eligibility  |                     +-------------------------+
|  - Required Hours       |                                  |
+-------------------------+                                  |
             |                                               |
             +-----------------------+-----------------------+
                                     |
                                     v
                      +-----------------------------+
                      |     Candidate Timetable     |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Independent Validator    |
                      | (Zero Solver Bias Engine)   |
                      +-----------------------------+
                                     |
             +-----------------------+-----------------------+
             |                                               |
             v                                               v
+-------------------------+                     +-------------------------+
|   Validation Result     |                     |      Quality Score      |
|   - Hard Violations     |                     |  - Overall Score        |
|   - Structured Errors   |                     |  - Gap/Dist Breakdowns  |
+-------------------------+                     +-------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |      SchedulingResult       |
                      +-----------------------------+
```

---

## Key Modules & Contracts

### 1. `SchedulingInput`
Immutable contract payload provided to the solver containing:
- `rooms`: Room capacities, availability, building information.
- `labs`: Physical lab capacities (workstations) and availability.
- `sections`: Student counts, branch, semester, assigned rooms.
- `batches`: Sub-partitioned section student groups for labs.
- `time_slots`: Configured theory/lab slots per day of week & period index.
- `subjects`: Theory/lab type, required weekly hours, eligible faculty IDs.
- `faculty_availability`: Unavailability slot constraints.
- `objective_weights`: Configurable weights for soft objectives.

### 2. Decision Variables
- Theory Variables: `(subject_id, faculty_id, section_id, room_id, slot_id) -> BoolVar`
- Lab Variables: `(subject_id, faculty_id, section_id, batch_id, lab_id, slot_id) -> BoolVar`

### 3. Hard Constraints
1. **Faculty Clash**: No faculty member scheduled for > 1 session at the same slot.
2. **Section Clash**: No section scheduled for > 1 theory session at the same slot.
3. **Room Clash**: No room scheduled for > 1 session at the same slot.
4. **Lab Clash**: No physical lab scheduled for > 1 batch session at the same slot.
5. **Room/Lab Capacity**: Assigned room/lab capacity >= section/batch student count.
6. **Faculty Eligibility**: Faculty taught must be in `eligible_faculty_ids`.
7. **Resource Availability**: Disabled rooms/labs/faculty unavailable slots excluded.
8. **Required Weekly Hours**: Sum of scheduled sessions == `subject.weekly_hours`.

### 4. Soft Objectives
- **Distribute Subject Days**: Minimize scheduling the same subject multiple times on the same day for a section.
- **Minimize Student Gaps**: Minimize idle periods between scheduled classes on a day for students.
- **Minimize Faculty Gaps**: Minimize idle periods between classes for faculty.
- **Balance Daily Workload**: Equalize class counts across working days.

### 5. Independent Validator
Decoupled rule engine (`IndependentTimetableValidator`) that evaluates candidate timetables without solver bias:
- Accepts solver-generated timetables or manual timetables.
- Performs standalone validation checks for clashes, capacity, eligibility, and weekly hours.
- Produces machine-readable `ValidationResult` with `ValidationError` list.

### 6. Conflict Diagnostics & Infeasibility
- Exposes structured error codes: `FACULTY_CLASH`, `ROOM_CLASH`, `SECTION_CLASH`, `LAB_CLASH`, `ROOM_CAPACITY`, `LAB_CAPACITY`, `FACULTY_INELIGIBLE`, `RESOURCE_UNAVAILABLE`, `MISSING_SESSION`.
- Handles solver statuses gracefully: `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `TIMEOUT`, `FAILED`.

---

## How to Run Standalone Demo & Test Suite

### Running Standalone Demo
```bash
python -m app.scheduling.demo
```

### Running Test Suite
```bash
python -m pytest
```
