from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.academic import SubjectCreate, SubjectUpdate
from app.schemas.contracts import APIResponse
from app.services.academic_service import AcademicService

router = APIRouter(prefix="/subjects", tags=["Subjects & Curriculum"])


@router.get("", response_model=APIResponse)
async def list_subjects(
    semester_id: Optional[int] = Query(None, description="Filter by semester ID"),
    scheme_id: Optional[int] = Query(None, description="Filter by scheme ID"),
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    stream_id: Optional[int] = Query(None, description="Filter by stream ID"),
    cycle_group: Optional[str] = Query(None, description="Filter: PHYSICS, CHEMISTRY, or COMMON"),
    subject_type: Optional[str] = Query(None, description="Filter: THEORY, LAB, INTEGRATED"),
    is_first_year: Optional[bool] = Query(None, description="Filter 1st year subjects"),
    db: AsyncSession = Depends(get_db),
):
    """List curriculum subjects with dynamic multi-dimensional filtering."""
    subjects = await AcademicService.list_subjects(
        db=db,
        semester_id=semester_id,
        scheme_id=scheme_id,
        branch_id=branch_id,
        stream_id=stream_id,
        cycle_group=cycle_group,
        subject_type=subject_type,
        is_first_year=is_first_year,
    )
    data = [
        {
            "id": s.id,
            "semester_id": s.semester_id,
            "branch_id": s.branch_id,
            "stream_id": s.stream_id,
            "cycle_group": s.cycle_group.value if s.cycle_group else None,
            "is_common": (s.is_first_year and s.cycle_group is None),
            "code": s.code,
            "name": s.name,
            "subject_type": s.subject_type.value,
            "weekly_hours": s.weekly_hours,
            "credits": s.credits,
            "is_first_year": s.is_first_year,
        }
        for s in subjects
    ]
    return APIResponse(data=data, message="Subjects retrieved successfully")


@router.post("", response_model=APIResponse)
async def create_subject(payload: SubjectCreate, db: AsyncSession = Depends(get_db)):
    """Add a new subject to curriculum."""
    subj = await AcademicService.create_subject(payload, db)
    return APIResponse(
        data={
            "id": subj.id,
            "code": subj.code,
            "name": subj.name,
            "subject_type": subj.subject_type.value,
            "weekly_hours": subj.weekly_hours,
            "credits": subj.credits,
            "cycle_group": subj.cycle_group.value if subj.cycle_group else None,
            "is_first_year": subj.is_first_year,
        },
        message="Subject created successfully",
    )


@router.get("/{subject_id}", response_model=APIResponse)
async def get_subject(subject_id: int, db: AsyncSession = Depends(get_db)):
    """Get single subject details."""
    subj = await AcademicService.get_subject(subject_id, db)
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    return APIResponse(
        data={
            "id": subj.id,
            "semester_id": subj.semester_id,
            "branch_id": subj.branch_id,
            "stream_id": subj.stream_id,
            "cycle_group": subj.cycle_group.value if subj.cycle_group else None,
            "is_common": (subj.is_first_year and subj.cycle_group is None),
            "code": subj.code,
            "name": subj.name,
            "subject_type": subj.subject_type.value,
            "weekly_hours": subj.weekly_hours,
            "credits": subj.credits,
            "is_first_year": subj.is_first_year,
        },
        message="Subject retrieved successfully",
    )


@router.put("/{subject_id}", response_model=APIResponse)
async def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update subject details."""
    subj = await AcademicService.update_subject(subject_id, payload, db)
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    return APIResponse(
        data={
            "id": subj.id,
            "code": subj.code,
            "name": subj.name,
            "subject_type": subj.subject_type.value,
            "weekly_hours": subj.weekly_hours,
            "credits": subj.credits,
        },
        message="Subject updated successfully",
    )


@router.delete("/{subject_id}", response_model=APIResponse)
async def delete_subject(subject_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a subject from catalogue."""
    success = await AcademicService.delete_subject(subject_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return APIResponse(data={"id": subject_id}, message="Subject deleted successfully")
