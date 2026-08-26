import re
from typing import List, Dict, Any, Optional
from app.ingestion.normalizer import AcademicNormalizer
from app.schemas.ingestion import (
    BranchCandidate,
    SubjectCandidate,
    FacultyCandidate,
    ParsedDataPayload,
)


class VTUBranchParser:
    """Parses VTU Circulars / Affiliation lists to extract engineering branches."""

    @classmethod
    def parse(cls, raw_text: str) -> List[BranchCandidate]:
        candidates: List[BranchCandidate] = []
        seen_codes = set()

        lines = raw_text.splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str or len(line_str) < 3:
                continue

            # Look for patterns like "1. Computer Science & Engineering (CSE)" or "BE - Civil Engineering"
            branch_match = re.search(
                r"(?:B\.?E\.?|B\.?Tech\.?|Bachelor of Engineering)?\s*(?:in|-)?\s*([A-Za-z\s&]{4,50})\s*(?:\(([A-Z]{2,6})\))?",
                line_str,
                re.IGNORECASE,
            )

            if branch_match:
                raw_name = branch_match.group(1).strip()
                norm_name, code, stream = AcademicNormalizer.normalize_branch(raw_name)

                # If explicit code in parenthesis
                if branch_match.group(2):
                    code = branch_match.group(2).upper()

                if code and code not in seen_codes and len(code) >= 2:
                    seen_codes.add(code)
                    candidates.append(
                        BranchCandidate(
                            name=norm_name,
                            code=code,
                            suggested_stream=stream,
                            confidence=0.92,
                        )
                    )

        # Keyword scan fallback if list format wasn't explicitly structured
        common_branches = [
            ("Computer Science & Engineering", "CSE", "CSE Stream"),
            ("Information Science & Engineering", "ISE", "CSE Stream"),
            ("Artificial Intelligence & Machine Learning", "AIML", "CSE Stream"),
            ("Artificial Intelligence & Data Science", "AIDS", "CSE Stream"),
            ("Electronics & Communication Engineering", "ECE", "EEE Stream"),
            ("Electrical & Electronics Engineering", "EEE", "EEE Stream"),
            ("Mechanical Engineering", "ME", "Mechanical Stream"),
            ("Civil Engineering", "CV", "Civil Stream"),
        ]
        for name, code, stream in common_branches:
            if code not in seen_codes and (code in raw_text or name.lower() in raw_text.lower()):
                seen_codes.add(code)
                candidates.append(
                    BranchCandidate(name=name, code=code, suggested_stream=stream, confidence=0.85)
                )

        return candidates


