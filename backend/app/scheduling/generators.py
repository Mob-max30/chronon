import time
from typing import Tuple, List, Dict, Any
from app.schemas.contracts import (
    SchedulingInput,
    TimetableSessionContract,
    SchedulingResult,
    ValidationResult,
    ValidationError,
    QualityScore,
)
from app.scheduling.solver.solver import ChrononCPSATSolver
from app.validation.validator import IndependentTimetableValidator


def generate_single(scheduling_input: SchedulingInput) -> SchedulingResult:
    """
    Complete standalone scheduling pipeline:
    SchedulingInput -> CP-SAT Model -> Solve -> Result Conversion -> Independent Validation -> Quality Score -> SchedulingResult
    """
    start_time = time.time()

    # 1. Input pre-validation
    if not scheduling_input.subjects or not scheduling_input.time_slots or not scheduling_input.sections:
        duration = time.time() - start_time
        val_result = ValidationResult(
            is_valid=False,
            total_hard_violations=1,
            total_soft_violations=0,
            errors=[
                ValidationError(
                    rule_code="INVALID_INPUT",
                    severity="ERROR",
                    message="Scheduling input missing required subjects, sections, or time slots.",
                )
            ],
        )
        return SchedulingResult(
            status="FAILED",
            is_valid=False,
            is_optimal=False,
            sessions=[],
            validation=val_result,
            conflicts=val_result.errors,
            quality=None,
            solver_stats={},
            execution_time_seconds=round(duration, 4),
            message="Scheduling failed due to invalid/empty input configuration.",
        )

    # 2. Instantiate and build CP-SAT solver
    solver = ChrononCPSATSolver(scheduling_input)
    solver.build_model()

    # 3. Execute CP-SAT Search
    status_str, duration, sessions, quality, solver_stats = solver.solve()

    # 4. Perform Independent Validation
    validator = IndependentTimetableValidator(sessions, scheduling_input)
    validation_result = validator.validate()

    is_optimal = (status_str == "OPTIMAL")
    is_valid = validation_result.is_valid and status_str in ("OPTIMAL", "FEASIBLE")

    msg = f"Scheduler finished with status {status_str}. Independent validation: {'PASSED' if is_valid else 'FAILED'}."

    return SchedulingResult(
        status=status_str,
        is_valid=is_valid,
        is_optimal=is_optimal,
        sessions=sessions,
        validation=validation_result,
        conflicts=validation_result.errors,
        quality=quality if is_valid else None,
        solver_stats=solver_stats,
        execution_time_seconds=round(duration, 4),
        message=msg,
    )


def generate_joint(sem1_input: SchedulingInput, sem2_input: SchedulingInput) -> SchedulingResult:
    """
    Coordinated joint optimization for 1st Year (Physics and Chemistry cycles
    sharing common labs, faculty, and rooms across Semester 1 and Semester 2).
    """
    combined_subjects = list(sem1_input.subjects) + list(sem2_input.subjects)
    combined_sections = list(sem1_input.sections) + list(sem2_input.sections)
    combined_batches = list(sem1_input.batches) + list(sem2_input.batches)

    joint_input = SchedulingInput(
        academic_year_id=sem1_input.academic_year_id,
        semester_ids=sem1_input.semester_ids + sem2_input.semester_ids,
        is_joint_first_year=True,
        rooms=sem1_input.rooms,
        labs=sem1_input.labs,
        sections=combined_sections,
        batches=combined_batches,
        time_slots=sem1_input.time_slots,
        subjects=combined_subjects,
        max_solver_time_seconds=max(sem1_input.max_solver_time_seconds, sem2_input.max_solver_time_seconds),
        max_workers=sem1_input.max_workers,
    )

    return generate_single(joint_input)
