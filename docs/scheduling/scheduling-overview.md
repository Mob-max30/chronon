# Scheduling Module Overview (Google OR-Tools CP-SAT)

## 1. Problem Formulation
Academic timetable scheduling is modeled as a Constraint Satisfaction Problem (CSP) / Integer Programming Problem solved with **Google OR-Tools CP-SAT**.

### Variables
Let boolean decision variable:
$$X(s, f, r, l, b, t) \in \{0, 1\}$$
indicate whether subject $s$ taught by faculty $f$ in room $r$ (or lab $l$) for section/batch $b$ is scheduled at time slot $t$.

## 2. Hard Constraints (Must NEVER be violated)
1. **No Faculty Clash**: A faculty member can conduct at most 1 session in any given time slot $t$.
2. **No Room Clash**: A physical classroom can host at most 1 session at time slot $t$.
3. **No Section Clash**: A section can attend at most 1 theory session at time slot $t$.
4. **No Batch Conflict**: Sub-batches of a section cannot be assigned to overlapping lab resources simultaneously unless co-scheduled in separate physical labs.
5. **Capacity Satisfaction**: Classroom capacity $\ge$ Section student count; Lab capacity $\ge$ Batch student count.
6. **Contiguous Lab Slots**: Lab practicals requiring 2 or 3 hours must be placed in consecutive periods on the same day without intermission breaks.

## 3. Soft Constraints & Multi-Objective Cost Function
1. **Daily Workload Distribution**: Avoid clustering all difficult subjects on a single day.
2. **Faculty Idle Gap Minimization**: Minimize unnecessary free gap hours for teaching staff.
3. **Subject Period Spacing**: Spread theory sessions evenly across the week (e.g. 1 hour per day rather than 3 consecutive hours).

## 4. Single Semester vs Joint First-Year Scheduling
- `generate_single(semester_id)`: Standard independent scheduling for upper semesters (Semesters 3-8).
- `generate_joint(sem1_id, sem2_id)`: Coordinated optimization for 1st Year (Physics and Chemistry cycles sharing common lab resources, faculty, and lecture halls).
