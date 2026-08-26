import re
from typing import Optional, Tuple


class AcademicNormalizer:
    """
    Normalizes extracted raw strings into canonical academic data formats.
    Cleans OCR artifacts, standardizes branch codes, subject codes, faculty titles, etc.
    """

    # Common VTU branch code canonical mappings
    BRANCH_CANONICAL_MAP = {
        "COMPUTER SCIENCE": "CSE",
        "COMPUTER SCIENCE AND ENGINEERING": "CSE",
        "COMPUTER SCIENCE & ENGINEERING": "CSE",
        "INFORMATION SCIENCE": "ISE",
        "INFORMATION SCIENCE AND ENGINEERING": "ISE",
        "INFORMATION SCIENCE & ENGINEERING": "ISE",
        "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING": "AIML",
        "ARTIFICIAL INTELLIGENCE & MACHINE LEARNING": "AIML",
        "AI AND ML": "AIML",
        "AI & ML": "AIML",
        "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE": "AIDS",
        "ARTIFICIAL INTELLIGENCE & DATA SCIENCE": "AIDS",
        "AI AND DS": "AIDS",
        "AI & DS": "AIDS",
        "ELECTRONICS AND COMMUNICATION": "ECE",
        "ELECTRONICS & COMMUNICATION ENGINEERING": "ECE",
        "ELECTRONICS AND COMMUNICATION ENGINEERING": "ECE",
        "MECHANICAL ENGINEERING": "ME",
        "CIVIL ENGINEERING": "CV",
        "ELECTRICAL AND ELECTRONICS ENGINEERING": "EEE",
        "ELECTRICAL & ELECTRONICS ENGINEERING": "EEE",
    }

    # Stream suggestion map for VTU first-year branches
    STREAM_SUGGESTION_MAP = {
        "CSE": "CSE Stream",
        "ISE": "CSE Stream",
        "AIML": "CSE Stream",
        "AIDS": "CSE Stream",
        "CSBS": "CSE Stream",
        "ECE": "EEE Stream",
        "EEE": "EEE Stream",
        "ETE": "EEE Stream",
        "ME": "Mechanical Stream",
        "CV": "Civil Stream",
    }

    @classmethod
    def normalize_subject_code(cls, raw_code: str) -> str:
        """
        Cleans and canonicalizes VTU subject codes (e.g., '21CS32', '22MATS11', 'BCS301', '21CSL38').
        Fixes common OCR confusions: 'O' -> '0', 'I' -> '1', hyphens, whitespace.
        """
        if not raw_code:
            return ""
        code = raw_code.strip().upper()
        # Remove hyphens and spaces
        code = re.sub(r"[\s\-_/]", "", code)
        return code

    @classmethod
    def normalize_subject_name(cls, raw_name: str) -> str:
        """Cleans and standardizes subject title."""
        if not raw_name:
            return ""
        cleaned = re.sub(r"\s+", " ", raw_name).strip()
        # Capitalize appropriately
        words = cleaned.split()
        return " ".join(words)

    @classmethod
    def normalize_branch(cls, raw_name_or_code: str) -> Tuple[str, str, str]:
        """
        Returns (canonical_name, code, suggested_stream).
        """
        cleaned = re.sub(r"[^A-Za-z0-9\s&]", "", raw_name_or_code).strip()
        upper = cleaned.upper()

        # Direct code match
        if upper in ["CSE", "ISE", "AIML", "AIDS", "ECE", "EEE", "ME", "CV", "CSBS"]:
            name_map = {
                "CSE": "Computer Science & Engineering",
                "ISE": "Information Science & Engineering",
                "AIML": "Artificial Intelligence & Machine Learning",
                "AIDS": "Artificial Intelligence & Data Science",
                "ECE": "Electronics & Communication Engineering",
                "EEE": "Electrical & Electronics Engineering",
                "ME": "Mechanical Engineering",
                "CV": "Civil Engineering",
                "CSBS": "Computer Science & Business Systems",
            }
            code = upper
            name = name_map.get(code, code)
            stream = cls.STREAM_SUGGESTION_MAP.get(code, "General Stream")
            return name, code, stream

        # Check full name matching
        for key, code in cls.BRANCH_CANONICAL_MAP.items():
            if key in upper:
                stream = cls.STREAM_SUGGESTION_MAP.get(code, "General Stream")
                return cleaned.title(), code, stream

        # Default fallback
        code = "".join([w[0] for w in cleaned.split() if w]).upper()[:4]
        return cleaned.title(), code if code else "GEN", "General Stream"

    @classmethod
    def normalize_faculty_name(cls, raw_name: str) -> Tuple[str, Optional[str]]:
        """
        Removes honorific prefixes (Dr., Prof., Mr., Mrs., Ms.) and returns (cleaned_name, title).
        """
        if not raw_name:
            return "", None

        name = re.sub(r"\s+", " ", raw_name).strip()
        detected_title = None

        title_patterns = [
            (r"^(Dr\.|Dr\b)", "Dr."),
            (r"^(Prof\.|Prof\b)", "Prof."),
            (r"^(Mr\.|Mr\b)", "Mr."),
            (r"^(Mrs\.|Mrs\b)", "Mrs."),
            (r"^(Ms\.|Ms\b)", "Ms."),
        ]

        for pattern, title in title_patterns:
            match = re.match(pattern, name, flags=re.IGNORECASE)
            if match:
                detected_title = title
                name = name[match.end():].strip()
                break

        # Remove trailing designations in parentheses e.g. "John Doe (HOD)"
        name = re.sub(r"\(.*?\)", "", name).strip()
        # Clean non-alphabetic leading characters
        name = re.sub(r"^[^A-Za-z]+", "", name).strip()
        # Title case
        name = name.title()
        return name, detected_title

    @classmethod
    def classify_subject_type(cls, code: str, name: str) -> str:
        """Determines if a subject is THEORY, LAB, or INTEGRATED."""
        combined = f"{code} {name}".upper()
        if any(keyword in combined for keyword in ["LAB", "LABORATORY", "PRACTICAL", "WORKSHOP", "PROJECT", "CAED", "DRAWING"]):
            return "LAB"
        if "INTEGRATED" in combined or "THEORY & PRACTICE" in combined:
            return "INTEGRATED"
        # VTU code convention: 'L' or 'P' in code, e.g. 21CSL38, BCSL305
        if re.search(r"[0-9]{2}[A-Z]+L[0-9]+", code) or re.search(r"^[A-Z]+L[0-9]+", code):
            return "LAB"
        return "THEORY"

    @classmethod
    def detect_cycle_group(cls, code: str, name: str) -> Optional[str]:
        """Detects if a subject belongs to PHYSICS or CHEMISTRY cycle."""
        combined = f"{code} {name}".upper()
        if any(k in combined for k in ["PHYSICS", "PHY", "ELECTRICAL", "MECHANICAL", "CIVIL", "CAD", "CAED"]):
            return "PHYSICS"
        if any(k in combined for k in ["CHEMISTRY", "CHEM", "PROGRAMMING", "ELECTRONICS", "ENGLISH", "KANNADA", "EVS"]):
            return "CHEMISTRY"
        return None
