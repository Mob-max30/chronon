import pytest
from app.scheduling.fixtures import get_sample_scheduling_input, get_manual_valid_timetable, get_manual_invalid_timetable


@pytest.mark.asyncio
async def test_validate_scheduling_input_endpoint(async_client):
    inp = get_sample_scheduling_input()
    payload = inp.model_dump(mode="json")
    response = await async_client.post("/api/v1/scheduling/validate-input", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["is_valid"] is True


@pytest.mark.asyncio
async def test_solve_scheduling_endpoint(async_client):
    inp = get_sample_scheduling_input()
    payload = inp.model_dump(mode="json")
    response = await async_client.post("/api/v1/scheduling/solve", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["is_valid"] is True
    assert len(res_data["data"]["sessions"]) > 0


@pytest.mark.asyncio
async def test_validate_sessions_endpoint_valid(async_client):
    sessions = [s.model_dump(mode="json") for s in get_manual_valid_timetable()]
    response = await async_client.post("/api/v1/scheduling/validate", json={"sessions": sessions})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["is_valid"] is True


@pytest.mark.asyncio
async def test_validate_sessions_endpoint_invalid(async_client):
    sessions = [s.model_dump(mode="json") for s in get_manual_invalid_timetable()]
    response = await async_client.post("/api/v1/scheduling/validate", json={"sessions": sessions})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is False
    assert res_data["data"]["is_valid"] is False
    assert res_data["data"]["total_hard_violations"] >= 2
