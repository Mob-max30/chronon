import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app




# ==============================================================================
# SECTION CALCULATION API TESTS
# ==============================================================================
@pytest.mark.asyncio
async def test_api_calculate_sections(async_client: AsyncClient):
    payload = {
        "student_count": 180,
        "room_capacity": 60,
        "naming_pattern": "ALPHABETIC",
    }
    response = await async_client.post("/api/v1/resources/sections/calculate", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert data["calculated_section_count"] == 3
    assert data["actual_section_count"] == 3
    assert data["is_override"] is False
    assert len(data["sections"]) == 3
    assert [s["name"] for s in data["sections"]] == ["A", "B", "C"]
    assert [s["student_count"] for s in data["sections"]] == [60, 60, 60]


@pytest.mark.asyncio
async def test_api_calculate_sections_remainder(async_client: AsyncClient):
    payload = {
        "student_count": 181,
        "room_capacity": 60,
        "naming_pattern": "ALPHABETIC",
    }
    response = await async_client.post("/api/v1/resources/sections/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["calculated_section_count"] == 4
    assert [s["student_count"] for s in data["sections"]] == [60, 60, 60, 1]


@pytest.mark.asyncio
async def test_api_calculate_sections_invalid_capacity(async_client: AsyncClient):
    payload = {
        "student_count": 180,
        "room_capacity": 0,  # Invalid
    }
    response = await async_client.post("/api/v1/resources/sections/calculate", json=payload)
    assert response.status_code == 422  # Pydantic validation: gt=0


@pytest.mark.asyncio
async def test_api_calculate_sections_override(async_client: AsyncClient):
    payload = {
        "student_count": 180,
        "room_capacity": 60,
        "manual_count": 4,
    }
    response = await async_client.post("/api/v1/resources/sections/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["calculated_section_count"] == 3
    assert data["actual_section_count"] == 4
    assert data["is_override"] is True


# ==============================================================================
# BATCH CALCULATION API TESTS
# ==============================================================================
@pytest.mark.asyncio
async def test_api_calculate_batches(async_client: AsyncClient):
    payload = {
        "section_students": 65,
        "lab_capacity": 30,
        "naming_pattern": "B{index}",
    }
    response = await async_client.post("/api/v1/resources/batches/calculate", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert data["calculated_batch_count"] == 3
    assert data["actual_batch_count"] == 3
    assert [b["name"] for b in data["batches"]] == ["B1", "B2", "B3"]
    assert [b["student_count"] for b in data["batches"]] == [30, 30, 5]
    assert sum(b["student_count"] for b in data["batches"]) == 65


@pytest.mark.asyncio
async def test_api_calculate_batches_invalid_input(async_client: AsyncClient):
    payload = {
        "section_students": -10,  # Invalid
        "lab_capacity": 30,
    }
    response = await async_client.post("/api/v1/resources/batches/calculate", json=payload)
    assert response.status_code == 422


# ==============================================================================
# TIME SLOT GENERATION API TESTS
# ==============================================================================
@pytest.mark.asyncio
async def test_api_generate_time_slots(async_client: AsyncClient):
    payload = {
        "institution_id": 1,
        "theory_duration_minutes": 60,
        "lab_duration_minutes": 120,
        "working_days": [0, 1],  # Mon, Tue
        "day_start_time": "09:00:00",
        "day_end_time": "12:00:00",
        "breaks": [],
    }
    response = await async_client.post("/api/v1/resources/time-slots/generate", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert len(data) == 6  # 3 periods * 2 days


# ==============================================================================
# ROOM & LAB CRUD API TESTS
# ==============================================================================
@pytest.mark.asyncio
async def test_api_room_crud(async_client: AsyncClient):
    # 1. Create Room
    create_payload = {
        "institution_id": 1,
        "name": "LH-301",
        "building": "Main Block",
        "capacity": 70,
        "room_type": "LECTURE_HALL",
        "is_active": True,
        "availabilities": [
            {"day_of_week": 0, "start_time": "09:00:00", "end_time": "17:00:00", "is_available": True}
        ],
    }
    res = await async_client.post("/api/v1/resources/rooms", json=create_payload)
    assert res.status_code == 201
    room_id = res.json()["data"]["id"]
    assert res.json()["data"]["name"] == "LH-301"
    assert res.json()["data"]["capacity"] == 70

    # 2. Get Room
    res_get = await async_client.get(f"/api/v1/resources/rooms/{room_id}")
    assert res_get.status_code == 200
    assert res_get.json()["data"]["name"] == "LH-301"

    # 3. Update Room
    res_update = await async_client.put(
        f"/api/v1/resources/rooms/{room_id}",
        json={"capacity": 75, "building": "Academic Block A"},
    )
    assert res_update.status_code == 200
    assert res_update.json()["data"]["capacity"] == 75

    # 4. List Rooms
    res_list = await async_client.get("/api/v1/resources/rooms")
    assert res_list.status_code == 200
    assert any(r["id"] == room_id for r in res_list.json()["data"])

    # 5. Delete Room
    res_del = await async_client.delete(f"/api/v1/resources/rooms/{room_id}")
    assert res_del.status_code == 200


@pytest.mark.asyncio
async def test_api_lab_crud(async_client: AsyncClient):
    # 1. Create Lab
    create_payload = {
        "institution_id": 1,
        "name": "AI-ML Lab",
        "building": "CS Department",
        "capacity": 35,
        "count": 2,
        "lab_type": "COMPUTER",
    }
    res = await async_client.post("/api/v1/resources/labs", json=create_payload)
    assert res.status_code == 201
    lab_id = res.json()["data"]["id"]
    assert res.json()["data"]["name"] == "AI-ML Lab"
    assert res.json()["data"]["count"] == 2

    # 2. Update Lab
    res_update = await async_client.put(f"/api/v1/resources/labs/{lab_id}", json={"count": 3})
    assert res_update.status_code == 200
    assert res_update.json()["data"]["count"] == 3

    # 3. Delete Lab
    res_del = await async_client.delete(f"/api/v1/resources/labs/{lab_id}")
    assert res_del.status_code == 200
