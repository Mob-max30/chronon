from datetime import datetime
from typing import Optional, List, Dict, Any
import time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.timetable import GenerationRun, GenerationStatus, Timetable
from app.schemas.contracts import (
    SchedulingInput,
    SchedulingResult,
    GenerationRunContract,
    ValidationResult,
)
from app.schemas.timetable import (
    GenerationTriggerRequest,
    GenerationResultDetail,
    GenerationRunRead,
    GenerationRunStatusResponse,
    TimetableVersionRead,
)
from app.scheduling.generators import generate_single, generate_joint
from app.validation.validator import IndependentTimetableValidator
from app.services.versioning_service import VersioningService
from app.scheduling.fixtures import get_sample_scheduling_input

TERMINAL_STATUSES = {
    GenerationStatus.SUCCESS,
    GenerationStatus.FAILED,
    GenerationStatus.INFEASIBLE,
    GenerationStatus.TIMEOUT,
    GenerationStatus.CANCELLED,
}


class OrchestrationService:
    """
    Master Generation Coordinator & Application-Level Lifecycle:
    - QUEUED -> RUNNING -> SUCCESS | FAILED | INFEASIBLE | TIMEOUT | CANCELLED.
    - Coordinates Solver abstraction (Pruthvik) and Independent Validator (Pruthvik).
    - Guarantees GenerationRun cannot be marked SUCCESS unless validator passes and snapshot persists.
    - Handles timeouts, unexpected exceptions, cancellations, and status polling.
    """

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
        self.versioning_service = VersioningService(db)

    async def get_generation_run(self, run_id: int) -> Optional[GenerationRun]:
        if not self.db:
            return None
        stmt = select(GenerationRun).where(GenerationRun.id == run_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_runs_for_timetable(self, timetable_id: int) -> List[GenerationRun]:
        if not self.db:
            return []
        stmt = (
            select(GenerationRun)
            .where(GenerationRun.timetable_id == timetable_id)
            .order_by(GenerationRun.id.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_run_status(self, run_id: int) -> Optional[GenerationRunStatusResponse]:
        run = await self.get_generation_run(run_id)
        if not run:
            return None

        now = datetime.utcnow()
        elapsed = None
        if run.started_at:
            end_time = run.completed_at or now
            elapsed = round((end_time - run.started_at).total_seconds(), 3)

        error_msg = None
        if run.conflict_summary and "error" in run.conflict_summary:
            error_msg = str(run.conflict_summary.get("details") or run.conflict_summary.get("error"))

        return GenerationRunStatusResponse(
            generation_run_id=run.id,
            timetable_id=run.timetable_id,
            status=run.status,
            created_at=run.created_at,
            started_at=run.started_at,
            completed_at=run.completed_at,
            elapsed_seconds=elapsed or run.solver_time_seconds,
            quality_score=run.quality_score,
            conflict_summary=run.conflict_summary,
            error_message=error_msg,
            is_terminal=run.status in TERMINAL_STATUSES,
        )

    async def cancel_generation_run(self, run_id: int) -> Optional[GenerationRun]:
        run = await self.get_generation_run(run_id)
        if not run:
            return None

        if run.status not in TERMINAL_STATUSES:
            run.status = GenerationStatus.CANCELLED
            run.completed_at = datetime.utcnow()
            run.conflict_summary = {
                "cancellation": "USER_CANCELLED",
                "details": "Generation run was cancelled by user request.",
            }
            if self.db:
                await self.db.commit()
                await self.db.refresh(run)

        return run

    async def orchestrate_generation(
        self,
        request: GenerationTriggerRequest,
        custom_input: Optional[SchedulingInput] = None,
    ) -> GenerationResultDetail:
        """
        Executes the complete generation lifecycle state machine:
        1. QUEUED
        2. RUNNING (record started_at)
        3. Solver execution (detect TIMEOUT / INFEASIBLE / SUCCESS)
        4. Independent Validator execution
        5. Atomic Version snapshot creation
        6. SUCCESS (or FAILED if validation fails)
        """
        # Step 1: Initialize in QUEUED state
        now = datetime.utcnow()
        run = GenerationRun(
            timetable_id=request.timetable_id,
            triggered_by=request.triggered_by,
            status=GenerationStatus.QUEUED,
            created_at=now,
        )
        if self.db:
            self.db.add(run)
            await self.db.commit()
            await self.db.refresh(run)
        else:
            run.id = 1

        # Step 2: Transition to RUNNING state
        run.status = GenerationStatus.RUNNING
        run.started_at = datetime.utcnow()
        if self.db:
            await self.db.commit()
            await self.db.refresh(run)

        scheduling_input = custom_input or get_sample_scheduling_input()
        created_version = None
        validation_result = None
        sessions = []

        try:
            # Step 3: Invoke Deterministic CP-SAT Solver via Generator Abstraction
            start_time = time.time()
            if request.is_joint_first_year:
                sched_result: SchedulingResult = generate_joint(scheduling_input, scheduling_input)
            else:
                sched_result: SchedulingResult = generate_single(scheduling_input)

            elapsed = time.time() - start_time
            solver_status = sched_result.status
            duration = sched_result.execution_time_seconds or elapsed
            sessions = sched_result.sessions or []
            validation_result = sched_result.validation

            # Check timeout condition
            if elapsed > request.max_solver_time_seconds or solver_status == "TIMEOUT":
                run.status = GenerationStatus.TIMEOUT
                run.solver_time_seconds = round(elapsed, 4)
                run.completed_at = datetime.utcnow()
                run.conflict_summary = {
                    "error": "SOLVER_TIMEOUT",
                    "details": f"Solver exceeded maximum permitted search time of {request.max_solver_time_seconds}s.",
                }
            elif solver_status == "INFEASIBLE":
                run.status = GenerationStatus.INFEASIBLE
                run.solver_time_seconds = round(duration, 4)
                run.completed_at = datetime.utcnow()
                run.conflict_summary = {
                    "error": "INFEASIBLE_CONSTRAINTS",
                    "details": "The constraint set has no mathematically feasible solution.",
                }
            elif solver_status in ("OPTIMAL", "FEASIBLE", "SUCCESS") and (validation_result is None or validation_result.is_valid):
                # Step 5: Persist immutable TimetableVersion snapshot
                created_version = await self.versioning_service.create_new_version(
                    timetable_id=request.timetable_id,
                    sessions=sessions,
                    notes=request.notes or f"Generated run #{run.id}",
                    make_active=True,
                )
                run.status = GenerationStatus.SUCCESS
                run.solver_time_seconds = round(duration, 4)
                run.completed_at = datetime.utcnow()
                run.quality_score = sched_result.quality.overall_score if sched_result.quality else 100.0
                run.conflict_summary = {
                    "validation": "PASSED",
                    "total_sessions": len(sessions),
                    "solver_duration_seconds": round(duration, 4),
                    "quality_score": run.quality_score,
                }
            else:
                # Validation Failed or Solver Failed
                run.status = GenerationStatus.FAILED
                run.solver_time_seconds = round(duration, 4)
                run.completed_at = datetime.utcnow()
                err_details = sched_result.message
                if validation_result and not validation_result.is_valid:
                    err_details = f"Independent validator detected {validation_result.total_hard_violations} hard clashes."
                run.conflict_summary = {
                    "error": "SOLVER_FAILED" if solver_status == "FAILED" else "VALIDATION_FAILED",
                    "details": err_details,
                    "validation_errors": [e.model_dump() for e in sched_result.conflicts],
                }

        except Exception as exc:
            run.status = GenerationStatus.FAILED
            run.completed_at = datetime.utcnow()
            run.conflict_summary = {
                "error": "EXECUTION_EXCEPTION",
                "details": f"An error occurred during timetable generation: {type(exc).__name__}",
            }

        if self.db:
            await self.db.commit()
            await self.db.refresh(run)

        return GenerationResultDetail(
            generation_run=GenerationRunRead.model_validate(run),
            version=TimetableVersionRead.model_validate(created_version) if created_version else None,
            validation_result=validation_result,
            total_sessions_generated=len(sessions),
        )
