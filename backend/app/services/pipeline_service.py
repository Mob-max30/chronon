"""
Pipeline Service: Assembles immutable SchedulingInput from live database records
across Academic Curriculum, Physical Resources, and Slot Configurations.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.academic import Subject, Faculty, FacultySubject, Stream, Branch
from app.models.resources import Room, Lab, Section, Batch, TimeSlot, LabSubjectMapping
from app.schemas.contracts import (
    SchedulingInput,
    RoomContract,
    LabContract,
    SectionContract,
    BatchContract,
    TimeSlotContract,
    SubjectRequirement,
    FacultyAvailability,
    ObjectiveWeights,
)
from app.scheduling.fixtures import get_sample_scheduling_input


async def build_scheduling_input_from_db(
    db: AsyncSession,
    academic_year_id: int,
    semester_ids: List[int],
    is_joint_first_year: bool = False,
    max_solver_time_seconds: int = 120,
    max_workers: int = 8,
) -> SchedulingInput:
    """
    Constructs a validated, frozen SchedulingInput contract by querying:
    - Active Rooms and Labs
    - Sections and partitioned Batches
    - TimeSlot periods across working days
    - Subject curriculum requirements and mapped faculty
    """
    # 1. Fetch Rooms
    room_stmt = select(Room).where(Room.is_active == True)  # noqa: E712
    room_res = await db.execute(room_stmt)
    db_rooms = room_res.scalars().all()
    rooms: List[RoomContract] = [
        RoomContract(
            id=r.id,
            name=r.name,
            capacity=r.capacity,
            building=r.building,
            is_available=r.is_active,
        )
        for r in db_rooms
    ]

    # 2. Fetch Labs
    lab_stmt = select(Lab)
    lab_res = await db.execute(lab_stmt)
    db_labs = lab_res.scalars().all()
    labs: List[LabContract] = [
        LabContract(
            id=l.id,
            name=l.name,
            capacity=l.capacity,
            building=l.building,
            lab_type=l.lab_type.value if hasattr(l.lab_type, "value") else str(l.lab_type),
            is_available=True,
        )
        for l in db_labs
    ]

    # 3. Fetch Sections
    sec_stmt = select(Section).where(Section.semester_id.in_(semester_ids))
    sec_res = await db.execute(sec_stmt)
    db_sections = sec_res.scalars().all()
    sections: List[SectionContract] = [
        SectionContract(
            id=s.id,
            branch_id=s.branch_id or 1,
            semester_id=s.semester_id,
            name=s.name,
            student_count=s.student_count,
            room_id=s.room_id,
        )
        for s in db_sections
    ]

    # 4. Fetch Batches
    sec_ids = [s.id for s in db_sections]
    batches: List[BatchContract] = []
    if sec_ids:
        batch_stmt = select(Batch).where(Batch.section_id.in_(sec_ids))
        batch_res = await db.execute(batch_stmt)
        db_batches = batch_res.scalars().all()
        batches = [
            BatchContract(
                id=b.id,
                section_id=b.section_id,
                name=b.name,
                student_count=b.student_count,
            )
            for b in db_batches
        ]

    # 5. Fetch Time Slots
    slot_stmt = select(TimeSlot).order_by(TimeSlot.day_of_week, TimeSlot.period_index)
    slot_res = await db.execute(slot_stmt)
    db_slots = slot_res.scalars().all()
    time_slots: List[TimeSlotContract] = [
        TimeSlotContract(
            id=ts.id,
            day_of_week=ts.day_of_week,
            period_index=ts.period_index,
            start_time=ts.start_time,
            end_time=ts.end_time,
            slot_type=ts.slot_type.value if hasattr(ts.slot_type, "value") else str(ts.slot_type),
        )
        for ts in db_slots
    ]

    # 6. Fetch Subjects & Faculty Mappings
    subj_stmt = (
        select(Subject)
        .options(selectinload(Subject.faculty_mappings))
        .where(Subject.semester_id.in_(semester_ids))
    )
    subj_res = await db.execute(subj_stmt)
    db_subjects = subj_res.scalars().all()

    # Fetch Lab Mappings for Subjects
    mapping_stmt = select(LabSubjectMapping)
    mapping_res = await db.execute(mapping_stmt)
    lab_mappings = {m.subject_id: m.lab_id for m in mapping_res.scalars().all()}

    subjects: List[SubjectRequirement] = []
    for s in db_subjects:
        eligible_fac = [m.faculty_id for m in s.faculty_mappings]
        if not eligible_fac:
            # Fallback if no faculty assigned yet
            eligible_fac = [1]
        req_lab = lab_mappings.get(s.id)
        subjects.append(
            SubjectRequirement(
                subject_id=s.id,
                subject_code=s.code,
                subject_name=s.name,
                subject_type=s.subject_type.value if hasattr(s.subject_type, "value") else str(s.subject_type),
                weekly_hours=s.weekly_hours,
                eligible_faculty_ids=eligible_fac,
                required_lab_id=req_lab,
            )
        )

    # 7. Fetch Faculty
    fac_stmt = select(Faculty).where(Faculty.is_active == True)  # noqa: E712
    fac_res = await db.execute(fac_stmt)
    db_faculty = fac_res.scalars().all()
    faculty_availability: List[FacultyAvailability] = [
        FacultyAvailability(
            faculty_id=f.id,
            name=f.name,
            unavailable_slot_ids=[],
            max_daily_hours=6,
        )
        for f in db_faculty
    ]

    # Fallback to rich sample if DB records are empty (for initial fresh environments)
    if not subjects or not sections or not time_slots:
        return get_sample_scheduling_input()

    return SchedulingInput(
        academic_year_id=academic_year_id,
        semester_ids=semester_ids,
        is_joint_first_year=is_joint_first_year,
        rooms=rooms,
        labs=labs,
        sections=sections,
        batches=batches,
        time_slots=time_slots,
        subjects=subjects,
        faculty_availability=faculty_availability,
        objective_weights=ObjectiveWeights(),
        max_solver_time_seconds=max_solver_time_seconds,
        max_workers=max_workers,
    )
