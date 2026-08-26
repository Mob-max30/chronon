from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.timetable import Timetable, TimetableStatus
from app.schemas.contracts import APIResponse
from app.schemas.timetable import (
    TimetableRead,
    TimetableCreate,
    TimetableStatusUpdate,
)

router = APIRouter(prefix="/timetables", tags=["Timetables"])


@router.get("", response_model=APIResponse)
async def list_timetables(
    academic_year_id: Optional[int] = None,
    status_filter: Optional[TimetableStatus] = None,
    db: AsyncSession = Depends(get_db),
):
    """List timetables optionally filtered by academic year and status."""
    if not db:
        return APIResponse(data=[], message="Timetables retrieved")

    stmt = select(Timetable)
    if academic_year_id:
        stmt = stmt.where(Timetable.academic_year_id == academic_year_id)
    if status_filter:
        stmt = stmt.where(Timetable.status == status_filter)
    stmt = stmt.order_by(Timetable.id.desc())

    result = await db.execute(stmt)
    timetables = result.scalars().all()
    return APIResponse(
        data=[TimetableRead.model_validate(t) for t in timetables],
        message="Timetables retrieved",
    )


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_timetable(payload: TimetableCreate, db: AsyncSession = Depends(get_db)):
    """Create a new timetable container for an academic year."""
    if not db:
        return APIResponse(data={"id": 1, **payload.model_dump()}, message="Timetable created")

    new_timetable = Timetable(
        academic_year_id=payload.academic_year_id,
        name=payload.name,
        status=payload.status,
    )
    db.add(new_timetable)
    await db.commit()
    await db.refresh(new_timetable)

    return APIResponse(
        data=TimetableRead.model_validate(new_timetable),
        message="Timetable container created",
    )


@router.patch("/{timetable_id}/status", response_model=APIResponse)
async def update_timetable_status(
    timetable_id: int,
    payload: TimetableStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update timetable status (DRAFT -> PUBLISHED -> ARCHIVED)."""
    if not db:
        return APIResponse(data=None, message="Status updated")

    stmt = select(Timetable).where(Timetable.id == timetable_id)
    result = await db.execute(stmt)
    timetable = result.scalars().first()
    if not timetable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timetable not found")

    timetable.status = payload.status
    await db.commit()
    await db.refresh(timetable)

    return APIResponse(
        data=TimetableRead.model_validate(timetable),
        message=f"Timetable status updated to {payload.status.value}",
    )
