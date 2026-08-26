from datetime import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class GridCellSession(BaseModel):
    session_id: int
    subject_id: int
    subject_code: str
    subject_name: str
    subject_type: str = "THEORY"  # THEORY, LAB, INTEGRATED
    faculty_id: int
    faculty_name: str
    section_id: int
    section_name: str
    batch_id: Optional[int] = None
    batch_name: Optional[str] = None
    room_id: Optional[int] = None
    room_name: Optional[str] = None
    lab_id: Optional[int] = None
    lab_name: Optional[str] = None
    stream_id: Optional[int] = None
    stream_name: Optional[str] = None
    cycle_group: Optional[str] = None  # PHYSICS_CYCLE, CHEMISTRY_CYCLE
    paired_slot_group: Optional[str] = None  # e.g., 'P1', 'P2', 'P3'
    has_conflict: bool = False
    conflict_messages: List[str] = Field(default_factory=list)


class GridCell(BaseModel):
    day_of_week: int
    period_index: int
    time_slot_id: int
    time_slot_label: str
    start_time: str
    end_time: str
    slot_type: str = "THEORY"  # THEORY, LAB, BREAK, LUNCH, NON_TEACHING
    sessions: List[GridCellSession] = Field(default_factory=list)
    has_conflict: bool = False
    conflict_details: List[Dict[str, Any]] = Field(default_factory=list)


class GridRow(BaseModel):
    day_of_week: int
    day_name: str
    cells: List[GridCell] = Field(default_factory=list)


class PairedSlotGroupItem(BaseModel):
    paired_slot_group: str
    day_of_week: int
    day_name: str
    period_index: int
    time_slot_label: str
    sessions: List[GridCellSession] = Field(default_factory=list)


class TimetableMatrixResponse(BaseModel):
    timetable_id: int
    version_id: Optional[int] = None
    view_type: str  # SECTION, FACULTY, ROOM, LAB, BATCH, FIRST_YEAR_CYCLE
    filter_applied: Dict[str, Any] = Field(default_factory=dict)
    periods_header: List[Dict[str, Any]] = Field(default_factory=list)
    rows: List[GridRow] = Field(default_factory=list)
    paired_slot_groups: List[PairedSlotGroupItem] = Field(default_factory=list)
    conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    total_sessions: int = 0


class TimetableExportResponse(BaseModel):
    timetable_id: int
    version_id: Optional[int] = None
    view_type: str
    export_format: str  # CSV, JSON, HTML
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
