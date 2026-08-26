import enum
from typing import List, Optional
from sqlalchemy import String, Integer, Boolean, Enum, ForeignKey, Date, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class InstitutionType(str, enum.Enum):
    VTU_AFFILIATED = "VTU_AFFILIATED"
    AUTONOMOUS_UNIVERSITY = "AUTONOMOUS_UNIVERSITY"


class TermType(str, enum.Enum):
    ODD = "ODD"
    EVEN = "EVEN"


class SubjectType(str, enum.Enum):
    THEORY = "THEORY"
    LAB = "LAB"
    INTEGRATED = "INTEGRATED"


class CycleGroup(str, enum.Enum):
    PHYSICS = "PHYSICS"
    CHEMISTRY = "CHEMISTRY"


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type: Mapped[InstitutionType] = mapped_column(
        Enum(InstitutionType), default=InstitutionType.VTU_AFFILIATED, nullable=False
    )

    schemes: Mapped[List["Scheme"]] = relationship("Scheme", back_populates="institution", cascade="all, delete-orphan")
    branches: Mapped[List["Branch"]] = relationship("Branch", back_populates="institution", cascade="all, delete-orphan")
    streams: Mapped[List["Stream"]] = relationship("Stream", back_populates="institution", cascade="all, delete-orphan")
    faculty: Mapped[List["Faculty"]] = relationship("Faculty", back_populates="institution", cascade="all, delete-orphan")


class AcademicYear(Base):
    __tablename__ = "academic_years"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # e.g., '2026-2027'
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    start_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)

    timetables: Mapped[List["Timetable"]] = relationship("Timetable", back_populates="academic_year")


class Scheme(Base):
    __tablename__ = "schemes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., '2022 Scheme'
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    institution: Mapped["Institution"] = relationship("Institution", back_populates="schemes")
    semesters: Mapped[List["Semester"]] = relationship("Semester", back_populates="scheme", cascade="all, delete-orphan")


class Stream(Base):
    """
    First-year Stream grouping multiple branches (e.g. CSE Stream -> CSE, ISE, AIML, AIDS).
    """
    __tablename__ = "streams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    institution_id: Mapped[Optional[int]] = mapped_column(ForeignKey("institutions.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., 'CSE Stream', 'Mechanical Stream'
    code: Mapped[str] = mapped_column(String(20), nullable=False)   # e.g., 'CSE-STR', 'ME-STR'
    physics_group_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chemistry_group_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    institution: Mapped[Optional["Institution"]] = relationship("Institution", back_populates="streams")
    branches: Mapped[List["Branch"]] = relationship("Branch", back_populates="stream")
    subjects: Mapped[List["Subject"]] = relationship("Subject", back_populates="stream")


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    stream_id: Mapped[Optional[int]] = mapped_column(ForeignKey("streams.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)  # e.g., 'Computer Science & Engineering'
    code: Mapped[str] = mapped_column(String(20), nullable=False)   # e.g., 'CSE'
    student_count: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    institution: Mapped["Institution"] = relationship("Institution", back_populates="branches")
    stream: Mapped[Optional["Stream"]] = relationship("Stream", back_populates="branches")
    sections: Mapped[List["Section"]] = relationship("Section", back_populates="branch", cascade="all, delete-orphan")


class Semester(Base):
    __tablename__ = "semesters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scheme_id: Mapped[int] = mapped_column(ForeignKey("schemes.id"), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 8
    term_type: Mapped[TermType] = mapped_column(Enum(TermType), nullable=False)  # ODD or EVEN

    scheme: Mapped["Scheme"] = relationship("Scheme", back_populates="semesters")
    subjects: Mapped[List["Subject"]] = relationship("Subject", back_populates="semester", cascade="all, delete-orphan")
    sections: Mapped[List["Section"]] = relationship("Section", back_populates="semester", cascade="all, delete-orphan")


class Subject(Base):
    """
    Curriculum Subject.
    For First-Year subjects:
    - stream_id specifies the Stream (CSE, ME, EEE)
    - cycle_group specifies PHYSICS or CHEMISTRY; cycle_group = NULL indicates common subject (e.g. Maths, English)
    """
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semesters.id"), nullable=False)
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)
    stream_id: Mapped[Optional[int]] = mapped_column(ForeignKey("streams.id"), nullable=True)
    cycle_group: Mapped[Optional[CycleGroup]] = mapped_column(Enum(CycleGroup), nullable=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False)  # e.g., '21CS32', '22MATS11'
    name: Mapped[str] = mapped_column(String(200), nullable=False)  # e.g., 'Data Structures and Applications'
    subject_type: Mapped[SubjectType] = mapped_column(Enum(SubjectType), nullable=False)
    weekly_hours: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_first_year: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    semester: Mapped["Semester"] = relationship("Semester", back_populates="subjects")
    stream: Mapped[Optional["Stream"]] = relationship("Stream", back_populates="subjects")
    faculty_mappings: Mapped[List["FacultySubject"]] = relationship("FacultySubject", back_populates="subject")
    lab_mappings: Mapped[List["LabSubjectMapping"]] = relationship("LabSubjectMapping", back_populates="subject")


class Faculty(Base):
    __tablename__ = "faculty"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    max_weekly_hours: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    institution: Mapped["Institution"] = relationship("Institution", back_populates="faculty")
    subject_mappings: Mapped[List["FacultySubject"]] = relationship("FacultySubject", back_populates="faculty")


class FacultySubject(Base):
    __tablename__ = "faculty_subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    stream_id: Mapped[Optional[int]] = mapped_column(ForeignKey("streams.id"), nullable=True)
    cycle_group: Mapped[Optional[CycleGroup]] = mapped_column(Enum(CycleGroup), nullable=True)
    preference_rank: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    faculty: Mapped["Faculty"] = relationship("Faculty", back_populates="subject_mappings")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="faculty_mappings")
