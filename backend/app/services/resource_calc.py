import math
from datetime import time, datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ==============================================================================
# SECTION CALCULATION DATA STRUCTURES
# ==============================================================================
class CalculatedSectionItem(BaseModel):
    name: str
    student_count: int
    room_id: Optional[int] = None
    stream_id: Optional[int] = None
    cycle_group: Optional[str] = None


class SectionCalculationResult(BaseModel):
    student_count: int
    room_capacity: int
    calculated_section_count: int
    actual_section_count: int
    is_override: bool
    sections: List[CalculatedSectionItem]


# ==============================================================================
# BATCH CALCULATION DATA STRUCTURES
# ==============================================================================
class CalculatedBatchItem(BaseModel):
    name: str
    student_count: int
    lab_id: Optional[int] = None


class BatchCalculationResult(BaseModel):
    section_students: int
    lab_capacity: int
    calculated_batch_count: int
    actual_batch_count: int
    is_override: bool
    batches: List[CalculatedBatchItem]


# ==============================================================================
# TIME SLOT GENERATION STRUCTURES
# ==============================================================================
class SlotBreakItem(BaseModel):
    name: str = "Break"
    start_time: time
    end_time: time
    slot_type: str = "BREAK"  # BREAK, LUNCH, NON_TEACHING


class SlotConfigInput(BaseModel):
    theory_duration_minutes: int = 55
    lab_duration_minutes: int = 110
    working_days: List[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5])  # 0=Mon, 5=Sat
    day_start_time: time = time(9, 0)
    day_end_time: time = time(17, 0)
    breaks: List[SlotBreakItem] = Field(default_factory=list)
    lunch_break: Optional[SlotBreakItem] = None
    non_teaching_periods: List[SlotBreakItem] = Field(default_factory=list)


class GeneratedTimeSlot(BaseModel):
    day_of_week: int
    period_index: int
    start_time: time
    end_time: time
    slot_type: str  # THEORY, LAB, BREAK, LUNCH, NON_TEACHING
    label: str


# ==============================================================================
# AVAILABILITY STRUCTURES
# ==============================================================================
class AvailabilityWindow(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time
    is_available: bool = True


class AvailabilityValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)


