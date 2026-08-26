from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.academic import InstitutionType, TermType, SubjectType


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


class BranchBase(BaseModel):
    institution_id: int
    name: str
    code: str


class BranchCreate(BranchBase):
    pass


class BranchRead(BranchBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SubjectBase(BaseModel):
    semester_id: int
    branch_id: Optional[int] = None
    code: str
    name: str
    subject_type: SubjectType = SubjectType.THEORY
    weekly_hours: int = 4
    credits: int = 3


class SubjectCreate(SubjectBase):
    pass


class SubjectRead(SubjectBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class FacultyBase(BaseModel):
    institution_id: int
    name: str
    employee_code: str
    email: Optional[str] = None
    max_weekly_hours: int = 18


class FacultyCreate(FacultyBase):
    pass


class FacultyRead(FacultyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
