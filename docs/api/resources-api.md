# Physical Resources & Timetable Presentation API Reference

All routes are mounted under the prefix `/api/v1`.

---

## 1. Classrooms (`/api/v1/resources/rooms`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/resources/rooms` | List all classrooms for an institution. |
| `POST` | `/resources/rooms` | Create a new classroom. |
| `GET` | `/resources/rooms/{room_id}` | Retrieve room details with availability windows. |
| `PUT` | `/resources/rooms/{room_id}` | Update room details. |
| `DELETE` | `/resources/rooms/{room_id}` | Soft delete / remove a classroom. |
| `POST` | `/resources/rooms/{room_id}/availability` | Add or update usable availability windows. |

---

## 2. Physical Laboratories (`/api/v1/resources/labs`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/resources/labs` | List all physical laboratories. |
| `POST` | `/resources/labs` | Create a new physical lab resource. |
| `GET` | `/resources/labs/{lab_id}` | Retrieve physical lab details. |
| `PUT` | `/resources/labs/{lab_id}` | Update physical lab. |
| `DELETE` | `/resources/labs/{lab_id}` | Delete physical lab. |
| `POST` | `/resources/labs/{lab_id}/availability` | Add or update lab availability windows. |

---

## 3. Academic Lab ⟷ Physical Lab Mappings (`/api/v1/resources/labs/mappings`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/resources/labs/mappings` | List all academic lab subject to physical lab mappings. |
| `POST` | `/resources/labs/mappings` | Bind an academic lab subject (`subject_id`) to a physical lab (`lab_id`). |
| `DELETE` | `/resources/labs/mappings/{id}` | Remove a mapping binding. |

---

## 4. Deterministic Calculation Endpoints

> **Rule:** Calculation endpoints are pure deterministic functions and NEVER invoke the CP-SAT solver.

### `POST /api/v1/resources/sections/calculate`
**Request Body:**
```json
{
  "student_count": 180,
  "room_capacity": 60,
  "naming_pattern": "ALPHABETIC",
  "balance_distribution": false,
  "manual_count": null,
  "stream_id": 1,
  "cycle_group": "PHYSICS_CYCLE"
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "student_count": 180,
    "room_capacity": 60,
    "calculated_section_count": 3,
    "actual_section_count": 3,
    "is_override": false,
    "sections": [
      { "name": "A", "student_count": 60, "stream_id": 1, "cycle_group": "PHYSICS_CYCLE" },
      { "name": "B", "student_count": 60, "stream_id": 1, "cycle_group": "PHYSICS_CYCLE" },
      { "name": "C", "student_count": 60, "stream_id": 1, "cycle_group": "PHYSICS_CYCLE" }
    ]
  }
}
```

### `POST /api/v1/resources/batches/calculate`
**Request Body:**
```json
{
  "section_students": 65,
  "lab_capacity": 30,
  "naming_pattern": "B{index}",
  "manual_count": null
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "section_students": 65,
    "lab_capacity": 30,
    "calculated_batch_count": 3,
    "actual_batch_count": 3,
    "is_override": false,
    "batches": [
      { "name": "B1", "student_count": 30 },
      { "name": "B2", "student_count": 30 },
      { "name": "B3", "student_count": 5 }
    ]
  }
}
```

---

## 5. Master Time Slots & Schedule Config

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/resources/slot-config` | Retrieve master day/interval configuration. |
| `POST` | `/resources/slot-config` | Create or update master schedule configuration. |
| `POST` | `/resources/time-slots/generate` | Pure deterministic preview generation of time slots. |
| `GET` | `/resources/time-slots` | List active time slots in database. |

---

## 6. Timetable Presentation & Export Endpoints

### `GET /api/v1/timetables/{id}/view`
**Query Parameters:**
- `view_type`: `SECTION`, `FACULTY`, `ROOM`, `LAB`, `BATCH`, `FIRST_YEAR_CYCLE`
- `section_id`, `faculty_id`, `room_id`, `lab_id`, `batch_id`, `stream_id`, `cycle_group`

**Response:** Returns a 2D matrix structure (`rows`, `periods_header`, `paired_slot_groups`, `conflicts`).

### `GET /api/v1/timetables/{id}/export`
**Query Parameters:**
- `export_format`: `csv` or `json`
- `view_type`: `SECTION`, `FACULTY`, etc.

**Response:** Standard CSV file attachment or structured JSON export.
