import enum
from typing import List, Optional
from sqlalchemy import String, Integer, Boolean, Enum, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class SlotType(str, enum.Enum):
    THEORY = "THEORY"
    LAB = "LAB"
    BREAK = "BREAK"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'LH-101', 'Room 304'
    building: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Lab(Base):
    __tablename__ = "labs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., 'CS Lab 1', 'Electronics Hardware Lab'
    building: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # Number of workstations
    lab_type: Mapped[str] = mapped_column(String(50), default="COMPUTER", nullable=False)

    subject_mappings: Mapped[List["LabSubjectMapping"]] = relationship("LabSubjectMapping", back_populates="lab")


class LabSubjectMapping(Base):
    """
    Decouples Academic Lab Subjects from Physical Lab Resources.
    Allows multiple academic lab subjects (DSA Lab, OS Lab, IDEA Lab) to map to one physical lab.
    """
    __tablename__ = "lab_subject_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    lab_id: Mapped[int] = mapped_column(ForeignKey("labs.id"), nullable=False)

    subject: Mapped["Subject"] = relationship("app.models.academic.Subject", back_populates="lab_mappings")
    lab: Mapped["Lab"] = relationship("Lab", back_populates="subject_mappings")


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), nullable=False)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semesters.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g., 'A', 'B', 'C'
    student_count: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.id"), nullable=True)

    branch: Mapped["app.models.academic.Branch"] = relationship("app.models.academic.Branch", back_populates="sections")
    semester: Mapped["app.models.academic.Semester"] = relationship("app.models.academic.Semester", back_populates="sections")
    batches: Mapped[List["Batch"]] = relationship("Batch", back_populates="section", cascade="all, delete-orphan")


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., 'B1', 'B2', 'B3'
    student_count: Mapped[int] = mapped_column(Integer, default=20, nullable=False)

    section: Mapped["Section"] = relationship("Section", back_populates="batches")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 5=Saturday
    period_index: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3, 4, etc.
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)
    slot_type: Mapped[SlotType] = mapped_column(Enum(SlotType), default=SlotType.THEORY, nullable=False)
