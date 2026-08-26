from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from app.models.ingestion import DocumentType, DocumentCategory, DocumentStatus


class DocumentBase(BaseModel):
    file_name: str
    file_type: DocumentType
    category: DocumentCategory = DocumentCategory.GENERAL


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    id: int
    status: DocumentStatus
    file_path: Optional[str] = None
    raw_text: Optional[str] = None
    page_count: int = 1
    parsed_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class BranchCandidate(BaseModel):
    name: str
    code: str
    suggested_stream: Optional[str] = None
    confidence: float = 0.95


class SubjectCandidate(BaseModel):
    code: str
    name: str
    semester: int
    subject_type: str = "THEORY"  # "THEORY", "LAB", "INTEGRATED"
    credits: int = 3
    weekly_hours: int = 4
    cycle_group: Optional[str] = None  # "PHYSICS", "CHEMISTRY", None
    stream_code: Optional[str] = None
    confidence: float = 0.95


class FacultyCandidate(BaseModel):
    name: str
    employee_code: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    specializations: List[str] = []
    confidence: float = 0.95


class ParsedDataPayload(BaseModel):
    raw_lines_found: int = 0
    detected_category: str = "GENERAL"
    branches: List[BranchCandidate] = []
    subjects: List[SubjectCandidate] = []
    faculty: List[FacultyCandidate] = []
    summary: str = ""


class DocumentConfirmation(BaseModel):
    document_id: int
    institution_id: int = 1
    scheme_id: Optional[int] = None
    confirmed_branches: Optional[List[BranchCandidate]] = None
    confirmed_subjects: Optional[List[SubjectCandidate]] = None
    confirmed_faculty: Optional[List[FacultyCandidate]] = None


class DocumentConfirmationResult(BaseModel):
    document_id: int
    status: str
    branches_imported: int = 0
    subjects_imported: int = 0
    faculty_imported: int = 0
    message: str = "Data confirmed and saved"
