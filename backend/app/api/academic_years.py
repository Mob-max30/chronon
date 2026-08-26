from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.academic import (
    AcademicYearRead,
    AcademicYearCreate,
    SemesterSelectionRequest,
    SemesterSelectionResponse,
)
from app.schemas.contracts import APIResponse
from app.services.academic_service import AcademicService

router = APIRouter(prefix="/academic-years", tags=["Academic Years Lifecycle"])


@router.get("", response_model=APIResponse)
async def list_academic_years(db: AsyncSession = Depends(get_db)):
    """List all registered academic years."""
    service = AcademicService(db)
    years = await service.get_all_years()
    return APIResponse(
        data=[AcademicYearRead.model_validate(y) for y in years],
        message="Academic years retrieved successfully",
    )


@router.get("/current", response_model=APIResponse)
async def get_current_year(db: AsyncSession = Depends(get_db)):
    """Get the currently active academic year session."""
    service = AcademicService(db)
    current = await service.get_current_year()
    if not current:
        return APIResponse(data=None, message="No active academic year found")
    return APIResponse(
        data=AcademicYearRead.model_validate(current),
        message="Current academic year retrieved",
    )


@router.get("/historical", response_model=APIResponse)
async def get_historical_years(db: AsyncSession = Depends(get_db)):
    """List historical (past) academic years."""
    service = AcademicService(db)
    historical = await service.get_historical_years()
    return APIResponse(
        data=[AcademicYearRead.model_validate(y) for y in historical],
        message="Historical academic years retrieved",
    )


@router.get("/{year_id}", response_model=APIResponse)
async def get_academic_year_by_id(year_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific academic year by ID."""
    service = AcademicService(db)
    year = await service.get_year_by_id(year_id)
    if not year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academic year with ID {year_id} not found",
        )
    return APIResponse(
        data=AcademicYearRead.model_validate(year),
        message="Academic year retrieved",
    )


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_academic_year(payload: AcademicYearCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new academic year.
    If is_current=True, atomically deactivates previous active years.
    """
    service = AcademicService(db)
    new_year = await service.create_academic_year(payload)
    return APIResponse(
        data=AcademicYearRead.model_validate(new_year),
        message="Academic year created successfully",
    )


@router.post("/{year_id}/set-current", response_model=APIResponse)
async def set_current_academic_year(year_id: int, db: AsyncSession = Depends(get_db)):
    """Atomically promotes an academic year to be the current active session."""
    service = AcademicService(db)
    updated = await service.set_current_year(year_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academic year with ID {year_id} not found",
        )
    return APIResponse(
        data=AcademicYearRead.model_validate(updated),
        message="Academic year set as current active session",
    )


@router.post("/validate-semester", response_model=APIResponse)
async def validate_semester(payload: SemesterSelectionRequest, db: AsyncSession = Depends(get_db)):
    """
    Validates that the selected Year level (1st-4th) matches the requested
    Semester number (1-8) and Odd/Even term type according to the Chronon workflow.
    """
    service = AcademicService(db)
    res = service.validate_semester_selection(payload)
    return APIResponse(
        data=res.model_dump(),
        message="Semester selection validated",
    )
