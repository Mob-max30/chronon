import pytest
from app.scheduling.fixtures import get_sample_scheduling_input
from app.schemas.contracts import SchedulingInput, ValidationResult
from app.scheduling.generators import generate_single


def test_valid_scheduling_input_accepted():
    """TEST 1: Valid SchedulingInput is accepted."""
    inp = get_sample_scheduling_input()
    assert isinstance(inp, SchedulingInput)
    assert len(inp.rooms) > 0
    assert len(inp.subjects) > 0


def test_invalid_scheduling_input_rejected():
    """TEST 2: Empty/Invalid SchedulingInput is rejected by pipeline."""
    invalid_inp = SchedulingInput(
        academic_year_id=1,
        semester_ids=[3],
        rooms=[],
        labs=[],
        sections=[],
        batches=[],
        time_slots=[],
        subjects=[],
    )
    res = generate_single(invalid_inp)
    assert res.status == "FAILED"
    assert not res.is_valid
    assert len(res.conflicts) > 0
