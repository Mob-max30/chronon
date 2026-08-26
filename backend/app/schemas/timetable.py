from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from app.models.timetable import TimetableStatus, GenerationStatus
from app.schemas.contracts import TimetableSessionContract, ValidationResult


class TimetableBase(BaseModel):
    academic_year_id: int
    name: str
    status: TimetableStatus = TimetableStatus.DRAFT


class TimetableCreate(TimetableBase):
    pass


class TimetableRead(TimetableBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TimetableStatusUpdate(BaseModel):
    status: TimetableStatus


class TimetableVersionBase(BaseModel):
    timetable_id: int
    version_number: int
    is_active: bool = False
    notes: Optional[str] = None


class TimetableVersionCreate(BaseModel):
    timetable_id: int
    notes: Optional[str] = None


class TimetableVersionRead(BaseModel):
    id: int
    timetable_id: int
    version_number: int
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TimetableVersionDetail(TimetableVersionRead):
    sessions: List[TimetableSessionContract] = []


class VersionSessionDiff(BaseModel):
    subject_id: int
    section_id: int
    batch_id: Optional[int] = None
    old_time_slot_id: Optional[int] = None
    new_time_slot_id: Optional[int] = None
    old_room_id: Optional[int] = None
    new_room_id: Optional[int] = None
    old_faculty_id: Optional[int] = None
    new_faculty_id: Optional[int] = None
    diff_type: str = Field(..., description="ADDED | REMOVED | MODIFIED")


class VersionDiffResponse(BaseModel):
    timetable_id: int
    from_version_number: int
    to_version_number: int
    total_sessions_from: int
    total_sessions_to: int
    total_differences: int
    differences: List[VersionSessionDiff] = []


class GenerationRunBase(BaseModel):
    timetable_id: int
    triggered_by: str = "system"
    status: GenerationStatus = GenerationStatus.QUEUED


class GenerationRunCreate(GenerationRunBase):
    pass


class GenerationTriggerRequest(BaseModel):
    timetable_id: int
    academic_year_id: int
    semester_ids: List[int]
    is_joint_first_year: bool = False
    triggered_by: str = "web_user"
    max_solver_time_seconds: int = 120
    notes: Optional[str] = None


class GenerationRunRead(BaseModel):
    id: int
    timetable_id: int
    triggered_by: str
    status: GenerationStatus
    solver_time_seconds: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    quality_score: Optional[float] = None
    conflict_summary: Optional[Dict[str, Any]] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GenerationRunStatusResponse(BaseModel):
    generation_run_id: int
    timetable_id: int
    status: GenerationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    elapsed_seconds: Optional[float] = None
    quality_score: Optional[float] = None
    conflict_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    is_terminal: bool


class GenerationResultDetail(BaseModel):
    generation_run: GenerationRunRead
    version: Optional[TimetableVersionRead] = None
    validation_result: Optional[ValidationResult] = None
    total_sessions_generated: int = 0
