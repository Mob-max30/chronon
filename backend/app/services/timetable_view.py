import csv
import io
from typing import List, Dict, Any, Optional
from datetime import time

from app.schemas.timetable_view import (
    GridCellSession,
    GridCell,
    GridRow,
    PairedSlotGroupItem,
    TimetableMatrixResponse,
    TimetableExportResponse,
)

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def build_timetable_matrix(
    timetable_id: int,
    version_id: Optional[int],
    view_type: str,
    filter_params: Dict[str, Any],
    sessions: List[Dict[str, Any]],
    time_slots: List[Dict[str, Any]],
    conflicts: Optional[List[Dict[str, Any]]] = None,
) -> TimetableMatrixResponse:
    """
    Pure assembler: transforms raw TimetableSession records and TimeSlot definitions
    into a structured 2D grid matrix (Days x Periods) supporting:
    - Multiple view perspectives (Section, Faculty, Room, Lab, Batch, First-Year Cycle)
    - Paired-slot group aggregation
    - Conflict diagnostic overlays
    """
    conflicts = conflicts or []
    conflict_by_session_id: Dict[int, List[Dict[str, Any]]] = {}
    for c in conflicts:
        for s_id in c.get("session_ids", []):
            conflict_by_session_id.setdefault(s_id, []).append(c)

    # Filter sessions based on view perspective
    filtered_sessions: List[Dict[str, Any]] = []
    for s in sessions:
        if view_type == "SECTION" and filter_params.get("section_id"):
            if s.get("section_id") != filter_params["section_id"]:
                continue
        elif view_type == "FACULTY" and filter_params.get("faculty_id"):
            if s.get("faculty_id") != filter_params["faculty_id"]:
                continue
        elif view_type == "ROOM" and filter_params.get("room_id"):
            if s.get("room_id") != filter_params["room_id"]:
                continue
        elif view_type == "LAB" and filter_params.get("lab_id"):
            if s.get("lab_id") != filter_params["lab_id"]:
                continue
        elif view_type == "BATCH" and filter_params.get("batch_id"):
            if s.get("batch_id") != filter_params["batch_id"]:
                continue
        elif view_type == "FIRST_YEAR_CYCLE":
            if filter_params.get("stream_id") and s.get("stream_id") != filter_params["stream_id"]:
                continue
            if filter_params.get("cycle_group") and s.get("cycle_group") != filter_params["cycle_group"]:
                continue

        filtered_sessions.append(s)

    # Index sessions by (day_of_week, period_index / time_slot_id)
    session_map: Dict[tuple, List[GridCellSession]] = {}
    paired_groups_map: Dict[str, List[GridCellSession]] = {}

    for s in filtered_sessions:
        s_id = s.get("id") or s.get("session_id", 0)
        s_conflicts = conflict_by_session_id.get(s_id, [])

        cell_session = GridCellSession(
            session_id=s_id,
            subject_id=s.get("subject_id", 0),
            subject_code=s.get("subject_code", "SUB"),
            subject_name=s.get("subject_name", "Subject"),
            subject_type=s.get("subject_type", "THEORY"),
            faculty_id=s.get("faculty_id", 0),
            faculty_name=s.get("faculty_name", "Faculty"),
            section_id=s.get("section_id", 0),
            section_name=s.get("section_name", "A"),
            batch_id=s.get("batch_id"),
            batch_name=s.get("batch_name"),
            room_id=s.get("room_id"),
            room_name=s.get("room_name"),
            lab_id=s.get("lab_id"),
            lab_name=s.get("lab_name"),
            stream_id=s.get("stream_id"),
            stream_name=s.get("stream_name"),
            cycle_group=s.get("cycle_group"),
            paired_slot_group=s.get("paired_slot_group"),
            has_conflict=len(s_conflicts) > 0,
            conflict_messages=[c.get("message", "Conflict detected") for c in s_conflicts],
        )

        day = s.get("day_of_week", 0)
        slot_id = s.get("time_slot_id", 0)
        period = s.get("period_index", 1)

        key = (day, slot_id) if slot_id else (day, period)
        session_map.setdefault(key, []).append(cell_session)

        # Track paired-slot groups
        if cell_session.paired_slot_group:
            paired_groups_map.setdefault(cell_session.paired_slot_group, []).append(cell_session)

    # Determine unique days and periods from time_slots
    days_present = sorted(list(set(ts.get("day_of_week", 0) for ts in time_slots))) or [0, 1, 2, 3, 4]
    
    # Periods header
    periods_header = []
    seen_periods = set()
    for ts in time_slots:
        p_idx = ts.get("period_index", 1)
        if p_idx not in seen_periods:
            seen_periods.add(p_idx)
            periods_header.append({
                "period_index": p_idx,
                "label": ts.get("label") or f"Period {p_idx}",
                "start_time": str(ts.get("start_time", "")),
                "end_time": str(ts.get("end_time", "")),
                "slot_type": ts.get("slot_type", "THEORY"),
            })
    periods_header.sort(key=lambda x: x["period_index"])

    # Build rows
    rows: List[GridRow] = []
    for day in days_present:
        day_name = DAY_NAMES[day] if day < len(DAY_NAMES) else f"Day {day}"
        day_slots = [ts for ts in time_slots if ts.get("day_of_week", 0) == day]
        day_slots.sort(key=lambda x: x.get("period_index", 1))

        cells: List[GridCell] = []
        for ts in day_slots:
            slot_id = ts.get("id", 0)
            p_idx = ts.get("period_index", 1)

            # Match sessions
            matched_sessions = session_map.get((day, slot_id)) or session_map.get((day, p_idx)) or []
            cell_has_conflict = any(s.has_conflict for s in matched_sessions)
            cell_conflict_details = []
            for s in matched_sessions:
                for c in conflict_by_session_id.get(s.session_id, []):
                    if c not in cell_conflict_details:
                        cell_conflict_details.append(c)

            cells.append(
                GridCell(
                    day_of_week=day,
                    period_index=p_idx,
                    time_slot_id=slot_id,
                    time_slot_label=ts.get("label") or f"Period {p_idx}",
                    start_time=str(ts.get("start_time", "")),
                    end_time=str(ts.get("end_time", "")),
                    slot_type=ts.get("slot_type", "THEORY"),
                    sessions=matched_sessions,
                    has_conflict=cell_has_conflict,
                    conflict_details=cell_conflict_details,
                )
            )

        rows.append(GridRow(day_of_week=day, day_name=day_name, cells=cells))

    # Build paired-slot groups list
    paired_groups: List[PairedSlotGroupItem] = []
    for group_key, group_sessions in paired_groups_map.items():
        if group_sessions:
            first_s = group_sessions[0]
            # Find matching slot info
            matching_slot = next((ts for ts in time_slots if ts.get("id") == first_s.session_id), None)
            day = group_sessions[0].session_id  # fallback
            paired_groups.append(
                PairedSlotGroupItem(
                    paired_slot_group=group_key,
                    day_of_week=0,
                    day_name="Paired Schedule",
                    period_index=1,
                    time_slot_label=f"Group {group_key}",
                    sessions=group_sessions,
                )
            )

    return TimetableMatrixResponse(
        timetable_id=timetable_id,
        version_id=version_id,
        view_type=view_type,
        filter_applied=filter_params,
        periods_header=periods_header,
        rows=rows,
        paired_slot_groups=paired_groups,
        conflicts=conflicts,
        total_sessions=len(filtered_sessions),
    )


def export_timetable_csv(matrix: TimetableMatrixResponse) -> str:
    """Exports timetable matrix to standard CSV text."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write Header Row
    headers = ["Day"] + [p["label"] for p in matrix.periods_header]
    writer.writerow(headers)

    # Write Data Rows
    for row in matrix.rows:
        row_values = [row.day_name]
        for cell in row.cells:
            if cell.slot_type in ("BREAK", "LUNCH"):
                cell_text = f"[{cell.slot_type}]"
            elif not cell.sessions:
                cell_text = "-"
            else:
                session_strs = []
                for s in cell.sessions:
                    loc = s.lab_name or s.room_name or ""
                    batch = f" ({s.batch_name})" if s.batch_name else ""
                    session_strs.append(f"{s.subject_code}{batch} - {s.faculty_name} [{loc}]")
                cell_text = " | ".join(session_strs)
            row_values.append(cell_text)
        writer.writerow(row_values)

    return output.getvalue()
