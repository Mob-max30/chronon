from datetime import time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.resources import SlotType


# ==============================================================================
# AVAILABILITY SCHEMAS
# ==============================================================================
class RoomAvailabilityBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time
    is_available: bool = True


class RoomAvailabilityCreate(RoomAvailabilityBase):
    pass


class RoomAvailabilityRead(RoomAvailabilityBase):
    id: int
    room_id: int
    model_config = ConfigDict(from_attributes=True)


class LabAvailabilityBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time
    is_available: bool = True


class LabAvailabilityCreate(LabAvailabilityBase):
    pass


class LabAvailabilityRead(LabAvailabilityBase):
    id: int
    lab_id: int
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# ROOM SCHEMAS
# ==============================================================================
class RoomBase(BaseModel):
    institution_id: int = 1
    name: str = Field(..., min_length=1, max_length=50)
    building: Optional[str] = None
    capacity: int = Field(60, gt=0, description="Classroom capacity > 0")
    room_type: str = "LECTURE_HALL"
    is_active: bool = True


class RoomCreate(RoomBase):
    availabilities: Optional[List[RoomAvailabilityCreate]] = Field(default_factory=list)


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    building: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    room_type: Optional[str] = None
    is_active: Optional[bool] = None
    availabilities: Optional[List[RoomAvailabilityCreate]] = None


class RoomRead(RoomBase):
    id: int
    availabilities: List[RoomAvailabilityRead] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# LAB SCHEMAS
# ==============================================================================
class LabBase(BaseModel):
    institution_id: int = 1
    name: str = Field(..., min_length=1, max_length=100)
    building: Optional[str] = None
    capacity: int = Field(30, gt=0, description="Workstation capacity per lab instance > 0")
    count: int = Field(1, ge=1, description="Number of identical physical lab rooms")
    lab_type: str = "COMPUTER"


class LabCreate(LabBase):
    availabilities: Optional[List[LabAvailabilityCreate]] = Field(default_factory=list)


class LabUpdate(BaseModel):
    name: Optional[str] = None
    building: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    count: Optional[int] = Field(None, ge=1)
    lab_type: Optional[str] = None
    availabilities: Optional[List[LabAvailabilityCreate]] = None


class LabRead(LabBase):
    id: int
    availabilities: List[LabAvailabilityRead] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# LAB-SUBJECT MAPPINGS
# ==============================================================================
class LabSubjectMappingCreate(BaseModel):
    subject_id: int
    lab_id: int


class LabSubjectMappingRead(BaseModel):
    id: int
    subject_id: int
    lab_id: int
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    lab_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# SECTION CALCULATION & CRUD SCHEMAS
# ==============================================================================
class CalculatedSectionItemSchema(BaseModel):
    name: str
    student_count: int
    room_id: Optional[int] = None
    stream_id: Optional[int] = None
    cycle_group: Optional[str] = None


class SectionCalculateRequest(BaseModel):
    student_count: int = Field(..., ge=0)
    room_capacity: int = Field(..., gt=0)
    naming_pattern: str = "ALPHABETIC"
    manual_count: Optional[int] = None
    manual_sections: Optional[List[CalculatedSectionItemSchema]] = None
    stream_id: Optional[int] = None
    cycle_group: Optional[str] = None
    balance_distribution: bool = False


class SectionCalculateResponse(BaseModel):
    student_count: int
    room_capacity: int
    calculated_section_count: int
    actual_section_count: int
    is_override: bool
    sections: List[CalculatedSectionItemSchema]


class SectionBase(BaseModel):
    branch_id: int
    semester_id: int
    name: str = Field(..., min_length=1, max_length=10)
    student_count: int = Field(60, ge=0)
    room_id: Optional[int] = None
    stream_id: Optional[int] = None
    cycle_group: Optional[str] = None
    is_override: bool = False


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    name: Optional[str] = None
    student_count: Optional[int] = Field(None, ge=0)
    room_id: Optional[int] = None
    stream_id: Optional[int] = None
    cycle_group: Optional[str] = None
    is_override: Optional[bool] = None


class SectionRead(SectionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# BATCH CALCULATION & CRUD SCHEMAS
# ==============================================================================
class CalculatedBatchItemSchema(BaseModel):
    name: str
    student_count: int
    lab_id: Optional[int] = None


class BatchCalculateRequest(BaseModel):
    section_students: int = Field(..., ge=0)
    lab_capacity: int = Field(..., gt=0)
    naming_pattern: str = "B{index}"
    manual_count: Optional[int] = None
    manual_batches: Optional[List[CalculatedBatchItemSchema]] = None
    lab_id: Optional[int] = None


class BatchCalculateResponse(BaseModel):
    section_students: int
    lab_capacity: int
    calculated_batch_count: int
    actual_batch_count: int
    is_override: bool
    batches: List[CalculatedBatchItemSchema]


class BatchBase(BaseModel):
    section_id: int
    name: str = Field(..., min_length=1, max_length=20)
    student_count: int = Field(20, ge=0)
    lab_id: Optional[int] = None


class BatchCreate(BatchBase):
    pass


class BatchUpdate(BaseModel):
    name: Optional[str] = None
    student_count: Optional[int] = Field(None, ge=0)
    lab_id: Optional[int] = None


class BatchRead(BatchBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# SLOT CONFIGURATION & TIME SLOTS
# ==============================================================================
class SlotBreakSchema(BaseModel):
    name: str = "Break"
    start_time: time
    end_time: time
    slot_type: str = "BREAK"


class SlotConfigBase(BaseModel):
    institution_id: int = 1
    name: str = "Standard Working Day"
    theory_duration_minutes: int = Field(55, gt=0)
    lab_duration_minutes: int = Field(110, gt=0)
    working_days: List[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5])
    day_start_time: time = time(9, 0)
    day_end_time: time = time(17, 0)
    breaks: List[SlotBreakSchema] = Field(default_factory=list)
    lunch_break: Optional[SlotBreakSchema] = None
    non_teaching_periods: List[SlotBreakSchema] = Field(default_factory=list)


class SlotConfigCreate(SlotConfigBase):
    pass


class SlotConfigRead(SlotConfigBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TimeSlotBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    period_index: int = Field(..., ge=1)
    start_time: time
    end_time: time
    slot_type: SlotType = SlotType.THEORY
    label: Optional[str] = None


class TimeSlotCreate(TimeSlotBase):
    pass


class TimeSlotRead(TimeSlotBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

