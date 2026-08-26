import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.academic import (
    Institution,
    InstitutionType,
    Scheme,
    Semester,
    TermType,
    Branch,
    Stream,
    Subject,
    Faculty,
    SubjectType,
    CycleGroup,
)
from app.schemas.academic import (
    BranchCreate,
    BranchUpdate,
    StudentCountUpdate,
    StreamCreate,
    CycleGroupSplitRequest,
    SubjectCreate,
    SubjectUpdate,
    FacultyCreate,
    FacultySubjectCreate,
)
from app.services.academic_service import AcademicService

# In-memory SQLite async DB for fast testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        # Seed basic institution, scheme, semester
        inst = Institution(name="VTU Autonomous Test College", code="VTU-TEST", type=InstitutionType.VTU_AFFILIATED)
        session.add(inst)
        await session.flush()

        scheme = Scheme(institution_id=inst.id, name="2022 Scheme", year=2022)
        session.add(scheme)
        await session.flush()

        sem1 = Semester(scheme_id=scheme.id, number=1, term_type=TermType.ODD)
        sem2 = Semester(scheme_id=scheme.id, number=2, term_type=TermType.EVEN)
        sem3 = Semester(scheme_id=scheme.id, number=3, term_type=TermType.ODD)
        session.add_all([sem1, sem2, sem3])
        await session.commit()

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_branch_and_student_counts(test_db_session: AsyncSession):
    """Test branch creation and student intake count management."""
    b1 = await AcademicService.create_branch(
        BranchCreate(institution_id=1, name="Computer Science & Engineering", code="CSE", student_count=180),
        test_db_session,
    )
    b2 = await AcademicService.create_branch(
        BranchCreate(institution_id=1, name="Information Science & Engineering", code="ISE", student_count=120),
        test_db_session,
    )
    assert b1.id is not None
    assert b1.code == "CSE"
    assert b1.student_count == 180

    # Batch update student counts
    updated = await AcademicService.update_student_counts(
        [
            StudentCountUpdate(branch_id=b1.id, student_count=240),
            StudentCountUpdate(branch_id=b2.id, student_count=150),
        ],
        test_db_session,
    )
    assert len(updated) == 2
    b1_refreshed = await AcademicService.get_branch(b1.id, test_db_session)
    assert b1_refreshed.student_count == 240


@pytest.mark.asyncio
async def test_first_year_stream_rollup_and_cycle_splits(test_db_session: AsyncSession):
    """Test first-year stream creation, branch rollup, and cycle group splits."""
    b1 = await AcademicService.create_branch(
        BranchCreate(institution_id=1, name="CSE", code="CSE", student_count=180),
        test_db_session,
    )
    b2 = await AcademicService.create_branch(
        BranchCreate(institution_id=1, name="ISE", code="ISE", student_count=120),
        test_db_session,
    )
    b3 = await AcademicService.create_branch(
        BranchCreate(institution_id=1, name="AIML", code="AIML", student_count=60),
        test_db_session,
    )

    # Create CSE Stream grouping CSE + ISE + AIML
    stream = await AcademicService.create_stream(
        StreamCreate(
            institution_id=1,
            name="CSE Stream",
            code="CSE-STR",
            branch_ids=[b1.id, b2.id, b3.id],
        ),
        test_db_session,
    )
    assert stream.id is not None

    # Verify stream rollup
    streams_list = await AcademicService.list_streams(test_db_session, institution_id=1)
    cse_stream = next(s for s in streams_list if s["id"] == stream.id)
    assert cse_stream["total_students"] == 360  # 180 + 120 + 60
    assert cse_stream["branch_count"] == 3

    # Test EVEN split
    even_split = await AcademicService.split_cycle_groups(
        CycleGroupSplitRequest(stream_id=stream.id, method="EVEN"),
        test_db_session,
    )
    assert even_split.physics_group_count == 180
    assert even_split.chemistry_group_count == 180

    # Test MANUAL split
    manual_split = await AcademicService.split_cycle_groups(
        CycleGroupSplitRequest(stream_id=stream.id, method="MANUAL", physics_count=200, chemistry_count=160),
        test_db_session,
    )
    assert manual_split.physics_group_count == 200
    assert manual_split.chemistry_group_count == 160

    # Test CAPACITY split (lab capacity 30)
    capacity_split = await AcademicService.split_cycle_groups(
        CycleGroupSplitRequest(stream_id=stream.id, method="CAPACITY", max_lab_capacity=30),
        test_db_session,
    )
    assert capacity_split.physics_group_count % 30 == 0


