from app.scheduling.fixtures import get_sample_scheduling_input
from app.scheduling.generators import generate_single


def test_quality_score_is_deterministic():
    """TEST 18: Quality score calculation is deterministic for identical input."""
    inp = get_sample_scheduling_input()
    res1 = generate_single(inp)
    res2 = generate_single(inp)

    assert res1.is_valid
    assert res2.is_valid
    assert res1.quality is not None
    assert res2.quality is not None
    assert res1.quality.overall_score == res2.quality.overall_score
    assert res1.quality.student_gap_score == res2.quality.student_gap_score
    assert res1.quality.faculty_gap_score == res2.quality.faculty_gap_score
