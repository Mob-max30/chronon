from typing import List, Dict
from collections import defaultdict
from app.schemas.contracts import (
    TimetableSessionContract,
    ValidationResult,
    ValidationError,
)


class IndependentTimetableValidator:
    """
    Independent Rule-Based Validator completely decoupled from the CP-SAT solver.
    Can validate any generated or manually modified timetable.
    """

    def __init__(self, sessions: List[TimetableSessionContract]):
        self.sessions = sessions

    def validate(self) -> ValidationResult:
        errors: List[ValidationError] = []

        # 1. Faculty Clash Check: One faculty member in multiple places at the same time slot
        faculty_slot_map: Dict[tuple, List[TimetableSessionContract]] = defaultdict(list)
        for s in self.sessions:
            faculty_slot_map[(s.faculty_id, s.time_slot_id)].append(s)

        for (fac_id, slot_id), sess_list in faculty_slot_map.items():
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

        # 2. Room Clash Check: One room hosted by multiple sessions at the same slot
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

        # 3. Section Clash Check: One section attending multiple theory sessions simultaneously
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

        hard_count = sum(1 for e in errors if e.severity == "ERROR")
        soft_count = sum(1 for e in errors if e.severity == "WARNING")

        return ValidationResult(
            is_valid=(hard_count == 0),
            total_hard_violations=hard_count,
            total_soft_violations=soft_count,
            errors=errors,
            summary={"total_sessions_checked": len(self.sessions)},
        )
