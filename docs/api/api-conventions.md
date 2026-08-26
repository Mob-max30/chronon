# API Conventions & Design Guidelines

## 1. REST Architecture Standards
- Standard base URL: `/api/v1/`
- JSON payload requests and responses.
- Clean standard HTTP status codes:
  - `200 OK`: Successful fetch/update.
  - `201 Created`: Successful resource creation.
  - `400 Bad Request`: Validation failure or malformed payload.
  - `404 Not Found`: Resource does not exist.
  - `422 Unprocessable Entity`: Schema validation error.
  - `500 Internal Server Error`: Unhandled server exception.

## 2. Standard Response Wrapper
All endpoints return standard envelope structures where appropriate:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

## 3. Standard Error Structure
```json
{
  "success": false,
  "error": {
    "code": "ROOM_CAPACITY_EXCEEDED",
    "message": "Section student count (65) exceeds room capacity (60).",
    "details": {
      "section_id": "sec_123",
      "room_id": "room_456"
    }
  }
}
```

## 4. Key Endpoints Grouping
- `/health`: System and dependency liveness.
- `/api/v1/academic-years`: Academic year selection and lifecycle.
- `/api/v1/branches`: Branch, course, and student count management.
- `/api/v1/subjects`: Subject catalog, theory/lab definitions, weekly hours.
- `/api/v1/faculty`: Faculty directory, preferences, and document ingestion.
- `/api/v1/resources`: Rooms, physical labs, sections, batches, and time slots.
- `/api/v1/generation`: Timetable trigger, status, and cancellation.
- `/api/v1/timetables`: Timetable matrix retrieval by section, faculty, room.
- `/api/v1/versions`: Version history, rollback, diffs, and publishing.
- `/api/v1/documents`: Document upload, OCR job status, and confirmed extractions.
