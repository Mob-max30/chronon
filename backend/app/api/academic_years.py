from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.academic import AcademicYearRead, AcademicYearCreate
from app.schemas.contracts import APIResponse

router = APIRouter(prefix="/academic-years", tags=["Academic Years"])


@router.get("", response_model=APIResponse)
async def list_academic_years(db: AsyncSession = Depends(get_db)):
    """List all academic years (current and past)."""
    # Scaffolding endpoint: returns empty list until records added
    return APIResponse(data=[], message="Academic years retrieved successfully")


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_academic_year(payload: AcademicYearCreate, db: AsyncSession = Depends(get_db)):
    """Create a new academic year."""
    return APIResponse(data={"id": 1, **payload.model_dump()}, message="Academic year created")
