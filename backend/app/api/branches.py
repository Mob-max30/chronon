from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.academic import (
    BranchCreate,
    BranchUpdate,
    BatchStudentCountUpdate,
    StreamCreate,
    StreamUpdate,
    CycleGroupSplitRequest,
)
from app.schemas.contracts import APIResponse
from app.services.academic_service import AcademicService

router = APIRouter(prefix="/branches", tags=["Branches & Academic Streams"])


@router.get("", response_model=APIResponse)
async def list_branches(
    institution_id: Optional[int] = Query(None, description="Filter by institution"),
    stream_id: Optional[int] = Query(None, description="Filter by stream"),
    db: AsyncSession = Depends(get_db),
):
    """List all configured branches with stream mappings and student counts."""
    branches = await AcademicService.list_branches(db, institution_id, stream_id)
    data = [
        {
            "id": b.id,
            "institution_id": b.institution_id,
            "stream_id": b.stream_id,
            "stream_name": b.stream.name if b.stream else None,
            "name": b.name,
            "code": b.code,
            "student_count": b.student_count,
            "is_active": b.is_active,
        }
        for b in branches
    ]
    return APIResponse(data=data, message="Branches retrieved successfully")


@router.post("", response_model=APIResponse)
async def create_branch(payload: BranchCreate, db: AsyncSession = Depends(get_db)):
    """Create a new branch in the catalogue."""
    branch = await AcademicService.create_branch(payload, db)
    return APIResponse(
        data={
            "id": branch.id,
            "institution_id": branch.institution_id,
            "stream_id": branch.stream_id,
            "name": branch.name,
            "code": branch.code,
            "student_count": branch.student_count,
            "is_active": branch.is_active,
        },
        message="Branch created successfully",
    )


@router.get("/streams", response_model=APIResponse)
async def list_streams(
    institution_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List first-year streams with aggregate student rollups and cycle splits."""
    streams = await AcademicService.list_streams(db, institution_id)
    return APIResponse(data=streams, message="Streams retrieved successfully")


@router.post("/streams", response_model=APIResponse)
async def create_stream(payload: StreamCreate, db: AsyncSession = Depends(get_db)):
    """Create a first-year stream and assign member branches."""
    stream = await AcademicService.create_stream(payload, db)
    return APIResponse(
        data={"id": stream.id, "name": stream.name, "code": stream.code},
        message="Stream created successfully",
    )


@router.post("/streams/{stream_id}/split", response_model=APIResponse)
async def split_cycle_groups(
    stream_id: int,
    payload: CycleGroupSplitRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate and update Physics/Chemistry cycle cohort student split for a stream.
    Supports EVEN, MANUAL, and CAPACITY methods.
    """
    payload.stream_id = stream_id
    try:
        result = await AcademicService.split_cycle_groups(payload, db)
        return APIResponse(data=result.model_dump(), message="Cycle split applied successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/student-counts", response_model=APIResponse)
async def update_student_counts(
    payload: BatchStudentCountUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update student intake counts across multiple branches."""
    updated = await AcademicService.update_student_counts(payload.counts, db)
    return APIResponse(
        data={"updated_count": len(updated)},
        message=f"Student counts updated for {len(updated)} branches",
    )


@router.get("/{branch_id}", response_model=APIResponse)
async def get_branch(branch_id: int, db: AsyncSession = Depends(get_db)):
    """Get single branch details."""
    branch = await AcademicService.get_branch(branch_id, db)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return APIResponse(
        data={
            "id": branch.id,
            "institution_id": branch.institution_id,
            "stream_id": branch.stream_id,
            "stream_name": branch.stream.name if branch.stream else None,
            "name": branch.name,
            "code": branch.code,
            "student_count": branch.student_count,
            "is_active": branch.is_active,
        },
        message="Branch retrieved",
    )


@router.put("/{branch_id}", response_model=APIResponse)
async def update_branch(
    branch_id: int,
    payload: BranchUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update branch attributes."""
    branch = await AcademicService.update_branch(branch_id, payload, db)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return APIResponse(
        data={
            "id": branch.id,
            "name": branch.name,
            "code": branch.code,
            "student_count": branch.student_count,
            "is_active": branch.is_active,
        },
        message="Branch updated",
    )
