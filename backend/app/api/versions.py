from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.contracts import APIResponse, TimetableSessionContract
from app.schemas.timetable import (
    TimetableVersionRead,
    TimetableVersionDetail,
    VersionDiffResponse,
)
from app.services.versioning_service import VersioningService

router = APIRouter(prefix="/versions", tags=["Timetable Versions"])


@router.get("/{timetable_id}", response_model=APIResponse)
async def get_version_history(timetable_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve complete version history list for a timetable."""
    service = VersioningService(db)
    versions = await service.get_versions_for_timetable(timetable_id)
    return APIResponse(
        data=[TimetableVersionRead.model_validate(v) for v in versions],
        message="Version history retrieved successfully",
    )


@router.get("/{timetable_id}/version/{version_id}", response_model=APIResponse)
async def get_version_detail(timetable_id: int, version_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve complete timetable version snapshot with its scheduled sessions."""
    service = VersioningService(db)
    version = await service.get_version_with_sessions(version_id)
    if not version or version.timetable_id != timetable_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timetable version not found")

    session_contracts = [
        TimetableSessionContract(
            id=s.id,
            version_id=s.version_id,
            subject_id=s.subject_id,
            faculty_id=s.faculty_id,
            section_id=s.section_id,
            batch_id=s.batch_id,
            room_id=s.room_id,
            lab_id=s.lab_id,
            time_slot_id=s.time_slot_id,
        )
        for s in (version.sessions or [])
    ]

    return APIResponse(
        data=TimetableVersionDetail(
            id=version.id,
            timetable_id=version.timetable_id,
            version_number=version.version_number,
            is_active=version.is_active,
            notes=version.notes,
            created_at=version.created_at,
            sessions=session_contracts,
        ).model_dump(),
        message="Version snapshot retrieved",
    )


@router.post("/{timetable_id}/version/{version_id}/set-active", response_model=APIResponse)
async def set_active_version(timetable_id: int, version_id: int, db: AsyncSession = Depends(get_db)):
    """Promotes/rolls back the active timetable version."""
    service = VersioningService(db)
    updated = await service.set_active_version(timetable_id, version_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return APIResponse(
        data=TimetableVersionRead.model_validate(updated),
        message=f"Version {updated.version_number} is now active",
    )


@router.post("/{timetable_id}/version/{version_id}/restore", response_model=APIResponse)
async def restore_version_as_new(
    timetable_id: int,
    version_id: int,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Restores a historical version by creating a new active copy, preserving snapshot immutability."""
    service = VersioningService(db)
    restored = await service.restore_version_as_new(timetable_id, version_id, notes=notes)
    if not restored:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return APIResponse(
        data=TimetableVersionRead.model_validate(restored),
        message=f"Version {version_id} restored as new Version {restored.version_number}",
    )


@router.get("/{timetable_id}/diff", response_model=APIResponse)
async def compare_versions(
    timetable_id: int,
    from_version_id: int = Query(..., description="Base version ID"),
    to_version_id: int = Query(..., description="Target version ID"),
    db: AsyncSession = Depends(get_db),
):
    """Computes session-by-session diff between two timetable versions."""
    service = VersioningService(db)
    v_from = await service.get_version_with_sessions(from_version_id)
    v_to = await service.get_version_with_sessions(to_version_id)

    if not v_from or not v_to or v_from.timetable_id != timetable_id or v_to.timetable_id != timetable_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both versions not found")

    diff = service.compute_version_diff(timetable_id, v_from, v_to)
    return APIResponse(
        data=diff.model_dump(),
        message="Version diff calculated successfully",
    )
