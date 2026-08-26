from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.academic import SubjectCreate
from app.schemas.contracts import APIResponse

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=APIResponse)
async def list_subjects(db: AsyncSession = Depends(get_db)):
    """List curriculum subjects."""
    return APIResponse(data=[], message="Subjects retrieved successfully")


@router.post("", response_model=APIResponse)
async def create_subject(payload: SubjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a subject."""
    return APIResponse(data={"id": 1, **payload.model_dump()}, message="Subject created")
