from app.scheduling.fixtures import get_sample_scheduling_input
from app.scheduling.solver.solver import ChrononCPSATSolver
from app.scheduling.generators import generate_single


def test_cpsat_solver_solves_basic_fixture():
    """TEST 14: CP-SAT can generate a valid timetable from basic fixture."""
    inp = get_sample_scheduling_input()
    solver = ChrononCPSATSolver(inp)
    solver.build_model()
    status_str, duration, sessions, quality, solver_stats = solver.solve()

    assert status_str in ("OPTIMAL", "FEASIBLE")
    assert duration >= 0.0
    assert len(sessions) > 0


def test_generated_timetable_passes_independent_validator():
    """TEST 15: Generated timetable passes independent validator."""
    inp = get_sample_scheduling_input()
    res = generate_single(inp)

    assert res.status in ("OPTIMAL", "FEASIBLE")
    assert res.is_valid
    assert res.validation.is_valid
    assert len(res.conflicts) == 0
