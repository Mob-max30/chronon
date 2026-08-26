import io
import pytest
import pytest_asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import UploadFile

from app.db.base import Base
from app.models.academic import Institution, InstitutionType, Scheme, Semester, TermType, Branch, Subject, Faculty
from app.ingestion.ocr.provider import MockOCRProvider, get_ocr_provider
from app.ingestion.normalizer import AcademicNormalizer
from app.ingestion.extractors import DocumentExtractor
from app.ingestion.parsers import VTUBranchParser, VTUSyllabusParser, FacultyListParser, DocumentParserEngine
from app.schemas.ingestion import DocumentConfirmation, BranchCandidate, SubjectCandidate, FacultyCandidate
from app.services.ingestion_service import IngestionService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_ingest_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        inst = Institution(name="VTU Central", code="VTU-01", type=InstitutionType.VTU_AFFILIATED)
        session.add(inst)
        await session.flush()

        scheme = Scheme(institution_id=inst.id, name="2022 Scheme", year=2022)
        session.add(scheme)
        await session.flush()

        sem1 = Semester(scheme_id=scheme.id, number=1, term_type=TermType.ODD)
        sem3 = Semester(scheme_id=scheme.id, number=3, term_type=TermType.ODD)
        session.add_all([sem1, sem3])
        await session.commit()

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


def test_ocr_provider_and_mock_fallback():
    """Verify OCR provider abstraction and MockOCRProvider."""
    mock_ocr = MockOCRProvider()
    mock_ocr.set_mock_text("sample_doc.png", "21CS32 Data Structures and Applications")

    extracted = mock_ocr.extract_text(Path("sample_doc.png"))
    assert "21CS32" in extracted

    structured = mock_ocr.extract_structured_data(Path("sample_doc.png"))
    assert structured["status"] == "EXTRACTED_PENDING_CONFIRMATION"

    provider = get_ocr_provider("mock")
    assert isinstance(provider, MockOCRProvider)


def test_academic_normalizer():
    """Verify code cleaning, title case formatting, and category detection."""
    # Subject Code Normalization
    assert AcademicNormalizer.normalize_subject_code(" 21cs-32 ") == "21CS32"
    assert AcademicNormalizer.normalize_subject_code("22_MATS_11") == "22MATS11"

    # Branch Normalization
    name, code, stream = AcademicNormalizer.normalize_branch("Computer Science & Engineering")
    assert code == "CSE"
    assert "CSE Stream" in stream

    name, code, stream = AcademicNormalizer.normalize_branch("Mechanical Engineering")
    assert code == "ME"
    assert "Mechanical Stream" in stream

    # Faculty Name Normalization
    name, title = AcademicNormalizer.normalize_faculty_name("Dr. Rajesh Kumar (HOD)")
    assert name == "Rajesh Kumar"
    assert title == "Dr."

    # Subject Type Classification
    assert AcademicNormalizer.classify_subject_type("21CSL35", "Data Structures Lab") == "LAB"
    assert AcademicNormalizer.classify_subject_type("21CS32", "Data Structures") == "THEORY"

    # Cycle Group Detection
    assert AcademicNormalizer.detect_cycle_group("22PHYS12", "Physics for CSE") == "PHYSICS"
    assert AcademicNormalizer.detect_cycle_group("22CHEM12", "Chemistry for CSE") == "CHEMISTRY"


def test_vtu_branch_parser():
    """Test extracting engineering branches from typical VTU circular text."""
    sample_text = """
    VISVESVARAYA TECHNOLOGICAL UNIVERSITY, BELAGAVI
    Approved Engineering Programmes for Academic Year 2026-27:
    1. B.E. in Computer Science and Engineering (CSE) - Intake: 180
    2. B.E. in Information Science and Engineering (ISE) - Intake: 120
    3. B.E. in Artificial Intelligence and Machine Learning (AIML) - Intake: 60
    4. B.E. in Mechanical Engineering (ME) - Intake: 60
    """
    candidates = VTUBranchParser.parse(sample_text)
    codes = [c.code for c in candidates]
    assert "CSE" in codes
    assert "ISE" in codes
    assert "AIML" in codes
    assert "ME" in codes


