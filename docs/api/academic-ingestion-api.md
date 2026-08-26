# Academic & Document Ingestion REST API Reference

**Domain Owner:** Ujwal (Branch: `ujwal`)  
**Base URL:** `/api/v1`

---

## 1. Branch & Stream Endpoints

### `GET /branches`
Retrieve all configured branches.
- **Query Params:** `institution_id` (int), `stream_id` (int)
- **Response:** `APIResponse[List[BranchRead]]`

### `POST /branches`
Create a new branch in the catalogue.
- **Payload:** `BranchCreate` (`name`, `code`, `student_count`, `stream_id`, `institution_id`)

### `GET /branches/streams`
Retrieve first-year streams with aggregate student rollups and cycle splits.
- **Response:** `APIResponse[List[StreamRead]]`

### `POST /branches/streams`
Create a first-year stream and assign member branch IDs.
- **Payload:** `StreamCreate` (`name`, `code`, `branch_ids`)

### `POST /branches/streams/{stream_id}/split`
Calculate and update Physics/Chemistry cycle cohort student split for a stream.
- **Payload:** `CycleGroupSplitRequest` (`method`: `"EVEN"` | `"MANUAL"` | `"CAPACITY"`, `physics_count`, `chemistry_count`, `max_lab_capacity`)

### `POST /branches/student-counts`
Batch update intake student counts across multiple branches.
- **Payload:** `BatchStudentCountUpdate` (`counts`: `[{ branch_id, student_count }]`)

---

## 2. Subject & Curriculum Endpoints

### `GET /subjects`
List curriculum subjects with multi-dimensional filtering.
- **Query Params:** `semester_id`, `scheme_id`, `branch_id`, `stream_id`, `cycle_group` (`"PHYSICS"`, `"CHEMISTRY"`, `"COMMON"`), `subject_type` (`"THEORY"`, `"LAB"`, `"INTEGRATED"`), `is_first_year` (bool)
- **Response:** `APIResponse[List[SubjectRead]]`

### `POST /subjects`
Add a new subject to curriculum.
- **Payload:** `SubjectCreate` (`code`, `name`, `semester_id`, `subject_type`, `weekly_hours`, `credits`, `cycle_group`, `is_first_year`)

### `GET /subjects/{id}`
Retrieve single subject details.

### `PUT /subjects/{id}`
Update subject attributes.

### `DELETE /subjects/{id}`
Remove a subject from the catalogue.

---

## 3. Faculty Endpoints

### `GET /faculty`
List faculty members with assigned subject mappings and workload constraints.
- **Query Params:** `institution_id`, `department`, `is_active`
- **Response:** `APIResponse[List[FacultyRead]]`

### `POST /faculty`
Add a new faculty member with optional initial subject assignments.
- **Payload:** `FacultyCreate` (`name`, `employee_code`, `email`, `department`, `designation`, `max_weekly_hours`)

### `GET /faculty/{id}`
Get detailed faculty profile including assigned subject mappings.

### `PUT /faculty/{id}`
Update faculty profile information.

### `POST /faculty/{id}/mappings`
Assign a curriculum subject to a faculty member with optional stream and cycle group metadata.
- **Payload:** `FacultySubjectCreate` (`subject_id`, `stream_id`, `cycle_group`, `preference_rank`, `is_primary`)

### `GET /faculty/by-subject/{subject_id}`
Retrieve all faculty members qualified / assigned to teach a specific subject.

---

## 4. Document Ingestion Endpoints

### `POST /documents/upload`
Upload VTU syllabus PDF, branch affiliation list, or department faculty roster.
- **Payload:** `multipart/form-data` (`file`)
- **Process:** Performs format detection, text extraction, domain parsing, and candidate staging.

### `GET /documents`
List all staged and confirmed documents.

### `GET /documents/{id}`
Get candidate preview details for a specific uploaded document.

### `POST /documents/confirm`
Confirm reviewed candidate entities (branches, subjects, faculty) and atomically commit to database tables.
- **Payload:** `DocumentConfirmation` (`document_id`, `confirmed_branches`, `confirmed_subjects`, `confirmed_faculty`)
