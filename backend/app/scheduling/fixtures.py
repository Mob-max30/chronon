from datetime import time
from typing import List
from app.schemas.contracts import (
    SchedulingInput,
    RoomContract,
    LabContract,
    SectionContract,
    BatchContract,
    TimeSlotContract,
    SubjectRequirement,
    FacultyAvailability,
    TimetableSessionContract,
)


def get_sample_scheduling_input() -> SchedulingInput:
    """
    Standard basic valid scheduling fixture (FIXTURE A).
    Includes multiple subjects, faculty, sections, rooms, and time slots across 5 working days (Monday-Friday).
    """
    rooms = [
        RoomContract(id=1, name="R101", capacity=60, building="Main Block"),
        RoomContract(id=2, name="R102", capacity=60, building="Main Block"),
        RoomContract(id=3, name="R103", capacity=60, building="Main Block"),
    ]
    labs = [
        LabContract(id=1, name="CS Lab 1", capacity=30, building="Computing Block", lab_type="COMPUTER"),
        LabContract(id=2, name="CS Lab 2", capacity=30, building="Computing Block", lab_type="COMPUTER"),
    ]
    sections = [
        SectionContract(id=1, branch_id=1, semester_id=3, name="Section A", student_count=60, room_id=1),
        SectionContract(id=2, branch_id=1, semester_id=3, name="Section B", student_count=60, room_id=2),
    ]
    batches = [
        BatchContract(id=1, section_id=1, name="3A-B1", student_count=30),
        BatchContract(id=2, section_id=1, name="3A-B2", student_count=30),
        BatchContract(id=3, section_id=2, name="3B-B1", student_count=30),
        BatchContract(id=4, section_id=2, name="3B-B2", student_count=30),
    ]

    # Create 5 days x 4 periods = 20 slots
    time_slots: List[TimeSlotContract] = []
    slot_id = 1
    for day in range(5):  # 0=Mon, 4=Fri
        for p in range(1, 5):  # 4 periods per day
            time_slots.append(
                TimeSlotContract(
                    id=slot_id,
                    day_of_week=day,
                    period_index=p,
                    start_time=time(9 + p - 1, 0),
                    end_time=time(10 + p - 1, 0),
                    slot_type="THEORY",
                )
            )
            slot_id += 1

    subjects = [
        SubjectRequirement(
            subject_id=101,
            subject_code="MAT301",
            subject_name="Mathematics III",
            subject_type="THEORY",
            weekly_hours=4,
            eligible_faculty_ids=[1, 2],
        ),
        SubjectRequirement(
            subject_id=102,
            subject_code="CS302",
            subject_name="Data Structures",
            subject_type="THEORY",
            weekly_hours=4,
            eligible_faculty_ids=[2, 3],
        ),
        SubjectRequirement(
            subject_id=103,
            subject_code="CS303",
            subject_name="Operating Systems",
            subject_type="THEORY",
            weekly_hours=4,
            eligible_faculty_ids=[3, 4],
        ),
        SubjectRequirement(
            subject_id=104,
            subject_code="CS304",
            subject_name="Database Systems",
            subject_type="THEORY",
            weekly_hours=4,
            eligible_faculty_ids=[1, 4],
        ),
    ]

    faculty_avail = [
        FacultyAvailability(faculty_id=1, name="F1", max_daily_hours=4),
        FacultyAvailability(faculty_id=2, name="F2", max_daily_hours=4),
        FacultyAvailability(faculty_id=3, name="F3", max_daily_hours=4),
        FacultyAvailability(faculty_id=4, name="F4", max_daily_hours=4),
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
        faculty_availability=faculty_avail,
        max_solver_time_seconds=10,
        max_workers=2,
    )


def get_faculty_conflict_fixture() -> SchedulingInput:
    """FIXTURE B: Single eligible faculty over-booked across multiple sections with tight slots."""
    base = get_sample_scheduling_input()
    limited_slots = base.time_slots[:2]  # Only 2 slots total
    subjects = [
        SubjectRequirement(
            subject_id=101,
            subject_code="MAT301",
            subject_name="Mathematics III",
            subject_type="THEORY",
            weekly_hours=2,
            eligible_faculty_ids=[1],
        ),
        SubjectRequirement(
            subject_id=102,
            subject_code="CS302",
            subject_name="Data Structures",
            subject_type="THEORY",
            weekly_hours=2,
            eligible_faculty_ids=[1],
        ),
    ]
    return SchedulingInput(
        academic_year_id=base.academic_year_id,
        semester_ids=base.semester_ids,
        is_joint_first_year=False,
        rooms=base.rooms,
        labs=base.labs,
        sections=base.sections,
        batches=base.batches,
        time_slots=limited_slots,
        subjects=subjects,
        max_solver_time_seconds=5,
        max_workers=2,
    )


