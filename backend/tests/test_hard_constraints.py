from app.scheduling.fixtures import (
    get_sample_scheduling_input,
    get_faculty_conflict_fixture,
    get_section_conflict_fixture,
    get_room_conflict_fixture,
    get_capacity_conflict_fixture,
    get_lab_conflict_fixture,
)
from app.scheduling.generators import generate_single


def test_subject_session_requirements_respected():
    """TEST 19: Subject session requirements are respected by solver."""
    inp = get_sample_scheduling_input()
    res = generate_single(inp)

    assert res.is_valid
    # Total scheduled sessions per section must equal sum of subject weekly hours
    expected_hours_per_sec = sum(s.weekly_hours for s in inp.subjects if s.subject_type != "LAB")
    for sec in inp.sections:
        sec_sessions = [s for s in res.sessions if s.section_id == sec.id]
        assert len(sec_sessions) == expected_hours_per_sec


def test_faculty_overbooking_handled():
    """TEST 3: Overbooking faculty returns infeasible or non-clashing solution."""
    inp = get_faculty_conflict_fixture()
    res = generate_single(inp)
    if res.is_valid:
        # If valid solution found, verify no faculty clash
        fac_slots = [(s.faculty_id, s.time_slot_id) for s in res.sessions]
        assert len(fac_slots) == len(set(fac_slots))
    else:
        assert res.status in ("INFEASIBLE", "FAILED")


def test_section_conflict_handled():
    """TEST 4: Section conflict handled gracefully."""
    inp = get_section_conflict_fixture()
    res = generate_single(inp)
    if res.is_valid:
        sec_slots = [(s.section_id, s.time_slot_id) for s in res.sessions]
        assert len(sec_slots) == len(set(sec_slots))
    else:
        assert res.status in ("INFEASIBLE", "FAILED")


def test_room_conflict_handled():
    """TEST 5: Room conflict handled gracefully."""
    inp = get_room_conflict_fixture()
    res = generate_single(inp)
    if res.is_valid:
        room_slots = [(s.room_id, s.time_slot_id) for s in res.sessions if s.room_id]
        assert len(room_slots) == len(set(room_slots))
    else:
        assert res.status in ("INFEASIBLE", "FAILED")


def test_lab_conflict_handled():
    """TEST 6: Lab conflict handled gracefully."""
    inp = get_lab_conflict_fixture()
    res = generate_single(inp)
    if res.is_valid:
        lab_slots = [(s.lab_id, s.time_slot_id) for s in res.sessions if s.lab_id]
        assert len(lab_slots) == len(set(lab_slots))
