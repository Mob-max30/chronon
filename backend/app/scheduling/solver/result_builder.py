from typing import List, Dict, Any
from ortools.sat.python import cp_model
from app.schemas.contracts import (
    SchedulingInput,
    TimetableSessionContract,
    QualityScore,
)
from app.scheduling.solver.variables import VariableBuilder


class ResultBuilder:
    """
    Converts CP-SAT model solution values into domain session contracts and quality score breakdowns.
    """

    def __init__(
        self,
        solver: cp_model.CpSolver,
        scheduling_input: SchedulingInput,
        var_builder: VariableBuilder,
    ):
        self.solver = solver
        self.input = scheduling_input
        self.var_builder = var_builder

    def extract_sessions(self) -> List[TimetableSessionContract]:
        """Extracts active sessions from solver variable assignments."""
        sessions: List[TimetableSessionContract] = []
        session_id_counter = 1

        for key, var in self.var_builder.theory_vars.items():
            if self.solver.Value(var) == 1:
                subj_id, fac_id, sec_id, room_id, slot_id = key
                sessions.append(
                    TimetableSessionContract(
                        id=session_id_counter,
                        version_id=1,
                        subject_id=subj_id,
                        faculty_id=fac_id,
                        section_id=sec_id,
                        batch_id=None,
                        room_id=room_id,
                        lab_id=None,
                        time_slot_id=slot_id,
                    )
                )
                session_id_counter += 1

        for key, var in self.var_builder.lab_vars.items():
            if self.solver.Value(var) == 1:
                subj_id, fac_id, sec_id, batch_id, lab_id, slot_id = key
                sessions.append(
                    TimetableSessionContract(
                        id=session_id_counter,
                        version_id=1,
                        subject_id=subj_id,
                        faculty_id=fac_id,
                        section_id=sec_id,
                        batch_id=batch_id,
                        room_id=None,
                        lab_id=lab_id,
                        time_slot_id=slot_id,
                    )
                )
                session_id_counter += 1

        return sessions

    def calculate_quality_score(self, sessions: List[TimetableSessionContract]) -> QualityScore:
        """Calculates deterministic quality score components based on scheduled sessions."""
        if not sessions:
            return QualityScore(
                overall_score=0.0,
                student_gap_score=0.0,
                faculty_gap_score=0.0,
                distribution_score=0.0,
                workload_balance_score=0.0,
                breakdown={"message": "No sessions scheduled"},
            )

        slot_map = {s.id: s for s in self.input.time_slots}

        # 1. Distribution Score (check how sessions are distributed across days)
        sec_subj_days: Dict[tuple, set] = {}
        for s in sessions:
            slot = slot_map.get(s.time_slot_id)
            if slot:
                key = (s.section_id, s.subject_id)
                if key not in sec_subj_days:
                    sec_subj_days[key] = set()
                sec_subj_days[key].add(slot.day_of_week)

        total_distributions = len(sec_subj_days)
        well_distributed = sum(1 for days in sec_subj_days.values() if len(days) >= 2)
        dist_score = (well_distributed / total_distributions * 100.0) if total_distributions > 0 else 100.0

        # 2. Student Gap Score (check gaps in student schedules)
        sec_day_slots: Dict[tuple, List[int]] = {}
        for s in sessions:
            slot = slot_map.get(s.time_slot_id)
            if slot:
                key = (s.section_id, slot.day_of_week)
                if key not in sec_day_slots:
                    sec_day_slots[key] = []
                sec_day_slots[key].append(slot.period_index)

        student_gaps = 0
        for periods in sec_day_slots.values():
            sorted_p = sorted(periods)
            for i in range(len(sorted_p) - 1):
                if sorted_p[i + 1] > sorted_p[i] + 1:
                    student_gaps += (sorted_p[i + 1] - sorted_p[i] - 1)

        stud_gap_score = max(0.0, 100.0 - (student_gaps * 5.0))

        # 3. Faculty Gap Score
        fac_day_slots: Dict[tuple, List[int]] = {}
        for s in sessions:
            slot = slot_map.get(s.time_slot_id)
            if slot:
                key = (s.faculty_id, slot.day_of_week)
                if key not in fac_day_slots:
                    fac_day_slots[key] = []
                fac_day_slots[key].append(slot.period_index)

        fac_gaps = 0
        for periods in fac_day_slots.values():
            sorted_p = sorted(periods)
            for i in range(len(sorted_p) - 1):
                if sorted_p[i + 1] > sorted_p[i] + 1:
                    fac_gaps += (sorted_p[i + 1] - sorted_p[i] - 1)

        fac_gap_score = max(0.0, 100.0 - (fac_gaps * 5.0))

        # 4. Workload Balance Score
        sec_day_counts: Dict[tuple, int] = {}
        for s in sessions:
            slot = slot_map.get(s.time_slot_id)
            if slot:
                key = (s.section_id, slot.day_of_week)
                sec_day_counts[key] = sec_day_counts.get(key, 0) + 1

        counts = list(sec_day_counts.values())
        if counts:
            max_c = max(counts)
            min_c = min(counts)
            workload_balance_score = max(0.0, 100.0 - ((max_c - min_c) * 10.0))
        else:
            workload_balance_score = 100.0

        overall = (dist_score * 0.3) + (stud_gap_score * 0.3) + (fac_gap_score * 0.2) + (workload_balance_score * 0.2)

        return QualityScore(
            overall_score=round(overall, 2),
            student_gap_score=round(stud_gap_score, 2),
            faculty_gap_score=round(fac_gap_score, 2),
            distribution_score=round(dist_score, 2),
            workload_balance_score=round(workload_balance_score, 2),
            breakdown={
                "total_sessions": len(sessions),
                "student_gaps_count": student_gaps,
                "faculty_gaps_count": fac_gaps,
            },
        )
