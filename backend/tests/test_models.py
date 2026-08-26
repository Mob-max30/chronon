from datetime import time
from app.models.academic import Institution, AcademicYear, Scheme, Branch, Subject, Faculty
from app.models.resources import Room, RoomAvailability, Lab, LabAvailability, LabSubjectMapping, Section, Batch, SlotConfig, TimeSlot
from app.models.timetable import Timetable, TimetableVersion, TimetableSession, GenerationRun
from app.models.ingestion import Document


def test_model_instantiation():
    """Verify all SQLAlchemy declarative models can be imported and initialized."""
    inst = Institution(name="VTU Central", code="VTU-01")
    assert inst.name == "VTU Central"

    ay = AcademicYear(name="2026-2027", is_current=True)
    assert ay.name == "2026-2027"

    room = Room(name="LH-101", capacity=60, room_type="LECTURE_HALL")
    assert room.capacity == 60
    assert room.room_type == "LECTURE_HALL"

    r_avail = RoomAvailability(room_id=1, day_of_week=0, start_time=time(9, 0), end_time=time(17, 0))
    assert r_avail.day_of_week == 0

    lab = Lab(name="CS Lab 1", capacity=30, count=2, lab_type="COMPUTER")
    assert lab.capacity == 30
    assert lab.count == 2

    l_avail = LabAvailability(lab_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(17, 0), is_available=True)
    assert l_avail.is_available is True

    sec = Section(branch_id=1, semester_id=1, name="A", student_count=60, stream_id=1, cycle_group="PHYSICS_CYCLE")
    assert sec.cycle_group == "PHYSICS_CYCLE"

    batch = Batch(section_id=1, name="B1", student_count=30, lab_id=1)
    assert batch.lab_id == 1

    slot_cfg = SlotConfig(
        institution_id=1,
        theory_duration_minutes=55,
        lab_duration_minutes=110,
        day_start_time=time(9, 0),
        day_end_time=time(17, 0),
    )
    assert slot_cfg.theory_duration_minutes == 55

    doc = Document(file_name="syllabus_2022.pdf", file_type="PDF")
    assert doc.file_name == "syllabus_2022.pdf"

