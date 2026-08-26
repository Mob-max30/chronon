from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.timetable import TimetableStatus, GenerationStatus


class TimetableBase(BaseModel):
    academic_year_id: int
    name: str
    status: TimetableStatus = TimetableStatus.DRAFT


class TimetableCreate(TimetableBase):
    pass


class TimetableRead(TimetableBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TimetableVersionBase(BaseModel):
    timetable_id: int
    version_number: int = 1
    is_active: bool = False
    notes: Optional[str] = None


class TimetableVersionCreate(TimetableVersionBase):
    pass


class TimetableVersionRead(TimetableVersionBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GenerationRunBase(BaseModel):
    timetable_id: int
    triggered_by: str = "user"
    status: GenerationStatus = GenerationStatus.PENDING


class GenerationRunRead(GenerationRunBase):
    id: int
    solver_time_seconds: Optional[float] = None
    conflict_summary: Optional[Dict[str, Any]] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
