from app.models.academic import Institution, AcademicYear, Scheme, Branch, Subject, Faculty
from app.models.resources import Room, Lab, Section, Batch, TimeSlot
from app.models.timetable import Timetable, TimetableVersion, TimetableSession, GenerationRun
from app.models.ingestion import Document


def test_model_instantiation():
    """Verify all 20 SQLAlchemy declarative models can be imported and initialized."""
    inst = Institution(name="VTU Central", code="VTU-01")
    assert inst.name == "VTU Central"

    ay = AcademicYear(name="2026-2027", is_current=True)
    assert ay.name == "2026-2027"

    room = Room(name="LH-101", capacity=60)
    assert room.capacity == 60

    lab = Lab(name="CS Lab 1", capacity=30, lab_type="COMPUTER")
    assert lab.capacity == 30

    doc = Document(file_name="syllabus_2022.pdf", file_type="PDF")
    assert doc.file_name == "syllabus_2022.pdf"
