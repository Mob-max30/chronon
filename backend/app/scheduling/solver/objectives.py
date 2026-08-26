from collections import defaultdict
from typing import Dict, List
from ortools.sat.python import cp_model
from app.schemas.contracts import SchedulingInput
from app.scheduling.solver.variables import VariableBuilder


class SoftObjectiveBuilder:
    """
    Builds soft objective terms and optimization goal for the CP-SAT model.
    """

    def __init__(
        self,
        model: cp_model.CpModel,
        scheduling_input: SchedulingInput,
        var_builder: VariableBuilder,
    ):
        self.model = model
        self.input = scheduling_input
        self.var_builder = var_builder
        self.penalty_terms: List[cp_model.LinearExpr] = []

    def apply_soft_objectives(self) -> None:
        """Configures multi-objective minimization penalty terms."""
        w = self.input.objective_weights

        self._penalize_subject_clustering_on_same_day(w.distribute_subject_days)
        self._penalize_student_gaps(w.minimize_student_gaps)
        self._penalize_faculty_gaps(w.minimize_faculty_gaps)

        if self.penalty_terms:
            self.model.Minimize(sum(self.penalty_terms))

    def _penalize_subject_clustering_on_same_day(self, weight: int) -> None:
        """Penalizes scheduling multiple sessions of the same subject for a section on the same day."""
        if weight <= 0:
            return

        slot_map = {s.id: s for s in self.input.time_slots}
        subj_sec_day_vars: Dict[tuple, List[cp_model.IntVar]] = defaultdict(list)

        for key, var in self.var_builder.theory_vars.items():
            subj_id, _, sec_id, _, slot_id = key
            slot = slot_map.get(slot_id)
            if slot:
                subj_sec_day_vars[(subj_id, sec_id, slot.day_of_week)].append(var)

        for (subj_id, sec_id, day), vars_list in subj_sec_day_vars.items():
            if len(vars_list) > 1:
                # Excess classes beyond 1 on the same day create a penalty
                count_var = self.model.NewIntVar(0, len(vars_list), f"subj_day_cnt_s{subj_id}_sec{sec_id}_d{day}")
                self.model.Add(count_var == sum(vars_list))

                excess_var = self.model.NewIntVar(0, len(vars_list), f"subj_day_exc_s{subj_id}_sec{sec_id}_d{day}")
                # excess_var >= count_var - 1
                self.model.Add(excess_var >= count_var - 1)
                self.penalty_terms.append(excess_var * weight)

    def _penalize_student_gaps(self, weight: int) -> None:
        """Penalizes idle gap periods for a section on a given day."""
        if weight <= 0:
            return

        slot_map = {s.id: s for s in self.input.time_slots}
        sec_day_slots: Dict[tuple, Dict[int, List[cp_model.IntVar]]] = defaultdict(lambda: defaultdict(list))

        for key, var in self.var_builder.theory_vars.items():
            _, _, sec_id, _, slot_id = key
            slot = slot_map.get(slot_id)
            if slot:
                sec_day_slots[(sec_id, slot.day_of_week)][slot.period_index].append(var)

        for (sec_id, day), period_dict in sec_day_slots.items():
            sorted_periods = sorted(period_dict.keys())
            for i in range(len(sorted_periods) - 1):
                p1 = sorted_periods[i]
                p2 = sorted_periods[i + 1]
                if p2 > p1 + 1:  # Non-consecutive period index gap
                    p1_active = self.model.NewBoolVar(f"p1_act_sec{sec_id}_d{day}_p{p1}")
                    p2_active = self.model.NewBoolVar(f"p2_act_sec{sec_id}_d{day}_p{p2}")

                    self.model.Add(p1_active == sum(period_dict[p1]))
                    self.model.Add(p2_active == sum(period_dict[p2]))

                    gap_active = self.model.NewBoolVar(f"gap_act_sec{sec_id}_d{day}_{p1}_{p2}")
                    self.model.AddBoolAnd([p1_active, p2_active]).OnlyEnforceIf(gap_active)
                    self.model.AddBoolOr([p1_active.Not(), p2_active.Not()]).OnlyEnforceIf(gap_active.Not())

                    self.penalty_terms.append(gap_active * weight * (p2 - p1 - 1))

    def _penalize_faculty_gaps(self, weight: int) -> None:
        """Penalizes idle gap periods for faculty on a given day."""
        if weight <= 0:
            return

        slot_map = {s.id: s for s in self.input.time_slots}
        fac_day_slots: Dict[tuple, Dict[int, List[cp_model.IntVar]]] = defaultdict(lambda: defaultdict(list))

        for key, var in self.var_builder.theory_vars.items():
            _, fac_id, _, _, slot_id = key
            slot = slot_map.get(slot_id)
            if slot:
                fac_day_slots[(fac_id, slot.day_of_week)][slot.period_index].append(var)

        for (fac_id, day), period_dict in fac_day_slots.items():
            sorted_periods = sorted(period_dict.keys())
            for i in range(len(sorted_periods) - 1):
                p1 = sorted_periods[i]
                p2 = sorted_periods[i + 1]
                if p2 > p1 + 1:
                    p1_active = self.model.NewBoolVar(f"fac_p1_act_f{fac_id}_d{day}_p{p1}")
                    p2_active = self.model.NewBoolVar(f"fac_p2_act_f{fac_id}_d{day}_p{p2}")

                    self.model.Add(p1_active == sum(period_dict[p1]))
                    self.model.Add(p2_active == sum(period_dict[p2]))

                    gap_active = self.model.NewBoolVar(f"fac_gap_act_f{fac_id}_d{day}_{p1}_{p2}")
                    self.model.AddBoolAnd([p1_active, p2_active]).OnlyEnforceIf(gap_active)
                    self.model.AddBoolOr([p1_active.Not(), p2_active.Not()]).OnlyEnforceIf(gap_active.Not())

                    self.penalty_terms.append(gap_active * weight * (p2 - p1 - 1))