def get_section_conflict_fixture() -> SchedulingInput:
    """FIXTURE C: Section required hours exceed available time slots."""
    base = get_sample_scheduling_input()
    limited_slots = base.time_slots[:2]  # 2 time slots total
    subjects = [
        SubjectRequirement(
            subject_id=101,
            subject_code="SUBJ1",
            subject_name="Subject 1",
            subject_type="THEORY",
            weekly_hours=2,
            eligible_faculty_ids=[1],
        ),
        SubjectRequirement(
            subject_id=102,
            subject_code="SUBJ2",
            subject_name="Subject 2",
            subject_type="THEORY",
            weekly_hours=2,
            eligible_faculty_ids=[2],
        ),
    ]
    return SchedulingInput(
        academic_year_id=base.academic_year_id,
        semester_ids=base.semester_ids,
        is_joint_first_year=False,
        rooms=base.rooms,
        labs=base.labs,
        sections=[base.sections[0]],  # Single section
        batches=base.batches,
        time_slots=limited_slots,
        subjects=subjects,
        max_solver_time_seconds=5,
        max_workers=2,
    )


def get_room_conflict_fixture() -> SchedulingInput:
    """FIXTURE D: Only 1 room available for 2 sections needing simultaneous slots."""
    base = get_sample_scheduling_input()
    single_room = [RoomContract(id=101, name="TinyRoom", capacity=60)]
    limited_slots = base.time_slots[:2]
    subjects = [
        SubjectRequirement(
            subject_id=101,
            subject_code="SUBJ1",
            subject_name="Subject 1",
            subject_type="THEORY",
            weekly_hours=2,
            eligible_faculty_ids=[1],
        ),
        SubjectRequirement(
            subject_id=102,
            subject_code="SUBJ2",
            subject_name="Subject 2",
            subject_type="THEORY",
            weekly_hours=2,
            eligible_faculty_ids=[2],
        ),
    ]
    sections = [
        SectionContract(id=1, branch_id=1, semester_id=3, name="Sec A", student_count=50, room_id=101),
        SectionContract(id=2, branch_id=1, semester_id=3, name="Sec B", student_count=50, room_id=101),
    ]
    return SchedulingInput(
        academic_year_id=base.academic_year_id,
        semester_ids=base.semester_ids,
        is_joint_first_year=False,
        rooms=single_room,
        labs=base.labs,
        sections=sections,
        batches=base.batches,
        time_slots=limited_slots,
        subjects=subjects,
        max_solver_time_seconds=5,
        max_workers=2,
    )


def get_capacity_conflict_fixture() -> SchedulingInput:
    """FIXTURE E: Assigned room capacity is smaller than section student count."""
    base = get_sample_scheduling_input()
    small_rooms = [RoomContract(id=1, name="Small Room", capacity=20)]  # Capacity 20
    large_sections = [SectionContract(id=1, branch_id=1, semester_id=3, name="BigSec", student_count=60, room_id=1)]
    return SchedulingInput(
        academic_year_id=base.academic_year_id,
        semester_ids=base.semester_ids,
        is_joint_first_year=False,
        rooms=small_rooms,
        labs=base.labs,
        sections=large_sections,
        batches=base.batches,
        time_slots=base.time_slots[:4],
        subjects=[base.subjects[0]],
        max_solver_time_seconds=5,
        max_workers=2,
    )


def get_lab_conflict_fixture() -> SchedulingInput:
    """FIXTURE F: Lab requirement with single available lab for concurrent batches."""
    base = get_sample_scheduling_input()
    lab_subject = SubjectRequirement(
        subject_id=201,
        subject_code="CS305L",
        subject_name="Data Structures Lab",
        subject_type="LAB",
        weekly_hours=2,
        eligible_faculty_ids=[1],
        required_lab_id=1,
    )
    return SchedulingInput(
        academic_year_id=base.academic_year_id,
        semester_ids=base.semester_ids,
        is_joint_first_year=False,
        rooms=base.rooms,
        labs=base.labs,
        sections=base.sections,
        batches=base.batches,
        time_slots=base.time_slots[:4],
        subjects=[lab_subject],
        max_solver_time_seconds=5,
        max_workers=2,
    )


def get_infeasible_fixture() -> SchedulingInput:
    """FIXTURE G: Infeasible scenario (1 time slot, 2 required classes for 1 section)."""
    base = get_sample_scheduling_input()
    single_slot = [base.time_slots[0]]  # Only 1 time slot
    subjects = [
        SubjectRequirement(
            subject_id=101,
            subject_code="SUB1",
            subject_name="Subject 1",
            subject_type="THEORY",
            weekly_hours=1,
            eligible_faculty_ids=[1],
        ),
        SubjectRequirement(
            subject_id=102,
            subject_code="SUB2",
            subject_name="Subject 2",
            subject_type="THEORY",
            weekly_hours=1,
            eligible_faculty_ids=[2],
        ),
    ]
    return SchedulingInput(
        academic_year_id=base.academic_year_id,
        semester_ids=base.semester_ids,
        is_joint_first_year=False,
        rooms=base.rooms,
        labs=base.labs,
        sections=[base.sections[0]],
        batches=base.batches,
        time_slots=single_slot,
        subjects=subjects,
        max_solver_time_seconds=3,
        max_workers=2,
    )


