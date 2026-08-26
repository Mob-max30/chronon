import pytest
from pydantic import ValidationError
from httpx import AsyncClient
from app.services.academic_service import AcademicService
from app.schemas.academic import (
    AcademicYearCreate,
    SemesterSelectionRequest,
    InstitutionType,
    TermType,
)


@pytest.mark.asyncio
async def test_academic_service_in_memory_creation():
    service = AcademicService(db=None)
    created = await service.create_academic_year(
        AcademicYearCreate(name="2026-2027", is_current=True)
    )
    assert created.name == "2026-2027"
    assert created.is_current is True


@pytest.mark.asyncio
async def test_academic_service_lifecycle_queries():
    service = AcademicService(db=None)
    years = await service.get_all_years()
    assert isinstance(years, list)

    historical = await service.get_historical_years()
    assert isinstance(historical, list)

    # Invalid ID query
    non_existent = await service.get_year_by_id(99999)
    assert non_existent is None


def test_semester_validation_valid_cases():
    service = AcademicService(db=None)

    # Year 2, Odd Sem (Sem 3)
    req_y2_odd = SemesterSelectionRequest(
        academic_year_id=1,
        institution_type=InstitutionType.VTU_AFFILIATED,
        year_level=2,
        term_type=TermType.ODD,
        semester_number=3,
    )
    res_y2_odd = service.validate_semester_selection(req_y2_odd)
    assert res_y2_odd.is_valid is True
    assert res_y2_odd.selected_semester == 3
    assert res_y2_odd.applicable_semesters == [3, 4]
    assert res_y2_odd.is_first_year_p_c_cycle is False

    # Year 1, Physics/Chem Cycle (Sem 1)
    req_y1 = SemesterSelectionRequest(
        academic_year_id=1,
        institution_type=InstitutionType.VTU_AFFILIATED,
        year_level=1,
        term_type=TermType.ODD,
        semester_number=1,
    )
    res_y1 = service.validate_semester_selection(req_y1)
    assert res_y1.is_valid is True
    assert res_y1.is_first_year_p_c_cycle is True


def test_semester_validation_invalid_combinations():
    # Year 2 with Sem 1 (Invalid year-semester match)
    with pytest.raises(ValidationError) as exc1:
        SemesterSelectionRequest(
            academic_year_id=1,
            institution_type=InstitutionType.VTU_AFFILIATED,
            year_level=2,
            term_type=TermType.ODD,
            semester_number=1,
        )
    assert "Semester 1 is invalid for Year 2" in str(exc1.value)

    # Year 3 with Even term_type but Odd semester number 5
    with pytest.raises(ValidationError) as exc2:
        SemesterSelectionRequest(
            academic_year_id=1,
            institution_type=InstitutionType.VTU_AFFILIATED,
            year_level=3,
            term_type=TermType.EVEN,
            semester_number=5,
        )
    assert "not an EVEN semester" in str(exc2.value)


@pytest.mark.asyncio
async def test_api_academic_years_endpoints(async_client: AsyncClient):
    # Test listing
    res = await async_client.get("/api/v1/academic-years")
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Test Current endpoint
    res_curr = await async_client.get("/api/v1/academic-years/current")
    assert res_curr.status_code == 200
    assert res_curr.json()["success"] is True

    # Test Historical endpoint
    res_hist = await async_client.get("/api/v1/academic-years/historical")
    assert res_hist.status_code == 200
    assert res_hist.json()["success"] is True

    # Test Validate-Semester Route
    payload = {
        "academic_year_id": 1,
        "institution_type": "VTU_AFFILIATED",
        "year_level": 2,
        "term_type": "ODD",
        "semester_number": 3,
        "is_first_year_joint": False,
    }
    res_val = await async_client.post("/api/v1/academic-years/validate-semester", json=payload)
    assert res_val.status_code == 200
    data = res_val.json()
    assert data["success"] is True
    assert data["data"]["selected_semester"] == 3
