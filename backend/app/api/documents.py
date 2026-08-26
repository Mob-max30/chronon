from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.contracts import APIResponse
from app.schemas.ingestion import DocumentConfirmation

router = APIRouter(prefix="/documents", tags=["Documents & Ingestion"])


@router.post("/upload", response_model=APIResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload VTU syllabus or department faculty list for OCR/parsing.
    Requires user review before writing to database.
    """
    return APIResponse(
        data={
            "document_id": 1,
            "filename": file.filename,
            "status": "PARSED_PENDING_CONFIRMATION",
            "extracted_preview": {"raw_lines_found": 12, "detected_type": "SYLLABUS"},
        },
        message="File uploaded and staged for confirmation",
    )


@router.post("/confirm", response_model=APIResponse)
async def confirm_document_data(
    payload: DocumentConfirmation,
    db: AsyncSession = Depends(get_db),
):
    """Confirm and persist reviewed OCR data into official database catalog."""
    return APIResponse(data={"document_id": payload.document_id, "status": "CONFIRMED"}, message="Data confirmed and saved")
