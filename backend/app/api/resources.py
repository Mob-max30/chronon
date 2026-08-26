from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.resources import RoomCreate, LabCreate, SectionCreate, BatchCreate, TimeSlotCreate
from app.schemas.contracts import APIResponse

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/rooms", response_model=APIResponse)
async def list_rooms(db: AsyncSession = Depends(get_db)):
    """List classrooms."""
    return APIResponse(data=[], message="Rooms retrieved")


@router.post("/rooms", response_model=APIResponse)
async def create_room(payload: RoomCreate, db: AsyncSession = Depends(get_db)):
    """Create a classroom."""
    return APIResponse(data={"id": 1, **payload.model_dump()}, message="Room created")


@router.get("/labs", response_model=APIResponse)
async def list_labs(db: AsyncSession = Depends(get_db)):
    """List physical hardware laboratories."""
    return APIResponse(data=[], message="Labs retrieved")


@router.post("/labs", response_model=APIResponse)
async def create_lab(payload: LabCreate, db: AsyncSession = Depends(get_db)):
    """Create a physical lab resource."""
    return APIResponse(data={"id": 1, **payload.model_dump()}, message="Lab created")
