from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.academic import FacultyCreate, FacultyUpdate, FacultySubjectCreate
from app.schemas.contracts import APIResponse
from app.services.academic_service import AcademicService

router = APIRouter(prefix="/faculty", tags=["Faculty & Workload"])


@router.get("", response_model=APIResponse)
async def list_faculty(
    institution_id: Optional[int] = Query(None, description="Filter by institution ID"),
    department: Optional[str] = Query(None, description="Filter by department name"),
    is_active: Optional[bool] = Query(None, description="Filter active faculty"),
    db: AsyncSession = Depends(get_db),
):
    """List faculty members with assigned subject mappings and workload parameters."""
    faculty_list = await AcademicService.list_faculty(
        db=db,
        institution_id=institution_id,
        department=department,
        is_active=is_active,
    )
    data = [
        {
            "id": f.id,
            "institution_id": f.institution_id,
            "name": f.name,
            "employee_code": f.employee_code,
            "email": f.email,
            "department": f.department,
            "designation": f.designation,
            "max_weekly_hours": f.max_weekly_hours,
            "is_active": f.is_active,
            "subject_count": len(f.subject_mappings),
            "subjects": [
                {
                    "subject_id": sm.subject_id,
                    "subject_code": sm.subject.code if sm.subject else None,
                    "subject_name": sm.subject.name if sm.subject else None,
                    "stream_id": sm.stream_id,
                    "cycle_group": sm.cycle_group.value if sm.cycle_group else None,
                    "preference_rank": sm.preference_rank,
                    "is_primary": sm.is_primary,
                }
                for sm in f.subject_mappings
            ],
        }
        for f in faculty_list
    ]
    return APIResponse(data=data, message="Faculty list retrieved successfully")


@router.post("", response_model=APIResponse)
async def create_faculty(payload: FacultyCreate, db: AsyncSession = Depends(get_db)):
    """Add a new faculty member with optional initial subject assignments."""
    fac = await AcademicService.create_faculty(payload, db)
    return APIResponse(
        data={
            "id": fac.id,
            "name": fac.name,
            "employee_code": fac.employee_code,
            "email": fac.email,
            "department": fac.department,
            "designation": fac.designation,
            "max_weekly_hours": fac.max_weekly_hours,
            "is_active": fac.is_active,
        },
        message="Faculty created successfully",
    )


@router.get("/by-subject/{subject_id}", response_model=APIResponse)
async def get_faculty_by_subject(subject_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve all faculty members eligible/assigned to teach a specific subject."""
    faculty_list = await AcademicService.get_faculty_by_subject(subject_id, db)
    data = [
        {
            "id": f.id,
            "name": f.name,
            "employee_code": f.employee_code,
            "email": f.email,
            "department": f.department,
            "designation": f.designation,
        }
        for f in faculty_list
    ]
    return APIResponse(data=data, message=f"Found {len(data)} faculty assigned to subject {subject_id}")


@router.get("/{faculty_id}", response_model=APIResponse)
async def get_faculty(faculty_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed faculty profile including subject assignments."""
    fac = await AcademicService.get_faculty(faculty_id, db)
    if not fac:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    return APIResponse(
        data={
            "id": fac.id,
            "institution_id": fac.institution_id,
            "name": fac.name,
            "employee_code": fac.employee_code,
            "email": fac.email,
            "department": fac.department,
            "designation": fac.designation,
            "max_weekly_hours": fac.max_weekly_hours,
            "is_active": fac.is_active,
            "subjects": [
                {
                    "subject_id": sm.subject_id,
                    "subject_code": sm.subject.code if sm.subject else None,
                    "subject_name": sm.subject.name if sm.subject else None,
                    "stream_id": sm.stream_id,
                    "cycle_group": sm.cycle_group.value if sm.cycle_group else None,
                    "preference_rank": sm.preference_rank,
                    "is_primary": sm.is_primary,
                }
                for sm in fac.subject_mappings
            ],
        },
        message="Faculty profile retrieved",
    )


@router.put("/{faculty_id}", response_model=APIResponse)
async def update_faculty(
    faculty_id: int,
    payload: FacultyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update faculty profile information."""
    fac = await AcademicService.update_faculty(faculty_id, payload, db)
    if not fac:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    return APIResponse(
        data={
            "id": fac.id,
            "name": fac.name,
            "employee_code": fac.employee_code,
            "department": fac.department,
            "designation": fac.designation,
            "max_weekly_hours": fac.max_weekly_hours,
            "is_active": fac.is_active,
        },
        message="Faculty profile updated",
    )


@router.post("/{faculty_id}/mappings", response_model=APIResponse)
async def assign_faculty_subject(
    faculty_id: int,
    payload: FacultySubjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Assign a curriculum subject to a faculty member with optional stream and cycle group metadata."""
    mapping = await AcademicService.assign_subject_to_faculty(faculty_id, payload, db)
    return APIResponse(
        data={
            "faculty_id": mapping.faculty_id,
            "subject_id": mapping.subject_id,
            "stream_id": mapping.stream_id,
            "cycle_group": mapping.cycle_group.value if mapping.cycle_group else None,
            "preference_rank": mapping.preference_rank,
            "is_primary": mapping.is_primary,
        },
        message="Subject successfully assigned to faculty",
    )
