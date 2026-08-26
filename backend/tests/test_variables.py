from ortools.sat.python import cp_model
from app.scheduling.fixtures import get_sample_scheduling_input
from app.scheduling.solver.variables import VariableBuilder


def test_variable_builder_creates_decision_variables():
    model = cp_model.CpModel()
    inp = get_sample_scheduling_input()
    builder = VariableBuilder(model, inp)
    builder.build_variables()

    assert len(builder.theory_vars) > 0
    # Every variable should be a valid CP-SAT BoolVar
    for key, var in builder.theory_vars.items():
        assert var is not None
