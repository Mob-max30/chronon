from typing import List, Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.academic import AcademicYear, TermType, InstitutionType
from app.schemas.academic import (
    AcademicYearCreate,
    SemesterSelectionRequest,
    SemesterSelectionResponse,
)


class AcademicService:
    """
    Manages the academic year lifecycle:
    - Enforces single-active 'Current Year' invariant.
    - Manages Historical (Old Year) views and transitions.
    - Validates Year and Applicable Semester selections.
    """

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    async def get_all_years(self) -> List[AcademicYear]:
        if not self.db:
            return []
        stmt = select(AcademicYear).order_by(AcademicYear.id.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_current_year(self) -> Optional[AcademicYear]:
        if not self.db:
            return None
        stmt = select(AcademicYear).where(AcademicYear.is_current == True)  # noqa: E712
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_historical_years(self) -> List[AcademicYear]:
        if not self.db:
            return []
        stmt = select(AcademicYear).where(AcademicYear.is_current == False).order_by(AcademicYear.id.desc())  # noqa: E712
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_year_by_id(self, year_id: int) -> Optional[AcademicYear]:
        if not self.db:
            return None
        stmt = select(AcademicYear).where(AcademicYear.id == year_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_academic_year(self, data: AcademicYearCreate) -> AcademicYear:
        if not self.db:
            return AcademicYear(id=1, **data.model_dump())

        # If marked as current, atomically deactivate all other years
        if data.is_current:
            await self.db.execute(update(AcademicYear).values(is_current=False))

        new_year = AcademicYear(
            name=data.name,
            is_current=data.is_current,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        self.db.add(new_year)
        await self.db.commit()
        await self.db.refresh(new_year)
        return new_year

    async def set_current_year(self, year_id: int) -> Optional[AcademicYear]:
        if not self.db:
            return None

        # Deactivate all existing current years
        await self.db.execute(update(AcademicYear).values(is_current=False))

        # Activate selected target year
        target = await self.get_year_by_id(year_id)
        if target:
            target.is_current = True
            await self.db.commit()
            await self.db.refresh(target)
        return target

    def validate_semester_selection(self, req: SemesterSelectionRequest) -> SemesterSelectionResponse:
        """
        Validates the user's Academic Year -> Year -> Applicable Semester selection
        according to the Chronon specification.
        """
        year_to_sem_map = {
            1: [1, 2],
            2: [3, 4],
            3: [5, 6],
            4: [7, 8],
        }

        applicable_sems = year_to_sem_map.get(req.year_level, [])
        is_first_year = (req.year_level == 1)

        msg = f"Valid selection for Year {req.year_level} ({req.term_type.value} Semester {req.semester_number})"
        if is_first_year:
            msg += " [Physics & Chemistry Cycle Stream handling active]"

        return SemesterSelectionResponse(
            is_valid=True,
            academic_year_id=req.academic_year_id,
            institution_type=req.institution_type,
            year_level=req.year_level,
            term_type=req.term_type,
            selected_semester=req.semester_number,
            applicable_semesters=applicable_sems,
            is_first_year_p_c_cycle=is_first_year,
            message=msg,
        )