def test_vtu_syllabus_parser():
    """Test extracting curriculum subjects from syllabus tables."""
    sample_text = """
    III SEMESTER - COMPUTER SCIENCE & ENGINEERING (2022 SCHEME)
    | Course Code | Course Title | Credits | Weekly Hours |
    | 21CS31 | Transform Calculus and Numerical Techniques | 3 | 4 |
    | 21CS32 | Data Structures and Applications | 4 | 4 |
    | 21CS33 | Analog and Digital Electronics | 3 | 4 |
    | 21CSL35 | Data Structures Laboratory | 1 | 2 |
    """
    candidates = VTUSyllabusParser.parse(sample_text, default_semester=3)
    codes = [c.code for c in candidates]
    assert "21CS31" in codes
    assert "21CS32" in codes
    assert "21CSL35" in codes

    dsa_lab = next(c for c in candidates if c.code == "21CSL35")
    assert dsa_lab.subject_type == "LAB"
    assert dsa_lab.semester == 3


def test_faculty_roster_parser():
    """Test extracting faculty members and contact details."""
    sample_text = """
    DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
    Faculty List:
    1. Dr. Rajesh Kumar | Professor & HOD | rajesh.kumar@college.edu | Computer Science
    2. Prof. Sneha Sharma | Associate Professor | sneha.sharma@college.edu | Mathematics
    3. Prof. Vikram Patil | Assistant Professor | vikram.patil@college.edu | Computer Science
    """
    candidates = FacultyListParser.parse(sample_text)
    names = [c.name for c in candidates]
    assert "Rajesh Kumar" in names
    assert "Sneha Sharma" in names
    assert "Vikram Patil" in names

    rajesh = next(c for c in candidates if c.name == "Rajesh Kumar")
    assert rajesh.email == "rajesh.kumar@college.edu"


def test_document_parser_engine_auto_categorization():
    """Test the parser engine automatic category classifier."""
    syllabus_text = "SEMESTER 3 2022 SCHEME 21CS32 Data Structures MODULE 1"
    res = DocumentParserEngine.parse_document(syllabus_text, "syllabus.pdf")
    assert res.detected_category == "SYLLABUS"
    assert len(res.subjects) >= 1

    faculty_text = "STAFF LIST Dr. Rajesh Kumar PROFESSOR DEPARTMENT OF CSE"
    res2 = DocumentParserEngine.parse_document(faculty_text, "faculty.docx")
    assert res2.detected_category == "FACULTY_ROSTER"
    assert len(res2.faculty) >= 1


@pytest.mark.asyncio
async def test_ingestion_service_confirmation_workflow(test_ingest_db: AsyncSession):
    """Test human-in-the-loop candidate review and confirmation into database."""
    # Create sample text file upload
    mock_content = """
    III SEMESTER CSE
    | 21CS32 | Data Structures and Applications | 4 | 4 |
    | 21CSL35 | Data Structures Laboratory | 1 | 2 |
    """
    file_bytes = mock_content.encode("utf-8")
    upload_file = UploadFile(
        filename="vtu_cse_3rd_sem.txt",
        file=io.BytesIO(file_bytes),
    )

    service = IngestionService()
    doc_record = await service.stage_document(upload_file, test_ingest_db)
    assert doc_record.id is not None
    assert doc_record.status.value == "PARSED"
    assert "21CS32" in doc_record.raw_text

    # User reviews candidates and confirms
    confirmation_payload = DocumentConfirmation(
        document_id=doc_record.id,
        institution_id=1,
        scheme_id=1,
        confirmed_branches=[
            BranchCandidate(name="Computer Science & Engineering", code="CSE", suggested_stream="CSE Stream")
        ],
        confirmed_subjects=[
            SubjectCandidate(code="21CS32", name="Data Structures and Applications", semester=3, subject_type="THEORY", credits=4, weekly_hours=4),
            SubjectCandidate(code="21CSL35", name="Data Structures Laboratory", semester=3, subject_type="LAB", credits=1, weekly_hours=2),
        ],
        confirmed_faculty=[
            FacultyCandidate(name="Prof. Rajesh Kumar", employee_code="FAC101", department="Computer Science & Engineering", designation="Professor", email="rajesh@college.edu")
        ],
    )

    result = await service.confirm_and_persist(confirmation_payload, test_ingest_db)
    assert result.status == "CONFIRMED"
    assert result.branches_imported == 1
    assert result.subjects_imported == 2
    assert result.faculty_imported == 1