class VTUSyllabusParser:
    """Parses VTU Curriculum schemes, syllabus tables, and course lists."""

    # VTU subject code regex e.g. 21CS32, 22MATS11, BCS301, 21CSL38, BENG106, 22PHY12
    CODE_REGEX = re.compile(
        r"\b([0-9]{2}[A-Z]{2,5}[0-9]{2,3}[A-Z]?|[B,M][A-Z]{2,4}[0-9]{3}[A-Z]?)\b"
    )

    @classmethod
    def parse(cls, raw_text: str, default_semester: int = 1) -> List[SubjectCandidate]:
        candidates: List[SubjectCandidate] = []
        seen_codes = set()

        lines = raw_text.splitlines()
        detected_sem = default_semester

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Detect Semester header e.g. "III SEMESTER", "SEMESTER 3", "1st Semester"
            sem_match = re.search(
                r"(?:SEMESTER|SEM)\s*[-:]?\s*([1-8]|I{1,3}|IV|V?I{0,3}|VII|VIII)",
                line_str,
                re.IGNORECASE,
            )
            if sem_match:
                roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
                val = sem_match.group(1).upper()
                if val in roman_map:
                    detected_sem = roman_map[val]
                elif val.isdigit():
                    detected_sem = int(val)

            # Match subject code in line
            code_match = cls.CODE_REGEX.search(line_str)
            if code_match:
                raw_code = code_match.group(1)
                code = AcademicNormalizer.normalize_subject_code(raw_code)

                if code in seen_codes or len(code) < 4:
                    continue

                # Extract subject name: remainder of line after code (or between pipes)
                parts = line_str.split(raw_code)
                after_text = parts[1] if len(parts) > 1 else ""

                # If table format with pipes: e.g. | 21CS32 | Data Structures | 3 | 4 |
                if "|" in line_str:
                    cells = [c.strip() for c in line_str.split("|") if c.strip()]
                    name_candidate = ""
                    for cell in cells:
                        if cell != raw_code and not cell.isdigit() and len(cell) > 3:
                            name_candidate = cell
                            break
                    name = AcademicNormalizer.normalize_subject_name(name_candidate) or f"Course {code}"
                else:
                    # Clean up non-name characters (numbers, credits)
                    clean_after = re.sub(r"^[^\w\s]+", "", after_text)
                    name_words = []
                    for word in clean_after.split():
                        if word.isdigit():
                            break
                        name_words.append(word)
                    name = AcademicNormalizer.normalize_subject_name(" ".join(name_words))
                    if not name or len(name) < 3:
                        name = f"Course {code}"

                subj_type = AcademicNormalizer.classify_subject_type(code, name)
                cycle_group = AcademicNormalizer.detect_cycle_group(code, name)

                # Default credits and weekly hours based on type
                credits = 1 if subj_type == "LAB" else 3
                weekly_hours = 2 if subj_type == "LAB" else 4

                seen_codes.add(code)
                candidates.append(
                    SubjectCandidate(
                        code=code,
                        name=name,
                        semester=detected_sem,
                        subject_type=subj_type,
                        credits=credits,
                        weekly_hours=weekly_hours,
                        cycle_group=cycle_group,
                        confidence=0.94,
                    )
                )

        return candidates


class FacultyListParser:
    """Parses faculty rosters, departmental staff lists, and workload documents."""

    DESIGNATION_KEYWORDS = [
        "PROFESSOR & HOD", "PROFESSOR", "ASSOCIATE PROFESSOR", "ASSISTANT PROFESSOR",
        "HEAD OF DEPARTMENT", "HOD", "DEAN", "LECTURER", "INSTRUCTOR"
    ]

    @classmethod
    def parse(cls, raw_text: str) -> List[FacultyCandidate]:
        candidates: List[FacultyCandidate] = []
        seen_names = set()
        emp_idx = 1001

        lines = raw_text.splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str or len(line_str) < 4:
                continue

            # Extract email if present
            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", line_str)
            email = email_match.group(0) if email_match else None

            # Extract designation
            detected_desig = None
            for desig in cls.DESIGNATION_KEYWORDS:
                if desig in line_str.upper():
                    detected_desig = desig.title()
                    break

            # Extract department
            detected_dept = None
            for dept in ["Computer Science", "Information Science", "AI & ML", "Mechanical", "Civil", "Electronics", "Mathematics", "Physics", "Chemistry"]:
                if dept.lower() in line_str.lower():
                    detected_dept = dept
                    break

            name_candidate = ""
            if "|" in line_str:
                cells = [c.strip() for c in line_str.split("|") if c.strip()]
                for cell in cells:
                    clean_cell = re.sub(r"^[0-9]+[\.\)\-\s]+", "", cell).strip()
                    # Skip if cell is email, degree, designation, or department
                    if re.search(r"@|PhD|M\.?Tech|B\.?E", clean_cell, re.IGNORECASE):
                        continue
                    if any(desig in clean_cell.upper() for desig in cls.DESIGNATION_KEYWORDS):
                        continue
                    if detected_dept and detected_dept.lower() in clean_cell.lower():
                        continue
                    if len(clean_cell) >= 3:
                        name_candidate = clean_cell
                        break
            else:
                # Look for name following title (Dr./Prof./Mr./Mrs./Ms.)
                title_match = re.search(r"\b(Dr\.?|Prof\.?|Mr\.?|Mrs\.?|Ms\.?)\s+([A-Za-z\s]{3,35})", line_str, re.IGNORECASE)
                if title_match:
                    raw_extracted = f"{title_match.group(1)} {title_match.group(2)}"
                    # Truncate at any designation or department keywords
                    for desig in cls.DESIGNATION_KEYWORDS:
                        if desig in raw_extracted.upper():
                            idx = raw_extracted.upper().find(desig)
                            raw_extracted = raw_extracted[:idx].strip()
                    for dept_kw in ["DEPARTMENT", "DEPT", "CSE", "ISE", "ECE", "ME", "CV"]:
                        if dept_kw in raw_extracted.upper():
                            idx = raw_extracted.upper().find(dept_kw)
                            raw_extracted = raw_extracted[:idx].strip()
                    name_candidate = raw_extracted
                else:
                    # Clean line from metadata
                    clean_line = re.sub(r"^[0-9]+[\.\)\-\s]+", "", line_str).strip()
                    if email:
                        clean_line = clean_line.replace(email, "")
                    if detected_desig:
                        clean_line = re.sub(re.escape(detected_desig), "", clean_line, flags=re.IGNORECASE)
                    name_candidate = clean_line

            norm_name, _ = AcademicNormalizer.normalize_faculty_name(name_candidate)

            # Verification
            if norm_name and len(norm_name) > 3 and norm_name not in seen_names:
                # Filter out header words or keywords
                if any(h in norm_name.upper() for h in ["NAME", "FACULTY", "DEPARTMENT", "SL NO", "DESIGNATION", "STAFF LIST", "PROFESSOR", "LECTURER"]):
                    continue
                seen_names.add(norm_name)
                emp_code = f"FAC{emp_idx}"
                emp_idx += 1

                candidates.append(
                    FacultyCandidate(
                        name=norm_name,
                        employee_code=emp_code,
                        department=detected_dept or "Computer Science & Engineering",
                        designation=detected_desig or "Assistant Professor",
                        email=email or f"{norm_name.lower().replace(' ', '.')}@college.edu",
                        specializations=[],
                        confidence=0.90,
                    )
                )

        return candidates