@pytest.mark.asyncio
async def test_subject_management_and_common_representation(test_db_session: AsyncSession):
    """Test subject creation with Theory/Lab, First-Year common subjects vs cycle-specific."""
    # Common 1st year Math
    math_sub = await AcademicService.create_subject(
        SubjectCreate(
            semester_id=1,
            stream_id=1,
            cycle_group=None,  # Common
            code="22MATS11",
            name="Mathematics-I for CSE",
            subject_type=SubjectType.THEORY,
            weekly_hours=4,
            credits=4,
            is_first_year=True,
        ),
        test_db_session,
    )
    # Cycle-specific Physics Lab
    phy_lab = await AcademicService.create_subject(
        SubjectCreate(
            semester_id=1,
            stream_id=1,
            cycle_group=CycleGroup.PHYSICS,
            code="22PHYL16",
            name="Physics Laboratory",
            subject_type=SubjectType.LAB,
            weekly_hours=2,
            credits=1,
            is_first_year=True,
        ),
        test_db_session,
    )
    # Cycle-specific Chemistry Lab
    chem_lab = await AcademicService.create_subject(
        SubjectCreate(
            semester_id=1,
            stream_id=1,
            cycle_group=CycleGroup.CHEMISTRY,
            code="22CHEL16",
            name="Chemistry Laboratory",
            subject_type=SubjectType.LAB,
            weekly_hours=2,
            credits=1,
            is_first_year=True,
        ),
        test_db_session,
    )

    # 3rd semester CSE theory
    dsa = await AcademicService.create_subject(
        SubjectCreate(
            semester_id=3,
            code="21CS32",
            name="Data Structures and Applications",
            subject_type=SubjectType.THEORY,
            weekly_hours=4,
            credits=4,
            is_first_year=False,
        ),
        test_db_session,
    )

    assert math_sub.cycle_group is None
    assert phy_lab.subject_type == SubjectType.LAB
    assert phy_lab.cycle_group == CycleGroup.PHYSICS

    # Query 1st year subjects
    first_year_subs = await AcademicService.list_subjects(test_db_session, is_first_year=True)
    assert len(first_year_subs) == 3

    # Query 3rd semester subjects
    sem3_subs = await AcademicService.list_subjects(test_db_session, semester_id=3)
    assert len(sem3_subs) == 1
    assert sem3_subs[0].code == "21CS32"


@pytest.mark.asyncio
async def test_faculty_management_and_multi_stream_mapping(test_db_session: AsyncSession):
    """Test faculty creation, active status, workload capacity, and multi-stream assignments."""
    # Create subject
    subj = await AcademicService.create_subject(
        SubjectCreate(
            semester_id=3,
            code="21CS32",
            name="Data Structures and Applications",
            subject_type=SubjectType.THEORY,
            weekly_hours=4,
            credits=4,
        ),
        test_db_session,
    )

    # Create faculty
    fac = await AcademicService.create_faculty(
        FacultyCreate(
            institution_id=1,
            name="Prof. Rajesh Kumar",
            employee_code="FAC101",
            email="rajesh.kumar@college.edu",
            department="Computer Science & Engineering",
            designation="Professor & HOD",
            max_weekly_hours=14,
            is_active=True,
        ),
        test_db_session,
    )
    assert fac.id is not None
    assert fac.max_weekly_hours == 14

    # Map faculty to subject with stream & cycle context
    mapping = await AcademicService.assign_subject_to_faculty(
        faculty_id=fac.id,
        payload=FacultySubjectCreate(
            subject_id=subj.id,
            stream_id=1,
            cycle_group=None,
            preference_rank=1,
            is_primary=True,
        ),
        db=test_db_session,
    )
    assert mapping.id is not None
    assert mapping.subject_id == subj.id

    # Verify query faculty by subject
    qualified = await AcademicService.get_faculty_by_subject(subj.id, test_db_session)
    assert len(qualified) == 1
    assert qualified[0].name == "Prof. Rajesh Kumar"


@pytest.mark.asyncio
async def test_academic_api_endpoints(test_db_session: AsyncSession):
    """Test FastAPI REST routes for Branches, Subjects, and Faculty."""
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create Branch
        res = await client.post(
            "/api/v1/branches",
            json={"institution_id": 1, "name": "Mechanical Engineering", "code": "ME", "student_count": 60},
        )
        assert res.status_code == 200
        b_data = res.json()["data"]
        assert b_data["code"] == "ME"

        # List Branches
        res = await client.get("/api/v1/branches")
        assert res.status_code == 200
        assert len(res.json()["data"]) >= 1

        # Create Subject
        res = await client.post(
            "/api/v1/subjects",
            json={
                "semester_id": 1,
                "code": "22MATS11",
                "name": "Maths",
                "subject_type": "THEORY",
                "weekly_hours": 4,
                "credits": 4,
                "is_first_year": True,
            },
        )
        assert res.status_code == 200
        s_data = res.json()["data"]
        assert s_data["code"] == "22MATS11"

        # List Subjects
        res = await client.get("/api/v1/subjects?is_first_year=true")
        assert res.status_code == 200
        assert len(res.json()["data"]) >= 1

        # Create Faculty
        res = await client.post(
            "/api/v1/faculty",
            json={
                "institution_id": 1,
                "name": "Dr. Sneha Sharma",
                "employee_code": "FAC102",
                "department": "Mathematics",
                "designation": "Associate Professor",
                "max_weekly_hours": 16,
            },
        )
        assert res.status_code == 200
        f_data = res.json()["data"]
        assert f_data["employee_code"] == "FAC102"

        # List Faculty
        res = await client.get("/api/v1/faculty")
        assert res.status_code == 200
        assert len(res.json()["data"]) >= 1
    app.dependency_overrides.pop(get_db, None)
