from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.contracts import SchedulingInput, APIResponse
from app.scheduling.generators import generate_single

router = APIRouter(prefix="/generation", tags=["Generation"])


@router.post("/trigger", response_model=APIResponse)
async def trigger_generation(
    payload: SchedulingInput,
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers deterministic CP-SAT timetable generation.
    """
    status, duration, sessions = generate_single(payload)
    return APIResponse(
        data={
            "status": status,
            "solver_time_seconds": duration,
            "total_sessions": len(sessions),
            "sessions": [s.model_dump() for s in sessions],
        },
        message="Generation completed",
    )
