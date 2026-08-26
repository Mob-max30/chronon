from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.academic import FacultyCreate
from app.schemas.contracts import APIResponse

router = APIRouter(prefix="/faculty", tags=["Faculty"])


@router.get("", response_model=APIResponse)
async def list_faculty(db: AsyncSession = Depends(get_db)):
    """List faculty members."""
    return APIResponse(data=[], message="Faculty list retrieved successfully")


@router.post("", response_model=APIResponse)
async def create_faculty(payload: FacultyCreate, db: AsyncSession = Depends(get_db)):
    """Create a faculty member record."""
    return APIResponse(data={"id": 1, **payload.model_dump()}, message="Faculty created")
