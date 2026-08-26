import time
from typing import Tuple, List, Dict, Any
from ortools.sat.python import cp_model
from app.schemas.contracts import (
    SchedulingInput,
    TimetableSessionContract,
    QualityScore,
)
from app.scheduling.solver.variables import VariableBuilder
from app.scheduling.solver.constraints import HardConstraintBuilder
from app.scheduling.solver.objectives import SoftObjectiveBuilder
from app.scheduling.solver.result_builder import ResultBuilder


class ChrononCPSATSolver:
    """
    Production-grade Google OR-Tools CP-SAT Solver for Chronon Timetable Generation.
    Fully deterministic with configurable worker threads, timeouts, hard constraints, and soft objectives.
    """

    def __init__(self, scheduling_input: SchedulingInput):
        self.input = scheduling_input
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        # Solver configuration
        self.solver.parameters.max_time_in_seconds = float(scheduling_input.max_solver_time_seconds)
        self.solver.parameters.num_search_workers = max(1, scheduling_input.max_workers)
        # Deterministic seed configuration
        self.solver.parameters.random_seed = 42

        # Internal components
        self.var_builder = VariableBuilder(self.model, self.input)
        self.constraint_builder = HardConstraintBuilder(self.model, self.input, self.var_builder)
        self.objective_builder = SoftObjectiveBuilder(self.model, self.input, self.var_builder)

    def build_model(self) -> None:
        """Builds decision variables, hard constraints, and soft objectives."""
        self.var_builder.build_variables()
        self.constraint_builder.apply_all_hard_constraints()
        self.objective_builder.apply_soft_objectives()

    def build_minimal_prototype_model(self) -> None:
        """Backward-compatible wrapper method for legacy callers."""
        self.build_model()

    def solve(self) -> Tuple[str, float, List[TimetableSessionContract], QualityScore, Dict[str, Any]]:
        """
        Executes CP-SAT solve search.
        Returns:
            (status_str, duration_seconds, sessions, quality_score, solver_stats)
        """
        start_time = time.time()
        cp_status = self.solver.Solve(self.model)
        duration = time.time() - start_time

        result_builder = ResultBuilder(self.solver, self.input, self.var_builder)

        solver_stats = {
            "cp_sat_status": self.solver.StatusName(cp_status),
            "wall_time_seconds": duration,
            "branches": self.solver.NumBranches(),
            "conflicts": self.solver.NumConflicts(),
        }

        if cp_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status_str = "OPTIMAL" if cp_status == cp_model.OPTIMAL else "FEASIBLE"
            sessions = result_builder.extract_sessions()
            quality = result_builder.calculate_quality_score(sessions)
            return status_str, duration, sessions, quality, solver_stats
        elif cp_status == cp_model.INFEASIBLE:
            sessions = []
            quality = QualityScore(
                overall_score=0.0,
                student_gap_score=0.0,
                faculty_gap_score=0.0,
                distribution_score=0.0,
                workload_balance_score=0.0,
                breakdown={"error": "Infeasible model constraints"},
            )
            return "INFEASIBLE", duration, sessions, quality, solver_stats
        elif cp_status == cp_model.UNKNOWN:
            sessions = []
            quality = QualityScore(
                overall_score=0.0,
                student_gap_score=0.0,
                faculty_gap_score=0.0,
                distribution_score=0.0,
                workload_balance_score=0.0,
                breakdown={"error": "Solver search limit / timeout reached"},
            )
            return "TIMEOUT", duration, sessions, quality, solver_stats
        else:
            sessions = []
            quality = QualityScore(
                overall_score=0.0,
                student_gap_score=0.0,
                faculty_gap_score=0.0,
                distribution_score=0.0,
                workload_balance_score=0.0,
                breakdown={"error": "Solver failed"},
            )
            return "FAILED", duration, sessions, quality, solver_stats
