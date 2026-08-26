from collections import defaultdict
from typing import Dict, List
from ortools.sat.python import cp_model
from app.schemas.contracts import SchedulingInput
from app.scheduling.solver.variables import VariableBuilder


class HardConstraintBuilder:
    """
    Formulates and applies all mathematical hard constraints to the CP-SAT model.
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

    def apply_all_hard_constraints(self) -> None:
        """Applies all hard constraints in domain priority order."""
        self._apply_subject_session_requirements()
        self._apply_faculty_clash()
        self._apply_section_clash()
        self._apply_room_clash()
        self._apply_lab_clash()
        self._apply_capacity_constraints()
        self._apply_resource_unavailability()
        if self.input.is_joint_first_year:
            self._apply_first_year_paired_slots()
            self._apply_cross_stream_shared_labs()

    def _apply_first_year_paired_slots(self) -> None:
        """Requirement: First-Year paired Physics & Chemistry cycle sections must share matching slot indices."""
        slot_ids = [s.id for s in self.input.time_slots]

        # Group sections by stream
        stream_sec_map: Dict[int, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        for sec in self.input.sections:
            if sec.stream_id and sec.cycle_group:
                stream_sec_map[sec.stream_id][sec.cycle_group].append(sec.id)

        phy_subjects = [s.subject_id for s in self.input.subjects if s.cycle_group == "PHYSICS_CYCLE"]
        chem_subjects = [s.subject_id for s in self.input.subjects if s.cycle_group == "CHEMISTRY_CYCLE"]

        for stream_id, cycle_map in stream_sec_map.items():
            phy_sec_ids = cycle_map.get("PHYSICS_CYCLE", [])
            chem_sec_ids = cycle_map.get("CHEMISTRY_CYCLE", [])

            if phy_sec_ids and chem_sec_ids and phy_subjects and chem_subjects:
                for slot_id in slot_ids:
                    phy_active_vars = [
                        var for key, var in self.var_builder.theory_vars.items()
                        if key[0] in phy_subjects and key[2] in phy_sec_ids and key[4] == slot_id
                    ]
                    chem_active_vars = [
                        var for key, var in self.var_builder.theory_vars.items()
                        if key[0] in chem_subjects and key[2] in chem_sec_ids and key[4] == slot_id
                    ]

                    phy_sum = sum(phy_active_vars) if phy_active_vars else 0
                    chem_sum = sum(chem_active_vars) if chem_active_vars else 0
                    self.model.Add(phy_sum == chem_sum)

    def _apply_cross_stream_shared_labs(self) -> None:
        """Prevents physical lab collisions across different first-year streams."""
        lab_slot_vars: Dict[tuple, List[cp_model.IntVar]] = defaultdict(list)
        for key, var in self.var_builder.lab_vars.items():
            lab_id = key[4]
            slot_id = key[5]
            lab_slot_vars[(lab_id, slot_id)].append(var)

        for (lab_id, slot_id), var_list in lab_slot_vars.items():
            if len(var_list) > 1:
                self.model.AddAtMostOne(var_list)

    def _apply_subject_session_requirements(self) -> None:
        """Requirement K: Every subject must meet its required weekly hours for each section/batch."""
        for subj in self.input.subjects:
            if subj.subject_type == "LAB":
                for sec in self.input.sections:
                    sec_batches = [b for b in self.input.batches if b.section_id == sec.id]
                    for batch in sec_batches:
                        batch_vars = [
                            var
                            for key, var in self.var_builder.lab_vars.items()
                            if key[0] == subj.subject_id and key[2] == sec.id and key[3] == batch.id
                        ]
                        if batch_vars:
                            self.model.Add(sum(batch_vars) == subj.weekly_hours)
            else:
                for sec in self.input.sections:
                    sec_vars = [
                        var
                        for key, var in self.var_builder.theory_vars.items()
                        if key[0] == subj.subject_id and key[2] == sec.id
                    ]
                    if sec_vars:
                        self.model.Add(sum(sec_vars) == subj.weekly_hours)

    def _apply_faculty_clash(self) -> None:
        """Constraint A: A faculty member cannot teach two sessions at the same time slot."""
        fac_slot_vars: Dict[tuple, List[cp_model.IntVar]] = defaultdict(list)

        for key, var in self.var_builder.theory_vars.items():
            _, fac_id, _, _, slot_id = key
            fac_slot_vars[(fac_id, slot_id)].append(var)

        for key, var in self.var_builder.lab_vars.items():
            _, fac_id, _, _, _, slot_id = key
            fac_slot_vars[(fac_id, slot_id)].append(var)

        for (fac_id, slot_id), var_list in fac_slot_vars.items():
            self.model.AddAtMostOne(var_list)

    def _apply_section_clash(self) -> None:
        """Constraint B: A section cannot attend two sessions at the same time slot."""
        sec_slot_vars: Dict[tuple, List[cp_model.IntVar]] = defaultdict(list)

        for key, var in self.var_builder.theory_vars.items():
            _, _, sec_id, _, slot_id = key
            sec_slot_vars[(sec_id, slot_id)].append(var)

        for key, var in self.var_builder.lab_vars.items():
            _, _, sec_id, _, _, slot_id = key
            sec_slot_vars[(sec_id, slot_id)].append(var)

        for (sec_id, slot_id), var_list in sec_slot_vars.items():
            self.model.AddAtMostOne(var_list)

    def _apply_room_clash(self) -> None:
        """Constraint C: A theory room cannot host two sessions at the same time slot."""
        room_slot_vars: Dict[tuple, List[cp_model.IntVar]] = defaultdict(list)

        for key, var in self.var_builder.theory_vars.items():
            _, _, _, room_id, slot_id = key
            room_slot_vars[(room_id, slot_id)].append(var)

        for (room_id, slot_id), var_list in room_slot_vars.items():
            self.model.AddAtMostOne(var_list)

    def _apply_lab_clash(self) -> None:
        """Constraint D: A physical lab cannot host multiple batch sessions at the same time slot."""
        lab_slot_vars: Dict[tuple, List[cp_model.IntVar]] = defaultdict(list)

        for key, var in self.var_builder.lab_vars.items():
            _, _, _, _, lab_id, slot_id = key
            lab_slot_vars[(lab_id, slot_id)].append(var)

        for (lab_id, slot_id), var_list in lab_slot_vars.items():
            self.model.AddAtMostOne(var_list)

    def _apply_capacity_constraints(self) -> None:
        """Constraints E & F: Assigned room and lab capacities must fit student counts."""
        room_map = {r.id: r for r in self.input.rooms}
        lab_map = {l.id: l for l in self.input.labs}
        sec_map = {s.id: s for s in self.input.sections}
        batch_map = {b.id: b for b in self.input.batches}

        for key, var in self.var_builder.theory_vars.items():
            _, _, sec_id, room_id, _ = key
            sec = sec_map.get(sec_id)
            room = room_map.get(room_id)
            if sec and room and room.capacity < sec.student_count:
                # Force variable to 0 (cannot assign room smaller than student count)
                self.model.Add(var == 0)

        for key, var in self.var_builder.lab_vars.items():
            _, _, _, batch_id, lab_id, _ = key
            batch = batch_map.get(batch_id)
            lab = lab_map.get(lab_id)
            if batch and lab and lab.capacity < batch.student_count:
                self.model.Add(var == 0)

    def _apply_resource_unavailability(self) -> None:
        """Constraint I: Disabled rooms, labs, or unavailable faculty slots cannot be assigned."""
        for room in self.input.rooms:
            if not room.is_available:
                for key, var in self.var_builder.theory_vars.items():
                    if key[3] == room.id:
                        self.model.Add(var == 0)

        for lab in self.input.labs:
            if not lab.is_available:
                for key, var in self.var_builder.lab_vars.items():
                    if key[4] == lab.id:
                        self.model.Add(var == 0)

        for fac_avail in self.input.faculty_availability:
            for unavail_slot_id in fac_avail.unavailable_slot_ids:
                for key, var in self.var_builder.theory_vars.items():
                    if key[1] == fac_avail.faculty_id and key[4] == unavail_slot_id:
                        self.model.Add(var == 0)
                for key, var in self.var_builder.lab_vars.items():
                    if key[1] == fac_avail.faculty_id and key[5] == unavail_slot_id:
                        self.model.Add(var == 0)
