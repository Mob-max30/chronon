import pytest
from app.scheduling.fixtures import get_sample_scheduling_input
from app.scheduling.solver import ChrononCPSATSolver
from app.scheduling.generators import generate_single


def test_ortools_import_and_basic_solve():
    """
    Verifies that Google OR-Tools CP-SAT can be imported, instantiated,
    and solves the sample scheduling constraint problem.
    """
    sample_input = get_sample_scheduling_input()
    solver_instance = ChrononCPSATSolver(sample_input)
    solver_instance.build_minimal_prototype_model()
    status, duration, sessions = solver_instance.solve()

    assert status in ("SUCCESS", "FEASIBLE", "OPTIMAL")
    assert duration >= 0.0


def test_generate_single_generator():
    sample_input = get_sample_scheduling_input()
    status, duration, sessions = generate_single(sample_input)
    assert status in ("SUCCESS", "FEASIBLE", "OPTIMAL")
