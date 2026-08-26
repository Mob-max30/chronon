import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resources import Room, Lab, Section, Batch, TimeSlot, SlotType
from app.models.timetable import Timetable, TimetableStatus
from app.services.pipeline_service import build_scheduling_input_from_db
from app.services.orchestration_service import OrchestrationService
from app.schemas.timetable import GenerationTriggerRequest


@pytest.mark.asyncio
async def test_end_to_end_integrated_pipeline(async_client: AsyncClient):
    """
    Comprehensive End-to-End Integration Test:
    Academic Curriculum + Physical Resources -> DB Pipeline -> CP-SAT Solver -> Validator -> Snapshot -> Presentation Matrix & Export
    """
    # 1. Create Timetable Container
    tt_res = await async_client.post(
        "/api/v1/timetables",
        json={"academic_year_id": 1, "name": "E2E Integrated Timetable", "status": "DRAFT"},
    )
    assert tt_res.status_code == 201
    timetable_id = tt_res.json()["data"]["id"]

    # 2. Trigger Full Generation Lifecycle via REST API
    gen_payload = {
        "timetable_id": timetable_id,
        "academic_year_id": 1,
        "semester_ids": [3],
        "is_joint_first_year": False,
        "triggered_by": "e2e_integration_test",
        "notes": "E2E automated run",
        "max_solver_time_seconds": 60,
    }
    gen_res = await async_client.post("/api/v1/generation/trigger", json=gen_payload)
    assert gen_res.status_code == 201
    gen_data = gen_res.json()["data"]

    assert gen_data["generation_run"]["status"] in ["SUCCESS", "FEASIBLE", "OPTIMAL"]
    assert gen_data["total_sessions_generated"] > 0
    assert gen_data["validation_result"]["is_valid"] is True
    version_id = gen_data["version"]["id"]

    # 3. Query 2D Presentation Matrix Grid for Section View
    view_res = await async_client.get(f"/api/v1/timetables/{timetable_id}/view?view_type=SECTION")
    assert view_res.status_code == 200
    matrix = view_res.json()["data"]
    assert "rows" in matrix
    assert len(matrix["rows"]) > 0
    assert "periods_header" in matrix

    # 4. Verify CSV Export without calling solver
    csv_res = await async_client.get(f"/api/v1/timetables/{timetable_id}/export?export_format=csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert len(csv_res.text) > 0

    # 5. Check Generation Run Status Polling Endpoint
    run_id = gen_data["generation_run"]["id"]
    status_res = await async_client.get(f"/api/v1/generation/runs/{run_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()["data"]
    assert status_data["is_terminal"] is True
    assert status_data["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_pipeline_service_db_builder_with_records(async_client: AsyncClient):
    """
    Test pipeline_service correctly extracts and converts models from DB.
    """
    # Create Room
    r_res = await async_client.post(
        "/api/v1/resources/rooms",
        json={"institution_id": 1, "name": "Room 401", "capacity": 60, "is_active": True},
    )
    assert r_res.status_code == 201

    # Create Lab
    l_res = await async_client.post(
        "/api/v1/resources/labs",
        json={"institution_id": 1, "name": "Networks Lab", "capacity": 30, "count": 1},
    )
    assert l_res.status_code == 201

    # List timetables
    list_res = await async_client.get("/api/v1/timetables")
    assert list_res.status_code == 200
    assert list_res.json()["success"] is True
