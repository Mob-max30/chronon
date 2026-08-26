from datetime import datetime, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ==============================================================================
# 1. API ERROR & RESPONSE WRAPPERS
# ==============================================================================
class APIErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class APIErrorResponse(BaseModel):
    success: bool = False
    error: APIErrorDetail


class APIResponse(BaseModel):
    success: bool = True
    data: Any
    message: Optional[str] = None


# ==============================================================================
# 2. VALIDATION CONTRACTS (DECOUPLED FROM SOLVER)
# ==============================================================================
class ValidationError(BaseModel):
    rule_code: str = Field(..., description="Unique error code (e.g. FACULTY_CLASH, ROOM_CLASH)")
    severity: str = Field("ERROR", description="'ERROR' (Hard Constraint) or 'WARNING' (Soft Constraint)")
    message: str
    session_ids: List[int] = Field(default_factory=list)
    conflicting_resource_id: Optional[int] = None
    time_slot_id: Optional[int] = None


class ValidationResult(BaseModel):
    is_valid: bool
    total_hard_violations: int = 0
    total_soft_violations: int = 0
    errors: List[ValidationError] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# 3. FIRST-YEAR STREAMS & CYCLE GROUPS
# ==============================================================================
class CycleGroupContract(BaseModel):
    cycle_name: str = Field(..., description="'PHYSICS_CYCLE' or 'CHEMISTRY_CYCLE'")
    semester_number: int  # 1 or 2
    subject_ids: List[int]
    section_ids: List[int]


class StreamContract(BaseModel):
    id: int
    name: str
    code: str
    branch_id: int
    cycle_groups: List[CycleGroupContract] = Field(default_factory=list)


# ==============================================================================
# 4. RESOURCE REPRESENTATIONS
# ==============================================================================
class RoomContract(BaseModel):
    id: int
    name: str
    capacity: int
    building: Optional[str] = None


class LabContract(BaseModel):
    id: int
    name: str
    capacity: int  # Workstations count
    building: Optional[str] = None
    lab_type: str = "COMPUTER"


class SectionContract(BaseModel):
    id: int
    branch_id: int
    semester_id: int
    name: str
    student_count: int
    room_id: Optional[int] = None


class BatchContract(BaseModel):
    id: int
    section_id: int
    name: str
    student_count: int


class TimeSlotContract(BaseModel):
    id: int
    day_of_week: int  # 0=Monday, 5=Saturday
    period_index: int
    start_time: time
    end_time: time
    slot_type: str = "THEORY"  # THEORY, LAB, BREAK


# ==============================================================================
# 5. SCHEDULING INPUT CONTRACT (IMMUTABLE PAYLOAD GIVEN TO SOLVER)
# ==============================================================================
class SubjectRequirement(BaseModel):
    subject_id: int
    subject_code: str
    subject_name: str
    subject_type: str  # THEORY, LAB, INTEGRATED
    weekly_hours: int
    eligible_faculty_ids: List[int]
    required_lab_id: Optional[int] = None


class SchedulingInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    academic_year_id: int
    semester_ids: List[int]
    is_joint_first_year: bool = False
    rooms: List[RoomContract]
    labs: List[LabContract]
    sections: List[SectionContract]
    batches: List[BatchContract]
    time_slots: List[TimeSlotContract]
    subjects: List[SubjectRequirement]
    max_solver_time_seconds: int = 120
    max_workers: int = 8


# ==============================================================================
# 6. TIMETABLE SESSION & VERSION CONTRACTS
# ==============================================================================
class TimetableSessionContract(BaseModel):
    id: Optional[int] = None
    version_id: int
    subject_id: int
    faculty_id: int
    section_id: int
    batch_id: Optional[int] = None
    room_id: Optional[int] = None
    lab_id: Optional[int] = None
    time_slot_id: int


class TimetableVersionContract(BaseModel):
    id: int
    timetable_id: int
    version_number: int
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    sessions: List[TimetableSessionContract] = Field(default_factory=list)


class GenerationRunContract(BaseModel):
    id: int
    timetable_id: int
    triggered_by: str
    status: str  # PENDING, RUNNING, SUCCESS, FAILED, INFEASIBLE
    solver_time_seconds: Optional[float] = None
    conflict_summary: Optional[Dict[str, Any]] = None
    created_at: datetime
