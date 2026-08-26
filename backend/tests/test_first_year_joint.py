from app.scheduling.fixtures import (
    get_first_year_joint_fixture,
    get_sample_scheduling_input,
)
from app.scheduling.generators import generate_joint, generate_single
from app.validation.validator import IndependentTimetableValidator
from app.schemas.contracts import TimetableSessionContract


def test_generate_joint_first_year_execution():
    """Verifies that generate_joint executes solver for 1st-year joint Physics and Chemistry cycles."""
    joint_input = get_first_year_joint_fixture()
    res = generate_joint(joint_input, joint_input)

    print("Validation errors:", res.validation.errors)
    assert res.status in ("OPTIMAL", "FEASIBLE")
    assert res.is_valid
    assert len(res.sessions) > 0


def test_first_year_paired_slot_constraint_satisfied():
    """Verifies that paired Physics and Chemistry cycle sections share matching slot indices."""
    joint_input = get_first_year_joint_fixture()
    res = generate_single(joint_input)

    print("Validation errors single:", res.validation.errors)
    assert res.is_valid

    # Group sessions by slot ID and check cycle counts
    subj_map = {s.subject_id: s for s in joint_input.subjects}
    sec_map = {s.id: s for s in joint_input.sections}

    slot_cycles = {}
    for s in res.sessions:
        sec = sec_map.get(s.section_id)
        subj = subj_map.get(s.subject_id)
        if sec and sec.stream_id and sec.cycle_group and subj and subj.cycle_group:
            slot_id = s.time_slot_id
            if slot_id not in slot_cycles:
                slot_cycles[slot_id] = {"PHYSICS_CYCLE": 0, "CHEMISTRY_CYCLE": 0}
            slot_cycles[slot_id][subj.cycle_group] += 1

    for slot_id, counts in slot_cycles.items():
        assert counts["PHYSICS_CYCLE"] == counts["CHEMISTRY_CYCLE"], f"Slot {slot_id} paired cycle mismatch"


def test_independent_validator_detects_paired_slot_mismatch():
    """Verifies independent validator catches paired slot mismatch when manually broken."""
    joint_input = get_first_year_joint_fixture()
    broken_sessions = [
        TimetableSessionContract(
            id=1,
            version_id=1,
            subject_id=501,  # Physics
            faculty_id=10,
            section_id=10,  # Physics Sec
            room_id=1,
            time_slot_id=1,
            stream_id=1,
            cycle_group="PHYSICS_CYCLE",
        ),
        # Missing corresponding Chemistry session at time_slot_id=1
    ]

    validator = IndependentTimetableValidator(broken_sessions, joint_input)
    val_res = validator.validate()

    assert not val_res.is_valid
    rule_codes = [e.rule_code for e in val_res.errors]
    assert "PAIRED_SLOT_MISMATCH" in rule_codes or "MISSING_SESSION" in rule_codes