class DocumentParserEngine:
    """
    Coordinator engine that categorizes documents and routes to appropriate domain parsers.
    """

    @classmethod
    def parse_document(cls, raw_text: str, filename: str = "") -> ParsedDataPayload:
        upper_text = raw_text.upper()

        # Category heuristics
        syllabus_score = sum(upper_text.count(k) for k in ["SEMESTER", "SCHEME", "CREDIT", "COURSE CODE", "SUBJECT CODE", "MODULE"])
        faculty_score = sum(upper_text.count(k) for k in ["PROFESSOR", "DEPARTMENT", "FACULTY", "STAFF", "DESIGNATION", "EMAIL"])
        branch_score = sum(upper_text.count(k) for k in ["BRANCH", "INTAKE", "AFFILIATED", "PROGRAMME", "PROGRAM", "COURSES OFFERED"])

        if syllabus_score >= max(faculty_score, branch_score, 3):
            category = "SYLLABUS"
        elif faculty_score >= max(syllabus_score, branch_score, 3):
            category = "FACULTY_ROSTER"
        elif branch_score >= 3:
            category = "BRANCH_LIST"
        else:
            category = "GENERAL"

        # Execute parsers
        branches = VTUBranchParser.parse(raw_text)
        subjects = VTUSyllabusParser.parse(raw_text)
        faculty = FacultyListParser.parse(raw_text)

        summary_parts = []
        if branches:
            summary_parts.append(f"{len(branches)} Branches identified")
        if subjects:
            summary_parts.append(f"{len(subjects)} Subjects identified")
        if faculty:
            summary_parts.append(f"{len(faculty)} Faculty members identified")

        summary = ", ".join(summary_parts) if summary_parts else "No structured academic candidates identified."

        return ParsedDataPayload(
            raw_lines_found=len(raw_text.splitlines()),
            detected_category=category,
            branches=branches,
            subjects=subjects,
            faculty=faculty,
            summary=summary,
        )
