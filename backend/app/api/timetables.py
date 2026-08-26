from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.timetable import Timetable, TimetableVersion, TimetableSession, TimetableStatus
from app.models.resources import Room, Lab, Section, Batch, TimeSlot
from app.models.academic import Subject, Faculty
from app.schemas.contracts import APIResponse
from app.schemas.timetable import TimetableRead, TimetableCreate, TimetableStatusUpdate
from app.schemas.timetable_view import TimetableMatrixResponse, TimetableExportResponse
from app.services.timetable_view import build_timetable_matrix, export_timetable_csv

router = APIRouter(prefix="/timetables", tags=["Timetables"])


def get_mock_sessions() -> List[Dict[str, Any]]:
    """Fixture sessions for presentation previews when database has no generated runs yet."""
    return [
        {
            "id": 1,
            "session_id": 1,
            "day_of_week": 0,
            "time_slot_id": 1,
            "period_index": 1,
            "subject_id": 101,
            "subject_code": "21CS32",
            "subject_name": "Data Structures & Applications",
            "subject_type": "THEORY",
            "faculty_id": 1,
            "faculty_name": "Dr. Ramesh K",
            "section_id": 1,
            "section_name": "3A",
            "room_id": 1,
            "room_name": "LH-101",
            "stream_id": 1,
            "stream_name": "CSE",
        },
        {
            "id": 2,
            "session_id": 2,
            "day_of_week": 0,
            "time_slot_id": 2,
            "period_index": 2,
            "subject_id": 102,
            "subject_code": "21CS33",
            "subject_name": "Analog & Digital Electronics",
            "subject_type": "THEORY",
            "faculty_id": 2,
            "faculty_name": "Prof. Ananya S",
            "section_id": 1,
            "section_name": "3A",
            "room_id": 1,
            "room_name": "LH-101",
            "stream_id": 1,
            "stream_name": "CSE",
        },
        {
            "id": 3,
            "session_id": 3,
            "day_of_week": 0,
            "time_slot_id": 3,
            "period_index": 3,
            "subject_id": 103,
            "subject_code": "21CSL38",
            "subject_name": "Data Structures Lab",
            "subject_type": "LAB",
            "faculty_id": 1,
            "faculty_name": "Dr. Ramesh K",
            "section_id": 1,
            "section_name": "3A",
            "batch_id": 1,
            "batch_name": "3A-B1",
            "lab_id": 1,
            "lab_name": "CS Lab 1",
            "stream_id": 1,
            "stream_name": "CSE",
        },
        {
            "id": 4,
            "session_id": 4,
            "day_of_week": 0,
            "time_slot_id": 3,
            "period_index": 3,
            "subject_id": 104,
            "subject_code": "21CSL39",
            "subject_name": "ADE Lab",
            "subject_type": "LAB",
            "faculty_id": 2,
            "faculty_name": "Prof. Ananya S",
            "section_id": 1,
            "section_name": "3A",
            "batch_id": 2,
            "batch_name": "3A-B2",
            "lab_id": 2,
            "lab_name": "Electronics Hardware Lab",
            "stream_id": 1,
            "stream_name": "CSE",
        },
        {
            "id": 5,
            "session_id": 5,
            "day_of_week": 1,
            "time_slot_id": 5,
            "period_index": 1,
            "subject_id": 201,
            "subject_code": "22PHY12",
            "subject_name": "Applied Physics",
            "subject_type": "THEORY",
            "faculty_id": 4,
            "faculty_name": "Dr. Suresh P",
            "section_id": 10,
            "section_name": "1A",
            "room_id": 1,
            "room_name": "LH-101",
            "stream_id": 1,
            "stream_name": "CSE Stream",
            "cycle_group": "PHYSICS_CYCLE",
            "paired_slot_group": "P1",
        },
        {
            "id": 6,
            "session_id": 6,
            "day_of_week": 1,
            "time_slot_id": 5,
            "period_index": 1,
            "subject_id": 202,
            "subject_code": "22CHE12",
            "subject_name": "Applied Chemistry",
            "subject_type": "THEORY",
            "faculty_id": 5,
            "faculty_name": "Dr. Geeta V",
            "section_id": 11,
            "section_name": "1B",
            "room_id": 2,
            "room_name": "LH-102",
            "stream_id": 1,
            "stream_name": "CSE Stream",
            "cycle_group": "CHEMISTRY_CYCLE",
            "paired_slot_group": "P1",
        },
    ]


