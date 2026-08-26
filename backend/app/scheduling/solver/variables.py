from typing import Dict, Tuple
from ortools.sat.python import cp_model
from app.schemas.contracts import SchedulingInput


class VariableBuilder:
    """
    Decoupled decision variable generator for CP-SAT timetable formulation.
    """

    def __init__(self, model: cp_model.CpModel, scheduling_input: SchedulingInput):
        self.model = model
        self.input = scheduling_input

        # theory_vars: (subject_id, faculty_id, section_id, room_id, slot_id) -> BoolVar
        self.theory_vars: Dict[Tuple[int, int, int, int, int], cp_model.IntVar] = {}

        # lab_vars: (subject_id, faculty_id, section_id, batch_id, lab_id, slot_id) -> BoolVar
        self.lab_vars: Dict[Tuple[int, int, int, int, int, int], cp_model.IntVar] = {}

    def build_variables(self) -> None:
        """Creates boolean decision variables based on subject requirements and available resources."""
        room_map = {r.id: r for r in self.input.rooms}

        for subj in self.input.subjects:
            if subj.subject_type == "LAB":
                # Create lab decision variables per batch
                lab_id = subj.required_lab_id or (self.input.labs[0].id if self.input.labs else 1)
                for sec in self.input.sections:
                    if subj.stream_id and sec.stream_id and subj.stream_id != sec.stream_id:
                        continue
                    if subj.cycle_group and sec.cycle_group and subj.cycle_group != sec.cycle_group:
                        continue
                    sec_batches = [b for b in self.input.batches if b.section_id == sec.id]
                    if not sec_batches:
                        continue
                    for batch in sec_batches:
                        for fac_id in subj.eligible_faculty_ids:
                            for slot in self.input.time_slots:
                                key = (subj.subject_id, fac_id, sec.id, batch.id, lab_id, slot.id)
                                var_name = f"lab_s{subj.subject_id}_f{fac_id}_sec{sec.id}_b{batch.id}_l{lab_id}_t{slot.id}"
                                self.lab_vars[key] = self.model.NewBoolVar(var_name)
            else:
                # Theory subject decision variables per section
                for sec in self.input.sections:
                    if subj.stream_id and sec.stream_id and subj.stream_id != sec.stream_id:
                        continue
                    if subj.cycle_group and sec.cycle_group and subj.cycle_group != sec.cycle_group:
                        continue
                    # Filter rooms: either section's dedicated room or any available room
                    candidate_rooms = self.input.rooms
                    if sec.room_id and sec.room_id in room_map:
                        candidate_rooms = [room_map[sec.room_id]]

                    for room in candidate_rooms:
                        for fac_id in subj.eligible_faculty_ids:
                            for slot in self.input.time_slots:
                                key = (subj.subject_id, fac_id, sec.id, room.id, slot.id)
                                var_name = f"theory_s{subj.subject_id}_f{fac_id}_sec{sec.id}_r{room.id}_t{slot.id}"
                                self.theory_vars[key] = self.model.NewBoolVar(var_name)
