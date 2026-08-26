from app.scheduling.fixtures import get_infeasible_fixture
from app.scheduling.generators import generate_single


def test_infeasible_fixture_returns_infeasible():
    """TEST 16: Infeasible fixture returns INFEASIBLE status without crashing."""
    inf_input = get_infeasible_fixture()
    res = generate_single(inf_input)

    assert res.status in ("INFEASIBLE", "FAILED")
    assert not res.is_valid
    assert res.sessions == []
    assert isinstance(res.message, str)
