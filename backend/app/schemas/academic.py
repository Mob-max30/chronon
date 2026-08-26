from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.academic import InstitutionType, TermType, SubjectType, CycleGroup


class InstitutionBase(BaseModel):
    name: str
    code: str
    type: InstitutionType = InstitutionType.VTU_AFFILIATED


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionRead(InstitutionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class AcademicYearBase(BaseModel):
    name: str = Field(..., description="e.g. 2026-2027")
    is_current: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def validate_year_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Academic year name cannot be empty")
        return v


class AcademicYearCreate(AcademicYearBase):
    pass


class AcademicYearRead(AcademicYearBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SemesterSelectionRequest(BaseModel):
    academic_year_id: int
    institution_type: InstitutionType = InstitutionType.VTU_AFFILIATED
    year_level: int = Field(..., ge=1, le=4, description="Engineering Year: 1, 2, 3, or 4")
    term_type: TermType = Field(..., description="ODD or EVEN")
    semester_number: int = Field(..., ge=1, le=8, description="Semester Number: 1 to 8")
    is_first_year_joint: bool = False

    @field_validator("semester_number")
    @classmethod
    def validate_year_semester_compatibility(cls, v: int, info) -> int:
        data = info.data
        year_level = data.get("year_level")
        term_type = data.get("term_type")

        if year_level is not None:
            valid_semesters_for_year = {
                1: [1, 2],
                2: [3, 4],
                3: [5, 6],
                4: [7, 8],
            }
            if v not in valid_semesters_for_year.get(year_level, []):
                raise ValueError(
                    f"Semester {v} is invalid for Year {year_level}. Expected one of {valid_semesters_for_year.get(year_level)}"
                )

        if term_type is not None:
            expected_odd = (v % 2 == 1)
            if term_type == TermType.ODD and not expected_odd:
                raise ValueError(f"Semester {v} is not an ODD semester")
            elif term_type == TermType.EVEN and expected_odd:
                raise ValueError(f"Semester {v} is not an EVEN semester")

        return v


class SemesterSelectionResponse(BaseModel):
    is_valid: bool = True
    academic_year_id: int
    institution_type: InstitutionType
    year_level: int
    term_type: TermType
    selected_semester: int
    applicable_semesters: List[int]
    is_first_year_p_c_cycle: bool
    message: str


class SchemeBase(BaseModel):
    institution_id: int
    name: str
    year: int


class SchemeCreate(SchemeBase):
    pass


class SchemeRead(SchemeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SemesterBase(BaseModel):
    scheme_id: int
    number: int
    term_type: TermType = TermType.ODD


class SemesterCreate(SemesterBase):
    pass


class SemesterRead(SemesterBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Stream & Cycle Group Schemas ---

class StreamBase(BaseModel):
    institution_id: Optional[int] = None
    name: str
    code: str
    physics_group_count: int = 0
    chemistry_group_count: int = 0


class StreamCreate(StreamBase):
    branch_ids: Optional[List[int]] = None


class StreamUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    branch_ids: Optional[List[int]] = None
    physics_group_count: Optional[int] = None
    chemistry_group_count: Optional[int] = None


class StreamRead(StreamBase):
    id: int
    total_students: int = 0
    branch_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class CycleGroupSplitMethod(str):
    EVEN = "EVEN"
    MANUAL = "MANUAL"
    CAPACITY = "CAPACITY"


class CycleGroupSplitRequest(BaseModel):
    stream_id: int
    method: str = "EVEN"  # "EVEN", "MANUAL", "CAPACITY"
    physics_count: Optional[int] = None
    chemistry_count: Optional[int] = None
    max_lab_capacity: Optional[int] = None  # Used when method is CAPACITY


class CycleGroupSplitResult(BaseModel):
    stream_id: int
    stream_name: str
    total_students: int
    physics_group_count: int
    chemistry_group_count: int
    split_method: str
    note: str = ""


# --- Branch Schemas ---

class BranchBase(BaseModel):
    institution_id: int
    stream_id: Optional[int] = None
    name: str
    code: str
    student_count: int = 60
    is_active: bool = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    stream_id: Optional[int] = None
    student_count: Optional[int] = None
    is_active: Optional[bool] = None


class BranchRead(BranchBase):
    id: int
    stream_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class StudentCountUpdate(BaseModel):
    branch_id: int
    student_count: int = Field(gt=0, description="Total intake students for branch")


class BatchStudentCountUpdate(BaseModel):
    counts: List[StudentCountUpdate]


# --- Subject Schemas ---

class SubjectBase(BaseModel):
    semester_id: int
    branch_id: Optional[int] = None
    stream_id: Optional[int] = None
    cycle_group: Optional[CycleGroup] = None
    code: str
    name: str
    subject_type: SubjectType = SubjectType.THEORY
    weekly_hours: int = 4
    credits: int = 3
    is_first_year: bool = False


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    semester_id: Optional[int] = None
    branch_id: Optional[int] = None
    stream_id: Optional[int] = None
    cycle_group: Optional[CycleGroup] = None
    code: Optional[str] = None
    name: Optional[str] = None
    subject_type: Optional[SubjectType] = None
    weekly_hours: Optional[int] = None
    credits: Optional[int] = None
    is_first_year: Optional[bool] = None


class SubjectRead(SubjectBase):
    id: int
    is_common: bool = False  # Calculated: True if first year & cycle_group is None
    model_config = ConfigDict(from_attributes=True)


# --- Faculty & Mapping Schemas ---

class FacultySubjectBase(BaseModel):
    subject_id: int
    stream_id: Optional[int] = None
    cycle_group: Optional[CycleGroup] = None
    preference_rank: int = 1
    is_primary: bool = True


class FacultySubjectCreate(FacultySubjectBase):
    pass


class FacultySubjectRead(FacultySubjectBase):
    id: int
    faculty_id: int
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class FacultyBase(BaseModel):
    institution_id: int
    name: str
    employee_code: str
    email: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    max_weekly_hours: int = 18
    is_active: bool = True


class FacultyCreate(FacultyBase):
    subject_mappings: Optional[List[FacultySubjectCreate]] = None


class FacultyUpdate(BaseModel):
    name: Optional[str] = None
    employee_code: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    max_weekly_hours: Optional[int] = None
    is_active: Optional[bool] = None


class FacultyRead(FacultyBase):
    id: int
    subject_mappings: List[FacultySubjectRead] = []
    model_config = ConfigDict(from_attributes=True)
