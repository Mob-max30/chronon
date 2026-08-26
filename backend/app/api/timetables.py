from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.contracts import APIResponse

router = APIRouter(prefix="/timetables", tags=["Timetables"])


@router.get("", response_model=APIResponse)
async def list_timetables(db: AsyncSession = Depends(get_db)):
    """List timetables for the current academic year."""
    return APIResponse(data=[], message="Timetables retrieved")


@router.get("/{timetable_id}/grid", response_model=APIResponse)
async def get_timetable_grid(
    timetable_id: int,
    section_id: int = None,
    faculty_id: int = None,
    room_id: int = None,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve formatted matrix grid filtered by Section, Faculty, or Room."""
    return APIResponse(
        data={"timetable_id": timetable_id, "filters": {"section_id": section_id, "faculty_id": faculty_id, "room_id": room_id}, "matrix": []},
        message="Timetable grid retrieved",
    )
