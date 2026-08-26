from app.models.timetable import TimetableVersion, TimetableSession
from app.schemas.contracts import TimetableSessionContract
from app.services.versioning_service import VersioningService


def test_version_diff_calculation():
    service = VersioningService(db=None)

    # Version 1 sessions
    v1_sess = [
        TimetableSession(id=1, version_id=1, subject_id=101, section_id=1, batch_id=None, room_id=10, faculty_id=1, time_slot_id=1),
        TimetableSession(id=2, version_id=1, subject_id=102, section_id=1, batch_id=None, room_id=10, faculty_id=2, time_slot_id=2),
    ]
    v1 = TimetableVersion(id=1, timetable_id=100, version_number=1, is_active=False)
    v1.sessions = v1_sess

    # Version 2 sessions: Subject 101 moved to Slot 3 (MODIFIED), Subject 102 removed, Subject 103 added
    v2_sess = [
        TimetableSession(id=3, version_id=2, subject_id=101, section_id=1, batch_id=None, room_id=10, faculty_id=1, time_slot_id=3),
        TimetableSession(id=4, version_id=2, subject_id=103, section_id=1, batch_id=None, room_id=11, faculty_id=3, time_slot_id=4),
    ]
    v2 = TimetableVersion(id=2, timetable_id=100, version_number=2, is_active=True)
    v2.sessions = v2_sess

    diff = service.compute_version_diff(
        timetable_id=100,
        from_version=v1,
        to_version=v2,
    )

    assert diff.timetable_id == 100
    assert diff.from_version_number == 1
    assert diff.to_version_number == 2
    assert diff.total_sessions_from == 2
    assert diff.total_sessions_to == 2
    assert diff.total_differences == 3

    diff_types = {d.subject_id: d.diff_type for d in diff.differences}
    assert diff_types[101] == "MODIFIED"
    assert diff_types[102] == "REMOVED"
    assert diff_types[103] == "ADDED"
