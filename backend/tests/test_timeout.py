from app.scheduling.fixtures import get_sample_scheduling_input
from app.scheduling.solver.solver import ChrononCPSATSolver


def test_timeout_parameter_configured():
    """TEST 17: Solver timeout parameters are configured properly."""
    inp = get_sample_scheduling_input()

    solver = ChrononCPSATSolver(inp)
    assert solver.solver.parameters.max_time_in_seconds == float(inp.max_solver_time_seconds)
