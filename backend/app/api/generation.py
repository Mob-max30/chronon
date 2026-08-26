from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.timetable import (
    GenerationTriggerRequest,
    GenerationResultDetail,
    GenerationRunRead,
    GenerationRunStatusResponse,
)
from app.schemas.contracts import APIResponse
from app.services.orchestration_service import OrchestrationService
from app.services.pipeline_service import build_scheduling_input_from_db

router = APIRouter(prefix="/generation", tags=["Generation Orchestration & Lifecycle"])


@router.post("/trigger", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def trigger_generation(
    payload: GenerationTriggerRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger end-to-end timetable generation:
    1. Loads active curriculum, faculty, rooms, labs, and slots from DB.
    2. Records QUEUED state.
    3. Transitions to RUNNING.
    4. Executes CP-SAT solver.
    5. Runs Independent Validator.
    6. Persists TimetableVersion snapshot on success.
    """
    service = OrchestrationService(db)
    scheduling_input = await build_scheduling_input_from_db(
        db=db,
        academic_year_id=payload.academic_year_id,
        semester_ids=payload.semester_ids,
        is_joint_first_year=payload.is_joint_first_year,
        max_solver_time_seconds=payload.max_solver_time_seconds,
    )
    result = await service.orchestrate_generation(payload, custom_input=scheduling_input)
    return APIResponse(
        data=result.model_dump(),
        message=f"Generation run completed with status: {result.generation_run.status}",
    )


@router.get("/runs/{run_id}", response_model=APIResponse)
async def get_generation_run_status(run_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve real-time generation run status for frontend polling,
    including elapsed time, terminal state flag, quality score, and structured conflict summary.
    """
    service = OrchestrationService(db)
    status_response = await service.get_run_status(run_id)
    if not status_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation run with ID {run_id} not found",
        )
    return APIResponse(
        data=status_response.model_dump(),
        message="Generation run status retrieved",
    )


@router.post("/runs/{run_id}/cancel", response_model=APIResponse)
async def cancel_generation_run(run_id: int, db: AsyncSession = Depends(get_db)):
    """
    Cancel an active or queued generation run.
    """
    service = OrchestrationService(db)
    cancelled = await service.cancel_generation_run(run_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation run with ID {run_id} not found",
        )
    return APIResponse(
        data=GenerationRunRead.model_validate(cancelled),
        message="Generation run cancelled successfully",
    )


@router.get("/timetable/{timetable_id}/runs", response_model=APIResponse)
async def get_timetable_runs(timetable_id: int, db: AsyncSession = Depends(get_db)):
    """List all generation runs recorded for a timetable container."""
    service = OrchestrationService(db)
    runs = await service.get_runs_for_timetable(timetable_id)
    return APIResponse(
        data=[GenerationRunRead.model_validate(r) for r in runs],
        message="Timetable generation runs retrieved",
    )


# Additional router to satisfy Section 47 canonical specification (/api/v1/generation-runs)
runs_router = APIRouter(prefix="/generation-runs", tags=["Generation Runs Canonical API"])


@runs_router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def trigger_generation_canonical(
    payload: GenerationTriggerRequest,
    db: AsyncSession = Depends(get_db),
):
    """Canonical trigger endpoint matching Section 47 specification: POST /api/v1/generation-runs"""
    return await trigger_generation(payload, db)


@runs_router.get("/{run_id}", response_model=APIResponse)
async def get_generation_run_status_canonical(run_id: int, db: AsyncSession = Depends(get_db)):
    """Canonical status endpoint matching Section 47 specification: GET /api/v1/generation-runs/{id}"""
    return await get_generation_run_status(run_id, db)


@runs_router.post("/{run_id}/cancel", response_model=APIResponse)
async def cancel_generation_run_canonical(run_id: int, db: AsyncSession = Depends(get_db)):
    """Canonical cancellation endpoint matching Section 47 specification: POST /api/v1/generation-runs/{id}/cancel"""
    return await cancel_generation_run(run_id, db)
