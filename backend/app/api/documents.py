from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.contracts import APIResponse
from app.schemas.ingestion import DocumentConfirmation
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/documents", tags=["Documents & VTU Ingestion"])
ingestion_service = IngestionService()


@router.post("/upload", response_model=APIResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload VTU syllabus, branch affiliation list, or department faculty roster.
    Extracts text (PDF/DOCX/OCR), parses domain candidates, and stages for user review.
    """
    try:
        doc = await ingestion_service.stage_document(file, db)
        return APIResponse(
            data={
                "document_id": doc.id,
                "file_name": doc.file_name,
                "file_type": doc.file_type.value,
                "category": doc.category.value,
                "status": doc.status.value,
                "page_count": doc.page_count,
                "parsed_data": doc.parsed_data,
            },
            message="Document uploaded and candidates extracted for review",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.get("", response_model=APIResponse)
async def list_documents(db: AsyncSession = Depends(get_db)):
    """List all staged and confirmed documents."""
    docs = await ingestion_service.list_documents(db)
    data = [
        {
            "id": d.id,
            "file_name": d.file_name,
            "file_type": d.file_type.value,
            "category": d.category.value,
            "status": d.status.value,
            "page_count": d.page_count,
            "summary": d.parsed_data.get("summary") if d.parsed_data else None,
        }
        for d in docs
    ]
    return APIResponse(data=data, message="Documents list retrieved")


@router.get("/{document_id}", response_model=APIResponse)
async def get_document_preview(document_id: int, db: AsyncSession = Depends(get_db)):
    """Get extracted candidates and details for a specific document review."""
    doc = await ingestion_service.get_document(document_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return APIResponse(
        data={
            "id": doc.id,
            "file_name": doc.file_name,
            "file_type": doc.file_type.value,
            "category": doc.category.value,
            "status": doc.status.value,
            "page_count": doc.page_count,
            "raw_text": doc.raw_text,
            "parsed_data": doc.parsed_data,
        },
        message="Document details retrieved",
    )


@router.post("/confirm", response_model=APIResponse)
@router.post("/{document_id}/confirm", response_model=APIResponse)
async def confirm_document_data(
    payload: DocumentConfirmation,
    document_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm and persist reviewed candidate entities (branches, subjects, faculty)
    into the authoritative database catalog.
    """
    if document_id:
        payload.document_id = document_id
    try:
        result = await ingestion_service.confirm_and_persist(payload, db)
        return APIResponse(data=result.model_dump(), message="Data confirmed and committed to catalog")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Confirmation failed: {str(e)}")
