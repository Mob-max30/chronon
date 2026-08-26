from app.scheduling.fixtures import (
    get_manual_valid_timetable,
    get_manual_invalid_timetable,
    get_sample_scheduling_input,
)
from app.validation.validator import IndependentTimetableValidator


def test_validator_accepts_manual_valid_timetable():
    """TEST 12 & MANDATORY INDEPENDENCE TEST A: Validator accepts hand-crafted valid timetable."""
    valid_sessions = get_manual_valid_timetable()
    validator = IndependentTimetableValidator(valid_sessions)
    res = validator.validate()

    assert res.is_valid
    assert res.total_hard_violations == 0
    assert len(res.errors) == 0


def test_validator_rejects_manual_invalid_timetable():
    """TEST 13 & MANDATORY INDEPENDENCE TEST B: Validator rejects hand-crafted invalid timetable."""
    invalid_sessions = get_manual_invalid_timetable()
    validator = IndependentTimetableValidator(invalid_sessions)
    res = validator.validate()

    assert not res.is_valid
    assert res.total_hard_violations >= 2
    rule_codes = [e.rule_code for e in res.errors]
    assert "FACULTY_CLASH" in rule_codes
    assert "ROOM_CLASH" in rule_codes


def test_validator_detects_faculty_eligibility_and_capacity_with_input():
    """TEST 7 & TEST 9: Input-aware independent validation detects eligibility & capacity violations."""
    inp = get_sample_scheduling_input()
    invalid_sessions = get_manual_valid_timetable()
    # Modify session 1 to have ineligible faculty ID 999
    invalid_sessions[0].faculty_id = 999

    validator = IndependentTimetableValidator(invalid_sessions, inp)
    res = validator.validate()

    assert not res.is_valid
    rule_codes = [e.rule_code for e in res.errors]
    assert "FACULTY_INELIGIBLE" in rule_codes
