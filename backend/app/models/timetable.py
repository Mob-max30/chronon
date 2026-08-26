import enum
from typing import List, Optional, Any, Dict
from sqlalchemy import String, Integer, Boolean, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TimetableStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class GenerationStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    INFEASIBLE = "INFEASIBLE"


class Timetable(Base):
    __tablename__ = "timetables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    academic_year_id: Mapped[int] = mapped_column(ForeignKey("academic_years.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[TimetableStatus] = mapped_column(
        Enum(TimetableStatus), default=TimetableStatus.DRAFT, nullable=False
    )

    academic_year: Mapped["app.models.academic.AcademicYear"] = relationship("app.models.academic.AcademicYear", back_populates="timetables")
    versions: Mapped[List["TimetableVersion"]] = relationship("TimetableVersion", back_populates="timetable", cascade="all, delete-orphan")
    generation_runs: Mapped[List["GenerationRun"]] = relationship("GenerationRun", back_populates="timetable", cascade="all, delete-orphan")


class TimetableVersion(Base):
    __tablename__ = "timetable_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timetable_id: Mapped[int] = mapped_column(ForeignKey("timetables.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    timetable: Mapped["Timetable"] = relationship("Timetable", back_populates="versions")
    sessions: Mapped[List["TimetableSession"]] = relationship("TimetableSession", back_populates="version", cascade="all, delete-orphan")


class TimetableSession(Base):
    __tablename__ = "timetable_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("timetable_versions.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id"), nullable=False)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    batch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("batches.id"), nullable=True)
    room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    lab_id: Mapped[Optional[int]] = mapped_column(ForeignKey("labs.id"), nullable=True)
    time_slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.id"), nullable=False)

    version: Mapped["TimetableVersion"] = relationship("TimetableVersion", back_populates="sessions")


class GenerationRun(Base):
    __tablename__ = "generation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timetable_id: Mapped[int] = mapped_column(ForeignKey("timetables.id"), nullable=False)
    triggered_by: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    status: Mapped[GenerationStatus] = mapped_column(
        Enum(GenerationStatus), default=GenerationStatus.PENDING, nullable=False
    )
    solver_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    conflict_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    timetable: Mapped["Timetable"] = relationship("Timetable", back_populates="generation_runs")
