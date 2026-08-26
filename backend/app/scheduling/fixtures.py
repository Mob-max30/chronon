from datetime import time
from app.schemas.contracts import (
    SchedulingInput,
    RoomContract,
    LabContract,
    SectionContract,
    BatchContract,
    TimeSlotContract,
    SubjectRequirement,
)


def get_sample_scheduling_input() -> SchedulingInput:
    """
    Provides a standardized sample scheduling input fixture for unit tests and local dev.
    """
    rooms = [
        RoomContract(id=1, name="LH-101", capacity=60, building="Main Block"),
        RoomContract(id=2, name="LH-102", capacity=60, building="Main Block"),
    ]
    labs = [
        LabContract(id=1, name="CS Lab 1", capacity=30, building="Computing Block", lab_type="COMPUTER"),
    ]
    sections = [
        SectionContract(id=1, branch_id=1, semester_id=3, name="3A", student_count=60, room_id=1),
        SectionContract(id=2, branch_id=1, semester_id=3, name="3B", student_count=60, room_id=2),
    ]
    batches = [
        BatchContract(id=1, section_id=1, name="3A-B1", student_count=30),
        BatchContract(id=2, section_id=1, name="3A-B2", student_count=30),
        BatchContract(id=3, section_id=2, name="3B-B1", student_count=30),
        BatchContract(id=4, section_id=2, name="3B-B2", student_count=30),
    ]
    time_slots = [
        TimeSlotContract(id=1, day_of_week=0, period_index=1, start_time=time(9, 0), end_time=time(10, 0), slot_type="THEORY"),
        TimeSlotContract(id=2, day_of_week=0, period_index=2, start_time=time(10, 0), end_time=time(11, 0), slot_type="THEORY"),
        TimeSlotContract(id=3, day_of_week=0, period_index=3, start_time=time(11, 15), end_time=time(12, 15), slot_type="THEORY"),
        TimeSlotContract(id=4, day_of_week=0, period_index=4, start_time=time(12, 15), end_time=time(13, 15), slot_type="THEORY"),
    ]
    subjects = [
        SubjectRequirement(
            subject_id=101,
            subject_code="21CS32",
            subject_name="Data Structures and Applications",
            subject_type="THEORY",
            weekly_hours=4,
            eligible_faculty_ids=[1, 2],
        ),
        SubjectRequirement(
            subject_id=102,
            subject_code="21CS33",
            subject_name="Analog and Digital Electronics",
            subject_type="THEORY",
            weekly_hours=4,
            eligible_faculty_ids=[3],
        ),
    ]

    return SchedulingInput(
        academic_year_id=1,
        semester_ids=[3],
        is_joint_first_year=False,
        rooms=rooms,
        labs=labs,
        sections=sections,
        batches=batches,
        time_slots=time_slots,
        subjects=subjects,
        max_solver_time_seconds=10,
        max_workers=2,
    )
