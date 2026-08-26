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

router = APIRouter(prefix="/generation", tags=["Generation Orchestration & Lifecycle"])


@router.post("/trigger", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def trigger_generation(
    payload: GenerationTriggerRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger end-to-end timetable generation:
    1. Records QUEUED state.
    2. Transitions to RUNNING.
    3. Executes CP-SAT solver.
    4. Runs Independent Validator.
    5. Persists TimetableVersion snapshot on success.
    """
    service = OrchestrationService(db)
    result = await service.orchestrate_generation(payload)
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