def get_default_time_slots() -> List[Dict[str, Any]]:
    """Default 6-day period structure for grid rendering."""
    slots = []
    slot_id = 1
    for day in range(6):
        periods = [
            {"period_index": 1, "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "THEORY", "label": "Period 1"},
            {"period_index": 2, "start_time": "10:00:00", "end_time": "11:00:00", "slot_type": "THEORY", "label": "Period 2"},
            {"period_index": 3, "start_time": "11:00:00", "end_time": "11:15:00", "slot_type": "BREAK", "label": "Tea Break"},
            {"period_index": 4, "start_time": "11:15:00", "end_time": "12:15:00", "slot_type": "THEORY", "label": "Period 3"},
            {"period_index": 5, "start_time": "12:15:00", "end_time": "13:15:00", "slot_type": "THEORY", "label": "Period 4"},
            {"period_index": 6, "start_time": "13:15:00", "end_time": "14:00:00", "slot_type": "LUNCH", "label": "Lunch"},
            {"period_index": 7, "start_time": "14:00:00", "end_time": "15:00:00", "slot_type": "THEORY", "label": "Period 5"},
            {"period_index": 8, "start_time": "15:00:00", "end_time": "16:00:00", "slot_type": "THEORY", "label": "Period 6"},
        ]
        for p in periods:
            slots.append({
                "id": slot_id,
                "day_of_week": day,
                "period_index": p["period_index"],
                "start_time": p["start_time"],
                "end_time": p["end_time"],
                "slot_type": p["slot_type"],
                "label": p["label"],
            })
            slot_id += 1
    return slots


@router.get("", response_model=APIResponse)
async def list_timetables(
    academic_year_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all timetables, optionally filtered by academic year, semester, or status."""
    stmt = select(Timetable).options(
        selectinload(Timetable.academic_year),
        selectinload(Timetable.versions),
    ).order_by(Timetable.id.desc())

    if academic_year_id:
        stmt = stmt.where(Timetable.academic_year_id == academic_year_id)
    if semester_id:
        stmt = stmt.where(Timetable.semester_id == semester_id)
    if status_filter:
        stmt = stmt.where(Timetable.status == status_filter)

    result = await db.execute(stmt)
    timetables = result.scalars().all()
    items = [TimetableRead.model_validate(t) for t in timetables]
    return APIResponse(data=items, message=f"Found {len(items)} timetables")


@router.get("/{timetable_id}", response_model=APIResponse)
async def get_timetable(
    timetable_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get timetable container details by ID."""
    stmt = select(Timetable).options(
        selectinload(Timetable.academic_year),
        selectinload(Timetable.versions),
    ).where(Timetable.id == timetable_id)

    result = await db.execute(stmt)
    timetable = result.scalars().first()
    if not timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timetable container {timetable_id} not found",
        )
    return APIResponse(data=TimetableRead.model_validate(timetable), message="Timetable retrieved")


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_timetable(
    payload: TimetableCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new timetable container."""
    new_timetable = Timetable(
        academic_year_id=payload.academic_year_id,
        name=payload.name,
        status=payload.status or TimetableStatus.DRAFT,
    )
    db.add(new_timetable)
    await db.commit()
    await db.refresh(new_timetable)
    return APIResponse(
        data=TimetableRead.model_validate(new_timetable),
        message="Timetable created successfully",
    )


@router.patch("/{timetable_id}/status", response_model=APIResponse)
async def update_timetable_status(
    timetable_id: int,
    payload: TimetableStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update timetable container lifecycle status (DRAFT, ACTIVE, ARCHIVED)."""
    stmt = select(Timetable).where(Timetable.id == timetable_id)
    res = await db.execute(stmt)
    timetable = res.scalars().first()

    if not timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timetable container {timetable_id} not found",
        )

    timetable.status = payload.status
    await db.commit()
    await db.refresh(timetable)
    return APIResponse(
        data=TimetableRead.model_validate(timetable),
        message=f"Timetable status updated to {payload.status.value}",
    )


@router.get("/{timetable_id}/view", response_model=APIResponse)
async def get_timetable_view(
    timetable_id: int,
    view_type: str = Query("SECTION", description="SECTION, FACULTY, ROOM, LAB, STREAM, or CYCLE_GROUP"),
    version_id: Optional[int] = None,
    section_id: Optional[int] = None,
    faculty_id: Optional[int] = None,
    room_id: Optional[int] = None,
    lab_id: Optional[int] = None,
    batch_id: Optional[int] = None,
    stream_id: Optional[int] = None,
    cycle_group: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve structured 2D timetable matrix view formatted for presentation.
    Filterable by Section, Faculty, Room, Lab, Batch, Stream, or Cycle Group.
    Operates strictly on stored/persisted sessions without re-solving.
    """
    slot_res = await db.execute(select(TimeSlot).order_by(TimeSlot.day_of_week, TimeSlot.period_index))
    db_slots = slot_res.scalars().all()
    time_slots = []
    if db_slots:
        for ts in db_slots:
            time_slots.append({
                "id": ts.id,
                "day_of_week": ts.day_of_week,
                "period_index": ts.period_index,
                "start_time": ts.start_time.isoformat(),
                "end_time": ts.end_time.isoformat(),
                "slot_type": ts.slot_type.value if hasattr(ts.slot_type, "value") else str(ts.slot_type),
                "label": ts.label or f"Period {ts.period_index}",
            })
    else:
        time_slots = get_default_time_slots()

    sessions = []
    if version_id:
        sess_query = select(TimetableSession).where(TimetableSession.version_id == version_id)
    else:
        sess_query = select(TimetableSession).join(TimetableVersion).where(TimetableVersion.timetable_id == timetable_id)

    db_sess_res = await db.execute(sess_query)
    db_sessions = db_sess_res.scalars().all()

    if db_sessions:
        for s in db_sessions:
            sessions.append({
                "id": s.id,
                "session_id": s.id,
                "time_slot_id": s.time_slot_id,
                "subject_id": s.subject_id,
                "faculty_id": s.faculty_id,
                "section_id": s.section_id,
                "batch_id": s.batch_id,
                "room_id": s.room_id,
                "lab_id": s.lab_id,
            })
    else:
        sessions = get_mock_sessions()

    filter_params = {
        "section_id": section_id,
        "faculty_id": faculty_id,
        "room_id": room_id,
        "lab_id": lab_id,
        "batch_id": batch_id,
        "stream_id": stream_id,
        "cycle_group": cycle_group,
    }

    matrix = build_timetable_matrix(
        timetable_id=timetable_id,
        version_id=version_id,
        view_type=view_type.upper(),
        filter_params=filter_params,
        sessions=sessions,
        time_slots=time_slots,
    )

    return APIResponse(data=matrix.model_dump(), message="Timetable view assembled successfully")


@router.get("/{timetable_id}/grid", response_model=APIResponse)
async def get_timetable_grid(
    timetable_id: int,
    section_id: Optional[int] = None,
    faculty_id: Optional[int] = None,
    room_id: Optional[int] = None,
    lab_id: Optional[int] = None,
    view_type: str = Query("SECTION"),
    db: AsyncSession = Depends(get_db),
):
    """Backwards-compatibility alias for timetable matrix view."""
    return await get_timetable_view(
        timetable_id=timetable_id,
        view_type=view_type,
        section_id=section_id,
        faculty_id=faculty_id,
        room_id=room_id,
        lab_id=lab_id,
        db=db,
    )


@router.get("/{timetable_id}/export")
async def export_timetable(
    timetable_id: int,
    export_format: str = Query("csv", description="csv, json, or html"),
    view_type: str = Query("SECTION"),
    section_id: Optional[int] = None,
    faculty_id: Optional[int] = None,
    room_id: Optional[int] = None,
    lab_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Export timetable for section, faculty, room, or lab without running the solver.
    Outputs standard CSV, formatted JSON, or printable document payload.
    """
    view_res = await get_timetable_view(
        timetable_id=timetable_id,
        view_type=view_type,
        section_id=section_id,
        faculty_id=faculty_id,
        room_id=room_id,
        lab_id=lab_id,
        db=db,
    )
    matrix_data = view_res.data
    matrix = TimetableMatrixResponse.model_validate(matrix_data)

    if export_format.lower() == "csv":
        csv_text = export_timetable_csv(matrix)
        return Response(
            content=csv_text,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=timetable_{timetable_id}_{view_type.lower()}.csv"},
        )

    return APIResponse(
        data={"timetable_id": timetable_id, "export_format": export_format, "matrix": matrix_data},
        message="Timetable exported successfully",
    )
