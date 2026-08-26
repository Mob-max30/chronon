from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.ingestion import DocumentType, DocumentStatus


class DocumentBase(BaseModel):
    file_name: str
    file_type: DocumentType


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    id: int
    status: DocumentStatus
    file_path: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)


class DocumentConfirmation(BaseModel):
    document_id: int
    confirmed_data: Dict[str, Any]
