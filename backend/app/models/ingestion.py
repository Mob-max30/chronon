import enum
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Enum, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class DocumentType(str, enum.Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    IMAGE = "IMAGE"


class DocumentCategory(str, enum.Enum):
    SYLLABUS = "SYLLABUS"
    BRANCH_LIST = "BRANCH_LIST"
    FACULTY_ROSTER = "FACULTY_ROSTER"
    GENERAL = "GENERAL"


class DocumentStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PARSED = "PARSED"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    category: Mapped[DocumentCategory] = mapped_column(
        Enum(DocumentCategory), default=DocumentCategory.GENERAL, nullable=False
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False
    )
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    parsed_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
