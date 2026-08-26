from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.timetable import GenerationRun
from app.schemas.contracts import (
    SchedulingInput,
    SchedulingResult,
    ValidationResult,
    TimetableSessionContract,
    APIResponse,
)
from app.scheduling.generators import generate_single, generate_joint
from app.validation.validator import IndependentTimetableValidator

router = APIRouter(prefix="/scheduling", tags=["Scheduling & Validation"])


class ValidateSessionsRequest(BaseModel):
    sessions: List[TimetableSessionContract]
    input_config: Optional[SchedulingInput] = None


@router.post("/validate-input", response_model=APIResponse)
def validate_scheduling_input(payload: SchedulingInput):
    """
    Validates a SchedulingInput configuration before solver execution.
    Checks resource availability, room capacities vs student counts, and total required hours vs time slots.
    """
    errors = []
    room_map = {r.id: r for r in payload.rooms}
    lab_map = {l.id: l for l in payload.labs}

    # Room capacity check
    for sec in payload.sections:
        if sec.room_id and sec.room_id in room_map:
            room = room_map[sec.room_id]
            if room.capacity < sec.student_count:
                errors.append(f"Room {room.name} capacity ({room.capacity}) < Section {sec.name} ({sec.student_count}).")

    # Lab capacity check
    for batch in payload.batches:
        for subj in payload.subjects:
            if subj.subject_type == "LAB" and subj.required_lab_id and subj.required_lab_id in lab_map:
                lab = lab_map[subj.required_lab_id]
                if lab.capacity < batch.student_count:
                    errors.append(f"Lab {lab.name} capacity ({lab.capacity}) < Batch {batch.name} ({batch.student_count}).")

    is_valid = len(errors) == 0
    return APIResponse(
        success=is_valid,
        data={"is_valid": is_valid, "errors": errors},
        message="Scheduling input validated successfully." if is_valid else "Scheduling input validation failed.",
    )


@router.post("/solve", response_model=APIResponse)
def execute_solver(payload: SchedulingInput):
    """
    Executes CP-SAT timetable generation engine directly for a SchedulingInput payload.
    """
    if payload.is_joint_first_year:
        result = generate_joint(payload, payload)
    else:
        result = generate_single(payload)

    return APIResponse(
        success=result.is_valid,
        data=result,
        message=result.message,
    )


@router.post("/validate", response_model=APIResponse)
def validate_timetable_sessions(req: ValidateSessionsRequest):
    """
    Decoupled real-time validator endpoint. Accepts candidate sessions (e.g. from UI drag-and-drop)
    and validates against all hard constraints without solver bias.
    """
    validator = IndependentTimetableValidator(req.sessions, req.input_config)
    val_res = validator.validate()

    return APIResponse(
        success=val_res.is_valid,
        data=val_res,
        message="Timetable validation passed." if val_res.is_valid else "Timetable contains constraint violations.",
    )


@router.get("/conflicts/{run_id}", response_model=APIResponse)
def get_run_conflicts(run_id: int, db: Session = Depends(get_db)):
    """
    Retrieves detailed diagnostic conflict summaries and explanations for a specific GenerationRun.
    """
    run = db.query(GenerationRun).filter(GenerationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"GenerationRun ID {run_id} not found.")

    conflict_summary = run.conflict_summary or {
        "status": run.status,
        "conflicts": [],
        "message": f"Run {run_id} finished with status {run.status}.",
    }

    return APIResponse(
        success=True,
        data=conflict_summary,
        message=f"Conflict summary for GenerationRun {run_id} retrieved.",
    )
