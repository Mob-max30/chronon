import pytest
import asyncio
from pydantic import ValidationError
from fastapi.testclient import TestClient
from app.main import app
from app.services.academic_service import AcademicService
from app.schemas.academic import (
    AcademicYearCreate,
    SemesterSelectionRequest,
    InstitutionType,
    TermType,
)

client = TestClient(app)


def test_academic_service_in_memory_creation():
    service = AcademicService(db=None)
    created = asyncio.run(
        service.create_academic_year(AcademicYearCreate(name="2026-2027", is_current=True))
    )
    assert created.name == "2026-2027"
    assert created.is_current is True


def test_academic_service_lifecycle_queries():
    service = AcademicService(db=None)
    years = asyncio.run(service.get_all_years())
    assert isinstance(years, list)

    historical = asyncio.run(service.get_historical_years())
    assert isinstance(historical, list)

    # Invalid ID query
    non_existent = asyncio.run(service.get_year_by_id(99999))
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
        is_first_year_joint=True,
    )
    res_y1 = service.validate_semester_selection(req_y1)
    assert res_y1.is_valid is True
    assert res_y1.selected_semester == 1
    assert res_y1.is_first_year_p_c_cycle is True


def test_semester_validation_invalid_combinations():
    # Mismatch between Year level and Semester (Year 2 with Semester 5)
    with pytest.raises(ValidationError) as exc_info:
        SemesterSelectionRequest(
            academic_year_id=1,
            institution_type=InstitutionType.VTU_AFFILIATED,
            year_level=2,
            term_type=TermType.ODD,
            semester_number=5,
        )
    assert "Semester 5 is invalid for Year 2" in str(exc_info.value)

    # Mismatch between TermType and parity (ODD requested for Sem 4)
    with pytest.raises(ValidationError) as exc_info2:
        SemesterSelectionRequest(
            academic_year_id=1,
            institution_type=InstitutionType.VTU_AFFILIATED,
            year_level=2,
            term_type=TermType.ODD,
            semester_number=4,
        )
    assert "Semester 4 is not an ODD semester" in str(exc_info2.value)


def test_api_academic_years_endpoints():
    # Test listing
    res = client.get("/api/v1/academic-years")
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Test Current endpoint
    res_curr = client.get("/api/v1/academic-years/current")
    assert res_curr.status_code == 200
    assert res_curr.json()["success"] is True

    # Test Historical endpoint
    res_hist = client.get("/api/v1/academic-years/historical")
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
    res_val = client.post("/api/v1/academic-years/validate-semester", json=payload)
    assert res_val.status_code == 200
    data = res_val.json()
    assert data["success"] is True
    assert data["data"]["selected_semester"] == 3
