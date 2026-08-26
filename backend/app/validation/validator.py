from typing import List, Dict, Optional
from collections import defaultdict
from app.schemas.contracts import (
    TimetableSessionContract,
    ValidationResult,
    ValidationError,
    SchedulingInput,
)


class IndependentTimetableValidator:
    """
    Independent Rule-Based Validator completely decoupled from the CP-SAT solver.
    Inspects candidate timetables directly against hard constraints.
    """

    def __init__(
        self,
        sessions: List[TimetableSessionContract],
        scheduling_input: Optional[SchedulingInput] = None,
    ):
        self.sessions = sessions
        self.input = scheduling_input

    def validate(self) -> ValidationResult:
        """Executes all independent rule checks."""
        errors: List[ValidationError] = []

        # 1. Faculty Clash Check
        self._check_faculty_clashes(errors)

        # 2. Section Clash Check
        self._check_section_clashes(errors)

        # 3. Room Clash Check
        self._check_room_clashes(errors)

        # 4. Lab Clash Check
        self._check_lab_clashes(errors)

        if self.input:
            # 5. Room Capacity Check
            self._check_room_capacities(errors)

            # 6. Lab Capacity Check
            self._check_lab_capacities(errors)

            # 7. Faculty Eligibility Check
            self._check_faculty_eligibility(errors)

            # 8. Weekly Hours Requirement Check
            self._check_subject_weekly_hours(errors)

            # 9. Resource Availability Check
            self._check_resource_availability(errors)

            # 10. First-Year Paired Slot Check
            if self.input.is_joint_first_year:
                self._check_first_year_paired_slots(errors)

        hard_count = sum(1 for e in errors if e.severity == "ERROR")
        soft_count = sum(1 for e in errors if e.severity == "WARNING")

        return ValidationResult(
            is_valid=(hard_count == 0),
            total_hard_violations=hard_count,
            total_soft_violations=soft_count,
            errors=errors,
            summary={"total_sessions_checked": len(self.sessions)},
        )

    def _check_first_year_paired_slots(self, errors: List[ValidationError]) -> None:
        """Validates that paired Physics and Chemistry cycle sections share identical slot indices."""
        if not self.input:
            return

        subj_map = {s.subject_id: s for s in self.input.subjects}
        sec_map = {s.id: s for s in self.input.sections}

        # Group sessions by stream and slot
        stream_slot_cycles: Dict[tuple, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for s in self.sessions:
            sec = sec_map.get(s.section_id)
            subj = subj_map.get(s.subject_id)
            if sec and sec.stream_id and sec.cycle_group and subj and subj.cycle_group:
                stream_slot_cycles[(sec.stream_id, s.time_slot_id)][subj.cycle_group] += 1

        for (stream_id, slot_id), cycle_counts in stream_slot_cycles.items():
            phy_count = cycle_counts.get("PHYSICS_CYCLE", 0)
            chem_count = cycle_counts.get("CHEMISTRY_CYCLE", 0)
            if phy_count != chem_count:
                errors.append(
                    ValidationError(
                        rule_code="PAIRED_SLOT_MISMATCH",
                        severity="ERROR",
                        message=f"Stream ID {stream_id} at TimeSlot {slot_id} has unequal cycle classes: Physics={phy_count}, Chemistry={chem_count}.",
                        time_slot_id=slot_id,
                        conflicting_resource_id=stream_id,
                    )
                )

    def _check_faculty_clashes(self, errors: List[ValidationError]) -> None:
        fac_slot_map: Dict[tuple, List[TimetableSessionContract]] = defaultdict(list)
        for s in self.sessions:
            fac_slot_map[(s.faculty_id, s.time_slot_id)].append(s)

        for (fac_id, slot_id), sess_list in fac_slot_map.items():
            if len(sess_list) > 1:
                errors.append(
                    ValidationError(
                        rule_code="FACULTY_CLASH",
                        severity="ERROR",
                        message=f"Faculty ID {fac_id} is assigned to {len(sess_list)} sessions simultaneously at TimeSlot {slot_id}.",
                        session_ids=[s.id for s in sess_list if s.id is not None],
                        conflicting_resource_id=fac_id,
                        time_slot_id=slot_id,
                    )
                )

    def _check_section_clashes(self, errors: List[ValidationError]) -> None:
        sec_slot_map: Dict[tuple, List[TimetableSessionContract]] = defaultdict(list)
        for s in self.sessions:
            if s.batch_id is None:  # Theory session for whole section
                sec_slot_map[(s.section_id, s.time_slot_id)].append(s)

        for (sec_id, slot_id), sess_list in sec_slot_map.items():
            if len(sess_list) > 1:
                errors.append(
                    ValidationError(
                        rule_code="SECTION_CLASH",
                        severity="ERROR",
                        message=f"Section ID {sec_id} has {len(sess_list)} concurrent whole-section sessions at TimeSlot {slot_id}.",
                        session_ids=[s.id for s in sess_list if s.id is not None],
                        conflicting_resource_id=sec_id,
                        time_slot_id=slot_id,
                    )
                )

    def _check_room_clashes(self, errors: List[ValidationError]) -> None:
        room_slot_map: Dict[tuple, List[TimetableSessionContract]] = defaultdict(list)
        for s in self.sessions:
            if s.room_id is not None:
                room_slot_map[(s.room_id, s.time_slot_id)].append(s)

        for (room_id, slot_id), sess_list in room_slot_map.items():
            if len(sess_list) > 1:
                errors.append(
                    ValidationError(
                        rule_code="ROOM_CLASH",
                        severity="ERROR",
                        message=f"Room ID {room_id} is assigned to {len(sess_list)} sessions simultaneously at TimeSlot {slot_id}.",
                        session_ids=[s.id for s in sess_list if s.id is not None],
                        conflicting_resource_id=room_id,
                        time_slot_id=slot_id,
                    )
                )

    def _check_lab_clashes(self, errors: List[ValidationError]) -> None:
        lab_slot_map: Dict[tuple, List[TimetableSessionContract]] = defaultdict(list)
        for s in self.sessions:
            if s.lab_id is not None:
                lab_slot_map[(s.lab_id, s.time_slot_id)].append(s)

        for (lab_id, slot_id), sess_list in lab_slot_map.items():
            if len(sess_list) > 1:
                errors.append(
                    ValidationError(
                        rule_code="LAB_CLASH",
                        severity="ERROR",
                        message=f"Lab ID {lab_id} is assigned to {len(sess_list)} batch sessions simultaneously at TimeSlot {slot_id}.",
                        session_ids=[s.id for s in sess_list if s.id is not None],
                        conflicting_resource_id=lab_id,
                        time_slot_id=slot_id,
                    )
                )

    def _check_room_capacities(self, errors: List[ValidationError]) -> None:
        if not self.input:
            return
        room_map = {r.id: r for r in self.input.rooms}
        sec_map = {s.id: s for s in self.input.sections}

        for s in self.sessions:
            if s.room_id is not None and s.room_id in room_map and s.section_id in sec_map:
                room = room_map[s.room_id]
                sec = sec_map[s.section_id]
                if room.capacity < sec.student_count:
                    errors.append(
                        ValidationError(
                            rule_code="ROOM_CAPACITY",
                            severity="ERROR",
                            message=f"Room ID {room.id} capacity ({room.capacity}) is smaller than Section ID {sec.id} student count ({sec.student_count}).",
                            session_ids=[s.id] if s.id else [],
                            conflicting_resource_id=room.id,
                            time_slot_id=s.time_slot_id,
                        )
                    )

    def _check_lab_capacities(self, errors: List[ValidationError]) -> None:
        if not self.input:
            return
        lab_map = {l.id: l for l in self.input.labs}
        batch_map = {b.id: b for b in self.input.batches}

        for s in self.sessions:
            if s.lab_id is not None and s.lab_id in lab_map and s.batch_id and s.batch_id in batch_map:
                lab = lab_map[s.lab_id]
                batch = batch_map[s.batch_id]
                if lab.capacity < batch.student_count:
                    errors.append(
                        ValidationError(
                            rule_code="LAB_CAPACITY",
                            severity="ERROR",
                            message=f"Lab ID {lab.id} capacity ({lab.capacity}) is smaller than Batch ID {batch.id} student count ({batch.student_count}).",
                            session_ids=[s.id] if s.id else [],
                            conflicting_resource_id=lab.id,
                            time_slot_id=s.time_slot_id,
                        )
                    )

    def _check_faculty_eligibility(self, errors: List[ValidationError]) -> None:
        if not self.input:
            return
        subj_map = {sub.subject_id: sub for sub in self.input.subjects}

        for s in self.sessions:
            if s.subject_id in subj_map:
                subj = subj_map[s.subject_id]
                if s.faculty_id not in subj.eligible_faculty_ids:
                    errors.append(
                        ValidationError(
                            rule_code="FACULTY_INELIGIBLE",
                            severity="ERROR",
                            message=f"Faculty ID {s.faculty_id} is not eligible to teach Subject ID {s.subject_id} ({subj.subject_code}).",
                            session_ids=[s.id] if s.id else [],
                            conflicting_resource_id=s.faculty_id,
                            time_slot_id=s.time_slot_id,
                        )
                    )

    def _check_subject_weekly_hours(self, errors: List[ValidationError]) -> None:
        if not self.input:
            return
        sec_subj_counts: Dict[tuple, int] = defaultdict(int)
        batch_subj_counts: Dict[tuple, int] = defaultdict(int)

        for s in self.sessions:
            if s.batch_id is not None:
                batch_subj_counts[(s.batch_id, s.subject_id)] += 1
            else:
                sec_subj_counts[(s.section_id, s.subject_id)] += 1

        for sec in self.input.sections:
            for subj in self.input.subjects:
                if subj.stream_id and sec.stream_id and subj.stream_id != sec.stream_id:
                    continue
                if subj.cycle_group and sec.cycle_group and subj.cycle_group != sec.cycle_group:
                    continue

                if subj.subject_type == "LAB":
                    sec_batches = [b for b in self.input.batches if b.section_id == sec.id]
                    for batch in sec_batches:
                        count = batch_subj_counts[(batch.id, subj.subject_id)]
                        if count != subj.weekly_hours:
                            errors.append(
                                ValidationError(
                                    rule_code="MISSING_SESSION",
                                    severity="ERROR",
                                    message=f"Batch ID {batch.id} has {count} sessions scheduled for Subject ID {subj.subject_id}, but {subj.weekly_hours} were required.",
                                    session_ids=[],
                                    conflicting_resource_id=subj.subject_id,
                                )
                            )
                else:
                    count = sec_subj_counts[(sec.id, subj.subject_id)]
                    if count != subj.weekly_hours:
                        errors.append(
                            ValidationError(
                                rule_code="MISSING_SESSION",
                                severity="ERROR",
                                message=f"Section ID {sec.id} has {count} sessions scheduled for Subject ID {subj.subject_id}, but {subj.weekly_hours} were required.",
                                session_ids=[],
                                conflicting_resource_id=subj.subject_id,
                            )
                        )

    def _check_resource_availability(self, errors: List[ValidationError]) -> None:
        if not self.input:
            return
        room_map = {r.id: r for r in self.input.rooms}
        lab_map = {l.id: l for l in self.input.labs}

        for s in self.sessions:
            if s.room_id and s.room_id in room_map and not room_map[s.room_id].is_available:
                errors.append(
                    ValidationError(
                        rule_code="RESOURCE_UNAVAILABLE",
                        severity="ERROR",
                        message=f"Room ID {s.room_id} is marked unavailable.",
                        session_ids=[s.id] if s.id else [],
                        conflicting_resource_id=s.room_id,
                        time_slot_id=s.time_slot_id,
                    )
                )
            if s.lab_id and s.lab_id in lab_map and not lab_map[s.lab_id].is_available:
                errors.append(
                    ValidationError(
                        rule_code="RESOURCE_UNAVAILABLE",
                        severity="ERROR",
                        message=f"Lab ID {s.lab_id} is marked unavailable.",
                        session_ids=[s.id] if s.id else [],
                        conflicting_resource_id=s.lab_id,
                        time_slot_id=s.time_slot_id,
                    )
                )
