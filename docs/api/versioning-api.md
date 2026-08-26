# Timetable Versioning & History API Specification

## 1. Overview
The Timetable Versioning subsystem guarantees that no historical timetable is ever overwritten or lost. Every successful generation run or manual modification creates an immutable `TimetableVersion` snapshot with its constituent `TimetableSession` records.

---

## 2. Core Invariants
1. **Append-Only Immutability**: Historical versions and their sessions are never mutated.
2. **Single Active Version**: For a given `Timetable` container, exactly one version has `is_active = True`.
3. **Traceability**: Each version references its parent `GenerationRun` (if generated) and creator notes.
4. **Non-destructive Rollback/Restore**: Restoring a historical version creates a *new* active version cloned from the snapshot, preserving the full audit trail.

---

## 3. Endpoints

### 3.1 List Versions for a Timetable
- **Endpoint**: `GET /api/v1/timetables/{timetable_id}/versions` (or `GET /api/v1/versions/{timetable_id}`)
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "timetable_id": 1,
      "version_number": 3,
      "is_active": true,
      "notes": "Restored copy of v1 with lab adjustment",
      "created_at": "2026-08-27T02:15:00Z"
    },
    {
      "id": 2,
      "timetable_id": 1,
      "version_number": 2,
      "is_active": false,
      "notes": "Second generation run",
      "created_at": "2026-08-27T02:05:00Z"
    },
    {
      "id": 1,
      "timetable_id": 1,
      "version_number": 1,
      "is_active": false,
      "notes": "Initial draft generation",
      "created_at": "2026-08-27T01:50:00Z"
    }
  ],
  "message": "Version history retrieved successfully"
}
```

---

### 3.2 Get Version Details with Scheduled Sessions
- **Endpoint**: `GET /api/v1/versions/detail/{version_id}` (or `GET /api/v1/versions/{timetable_id}/version/{version_id}`)
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "timetable_id": 1,
    "version_number": 1,
    "is_active": false,
    "notes": "Initial draft generation",
    "created_at": "2026-08-27T01:50:00Z",
    "sessions": [
      {
        "id": 101,
        "version_id": 1,
        "subject_id": 10,
        "faculty_id": 4,
        "section_id": 1,
        "batch_id": null,
        "room_id": 1,
        "lab_id": null,
        "time_slot_id": 1
      }
    ]
  },
  "message": "Version snapshot retrieved"
}
```

---

### 3.3 Compare Two Versions (Version Diff)
Computes session-by-session differential between two timetable version snapshots.

- **Endpoint**: `GET /api/v1/versions/{from_id}/compare/{to_id}` (or `GET /api/v1/versions/{timetable_id}/diff?from_version_id={from}&to_version_id={to}`)
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "data": {
    "timetable_id": 1,
    "from_version_id": 1,
    "to_version_id": 2,
    "from_version_number": 1,
    "to_version_number": 2,
    "total_sessions_from": 48,
    "total_sessions_to": 48,
    "total_differences": 2,
    "differences": [
      {
        "diff_type": "MODIFIED",
        "subject_id": 10,
        "section_id": 1,
        "batch_id": null,
        "from_slot_id": 1,
        "to_slot_id": 3,
        "from_room_id": 1,
        "to_room_id": 2,
        "from_faculty_id": 4,
        "to_faculty_id": 4,
        "details": "Session moved from Slot 1 (LH-101) to Slot 3 (LH-102)"
      }
    ]
  },
  "message": "Version diff calculated successfully"
}
```

---

### 3.4 Set Active Version (Direct Activation)
- **Endpoint**: `POST /api/v1/versions/{timetable_id}/version/{version_id}/set-active`
- **Response (`200 OK`)**: Updates `is_active` flag atomically across versions.

---

### 3.5 Restore Historical Version as New Version
Clones all sessions from the historical version into a brand new active version number, preserving complete immutability of the source version.

- **Endpoint**: `POST /api/v1/versions/restore/{version_id}` (or `POST /api/v1/versions/{timetable_id}/version/{version_id}/restore`)
- **Request Body (Optional)**:
```json
{
  "notes": "Restored v1 copy after committee review"
}
```
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "data": {
    "id": 5,
    "timetable_id": 1,
    "version_number": 4,
    "is_active": true,
    "notes": "Restored v1 copy after committee review",
    "created_at": "2026-08-27T02:20:00Z"
  },
  "message": "Version 1 restored as new Version 4"
}
```
