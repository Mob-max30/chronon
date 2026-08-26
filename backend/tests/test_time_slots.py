import pytest
from datetime import time
from app.services.resource_calc import (
    generate_time_slots,
    validate_availability_windows,
    SlotConfigInput,
    SlotBreakItem,
    AvailabilityWindow,
)


class TestTimeSlotGeneration:
    def test_basic_day_slots(self):
        """Generate 55-min slots between 09:00 and 17:00 with no breaks."""
        cfg = SlotConfigInput(
            theory_duration_minutes=60,
            lab_duration_minutes=120,
            working_days=[0],  # Monday
            day_start_time=time(9, 0),
            day_end_time=time(13, 0),
            breaks=[],
        )
        slots = generate_time_slots(cfg)
        assert len(slots) == 4
        assert slots[0].start_time == time(9, 0)
        assert slots[0].end_time == time(10, 0)
        assert slots[3].start_time == time(12, 0)
        assert slots[3].end_time == time(13, 0)

    def test_slots_with_break_and_lunch(self):
        """Slots should properly insert Break and Lunch and resume after."""
        cfg = SlotConfigInput(
            theory_duration_minutes=60,
            working_days=[0],
            day_start_time=time(9, 0),
            day_end_time=time(14, 0),
            breaks=[
                SlotBreakItem(name="Tea Break", start_time=time(11, 0), end_time=time(11, 15), slot_type="BREAK")
            ],
            lunch_break=SlotBreakItem(name="Lunch Break", start_time=time(13, 0), end_time=time(14, 0), slot_type="LUNCH"),
        )
        slots = generate_time_slots(cfg)
        types = [s.slot_type for s in slots]
        assert "BREAK" in types
        assert "LUNCH" in types
        tea_slot = next(s for s in slots if s.slot_type == "BREAK")
        assert tea_slot.start_time == time(11, 0)
        assert tea_slot.end_time == time(11, 15)

    def test_invalid_start_end_time_raises(self):
        """End time <= Start time raises ValueError."""
        cfg = SlotConfigInput(day_start_time=time(17, 0), day_end_time=time(9, 0))
        with pytest.raises(ValueError, match="Day end time must be after day start time"):
            generate_time_slots(cfg)

    def test_overlapping_breaks_raise(self):
        """Overlapping breaks must raise ValueError."""
        cfg = SlotConfigInput(
            breaks=[
                SlotBreakItem(name="Break 1", start_time=time(10, 0), end_time=time(11, 0)),
                SlotBreakItem(name="Break 2", start_time=time(10, 30), end_time=time(11, 30)),
            ]
        )
        with pytest.raises(ValueError, match="overlap"):
            generate_time_slots(cfg)


class TestAvailabilityValidation:
    def test_valid_availability_windows(self):
        windows = [
            AvailabilityWindow(day_of_week=0, start_time=time(9, 0), end_time=time(13, 0)),
            AvailabilityWindow(day_of_week=0, start_time=time(14, 0), end_time=time(17, 0)),
            AvailabilityWindow(day_of_week=1, start_time=time(9, 0), end_time=time(17, 0)),
        ]
        res = validate_availability_windows(windows)
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_overlapping_windows_rejected(self):
        windows = [
            AvailabilityWindow(day_of_week=0, start_time=time(9, 0), end_time=time(13, 0)),
            AvailabilityWindow(day_of_week=0, start_time=time(12, 0), end_time=time(15, 0)),  # Overlaps
        ]
        res = validate_availability_windows(windows)
        assert res.is_valid is False
        assert len(res.errors) > 0
        assert "overlaps" in res.errors[0]

    def test_invalid_time_range_rejected(self):
        windows = [
            AvailabilityWindow(day_of_week=0, start_time=time(15, 0), end_time=time(9, 0)),
        ]
        res = validate_availability_windows(windows)
        assert res.is_valid is False
        assert "start_time" in res.errors[0]
