from typing import List, Dict, Any, Tuple
import time
from ortools.sat.python import cp_model
from app.schemas.contracts import (
    SchedulingInput,
    TimetableSessionContract,
    GenerationRunContract,
)


class ChrononCPSATSolver:
    """
    Core Deterministic Timetable Solver using Google OR-Tools CP-SAT.
    """

    def __init__(self, scheduling_input: SchedulingInput):
        self.input = scheduling_input
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = float(scheduling_input.max_solver_time_seconds)
        self.solver.parameters.num_search_workers = scheduling_input.max_workers

        # Decision variables map: (subject_id, faculty_id, section_id, batch_id, room_id, lab_id, slot_id) -> BoolVar
        self.decision_vars: Dict[Tuple, cp_model.IntVar] = {}

    def build_minimal_prototype_model(self) -> None:
        """
        Builds a verified minimal constraint satisfaction model proving CP-SAT formulation.
        """
        # Create decision variables for each required subject-section-slot
        for subj in self.input.subjects:
            for sec in self.input.sections:
                for fac_id in subj.eligible_faculty_ids:
                    for slot in self.input.time_slots:
                        var_name = f"sess_s{subj.subject_id}_f{fac_id}_sec{sec.id}_t{slot.id}"
                        self.decision_vars[(subj.subject_id, fac_id, sec.id, None, sec.room_id, None, slot.id)] = (
                            self.model.NewBoolVar(var_name)
                        )

        # Basic Hard Constraint 1: Faculty cannot be in two places at the same slot
        for fac_id in set(f for s in self.input.subjects for f in s.eligible_faculty_ids):
            for slot in self.input.time_slots:
                vars_for_faculty = [
                    var
                    for key, var in self.decision_vars.items()
                    if key[1] == fac_id and key[6] == slot.id
                ]
                if vars_for_faculty:
                    self.model.AddAtMostOne(vars_for_faculty)

        # Basic Hard Constraint 2: Section cannot have two theory classes at the same slot
        for sec in self.input.sections:
            for slot in self.input.time_slots:
                vars_for_section = [
                    var
                    for key, var in self.decision_vars.items()
                    if key[2] == sec.id and key[6] == slot.id
                ]
                if vars_for_section:
                    self.model.AddAtMostOne(vars_for_section)

        # Basic Objective: Maximize total scheduled subject sessions
        if self.decision_vars:
            self.model.Maximize(sum(self.decision_vars.values()))

    def solve(self) -> Tuple[str, float, List[TimetableSessionContract]]:
        """
        Executes CP-SAT search and returns status, solve duration, and scheduled sessions.
        """
        start_time = time.time()
        status = self.solver.Solve(self.model)
        duration = time.time() - start_time

        sessions: List[TimetableSessionContract] = []

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status_str = "SUCCESS"
            for key, var in self.decision_vars.items():
                if self.solver.Value(var) == 1:
                    s_id, f_id, sec_id, b_id, r_id, l_id, slot_id = key
                    sessions.append(
                        TimetableSessionContract(
                            version_id=1,
                            subject_id=s_id,
                            faculty_id=f_id,
                            section_id=sec_id,
                            batch_id=b_id,
                            room_id=r_id,
                            lab_id=l_id,
                            time_slot_id=slot_id,
                        )
                    )
        elif status == cp_model.INFEASIBLE:
            status_str = "INFEASIBLE"
        else:
            status_str = "FAILED"

        return status_str, duration, sessions