def get_manual_valid_timetable() -> List[TimetableSessionContract]:
    """FIXTURE H: Hand-crafted valid timetable sessions for independent validator tests."""
    return [
        TimetableSessionContract(
            id=1,
            version_id=1,
            subject_id=101,
            faculty_id=1,
            section_id=1,
            room_id=1,
            time_slot_id=1,
        ),
        TimetableSessionContract(
            id=2,
            version_id=1,
            subject_id=102,
            faculty_id=2,
            section_id=2,
            room_id=2,
            time_slot_id=1,
        ),
        TimetableSessionContract(
            id=3,
            version_id=1,
            subject_id=102,
            faculty_id=2,
            section_id=1,
            room_id=1,
            time_slot_id=2,
        ),
        TimetableSessionContract(
            id=4,
            version_id=1,
            subject_id=101,
            faculty_id=1,
            section_id=2,
            room_id=2,
            time_slot_id=2,
        ),
    ]


def get_manual_invalid_timetable() -> List[TimetableSessionContract]:
    """Hand-crafted invalid timetable with faculty and room collisions for independent validator tests."""
    return [
        TimetableSessionContract(
            id=10,
            version_id=1,
            subject_id=101,
            faculty_id=1,
            section_id=1,
            room_id=1,
            time_slot_id=1,
        ),
        # Faculty 1 double booked at time_slot_id=1
        TimetableSessionContract(
            id=11,
            version_id=1,
            subject_id=102,
            faculty_id=1,
            section_id=2,
            room_id=2,
            time_slot_id=1,
        ),
        # Room 1 double booked at time_slot_id=2
        TimetableSessionContract(
            id=12,
            version_id=1,
            subject_id=103,
            faculty_id=2,
            section_id=1,
            room_id=1,
            time_slot_id=2,
        ),
        TimetableSessionContract(
            id=13,
            version_id=1,
            subject_id=104,
            faculty_id=3,
            section_id=2,
            room_id=1,
            time_slot_id=2,
        ),
    ]


def get_first_year_joint_fixture() -> SchedulingInput:
    """
    Standard First-Year Joint Scheduling Fixture.
    Covers Semester 1 and Semester 2 with paired Physics and Chemistry cycle sections across CSE Stream.
    """
    rooms = [
        RoomContract(id=1, name="R101", capacity=60, building="1st Year Block"),
        RoomContract(id=2, name="R102", capacity=60, building="1st Year Block"),
    ]
    labs = [
        LabContract(id=1, name="Physics Lab", capacity=30, building="Science Block", lab_type="PHYSICS"),
        LabContract(id=2, name="Chemistry Lab", capacity=30, building="Science Block", lab_type="CHEMISTRY"),
    ]
    sections = [
        SectionContract(id=10, branch_id=1, semester_id=1, name="1A-PHY", student_count=60, room_id=1, stream_id=1, cycle_group="PHYSICS_CYCLE"),
        SectionContract(id=11, branch_id=1, semester_id=1, name="1B-CHEM", student_count=60, room_id=2, stream_id=1, cycle_group="CHEMISTRY_CYCLE"),
    ]
    batches = [
        BatchContract(id=101, section_id=10, name="1A-B1", student_count=30),
        BatchContract(id=102, section_id=10, name="1A-B2", student_count=30),
        BatchContract(id=111, section_id=11, name="1B-B1", student_count=30),
        BatchContract(id=112, section_id=11, name="1B-B2", student_count=30),
    ]

    # Create 5 days x 4 periods = 20 slots
    time_slots: List[TimeSlotContract] = []
    slot_id = 1
    for day in range(5):
        for p in range(1, 5):
            time_slots.append(
                TimeSlotContract(
                    id=slot_id,
                    day_of_week=day,
                    period_index=p,
                    start_time=time(9 + p - 1, 0),
                    end_time=time(10 + p - 1, 0),
                    slot_type="THEORY",
                )
            )
            slot_id += 1

    subjects = [
        SubjectRequirement(
            subject_id=501,
            subject_code="PHY101",
            subject_name="Engineering Physics",
            subject_type="THEORY",
            weekly_hours=4,
            eligible_faculty_ids=[10, 11],
            stream_id=1,
            cycle_group="PHYSICS_CYCLE",
        ),
        SubjectRequirement(
            subject_id=502,
            subject_code="CHE101",
            subject_name="Engineering Chemistry",
            subject_type="THEORY",
            weekly_hours=4,
            eligible_faculty_ids=[12, 13],
            stream_id=1,
            cycle_group="CHEMISTRY_CYCLE",
        ),
    ]

    return SchedulingInput(
        academic_year_id=1,
        semester_ids=[1, 2],
        is_joint_first_year=True,
        rooms=rooms,
        labs=labs,
        sections=sections,
        batches=batches,
        time_slots=time_slots,
        subjects=subjects,
        max_solver_time_seconds=10,
        max_workers=2,
    )

