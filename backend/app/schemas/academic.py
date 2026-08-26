from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
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
    name: str
    is_current: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AcademicYearCreate(AcademicYearBase):
    pass


class AcademicYearRead(AcademicYearBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


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
