# Timetable Export API Specification & Application Contract

## 1. Overview
The Timetable Export API provides standardized, presentation-ready timetable outputs (CSV, JSON, Matrix, Printable format) for Sections, Faculty, Rooms, Labs, and Batches.

### Fundamental Architectural Rule:
**Exports operate strictly on already generated, stored timetable session data.**
An export endpoint must **NEVER** re-run the solver, alter sessions, or create new versions.

---

## 2. API Contract

### 2.1 Matrix View & Presentation Grid
- **Endpoint**: `GET /api/v1/timetables/{timetable_id}/view`
- **Query Parameters**:
  - `view_type`: `SECTION` | `FACULTY` | `ROOM` | `LAB` | `STREAM` | `CYCLE_GROUP` (default: `SECTION`)
  - `version_id` *(optional)*: Specify historical version ID (defaults to active version)
  - `section_id` *(optional)*: Filter by section
  - `faculty_id` *(optional)*: Filter by faculty member
  - `room_id` *(optional)*: Filter by classroom
  - `lab_id` *(optional)*: Filter by laboratory
  - `batch_id` *(optional)*: Filter by lab batch
  - `stream_id` *(optional)*: Filter by first-year stream
  - `cycle_group` *(optional)*: Filter by `PHYSICS_CYCLE` or `CHEMISTRY_CYCLE`

- **Response (`200 OK`)**:
```json
{
  "success": true,
  "data": {
    "timetable_id": 1,
    "version_id": 3,
    "view_type": "SECTION",
    "periods_header": [
      {"period_index": 1, "label": "Period 1", "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "THEORY"},
      {"period_index": 2, "label": "Period 2", "start_time": "10:00:00", "end_time": "11:00:00", "slot_type": "THEORY"}
    ],
    "rows": [
      {
        "day_of_week": 0,
        "day_name": "Monday",
        "slots": [
          {
            "period_index": 1,
            "session_id": 101,
            "subject_code": "21CS32",
            "subject_name": "Data Structures & Applications",
            "faculty_name": "Dr. Ramesh K",
            "room_name": "LH-101",
            "is_lab": false
          }
        ]
      }
    ]
  },
  "message": "Timetable view assembled successfully"
}
```

---

### 2.2 Direct File Export
- **Endpoint**: `GET /api/v1/timetables/{timetable_id}/export`
- **Query Parameters**:
  - `export_format`: `csv` | `json` | `html` (default: `csv`)
  - `view_type`: `SECTION` | `FACULTY` | `ROOM` | `LAB`
  - `section_id`, `faculty_id`, `room_id`, `lab_id` *(optional filters)*

- **Response Headers**:
  - For CSV: `Content-Type: text/csv`, `Content-Disposition: attachment; filename=timetable_1_section.csv`
  - For JSON: `Content-Type: application/json`

---

## 3. CSV Format Structure

```csv
Day,Period 1 (09:00-10:00),Period 2 (10:00-11:00),Period 3 (11:15-12:15),Period 4 (12:15-13:15)
Monday,"21CS32 (Dr. Ramesh K, LH-101)","21CS33 (Prof. Ananya S, LH-101)","21CSL38 Lab (Dr. Ramesh K, CS Lab 1, Batch: 3A-B1)","21CSL38 Lab (Dr. Ramesh K, CS Lab 1, Batch: 3A-B1)"
Tuesday,"21CS34 (Dr. Geeta V, LH-101)","21CS32 (Dr. Ramesh K, LH-101)","21CS33 (Prof. Ananya S, LH-101)","FREE"
```
