from app.scheduling.fixtures import (
    get_sample_scheduling_input,
    get_infeasible_fixture,
    get_manual_valid_timetable,
    get_manual_invalid_timetable,
)
from app.scheduling.generators import generate_single
from app.validation.validator import IndependentTimetableValidator


def test_full_standalone_scheduler_pipeline_regression():
    """TEST 20: Comprehensive regression test covering the entire standalone scheduler pipeline."""
    # 1. Valid Input Execution
    basic_inp = get_sample_scheduling_input()
    res = generate_single(basic_inp)

    assert res.status in ("OPTIMAL", "FEASIBLE")
    assert res.is_valid
    assert len(res.sessions) == sum(s.weekly_hours for s in basic_inp.subjects if s.subject_type != "LAB") * len(basic_inp.sections)
    assert res.quality.overall_score >= 0.0
    assert res.execution_time_seconds > 0.0

    # 2. Infeasible Input Execution
    inf_inp = get_infeasible_fixture()
    inf_res = generate_single(inf_inp)
    assert not inf_res.is_valid

    # 3. Independent Validator Execution
    val_valid = IndependentTimetableValidator(get_manual_valid_timetable()).validate()
    assert val_valid.is_valid

    val_invalid = IndependentTimetableValidator(get_manual_invalid_timetable()).validate()
    assert not val_invalid.is_valid
