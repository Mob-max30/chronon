# Generation Lifecycle & Orchestration API Specification

## 1. Overview
The Generation Lifecycle API coordinates the transition of a timetable scheduling request from user parameters into an optimized, independently validated, and snapshot-persisted timetable version.

Chronon enforces deterministic scheduling using Google OR-Tools CP-SAT and verifies all output with an independent validator prior to persisting any version snapshot.

---

## 2. GenerationRun State Machine

```
   [ USER REQUEST ]
          │
          ▼
     ┌──────────┐
     │  QUEUED  │
     └────┬─────┘
          │
          ▼
     ┌──────────┐
     │ RUNNING  │◄────────────┐
     └────┬─────┘             │
          │                   │
   ┌──────┴───────────────────┴───────┐
   │                                  │
   ▼                                  ▼
┌──────────┐ ┌────────────┐ ┌─────────┴──┐ ┌───────────┐ ┌───────────┐
│ SUCCESS  │ │ INFEASIBLE │ │  TIMEOUT   │ │  FAILED   │ │ CANCELLED │
└──────────┘ └────────────┘ └────────────┘ └───────────┘ └───────────┘
```

### State Definitions:
- **`QUEUED`**: Generation run has been initialized in the database with request parameters and assigned a unique ID.
- **`RUNNING`**: Input has been assembled from the database and handed to the CP-SAT solver.
- **`SUCCESS`**: Solver found an optimal/feasible solution, independent validation passed with 0 hard conflicts, and an immutable `TimetableVersion` snapshot has been committed.
- **`INFEASIBLE`**: Mathematical model proved that no conflict-free timetable exists given the current constraints, rooms, labs, or faculty limits.
- **`TIMEOUT`**: Solver exceeded the user-configured maximum allowed execution time without finding a solution.
- **`FAILED`**: Solver threw an exception or the independent validation layer flagged hard rule violations.
- **`CANCELLED`**: User aborted an ongoing or queued generation run.

---

## 3. Endpoints

### 3.1 Trigger Generation
Triggers the full end-to-end timetable generation lifecycle.

- **Endpoint**: `POST /api/v1/generation/trigger` (or `POST /api/v1/generation-runs`)
- **Request Body**:
```json
{
  "timetable_id": 1,
  "academic_year_id": 1,
  "semester_ids": [3],
  "is_joint_first_year": false,
  "triggered_by": "coordinator_pranav",
  "notes": "Fall 2026 CS Regular Schedule",
  "max_solver_time_seconds": 60
}
```

- **Success Response (`201 Created`)**:
```json
{
  "success": true,
  "data": {
    "generation_run": {
      "id": 12,
      "timetable_id": 1,
      "status": "SUCCESS",
      "triggered_by": "coordinator_pranav",
      "created_at": "2026-08-27T02:00:00Z",
      "started_at": "2026-08-27T02:00:01Z",
      "completed_at": "2026-08-27T02:00:04Z",
      "solver_time_seconds": 2.45,
      "quality_score": 96.5,
      "conflict_summary": {
        "validation": "PASSED",
        "total_sessions": 48,
        "solver_duration_seconds": 2.45,
        "quality_score": 96.5
      }
    },
    "version": {
      "id": 4,
      "timetable_id": 1,
      "version_number": 3,
      "is_active": true,
      "notes": "Fall 2026 CS Regular Schedule",
      "created_at": "2026-08-27T02:00:04Z"
    },
    "validation_result": {
      "is_valid": true,
      "total_hard_violations": 0,
      "total_soft_violations": 2,
      "violations": []
    },
    "total_sessions_generated": 48
  },
  "message": "Generation run completed with status: SUCCESS"
}
```

---

### 3.2 Poll Generation Run Status
Retrieves current execution status, elapsed time, terminal state flag, quality score, and structured conflict summary.

- **Endpoint**: `GET /api/v1/generation/runs/{run_id}` (or `GET /api/v1/generation-runs/{run_id}`)
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "data": {
    "generation_run_id": 12,
    "timetable_id": 1,
    "status": "SUCCESS",
    "created_at": "2026-08-27T02:00:00Z",
    "started_at": "2026-08-27T02:00:01Z",
    "completed_at": "2026-08-27T02:00:04Z",
    "elapsed_seconds": 2.45,
    "quality_score": 96.5,
    "conflict_summary": {
      "validation": "PASSED",
      "total_sessions": 48
    },
    "error_message": null,
    "is_terminal": true
  },
  "message": "Generation run status retrieved"
}
```

---

### 3.3 Cancel Generation Run
Cancels a running or queued generation task.

- **Endpoint**: `POST /api/v1/generation/runs/{run_id}/cancel` (or `POST /api/v1/generation-runs/{run_id}/cancel`)
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "data": {
    "id": 12,
    "status": "CANCELLED",
    "conflict_summary": {
      "cancellation": "USER_CANCELLED",
      "details": "Generation run was cancelled by user request."
    }
  },
  "message": "Generation run cancelled successfully"
}
```

---

### 3.4 List Runs for Timetable
- **Endpoint**: `GET /api/v1/generation/timetable/{timetable_id}/runs`
- **Response (`200 OK`)**: Array of `GenerationRunRead` records.
