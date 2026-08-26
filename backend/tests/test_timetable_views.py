import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.timetable_view import build_timetable_matrix, export_timetable_csv


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def test_build_timetable_matrix_structure():
    sessions = [
        {
            "id": 1,
            "day_of_week": 0,
            "time_slot_id": 1,
            "period_index": 1,
            "subject_code": "21CS32",
            "subject_name": "DSA",
            "faculty_name": "Dr. Ramesh",
            "section_id": 1,
            "section_name": "A",
            "room_name": "LH-101",
        },
        {
            "id": 2,
            "day_of_week": 0,
            "time_slot_id": 2,
            "period_index": 2,
            "subject_code": "21CS33",
            "subject_name": "ADE",
            "faculty_name": "Prof. Ananya",
            "section_id": 1,
            "section_name": "A",
            "room_name": "LH-101",
        },
    ]
    time_slots = [
        {"id": 1, "day_of_week": 0, "period_index": 1, "label": "P1", "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "THEORY"},
        {"id": 2, "day_of_week": 0, "period_index": 2, "label": "P2", "start_time": "10:00:00", "end_time": "11:00:00", "slot_type": "THEORY"},
    ]

    matrix = build_timetable_matrix(
        timetable_id=1,
        version_id=1,
        view_type="SECTION",
        filter_params={"section_id": 1},
        sessions=sessions,
        time_slots=time_slots,
    )

    assert matrix.timetable_id == 1
    assert len(matrix.rows) == 1
    assert matrix.rows[0].day_name == "Monday"
    assert len(matrix.rows[0].cells) == 2
    assert matrix.rows[0].cells[0].sessions[0].subject_code == "21CS32"
    assert matrix.rows[0].cells[1].sessions[0].subject_code == "21CS33"


def test_paired_slot_group_aggregation():
    sessions = [
        {
            "id": 10,
            "day_of_week": 1,
            "time_slot_id": 5,
            "period_index": 1,
            "subject_code": "22PHY12",
            "faculty_name": "Dr. Suresh",
            "section_name": "1A",
            "cycle_group": "PHYSICS_CYCLE",
            "paired_slot_group": "P3",
        },
        {
            "id": 11,
            "day_of_week": 1,
            "time_slot_id": 5,
            "period_index": 1,
            "subject_code": "22CHE12",
            "faculty_name": "Dr. Geeta",
            "section_name": "1B",
            "cycle_group": "CHEMISTRY_CYCLE",
            "paired_slot_group": "P3",
        },
    ]
    time_slots = [
        {"id": 5, "day_of_week": 1, "period_index": 1, "label": "P1", "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "THEORY"}
    ]

    matrix = build_timetable_matrix(
        timetable_id=1,
        version_id=1,
        view_type="FIRST_YEAR_CYCLE",
        filter_params={},
        sessions=sessions,
        time_slots=time_slots,
    )

    assert len(matrix.paired_slot_groups) == 1
    assert matrix.paired_slot_groups[0].paired_slot_group == "P3"
    assert len(matrix.paired_slot_groups[0].sessions) == 2


def test_conflict_diagnostic_overlay():
    sessions = [
        {"id": 101, "day_of_week": 0, "time_slot_id": 1, "period_index": 1, "subject_code": "DSA", "faculty_name": "Dr. R", "section_id": 1, "room_id": 1},
    ]
    time_slots = [
        {"id": 1, "day_of_week": 0, "period_index": 1, "label": "P1", "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "THEORY"}
    ]
    conflicts = [
        {
            "rule_code": "ROOM_CLASH",
            "severity": "ERROR",
            "message": "Room LH-101 double booked",
            "session_ids": [101, 102],
        }
    ]

    matrix = build_timetable_matrix(
        timetable_id=1,
        version_id=1,
        view_type="SECTION",
        filter_params={},
        sessions=sessions,
        time_slots=time_slots,
        conflicts=conflicts,
    )

    cell = matrix.rows[0].cells[0]
    assert cell.has_conflict is True
    assert len(cell.conflict_details) == 1
    assert cell.sessions[0].has_conflict is True


def test_csv_export():
    sessions = [
        {"id": 1, "day_of_week": 0, "time_slot_id": 1, "period_index": 1, "subject_code": "21CS32", "faculty_name": "Dr. Ramesh", "room_name": "LH-101"},
    ]
    time_slots = [
        {"id": 1, "day_of_week": 0, "period_index": 1, "label": "Period 1", "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "THEORY"}
    ]
    matrix = build_timetable_matrix(1, 1, "SECTION", {}, sessions, time_slots)
    csv_text = export_timetable_csv(matrix)
    assert "Day,Period 1" in csv_text
    assert "Monday" in csv_text
    assert "21CS32 - Dr. Ramesh [LH-101]" in csv_text


@pytest.mark.asyncio
async def test_api_timetable_view(async_client: AsyncClient):
    res = await async_client.get("/api/v1/timetables/1/view?view_type=SECTION")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert "rows" in data
    assert "periods_header" in data
    assert "paired_slot_groups" in data


@pytest.mark.asyncio
async def test_api_timetable_export_csv(async_client: AsyncClient):
    res = await async_client.get("/api/v1/timetables/1/export?export_format=csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "Period 1" in res.text
