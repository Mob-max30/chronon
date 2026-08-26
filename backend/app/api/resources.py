from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.resources import (
    Room,
    RoomAvailability,
    Lab,
    LabAvailability,
    LabSubjectMapping,
    Section,
    Batch,
    SlotConfig,
    TimeSlot,
    SlotType,
)
from app.models.academic import Subject
from app.schemas.resources import (
    RoomCreate,
    RoomUpdate,
    RoomRead,
    LabCreate,
    LabUpdate,
    LabRead,
    LabSubjectMappingCreate,
    LabSubjectMappingRead,
    SectionCalculateRequest,
    SectionCalculateResponse,
    SectionCreate,
    SectionUpdate,
    SectionRead,
    BatchCalculateRequest,
    BatchCalculateResponse,
    BatchCreate,
    BatchUpdate,
    BatchRead,
    SlotConfigCreate,
    SlotConfigRead,
    TimeSlotCreate,
    TimeSlotRead,
)
from app.schemas.contracts import APIResponse
from app.services.resource_calc import (
    calculate_sections,
    calculate_batches,
    generate_time_slots,
    SlotConfigInput,
    SlotBreakItem,
    CalculatedSectionItem,
    CalculatedBatchItem,
)

router = APIRouter(prefix="/resources", tags=["Resources"])


