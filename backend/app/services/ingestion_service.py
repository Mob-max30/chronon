import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.ingestion import Document, DocumentType, DocumentCategory, DocumentStatus
from app.models.academic import Branch, Subject, Faculty, Stream, Semester, Scheme, SubjectType, CycleGroup
from app.schemas.ingestion import (
    DocumentRead,
    ParsedDataPayload,
    DocumentConfirmation,
    DocumentConfirmationResult,
    BranchCandidate,
    SubjectCandidate,
    FacultyCandidate,
)
from app.ingestion.extractors import DocumentExtractor
from app.ingestion.parsers import DocumentParserEngine


class IngestionService:
    """
    Manages document storage, multi-format text extraction, parsing,
    candidate staging, and human-in-the-loop confirmation into the academic catalogue.
    """

    UPLOAD_DIR = Path("backend/uploads")

    def __init__(self, extractor: Optional[DocumentExtractor] = None):
        self.extractor = extractor or DocumentExtractor()
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async def stage_document(
        self,
        file: UploadFile,
        db: AsyncSession,
    ) -> Document:
        """
        Saves uploaded file, extracts text, parses candidate entities,
        and saves Document model in PARSED status for human review.
        """
        file_name = file.filename or "uploaded_document"
        suffix = Path(file_name).suffix.lower()

        # Determine DocumentType
        if suffix == ".pdf":
            doc_type = DocumentType.PDF
        elif suffix in [".docx", ".doc"]:
            doc_type = DocumentType.DOCX
        else:
            doc_type = DocumentType.IMAGE

        # Save to local disk
        saved_file_path = self.UPLOAD_DIR / f"doc_{file_name}"
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        raw_text, page_count, metadata = self.extractor.extract(saved_file_path)

        # Parse structured domain candidates
        parsed_payload: ParsedDataPayload = DocumentParserEngine.parse_document(raw_text, file_name)

        # Map detected category
        cat_map = {
            "SYLLABUS": DocumentCategory.SYLLABUS,
            "BRANCH_LIST": DocumentCategory.BRANCH_LIST,
            "FACULTY_ROSTER": DocumentCategory.FACULTY_ROSTER,
            "GENERAL": DocumentCategory.GENERAL,
        }
        category = cat_map.get(parsed_payload.detected_category, DocumentCategory.GENERAL)

        # Create Document record
        doc_record = Document(
            file_name=file_name,
            file_type=doc_type,
            category=category,
            status=DocumentStatus.PARSED,
            file_path=str(saved_file_path),
            raw_text=raw_text,
            page_count=page_count,
            parsed_data=parsed_payload.model_dump(),
        )
        db.add(doc_record)
        await db.commit()
        await db.refresh(doc_record)
        return doc_record

    async def get_document(self, document_id: int, db: AsyncSession) -> Optional[Document]:
        stmt = select(Document).where(Document.id == document_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_documents(self, db: AsyncSession) -> List[Document]:
        stmt = select(Document).order_by(Document.id.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def confirm_and_persist(
        self,
        payload: DocumentConfirmation,
        db: AsyncSession,
    ) -> DocumentConfirmationResult:
        """
        Takes human-reviewed and verified candidate entities and persists them
        transactionally into Branches, Subjects, and Faculty tables.
        """
        doc = await self.get_document(payload.document_id, db)
        if not doc:
            raise ValueError(f"Document with ID {payload.document_id} not found")

        branches_count = 0
        subjects_count = 0
        faculty_count = 0

        institution_id = payload.institution_id

        # 1. Process Confirmed Branches
        if payload.confirmed_branches:
            for b in payload.confirmed_branches:
                # Check if branch exists
                b_stmt = select(Branch).where(
                    Branch.institution_id == institution_id,
                    Branch.code == b.code.upper(),
                )
                b_res = await db.execute(b_stmt)
                existing_b = b_res.scalars().first()

                # Find or create suggested stream
                stream_id = None
                if b.suggested_stream:
                    s_stmt = select(Stream).where(Stream.name == b.suggested_stream)
                    s_res = await db.execute(s_stmt)
                    existing_s = s_res.scalars().first()
                    if not existing_s:
                        new_s = Stream(
                            institution_id=institution_id,
                            name=b.suggested_stream,
                            code=b.suggested_stream[:10].upper().replace(" ", "-"),
                        )
                        db.add(new_s)
                        await db.flush()
                        stream_id = new_s.id
                    else:
                        stream_id = existing_s.id

                if not existing_b:
                    new_branch = Branch(
                        institution_id=institution_id,
                        name=b.name,
                        code=b.code.upper(),
                        stream_id=stream_id,
                        student_count=60,
                        is_active=True,
                    )
                    db.add(new_branch)
                    branches_count += 1
                else:
                    existing_b.name = b.name
                    if stream_id:
                        existing_b.stream_id = stream_id

        # 2. Process Confirmed Subjects
        if payload.confirmed_subjects:
            scheme_id = payload.scheme_id or 1
            # Ensure semester records exist
            for s in payload.confirmed_subjects:
                sem_num = s.semester or 1
                sem_stmt = select(Semester).where(
                    Semester.scheme_id == scheme_id,
                    Semester.number == sem_num,
                )
                sem_res = await db.execute(sem_stmt)
                existing_sem = sem_res.scalars().first()
                if not existing_sem:
                    existing_sem = Semester(
                        scheme_id=scheme_id,
                        number=sem_num,
                        term_type="ODD" if sem_num % 2 != 0 else "EVEN",
                    )
                    db.add(existing_sem)
                    await db.flush()

                # Check if subject code already exists
                sub_stmt = select(Subject).where(
                    Subject.code == s.code.upper(),
                    Subject.semester_id == existing_sem.id,
                )
                sub_res = await db.execute(sub_stmt)
                existing_sub = sub_res.scalars().first()

                st_type = SubjectType.THEORY
                if s.subject_type.upper() == "LAB":
                    st_type = SubjectType.LAB
                elif s.subject_type.upper() == "INTEGRATED":
                    st_type = SubjectType.INTEGRATED

                cg = None
                if s.cycle_group:
                    cg = CycleGroup.PHYSICS if s.cycle_group.upper() == "PHYSICS" else CycleGroup.CHEMISTRY

                if not existing_sub:
                    new_sub = Subject(
                        semester_id=existing_sem.id,
                        code=s.code.upper(),
                        name=s.name,
                        subject_type=st_type,
                        weekly_hours=s.weekly_hours or 4,
                        credits=s.credits or 3,
                        cycle_group=cg,
                        is_first_year=(sem_num in [1, 2]),
                    )
                    db.add(new_sub)
                    subjects_count += 1
                else:
                    existing_sub.name = s.name
                    existing_sub.subject_type = st_type
                    existing_sub.credits = s.credits or existing_sub.credits
                    existing_sub.weekly_hours = s.weekly_hours or existing_sub.weekly_hours
                    existing_sub.cycle_group = cg

        # 3. Process Confirmed Faculty
        if payload.confirmed_faculty:
            for f in payload.confirmed_faculty:
                emp_code = f.employee_code or f"EMP{hash(f.name) % 10000:04d}"
                fac_stmt = select(Faculty).where(
                    Faculty.institution_id == institution_id,
                    Faculty.employee_code == emp_code,
                )
                fac_res = await db.execute(fac_stmt)
                existing_fac = fac_res.scalars().first()

                if not existing_fac:
                    new_fac = Faculty(
                        institution_id=institution_id,
                        name=f.name,
                        employee_code=emp_code,
                        email=f.email,
                        department=f.department,
                        designation=f.designation,
                        max_weekly_hours=18,
                        is_active=True,
                    )
                    db.add(new_fac)
                    faculty_count += 1
                else:
                    existing_fac.name = f.name
                    existing_fac.email = f.email or existing_fac.email
                    existing_fac.department = f.department or existing_fac.department
                    existing_fac.designation = f.designation or existing_fac.designation

        # Update Document status
        doc.status = DocumentStatus.CONFIRMED
        await db.commit()

        return DocumentConfirmationResult(
            document_id=doc.id,
            status="CONFIRMED",
            branches_imported=branches_count,
            subjects_imported=subjects_count,
            faculty_imported=faculty_count,
            message=f"Successfully imported {branches_count} branches, {subjects_count} subjects, and {faculty_count} faculty members.",
        )
