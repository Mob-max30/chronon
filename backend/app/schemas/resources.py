from datetime import time
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.resources import SlotType


class RoomBase(BaseModel):
    institution_id: int
    name: str
    building: Optional[str] = None
    capacity: int = 60
    is_active: bool = True


class RoomCreate(RoomBase):
    pass


class RoomRead(RoomBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class LabBase(BaseModel):
    institution_id: int
    name: str
    building: Optional[str] = None
    capacity: int = 30
    lab_type: str = "COMPUTER"


class LabCreate(LabBase):
    pass


class LabRead(LabBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SectionBase(BaseModel):
    branch_id: int
    semester_id: int
    name: str
    student_count: int = 60
    room_id: Optional[int] = None


class SectionCreate(SectionBase):
    pass


class SectionRead(SectionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BatchBase(BaseModel):
    section_id: int
    name: str
    student_count: int = 20


class BatchCreate(BatchBase):
    pass


class BatchRead(BatchBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TimeSlotBase(BaseModel):
    day_of_week: int
    period_index: int
    start_time: time
    end_time: time
    slot_type: SlotType = SlotType.THEORY


class TimeSlotCreate(TimeSlotBase):
    pass


class TimeSlotRead(TimeSlotBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
