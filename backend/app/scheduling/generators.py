from typing import List, Tuple
from app.schemas.contracts import SchedulingInput, TimetableSessionContract
from app.scheduling.solver import ChrononCPSATSolver


def generate_single(scheduling_input: SchedulingInput) -> Tuple[str, float, List[TimetableSessionContract]]:
    """
    Generates timetable for an independent upper-semester or single semester cohort.
    """
    solver_instance = ChrononCPSATSolver(scheduling_input)
    solver_instance.build_minimal_prototype_model()
    return solver_instance.solve()


def generate_joint(sem1_input: SchedulingInput, sem2_input: SchedulingInput) -> Tuple[str, float, List[TimetableSessionContract]]:
    """
    Coordinated joint optimization for 1st Year (Physics and Chemistry cycles
    sharing common labs, faculty, and rooms across Semester 1 and Semester 2).
    """
    # Combine inputs into joint formulation
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

    solver_instance = ChrononCPSATSolver(joint_input)
    solver_instance.build_minimal_prototype_model()
    return solver_instance.solve()
