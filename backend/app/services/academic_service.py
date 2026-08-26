import math
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.academic import (
    Branch,
    Stream,
    Subject,
    Faculty,
    FacultySubject,
    Semester,
    Scheme,
    Institution,
    SubjectType,
    CycleGroup,
)
from app.schemas.academic import (
    BranchCreate,
    BranchUpdate,
    StudentCountUpdate,
    StreamCreate,
    StreamUpdate,
    CycleGroupSplitRequest,
    CycleGroupSplitResult,
    SubjectCreate,
    SubjectUpdate,
    FacultyCreate,
    FacultyUpdate,
    FacultySubjectCreate,
)


class AcademicService:
    """
    Core business service for Academic Information Management:
    - Branch catalogue and student counts
    - First-Year Stream grouping and student rollup
    - Physics/Chemistry cycle-group cohort splitting
    - Subject curriculum management and common-subject resolution
    - Faculty roster and multi-stream subject assignments
    """

    # --- Branch & Student Count Operations ---

    @classmethod
    async def list_branches(
        cls,
        db: AsyncSession,
        institution_id: Optional[int] = None,
        stream_id: Optional[int] = None,
    ) -> List[Branch]:
        stmt = select(Branch).options(selectinload(Branch.stream))
        if institution_id:
            stmt = stmt.where(Branch.institution_id == institution_id)
        if stream_id:
            stmt = stmt.where(Branch.stream_id == stream_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_branch(cls, branch_id: int, db: AsyncSession) -> Optional[Branch]:
        stmt = select(Branch).options(selectinload(Branch.stream)).where(Branch.id == branch_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def create_branch(cls, payload: BranchCreate, db: AsyncSession) -> Branch:
        branch = Branch(
            institution_id=payload.institution_id,
            stream_id=payload.stream_id,
            name=payload.name,
            code=payload.code.upper(),
            student_count=payload.student_count,
            is_active=payload.is_active,
        )
        db.add(branch)
        await db.commit()
        await db.refresh(branch)
        return branch

    @classmethod
    async def update_branch(cls, branch_id: int, payload: BranchUpdate, db: AsyncSession) -> Optional[Branch]:
        branch = await cls.get_branch(branch_id, db)
        if not branch:
            return None
        for key, val in payload.model_dump(exclude_unset=True).items():
            setattr(branch, key, val)
        await db.commit()
        await db.refresh(branch)
        return branch

    @classmethod
    async def update_student_counts(
        cls,
        updates: List[StudentCountUpdate],
        db: AsyncSession,
    ) -> List[Branch]:
        updated_branches: List[Branch] = []
        for item in updates:
            branch = await cls.get_branch(item.branch_id, db)
            if branch:
                branch.student_count = item.student_count
                updated_branches.append(branch)
        await db.commit()
        return updated_branches

    # --- First-Year Stream & Cycle Group Engine ---

    @classmethod
    async def list_streams(cls, db: AsyncSession, institution_id: Optional[int] = None) -> List[Dict[str, Any]]:
        stmt = select(Stream).options(selectinload(Stream.branches))
        if institution_id:
            stmt = stmt.where(Stream.institution_id == institution_id)
        result = await db.execute(stmt)
        streams = result.scalars().all()

        output = []
        for s in streams:
            total_students = sum(b.student_count for b in s.branches)
            output.append({
                "id": s.id,
                "institution_id": s.institution_id,
                "name": s.name,
                "code": s.code,
                "physics_group_count": s.physics_group_count or (total_students // 2),
                "chemistry_group_count": s.chemistry_group_count or (total_students - (total_students // 2)),
                "total_students": total_students,
                "branch_count": len(s.branches),
                "branches": [{"id": b.id, "name": b.name, "code": b.code, "student_count": b.student_count} for b in s.branches],
            })
        return output

    @classmethod
    async def get_stream(cls, stream_id: int, db: AsyncSession) -> Optional[Stream]:
        stmt = select(Stream).options(selectinload(Stream.branches)).where(Stream.id == stream_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def create_stream(cls, payload: StreamCreate, db: AsyncSession) -> Stream:
        stream = Stream(
            institution_id=payload.institution_id,
            name=payload.name,
            code=payload.code.upper(),
            physics_group_count=payload.physics_group_count,
            chemistry_group_count=payload.chemistry_group_count,
        )
        db.add(stream)
        await db.flush()

        if payload.branch_ids:
            for b_id in payload.branch_ids:
                branch = await cls.get_branch(b_id, db)
                if branch:
                    branch.stream_id = stream.id

        await db.commit()
        await db.refresh(stream)
        return stream

    @classmethod
    async def update_stream(cls, stream_id: int, payload: StreamUpdate, db: AsyncSession) -> Optional[Stream]:
        stream = await cls.get_stream(stream_id, db)
        if not stream:
            return None

        update_data = payload.model_dump(exclude_unset=True, exclude={"branch_ids"})
        for key, val in update_data.items():
            setattr(stream, key, val)

        if payload.branch_ids is not None:
            # Clear old stream assignments
            for b in stream.branches:
                b.stream_id = None
            # Assign new branches
            for b_id in payload.branch_ids:
                branch = await cls.get_branch(b_id, db)
                if branch:
                    branch.stream_id = stream.id

        await db.commit()
        await db.refresh(stream)
        return stream

    @classmethod
    async def split_cycle_groups(
        cls,
        req: CycleGroupSplitRequest,
        db: AsyncSession,
    ) -> CycleGroupSplitResult:
        """
        Calculates and updates Physics/Chemistry cycle cohort student split.
        Supports:
        - EVEN: deterministic half split (ceil/floor)
        - MANUAL: user defined override
        - CAPACITY: lab-capacity constrained batching
        """
        stream = await cls.get_stream(req.stream_id, db)
        if not stream:
            raise ValueError(f"Stream with ID {req.stream_id} not found")

        total_students = sum(b.student_count for b in stream.branches)
        if total_students == 0:
            total_students = 120  # Fallback default if branches not yet assigned

        method = req.method.upper()
        note = ""

        if method == "EVEN":
            phy_count = math.ceil(total_students / 2)
            chem_count = total_students - phy_count
            note = f"Equally divided {total_students} students: {phy_count} Physics, {chem_count} Chemistry."

        elif method == "MANUAL":
            phy_count = req.physics_count or math.ceil(total_students / 2)
            chem_count = req.chemistry_count or (total_students - phy_count)
            note = f"Manual override applied: {phy_count} Physics, {chem_count} Chemistry."

        elif method == "CAPACITY":
            lab_cap = req.max_lab_capacity or 30
            # Fit physics group to multiple of lab capacity where possible
            batches = max(1, round((total_students / 2) / lab_cap))
            phy_count = min(total_students, batches * lab_cap)
            chem_count = max(0, total_students - phy_count)
            note = f"Capacity-aligned split with lab capacity {lab_cap}: {phy_count} Physics, {chem_count} Chemistry."

        else:
            phy_count = math.ceil(total_students / 2)
            chem_count = total_students - phy_count
            note = "Default even split applied."

        stream.physics_group_count = phy_count
        stream.chemistry_group_count = chem_count
        await db.commit()

        return CycleGroupSplitResult(
            stream_id=stream.id,
            stream_name=stream.name,
            total_students=total_students,
            physics_group_count=phy_count,
            chemistry_group_count=chem_count,
            split_method=method,
            note=note,
        )

    # --- Subject Management ---

    @classmethod
    async def list_subjects(
        cls,
        db: AsyncSession,
        semester_id: Optional[int] = None,
        scheme_id: Optional[int] = None,
        branch_id: Optional[int] = None,
        stream_id: Optional[int] = None,
        cycle_group: Optional[str] = None,
        subject_type: Optional[str] = None,
        is_first_year: Optional[bool] = None,
    ) -> List[Subject]:
        stmt = select(Subject).options(
            selectinload(Subject.semester),
            selectinload(Subject.stream),
            selectinload(Subject.faculty_mappings),
        )

        if semester_id:
            stmt = stmt.where(Subject.semester_id == semester_id)
        if branch_id:
            stmt = stmt.where((Subject.branch_id == branch_id) | (Subject.branch_id.is_(None)))
        if stream_id:
            stmt = stmt.where((Subject.stream_id == stream_id) | (Subject.stream_id.is_(None)))
        if cycle_group:
            if cycle_group.upper() == "COMMON":
                stmt = stmt.where(Subject.cycle_group.is_(None))
            elif cycle_group.upper() in ["PHYSICS", "CHEMISTRY"]:
                cg_enum = CycleGroup.PHYSICS if cycle_group.upper() == "PHYSICS" else CycleGroup.CHEMISTRY
                stmt = stmt.where((Subject.cycle_group == cg_enum) | (Subject.cycle_group.is_(None)))
        if subject_type:
            st_map = {"THEORY": SubjectType.THEORY, "LAB": SubjectType.LAB, "INTEGRATED": SubjectType.INTEGRATED}
            if subject_type.upper() in st_map:
                stmt = stmt.where(Subject.subject_type == st_map[subject_type.upper()])
        if is_first_year is not None:
            stmt = stmt.where(Subject.is_first_year == is_first_year)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_subject(cls, subject_id: int, db: AsyncSession) -> Optional[Subject]:
        stmt = select(Subject).options(
            selectinload(Subject.semester),
            selectinload(Subject.stream),
            selectinload(Subject.faculty_mappings),
        ).where(Subject.id == subject_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def create_subject(cls, payload: SubjectCreate, db: AsyncSession) -> Subject:
        subj = Subject(
            semester_id=payload.semester_id,
            branch_id=payload.branch_id,
            stream_id=payload.stream_id,
            cycle_group=payload.cycle_group,
            code=payload.code.upper(),
            name=payload.name,
            subject_type=payload.subject_type,
            weekly_hours=payload.weekly_hours,
            credits=payload.credits,
            is_first_year=payload.is_first_year,
        )
        db.add(subj)
        await db.commit()
        await db.refresh(subj)
        return subj

    @classmethod
    async def update_subject(cls, subject_id: int, payload: SubjectUpdate, db: AsyncSession) -> Optional[Subject]:
        subj = await cls.get_subject(subject_id, db)
        if not subj:
            return None
        for key, val in payload.model_dump(exclude_unset=True).items():
            setattr(subj, key, val)
        await db.commit()
        await db.refresh(subj)
        return subj

    @classmethod
    async def delete_subject(cls, subject_id: int, db: AsyncSession) -> bool:
        subj = await cls.get_subject(subject_id, db)
        if not subj:
            return False
        await db.delete(subj)
        await db.commit()
        return True

    # --- Faculty & Subject Mapping Management ---

    @classmethod
    async def list_faculty(
        cls,
        db: AsyncSession,
        institution_id: Optional[int] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[Faculty]:
        stmt = select(Faculty).options(selectinload(Faculty.subject_mappings).selectinload(FacultySubject.subject))
        if institution_id:
            stmt = stmt.where(Faculty.institution_id == institution_id)
        if department:
            stmt = stmt.where(Faculty.department.ilike(f"%{department}%"))
        if is_active is not None:
            stmt = stmt.where(Faculty.is_active == is_active)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_faculty(cls, faculty_id: int, db: AsyncSession) -> Optional[Faculty]:
        stmt = select(Faculty).options(
            selectinload(Faculty.subject_mappings).selectinload(FacultySubject.subject)
        ).where(Faculty.id == faculty_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def create_faculty(cls, payload: FacultyCreate, db: AsyncSession) -> Faculty:
        fac = Faculty(
            institution_id=payload.institution_id,
            name=payload.name,
            employee_code=payload.employee_code.upper(),
            email=payload.email,
            department=payload.department,
            designation=payload.designation,
            max_weekly_hours=payload.max_weekly_hours,
            is_active=payload.is_active,
        )
        db.add(fac)
        await db.flush()

        if payload.subject_mappings:
            for sm in payload.subject_mappings:
                fs = FacultySubject(
                    faculty_id=fac.id,
                    subject_id=sm.subject_id,
                    stream_id=sm.stream_id,
                    cycle_group=sm.cycle_group,
                    preference_rank=sm.preference_rank,
                    is_primary=sm.is_primary,
                )
                db.add(fs)

        await db.commit()
        await db.refresh(fac)
        return fac

    @classmethod
    async def update_faculty(cls, faculty_id: int, payload: FacultyUpdate, db: AsyncSession) -> Optional[Faculty]:
        fac = await cls.get_faculty(faculty_id, db)
        if not fac:
            return None
        for key, val in payload.model_dump(exclude_unset=True).items():
            setattr(fac, key, val)
        await db.commit()
        await db.refresh(fac)
        return fac

    @classmethod
    async def assign_subject_to_faculty(
        cls,
        faculty_id: int,
        payload: FacultySubjectCreate,
        db: AsyncSession,
    ) -> FacultySubject:
        # Check if mapping already exists
        stmt = select(FacultySubject).where(
            FacultySubject.faculty_id == faculty_id,
            FacultySubject.subject_id == payload.subject_id,
            FacultySubject.stream_id == payload.stream_id,
            FacultySubject.cycle_group == payload.cycle_group,
        )
        res = await db.execute(stmt)
        existing = res.scalars().first()

        if existing:
            existing.preference_rank = payload.preference_rank
            existing.is_primary = payload.is_primary
            await db.commit()
            await db.refresh(existing)
            return existing

        fs = FacultySubject(
            faculty_id=faculty_id,
            subject_id=payload.subject_id,
            stream_id=payload.stream_id,
            cycle_group=payload.cycle_group,
            preference_rank=payload.preference_rank,
            is_primary=payload.is_primary,
        )
        db.add(fs)
        await db.commit()
        await db.refresh(fs)
        return fs

    @classmethod
    async def get_faculty_by_subject(cls, subject_id: int, db: AsyncSession) -> List[Faculty]:
        stmt = select(Faculty).join(FacultySubject).where(
            FacultySubject.subject_id == subject_id,
            Faculty.is_active == True,
        ).distinct()
        result = await db.execute(stmt)
        return list(result.scalars().all())
