from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.academic import BranchCreate
from app.schemas.contracts import APIResponse

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.get("", response_model=APIResponse)
async def list_branches(db: AsyncSession = Depends(get_db)):
    """List all branches/courses."""
    return APIResponse(data=[], message="Branches retrieved successfully")


@router.post("", response_model=APIResponse)
async def create_branch(payload: BranchCreate, db: AsyncSession = Depends(get_db)):
    """Create a new branch."""
    return APIResponse(data={"id": 1, **payload.model_dump()}, message="Branch created")