# ==============================================================================
# ROOM ENDPOINTS
# ==============================================================================
@router.get("/rooms", response_model=APIResponse)
async def list_rooms(
    institution_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """List classrooms with optional institution filter."""
    query = select(Room).options(selectinload(Room.availabilities))
    if institution_id:
        query = query.where(Room.institution_id == institution_id)
    result = await db.execute(query)
    rooms = result.scalars().all()
    rooms_data = [RoomRead.model_validate(r).model_dump() for r in rooms]
    return APIResponse(data=rooms_data, message="Rooms retrieved successfully")


@router.post("/rooms", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_room(payload: RoomCreate, db: AsyncSession = Depends(get_db)):
    """Create a classroom with optional availability windows."""
    if payload.capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room capacity must be greater than 0",
        )

    room = Room(
        institution_id=payload.institution_id,
        name=payload.name,
        building=payload.building,
        capacity=payload.capacity,
        room_type=payload.room_type,
        is_active=payload.is_active,
    )
    db.add(room)
    await db.flush()

    if payload.availabilities:
        for avail in payload.availabilities:
            ra = RoomAvailability(
                room_id=room.id,
                day_of_week=avail.day_of_week,
                start_time=avail.start_time,
                end_time=avail.end_time,
                is_available=avail.is_available,
            )
            db.add(ra)

    await db.commit()
    await db.refresh(room, ["availabilities"])
    return APIResponse(
        data=RoomRead.model_validate(room).model_dump(),
        message="Room created successfully",
    )


@router.get("/rooms/{room_id}", response_model=APIResponse)
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a single classroom by ID."""
    result = await db.execute(
        select(Room).options(selectinload(Room.availabilities)).where(Room.id == room_id)
    )
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {room_id} not found")
    return APIResponse(data=RoomRead.model_validate(room).model_dump(), message="Room retrieved")


@router.put("/rooms/{room_id}", response_model=APIResponse)
async def update_room(room_id: int, payload: RoomUpdate, db: AsyncSession = Depends(get_db)):
    """Update classroom details."""
    result = await db.execute(
        select(Room).options(selectinload(Room.availabilities)).where(Room.id == room_id)
    )
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {room_id} not found")

    if payload.name is not None:
        room.name = payload.name
    if payload.building is not None:
        room.building = payload.building
    if payload.capacity is not None:
        if payload.capacity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Capacity must be > 0")
        room.capacity = payload.capacity
    if payload.room_type is not None:
        room.room_type = payload.room_type
    if payload.is_active is not None:
        room.is_active = payload.is_active

    if payload.availabilities is not None:
        await db.execute(delete(RoomAvailability).where(RoomAvailability.room_id == room_id))
        for avail in payload.availabilities:
            db.add(
                RoomAvailability(
                    room_id=room.id,
                    day_of_week=avail.day_of_week,
                    start_time=avail.start_time,
                    end_time=avail.end_time,
                    is_available=avail.is_available,
                )
            )

    await db.commit()
    await db.refresh(room, ["availabilities"])
    return APIResponse(data=RoomRead.model_validate(room).model_dump(), message="Room updated successfully")


@router.delete("/rooms/{room_id}", response_model=APIResponse)
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a classroom."""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {room_id} not found")
    await db.delete(room)
    await db.commit()
    return APIResponse(data={"deleted_id": room_id}, message="Room deleted successfully")


# ==============================================================================
# LAB ENDPOINTS
# ==============================================================================
@router.get("/labs", response_model=APIResponse)
async def list_labs(
    institution_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """List physical laboratories with workstation capacity and count."""
    query = select(Lab).options(selectinload(Lab.availabilities))
    if institution_id:
        query = query.where(Lab.institution_id == institution_id)
    result = await db.execute(query)
    labs = result.scalars().all()
    labs_data = [LabRead.model_validate(l).model_dump() for l in labs]
    return APIResponse(data=labs_data, message="Labs retrieved successfully")


@router.post("/labs", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_lab(payload: LabCreate, db: AsyncSession = Depends(get_db)):
    """Create a physical laboratory resource."""
    if payload.capacity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lab capacity must be > 0")
    if payload.count <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lab count must be >= 1")

    lab = Lab(
        institution_id=payload.institution_id,
        name=payload.name,
        building=payload.building,
        capacity=payload.capacity,
        count=payload.count,
        lab_type=payload.lab_type,
    )
    db.add(lab)
    await db.flush()

    if payload.availabilities:
        for avail in payload.availabilities:
            la = LabAvailability(
                lab_id=lab.id,
                day_of_week=avail.day_of_week,
                start_time=avail.start_time,
                end_time=avail.end_time,
                is_available=avail.is_available,
            )
            db.add(la)

    await db.commit()
    await db.refresh(lab, ["availabilities"])
    return APIResponse(data=LabRead.model_validate(lab).model_dump(), message="Lab created successfully")


@router.get("/labs/{lab_id}", response_model=APIResponse)
async def get_lab(lab_id: int, db: AsyncSession = Depends(get_db)):
    """Get physical laboratory by ID."""
    result = await db.execute(
        select(Lab).options(selectinload(Lab.availabilities)).where(Lab.id == lab_id)
    )
    lab = result.scalar_one_or_none()
    if not lab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lab {lab_id} not found")
    return APIResponse(data=LabRead.model_validate(lab).model_dump(), message="Lab retrieved")


@router.put("/labs/{lab_id}", response_model=APIResponse)
async def update_lab(lab_id: int, payload: LabUpdate, db: AsyncSession = Depends(get_db)):
    """Update physical laboratory."""
    result = await db.execute(
        select(Lab).options(selectinload(Lab.availabilities)).where(Lab.id == lab_id)
    )
    lab = result.scalar_one_or_none()
    if not lab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lab {lab_id} not found")

    if payload.name is not None:
        lab.name = payload.name
    if payload.building is not None:
        lab.building = payload.building
    if payload.capacity is not None:
        if payload.capacity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Capacity must be > 0")
        lab.capacity = payload.capacity
    if payload.count is not None:
        if payload.count <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Count must be >= 1")
        lab.count = payload.count
    if payload.lab_type is not None:
        lab.lab_type = payload.lab_type

    if payload.availabilities is not None:
        await db.execute(delete(LabAvailability).where(LabAvailability.lab_id == lab_id))
        for avail in payload.availabilities:
            db.add(
                LabAvailability(
                    lab_id=lab.id,
                    day_of_week=avail.day_of_week,
                    start_time=avail.start_time,
                    end_time=avail.end_time,
                    is_available=avail.is_available,
                )
            )

    await db.commit()
    await db.refresh(lab, ["availabilities"])
    return APIResponse(data=LabRead.model_validate(lab).model_dump(), message="Lab updated successfully")


@router.delete("/labs/{lab_id}", response_model=APIResponse)
async def delete_lab(lab_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a laboratory."""
    result = await db.execute(select(Lab).where(Lab.id == lab_id))
    lab = result.scalar_one_or_none()
    if not lab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lab {lab_id} not found")
    await db.delete(lab)
    await db.commit()
    return APIResponse(data={"deleted_id": lab_id}, message="Lab deleted successfully")


# ==============================================================================
# LAB-SUBJECT MAPPINGS (ACADEMIC LAB -> PHYSICAL LAB DECOUPLING)
# ==============================================================================
@router.get("/labs/mappings", response_model=APIResponse)
async def list_lab_mappings(db: AsyncSession = Depends(get_db)):
    """List shared lab mappings connecting Academic Lab Subjects to Physical Labs."""
    result = await db.execute(
        select(LabSubjectMapping).options(
            selectinload(LabSubjectMapping.subject),
            selectinload(LabSubjectMapping.lab),
        )
    )
    mappings = result.scalars().all()
    data = []
    for m in mappings:
        data.append({
            "id": m.id,
            "subject_id": m.subject_id,
            "lab_id": m.lab_id,
            "subject_name": m.subject.name if m.subject else None,
            "subject_code": m.subject.code if m.subject else None,
            "lab_name": m.lab.name if m.lab else None,
        })
    return APIResponse(data=data, message="Lab subject mappings retrieved successfully")


@router.post("/labs/mappings", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_lab_mapping(payload: LabSubjectMappingCreate, db: AsyncSession = Depends(get_db)):
    """Map an academic lab subject (e.g. DSA Lab) to a physical lab (e.g. CS Lab 1)."""
    mapping = LabSubjectMapping(
        subject_id=payload.subject_id,
        lab_id=payload.lab_id,
    )
    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    return APIResponse(
        data={"id": mapping.id, "subject_id": mapping.subject_id, "lab_id": mapping.lab_id},
        message="Lab mapping created successfully",
    )


@router.delete("/labs/mappings/{mapping_id}", response_model=APIResponse)
async def delete_lab_mapping(mapping_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a lab mapping."""
    result = await db.execute(select(LabSubjectMapping).where(LabSubjectMapping.id == mapping_id))
    mapping = result.scalar_one_or_none()
    if not mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mapping {mapping_id} not found")
    await db.delete(mapping)
    await db.commit()
    return APIResponse(data={"deleted_id": mapping_id}, message="Mapping deleted successfully")


# ==============================================================================
# SECTION CALCULATION & CRUD
# ==============================================================================
@router.post("/sections/calculate", response_model=APIResponse)
async def calculate_sections_endpoint(payload: SectionCalculateRequest):
    """
    Pure, deterministic backend section calculation endpoint.
    Formula: ceil(student_count / room_capacity)
    Does NOT invoke OR-Tools or solver.
    """
    try:
        manual_sec = None
        if payload.manual_sections:
            manual_sec = [
                CalculatedSectionItem(
                    name=s.name,
                    student_count=s.student_count,
                    room_id=s.room_id,
                    stream_id=s.stream_id,
                    cycle_group=s.cycle_group,
                )
                for s in payload.manual_sections
            ]

        res = calculate_sections(
            student_count=payload.student_count,
            room_capacity=payload.room_capacity,
            naming_pattern=payload.naming_pattern,
            manual_count=payload.manual_count,
            manual_sections=manual_sec,
            stream_id=payload.stream_id,
            cycle_group=payload.cycle_group,
            balance_distribution=payload.balance_distribution,
        )
        return APIResponse(data=res.model_dump(), message="Sections calculated deterministically")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sections", response_model=APIResponse)
async def list_sections(
    branch_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """List sections with optional branch/semester filter."""
    query = select(Section)
    if branch_id:
        query = query.where(Section.branch_id == branch_id)
    if semester_id:
        query = query.where(Section.semester_id == semester_id)
    result = await db.execute(query)
    sections = result.scalars().all()
    data = [SectionRead.model_validate(s).model_dump() for s in sections]
    return APIResponse(data=data, message="Sections retrieved successfully")


@router.post("/sections", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_section(payload: SectionCreate, db: AsyncSession = Depends(get_db)):
    """Create a section."""
    section = Section(
        branch_id=payload.branch_id,
        semester_id=payload.semester_id,
        name=payload.name,
        student_count=payload.student_count,
        room_id=payload.room_id,
        stream_id=payload.stream_id,
        cycle_group=payload.cycle_group,
        is_override=payload.is_override,
    )
    db.add(section)
    await db.commit()
    await db.refresh(section)
    return APIResponse(data=SectionRead.model_validate(section).model_dump(), message="Section created successfully")


@router.put("/sections/{section_id}", response_model=APIResponse)
async def update_section(section_id: int, payload: SectionUpdate, db: AsyncSession = Depends(get_db)):
    """Update section details."""
    result = await db.execute(select(Section).where(Section.id == section_id))
    sec = result.scalar_one_or_none()
    if not sec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Section {section_id} not found")

    if payload.name is not None:
        sec.name = payload.name
    if payload.student_count is not None:
        sec.student_count = payload.student_count
    if payload.room_id is not None:
        sec.room_id = payload.room_id
    if payload.stream_id is not None:
        sec.stream_id = payload.stream_id
    if payload.cycle_group is not None:
        sec.cycle_group = payload.cycle_group
    if payload.is_override is not None:
        sec.is_override = payload.is_override

    await db.commit()
    await db.refresh(sec)
    return APIResponse(data=SectionRead.model_validate(sec).model_dump(), message="Section updated successfully")


@router.delete("/sections/{section_id}", response_model=APIResponse)
async def delete_section(section_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a section."""
    result = await db.execute(select(Section).where(Section.id == section_id))
    sec = result.scalar_one_or_none()
    if not sec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Section {section_id} not found")
    await db.delete(sec)
    await db.commit()
    return APIResponse(data={"deleted_id": section_id}, message="Section deleted successfully")


# ==============================================================================
# BATCH CALCULATION & CRUD
# ==============================================================================
@router.post("/batches/calculate", response_model=APIResponse)
async def calculate_batches_endpoint(payload: BatchCalculateRequest):
    """
    Pure, deterministic backend batch calculation endpoint.
    Formula: ceil(section_students / lab_capacity)
    Does NOT invoke OR-Tools or solver.
    """
    try:
        manual_b = None
        if payload.manual_batches:
            manual_b = [
                CalculatedBatchItem(
                    name=b.name,
                    student_count=b.student_count,
                    lab_id=b.lab_id,
                )
                for b in payload.manual_batches
            ]

        res = calculate_batches(
            section_students=payload.section_students,
            lab_capacity=payload.lab_capacity,
            naming_pattern=payload.naming_pattern,
            manual_count=payload.manual_count,
            manual_batches=manual_b,
            lab_id=payload.lab_id,
        )
        return APIResponse(data=res.model_dump(), message="Batches calculated deterministically")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/batches", response_model=APIResponse)
async def list_batches(
    section_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """List lab batches for a section."""
    query = select(Batch)
    if section_id:
        query = query.where(Batch.section_id == section_id)
    result = await db.execute(query)
    batches = result.scalars().all()
    data = [BatchRead.model_validate(b).model_dump() for b in batches]
    return APIResponse(data=data, message="Batches retrieved successfully")


@router.post("/batches", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(payload: BatchCreate, db: AsyncSession = Depends(get_db)):
    """Create a batch."""
    batch = Batch(
        section_id=payload.section_id,
        name=payload.name,
        student_count=payload.student_count,
        lab_id=payload.lab_id,
    )
    db.add(batch)
    await db.commit()
    await db.refresh(batch)
    return APIResponse(data=BatchRead.model_validate(batch).model_dump(), message="Batch created successfully")


@router.delete("/batches/{batch_id}", response_model=APIResponse)
async def delete_batch(batch_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a batch."""
    result = await db.execute(select(Batch).where(Batch.id == batch_id))
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch {batch_id} not found")
    await db.delete(batch)
    await db.commit()
    return APIResponse(data={"deleted_id": batch_id}, message="Batch deleted successfully")


# ==============================================================================
# SLOT CONFIGURATION & TIME SLOTS
# ==============================================================================
@router.get("/slot-config", response_model=APIResponse)
async def get_slot_config(
    institution_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve slot configuration for an institution."""
    result = await db.execute(
        select(SlotConfig).where(SlotConfig.institution_id == institution_id)
    )
    cfg = result.scalar_one_or_none()
    if not cfg:
        # Default configuration
        return APIResponse(
            data={
                "institution_id": institution_id,
                "name": "Standard Working Day",
                "theory_duration_minutes": 55,
                "lab_duration_minutes": 110,
                "working_days": [0, 1, 2, 3, 4, 5],
                "day_start_time": "09:00:00",
                "day_end_time": "17:00:00",
                "breaks": [{"name": "Morning Break", "start_time": "11:00:00", "end_time": "11:15:00", "slot_type": "BREAK"}],
                "lunch_break": {"name": "Lunch Break", "start_time": "13:00:00", "end_time": "14:00:00", "slot_type": "LUNCH"},
                "non_teaching_periods": [],
            },
            message="Default slot config retrieved",
        )
    return APIResponse(data=SlotConfigRead.model_validate(cfg).model_dump(), message="Slot config retrieved")


@router.post("/slot-config", response_model=APIResponse)
async def save_slot_config(payload: SlotConfigCreate, db: AsyncSession = Depends(get_db)):
    """Save or update master slot configuration."""
    result = await db.execute(
        select(SlotConfig).where(SlotConfig.institution_id == payload.institution_id)
    )
    cfg = result.scalar_one_or_none()

    breaks_data = [b.model_dump(mode="json") for b in payload.breaks]
    lunch_data = payload.lunch_break.model_dump(mode="json") if payload.lunch_break else None
    non_teaching_data = [nt.model_dump(mode="json") for nt in payload.non_teaching_periods]

    if cfg:
        cfg.name = payload.name
        cfg.theory_duration_minutes = payload.theory_duration_minutes
        cfg.lab_duration_minutes = payload.lab_duration_minutes
        cfg.working_days = payload.working_days
        cfg.day_start_time = payload.day_start_time
        cfg.day_end_time = payload.day_end_time
        cfg.breaks = breaks_data
        cfg.lunch_break = lunch_data
        cfg.non_teaching_periods = non_teaching_data
    else:
        cfg = SlotConfig(
            institution_id=payload.institution_id,
            name=payload.name,
            theory_duration_minutes=payload.theory_duration_minutes,
            lab_duration_minutes=payload.lab_duration_minutes,
            working_days=payload.working_days,
            day_start_time=payload.day_start_time,
            day_end_time=payload.day_end_time,
            breaks=breaks_data,
            lunch_break=lunch_data,
            non_teaching_periods=non_teaching_data,
        )
        db.add(cfg)

    await db.commit()
    await db.refresh(cfg)
    return APIResponse(data=SlotConfigRead.model_validate(cfg).model_dump(), message="Slot config saved successfully")


@router.post("/time-slots/generate", response_model=APIResponse)
async def generate_slots_endpoint(payload: SlotConfigCreate):
    """
    Pure generator for time slot schedules from slot configuration.
    Calculates period sequences, breaks, lunch, and working day periods.
    """
    try:
        cfg_input = SlotConfigInput(
            theory_duration_minutes=payload.theory_duration_minutes,
            lab_duration_minutes=payload.lab_duration_minutes,
            working_days=payload.working_days,
            day_start_time=payload.day_start_time,
            day_end_time=payload.day_end_time,
            breaks=[SlotBreakItem(name=b.name, start_time=b.start_time, end_time=b.end_time, slot_type=b.slot_type) for b in payload.breaks],
            lunch_break=SlotBreakItem(name=payload.lunch_break.name, start_time=payload.lunch_break.start_time, end_time=payload.lunch_break.end_time, slot_type=payload.lunch_break.slot_type) if payload.lunch_break else None,
            non_teaching_periods=[SlotBreakItem(name=nt.name, start_time=nt.start_time, end_time=nt.end_time, slot_type=nt.slot_type) for nt in payload.non_teaching_periods],
        )
        slots = generate_time_slots(cfg_input)
        return APIResponse(
            data=[s.model_dump(mode="json") for s in slots],
            message=f"Generated {len(slots)} time slots across {len(payload.working_days)} working days",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/time-slots", response_model=APIResponse)
async def list_time_slots(
    day_of_week: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """List persistent time slots."""
    query = select(TimeSlot)
    if day_of_week is not None:
        query = query.where(TimeSlot.day_of_week == day_of_week)
    result = await db.execute(query.order_by(TimeSlot.day_of_week, TimeSlot.period_index))
    slots = result.scalars().all()
    data = [TimeSlotRead.model_validate(s).model_dump() for s in slots]
    return APIResponse(data=data, message="Time slots retrieved successfully")


@router.post("/time-slots", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_time_slot(payload: TimeSlotCreate, db: AsyncSession = Depends(get_db)):
    """Create a single time slot."""
    slot = TimeSlot(
        day_of_week=payload.day_of_week,
        period_index=payload.period_index,
        start_time=payload.start_time,
        end_time=payload.end_time,
        slot_type=payload.slot_type,
        label=payload.label,
    )
    db.add(slot)
    await db.commit()
    await db.refresh(slot)
    return APIResponse(data=TimeSlotRead.model_validate(slot).model_dump(), message="Time slot created successfully")
