# Timetable Versioning & Historical Immutability Architecture

## 1. Architectural Principles
1. **Never Overwrite Historical Data**: Once generated and validated, a `TimetableVersion` snapshot and its `TimetableSession` rows are permanently immutable.
2. **Deterministic Diffing**: Diffs between versions are calculated dynamically by comparing session tuples `(subject_id, section_id, batch_id)` across time slots, rooms, and faculty.
3. **Cloning on Restore**: When an administrator requests to restore a historical version, Chronon copies the session records into a new version increment rather than mutating previous history.

---

## 2. Entity Model

```
┌────────────────────────┐
│     AcademicYear       │
│  (is_current: boolean) │
└───────────┬────────────┘
            │ 1:N
            ▼
┌────────────────────────┐
│       Timetable        │
│  (Container / Scope)   │
└───────────┬────────────┘
            │ 1:N
            ▼
┌────────────────────────┐         ┌────────────────────────┐
│    TimetableVersion    │◄────────┤     GenerationRun      │
│  (is_active: boolean)  │  1:1    │  (Status, Score, Logs) │
│  (version_number: int) │         └────────────────────────┘
└───────────┬────────────┘
            │ 1:N
            ▼
┌────────────────────────┐
│    TimetableSession    │
│  (Subject, Section,    │
│   Faculty, Room, Lab,  │
│   TimeSlot, Batch)     │
└────────────────────────┘
```
