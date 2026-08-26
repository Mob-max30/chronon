from app.schemas.contracts import TimetableSessionContract
from app.validation.validator import IndependentTimetableValidator


def test_validator_detects_faculty_clash():
    # Construct 2 sessions where Faculty 1 is scheduled at TimeSlot 1 in 2 different sections
    conflicting_sessions = [
        TimetableSessionContract(
            id=1,
            version_id=1,
            subject_id=101,
            faculty_id=1,
            section_id=1,
            room_id=1,
            time_slot_id=1,
        ),
        TimetableSessionContract(
            id=2,
            version_id=1,
            subject_id=102,
            faculty_id=1,
            section_id=2,
            room_id=2,
            time_slot_id=1,
        ),
    ]

    validator = IndependentTimetableValidator(conflicting_sessions)
    result = validator.validate()

    assert not result.is_valid
    assert result.total_hard_violations == 1
    assert any(err.rule_code == "FACULTY_CLASH" for err in result.errors)


def test_validator_passes_valid_schedule():
    valid_sessions = [
        TimetableSessionContract(
            id=1,
            version_id=1,
            subject_id=101,
            faculty_id=1,
            section_id=1,
            room_id=1,
            time_slot_id=1,
        ),
        TimetableSessionContract(
            id=2,
            version_id=1,
            subject_id=102,
            faculty_id=2,
            section_id=2,
            room_id=2,
            time_slot_id=1,
        ),
    ]

    validator = IndependentTimetableValidator(valid_sessions)
    result = validator.validate()

    assert result.is_valid
    assert result.total_hard_violations == 0