# ==============================================================================
# 1. DETERMINISTIC SECTION CALCULATION
# ==============================================================================
def get_alphabetic_section_name(index: int) -> str:
    """Returns 'A', 'B', ... 'Z', 'AA', 'AB' based on 0-based index."""
    name = ""
    while index >= 0:
        name = chr(ord('A') + (index % 26)) + name
        index = (index // 26) - 1
    return name


def calculate_sections(
    student_count: int,
    room_capacity: int,
    naming_pattern: str = "ALPHABETIC",
    manual_count: Optional[int] = None,
    manual_sections: Optional[List[CalculatedSectionItem]] = None,
    stream_id: Optional[int] = None,
    cycle_group: Optional[str] = None,
    balance_distribution: bool = False,
) -> SectionCalculationResult:
    """
    Pure, deterministic backend section calculation.
    Formula: ceil(student_count / room_capacity)
    
    Requirements:
    - student_count >= 0
    - room_capacity > 0
    - Support manual override with is_override flag
    - Named sections (configurable naming)
    """
    if student_count < 0:
        raise ValueError(f"Student count must be non-negative, got {student_count}")
    if room_capacity <= 0:
        raise ValueError(f"Room capacity must be greater than 0, got {room_capacity}")

    if student_count == 0:
        calculated_count = 0
    else:
        calculated_count = math.ceil(student_count / room_capacity)

    # Check for manual override of explicit section list
    if manual_sections is not None and len(manual_sections) > 0:
        return SectionCalculationResult(
            student_count=student_count,
            room_capacity=room_capacity,
            calculated_section_count=calculated_count,
            actual_section_count=len(manual_sections),
            is_override=True,
            sections=manual_sections,
        )

    # Check for manual override of section count
    is_override = False
    actual_count = calculated_count
    if manual_count is not None:
        if manual_count < 0:
            raise ValueError(f"Manual section count must be non-negative, got {manual_count}")
        actual_count = manual_count
        is_override = (manual_count != calculated_count)

    if actual_count == 0:
        return SectionCalculationResult(
            student_count=student_count,
            room_capacity=room_capacity,
            calculated_section_count=calculated_count,
            actual_section_count=0,
            is_override=is_override,
            sections=[],
        )

    # Distribute student counts
    sections: List[CalculatedSectionItem] = []
    if balance_distribution:
        # Balanced split: e.g. 181 across 4 sections -> 46, 45, 45, 45
        base_size = student_count // actual_count
        remainder = student_count % actual_count
        counts = [base_size + (1 if i < remainder else 0) for i in range(actual_count)]
    else:
        # Full capacity filling: e.g. 181 across 4 with cap 60 -> 60, 60, 60, 1
        counts = []
        remaining = student_count
        for i in range(actual_count):
            if i == actual_count - 1:
                counts.append(remaining)
            else:
                allocated = min(room_capacity, remaining)
                counts.append(allocated)
                remaining -= allocated

    for idx, count in enumerate(counts):
        if naming_pattern == "ALPHABETIC":
            name = get_alphabetic_section_name(idx)
        else:
            name = naming_pattern.format(index=idx + 1)

        sections.append(
            CalculatedSectionItem(
                name=name,
                student_count=count,
                stream_id=stream_id,
                cycle_group=cycle_group,
            )
        )

    return SectionCalculationResult(
        student_count=student_count,
        room_capacity=room_capacity,
        calculated_section_count=calculated_count,
        actual_section_count=actual_count,
        is_override=is_override,
        sections=sections,
    )


# ==============================================================================
# 2. DETERMINISTIC BATCH CALCULATION
# ==============================================================================
def calculate_batches(
    section_students: int,
    lab_capacity: int,
    naming_pattern: str = "B{index}",
    manual_count: Optional[int] = None,
    manual_batches: Optional[List[CalculatedBatchItem]] = None,
    lab_id: Optional[int] = None,
) -> BatchCalculationResult:
    """
    Pure, deterministic backend batch calculation.
    Formula: ceil(section_students / lab_capacity)
    
    Requirements:
    - section_students >= 0
    - lab_capacity > 0
    - Batch student counts MUST sum to section_students
    - Separate batch logic from section logic (never use number of rooms)
    """
    if section_students < 0:
        raise ValueError(f"Section student count must be non-negative, got {section_students}")
    if lab_capacity <= 0:
        raise ValueError(f"Lab capacity must be greater than 0, got {lab_capacity}")

    if section_students == 0:
        calculated_count = 0
    else:
        calculated_count = math.ceil(section_students / lab_capacity)

    # Check for explicit manual batch list
    if manual_batches is not None and len(manual_batches) > 0:
        total_batch_students = sum(b.student_count for b in manual_batches)
        if total_batch_students != section_students:
            raise ValueError(
                f"Manual batch student counts sum ({total_batch_students}) does not match section students ({section_students})"
            )
        return BatchCalculationResult(
            section_students=section_students,
            lab_capacity=lab_capacity,
            calculated_batch_count=calculated_count,
            actual_batch_count=len(manual_batches),
            is_override=True,
            batches=manual_batches,
        )

    # Check for manual override of batch count
    is_override = False
    actual_count = calculated_count
    if manual_count is not None:
        if manual_count < 0:
            raise ValueError(f"Manual batch count must be non-negative, got {manual_count}")
        actual_count = manual_count
        is_override = (manual_count != calculated_count)

    if actual_count == 0:
        return BatchCalculationResult(
            section_students=section_students,
            lab_capacity=lab_capacity,
            calculated_batch_count=calculated_count,
            actual_batch_count=0,
            is_override=is_override,
            batches=[],
        )

    # Partition students: fill up to lab_capacity, remainder into last batch
    # Example: 60 students, cap 30 -> B1=30, B2=30
    # Example: 65 students, cap 30 -> B1=30, B2=30, B3=5
    batches: List[CalculatedBatchItem] = []
    remaining = section_students

    for idx in range(actual_count):
        batch_name = naming_pattern.format(index=idx + 1)
        if idx == actual_count - 1:
            allocated = remaining
        else:
            allocated = min(lab_capacity, remaining)
            remaining -= allocated

        batches.append(
            CalculatedBatchItem(
                name=batch_name,
                student_count=allocated,
                lab_id=lab_id,
            )
        )

    # Invariant validation
    total_assigned = sum(b.student_count for b in batches)
    assert total_assigned == section_students, f"Batch sum invariant violated: {total_assigned} != {section_students}"

    return BatchCalculationResult(
        section_students=section_students,
        lab_capacity=lab_capacity,
        calculated_batch_count=calculated_count,
        actual_batch_count=actual_count,
        is_override=is_override,
        batches=batches,
    )


# ==============================================================================
# 3. TIME SLOT GENERATION
# ==============================================================================
def time_to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def minutes_to_time(mins: int) -> time:
    hours = (mins // 60) % 24
    minutes = mins % 60
    return time(hours, minutes)


def generate_time_slots(config: SlotConfigInput) -> List[GeneratedTimeSlot]:
    """
    Deterministically generates the time slot grid based on slot configuration.
    Handles start/end times, theory periods, breaks, lunch, and non-teaching windows.
    """
    if config.theory_duration_minutes <= 0:
        raise ValueError("Theory duration must be greater than 0 minutes")
    if config.lab_duration_minutes <= 0:
        raise ValueError("Lab duration must be greater than 0 minutes")

    start_mins = time_to_minutes(config.day_start_time)
    end_mins = time_to_minutes(config.day_end_time)

    if end_mins <= start_mins:
        raise ValueError("Day end time must be after day start time")

    # Collect all fixed blocks (breaks, lunch, non-teaching)
    fixed_blocks: List[Dict[str, Any]] = []
    for b in config.breaks:
        fixed_blocks.append({
            "name": b.name,
            "start": time_to_minutes(b.start_time),
            "end": time_to_minutes(b.end_time),
            "type": b.slot_type or "BREAK",
        })
    if config.lunch_break:
        fixed_blocks.append({
            "name": config.lunch_break.name or "Lunch",
            "start": time_to_minutes(config.lunch_break.start_time),
            "end": time_to_minutes(config.lunch_break.end_time),
            "type": "LUNCH",
        })
    for nt in config.non_teaching_periods:
        fixed_blocks.append({
            "name": nt.name,
            "start": time_to_minutes(nt.start_time),
            "end": time_to_minutes(nt.end_time),
            "type": "NON_TEACHING",
        })

    # Sort fixed blocks by start time
    fixed_blocks.sort(key=lambda x: x["start"])

    # Validate no overlapping fixed blocks
    for i in range(len(fixed_blocks) - 1):
        if fixed_blocks[i]["end"] > fixed_blocks[i + 1]["start"]:
            raise ValueError(
                f"Fixed blocks '{fixed_blocks[i]['name']}' and '{fixed_blocks[i + 1]['name']}' overlap"
            )

    all_slots: List[GeneratedTimeSlot] = []

    for day in config.working_days:
        if day < 0 or day > 6:
            raise ValueError(f"Invalid day_of_week {day}. Must be between 0 (Monday) and 6 (Sunday).")

        curr_time = start_mins
        period_idx = 1

        while curr_time < end_mins:
            # Check if current time falls within or immediately touches a fixed block
            matching_fixed = next((fb for fb in fixed_blocks if fb["start"] <= curr_time < fb["end"]), None)
            if matching_fixed:
                # Add fixed block slot
                all_slots.append(
                    GeneratedTimeSlot(
                        day_of_week=day,
                        period_index=period_idx,
                        start_time=minutes_to_time(matching_fixed["start"]),
                        end_time=minutes_to_time(matching_fixed["end"]),
                        slot_type=matching_fixed["type"],
                        label=matching_fixed["name"],
                    )
                )
                curr_time = matching_fixed["end"]
                period_idx += 1
                continue

            # Check next fixed block
            next_fixed = next((fb for fb in fixed_blocks if fb["start"] > curr_time), None)
            slot_end = curr_time + config.theory_duration_minutes

            if next_fixed and slot_end > next_fixed["start"]:
                # If theory slot would collide into next fixed block, clamp or adjust
                if next_fixed["start"] > curr_time:
                    all_slots.append(
                        GeneratedTimeSlot(
                            day_of_week=day,
                            period_index=period_idx,
                            start_time=minutes_to_time(curr_time),
                            end_time=minutes_to_time(next_fixed["start"]),
                            slot_type="THEORY",
                            label=f"Period {period_idx}",
                        )
                    )
                    period_idx += 1
                curr_time = next_fixed["start"]
            elif slot_end <= end_mins:
                all_slots.append(
                    GeneratedTimeSlot(
                        day_of_week=day,
                        period_index=period_idx,
                        start_time=minutes_to_time(curr_time),
                        end_time=minutes_to_time(slot_end),
                        slot_type="THEORY",
                        label=f"Period {period_idx}",
                    )
                )
                curr_time = slot_end
                period_idx += 1
            else:
                # Reached end of day
                break

    return all_slots


# ==============================================================================
# 4. AVAILABILITY WINDOW VALIDATION
# ==============================================================================
def validate_availability_windows(windows: List[AvailabilityWindow]) -> AvailabilityValidationResult:
    """Validates that availability windows have valid time ranges and no internal overlaps."""
    errors: List[str] = []

    # Check time ranges
    for w in windows:
        if w.day_of_week < 0 or w.day_of_week > 6:
            errors.append(f"Invalid day_of_week {w.day_of_week}. Must be 0..6.")
        if time_to_minutes(w.end_time) <= time_to_minutes(w.start_time):
            errors.append(f"Invalid window: start_time ({w.start_time}) must be before end_time ({w.end_time})")

    # Check overlaps per day
    by_day: Dict[int, List[AvailabilityWindow]] = {}
    for w in windows:
        by_day.setdefault(w.day_of_week, []).append(w)

    for day, day_windows in by_day.items():
        sorted_w = sorted(day_windows, key=lambda x: time_to_minutes(x.start_time))
        for i in range(len(sorted_w) - 1):
            w1_end = time_to_minutes(sorted_w[i].end_time)
            w2_start = time_to_minutes(sorted_w[i + 1].start_time)
            if w1_end > w2_start:
                errors.append(
                    f"Day {day}: availability window {sorted_w[i].start_time}-{sorted_w[i].end_time} overlaps with {sorted_w[i+1].start_time}-{sorted_w[i+1].end_time}"
                )

    return AvailabilityValidationResult(is_valid=len(errors) == 0, errors=errors)
