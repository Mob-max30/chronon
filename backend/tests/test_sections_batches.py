import pytest
from app.services.resource_calc import (
    calculate_sections,
    calculate_batches,
    CalculatedSectionItem,
    CalculatedBatchItem,
    get_alphabetic_section_name,
)


# ==============================================================================
# SECTION CALCULATION UNIT TESTS
# ==============================================================================
class TestSectionCalculation:
    def test_zero_students(self):
        """0 students should produce 0 sections."""
        res = calculate_sections(student_count=0, room_capacity=60)
        assert res.calculated_section_count == 0
        assert res.actual_section_count == 0
        assert res.is_override is False
        assert len(res.sections) == 0

    def test_exact_capacity(self):
        """180 students with room capacity 60 -> exactly 3 sections."""
        res = calculate_sections(student_count=180, room_capacity=60)
        assert res.calculated_section_count == 3
        assert res.actual_section_count == 3
        assert res.is_override is False
        assert len(res.sections) == 3
        assert [s.name for s in res.sections] == ["A", "B", "C"]
        assert [s.student_count for s in res.sections] == [60, 60, 60]

    def test_single_section_exact(self):
        """60 students with capacity 60 -> exactly 1 section."""
        res = calculate_sections(student_count=60, room_capacity=60)
        assert res.calculated_section_count == 1
        assert res.actual_section_count == 1
        assert [s.name for s in res.sections] == ["A"]
        assert res.sections[0].student_count == 60

    def test_remainder_ceil(self):
        """181 students with capacity 60 -> 4 sections (60, 60, 60, 1)."""
        res = calculate_sections(student_count=181, room_capacity=60)
        assert res.calculated_section_count == 4
        assert res.actual_section_count == 4
        assert len(res.sections) == 4
        assert [s.name for s in res.sections] == ["A", "B", "C", "D"]
        assert [s.student_count for s in res.sections] == [60, 60, 60, 1]
        assert sum(s.student_count for s in res.sections) == 181

    def test_capacity_one(self):
        """5 students with capacity 1 -> 5 sections of 1."""
        res = calculate_sections(student_count=5, room_capacity=1)
        assert res.calculated_section_count == 5
        assert res.actual_section_count == 5
        assert [s.student_count for s in res.sections] == [1, 1, 1, 1, 1]

    def test_invalid_capacity_raises(self):
        """Room capacity <= 0 must raise ValueError."""
        with pytest.raises(ValueError, match="Room capacity must be greater than 0"):
            calculate_sections(student_count=60, room_capacity=0)
        with pytest.raises(ValueError, match="Room capacity must be greater than 0"):
            calculate_sections(student_count=60, room_capacity=-10)

    def test_negative_students_raises(self):
        """Student count < 0 must raise ValueError."""
        with pytest.raises(ValueError, match="Student count must be non-negative"):
            calculate_sections(student_count=-5, room_capacity=60)

    def test_manual_count_override(self):
        """Manual section count override sets is_override=True."""
        res = calculate_sections(student_count=180, room_capacity=60, manual_count=4)
        assert res.calculated_section_count == 3
        assert res.actual_section_count == 4
        assert res.is_override is True
        assert len(res.sections) == 4

    def test_explicit_section_list_override(self):
        """Passing manual section list returns custom sections and is_override=True."""
        custom_sections = [
            CalculatedSectionItem(name="Sec-1", student_count=90),
            CalculatedSectionItem(name="Sec-2", student_count=90),
        ]
        res = calculate_sections(student_count=180, room_capacity=60, manual_sections=custom_sections)
        assert res.calculated_section_count == 3
        assert res.actual_section_count == 2
        assert res.is_override is True
        assert res.sections == custom_sections

    def test_first_year_stream_and_cycle_preservation(self):
        """First-year metadata (stream_id, cycle_group) is attached to all generated sections."""
        res = calculate_sections(
            student_count=120,
            room_capacity=60,
            stream_id=10,
            cycle_group="PHYSICS_CYCLE",
        )
        assert res.actual_section_count == 2
        for s in res.sections:
            assert s.stream_id == 10
            assert s.cycle_group == "PHYSICS_CYCLE"

    def test_balanced_distribution(self):
        """Balanced split distributes students evenly across sections."""
        res = calculate_sections(student_count=181, room_capacity=60, balance_distribution=True)
        assert res.actual_section_count == 4
        assert [s.student_count for s in res.sections] == [46, 45, 45, 45]
        assert sum(s.student_count for s in res.sections) == 181

    def test_determinism_repeated_calculation(self):
        """Repeated calculation with same inputs produces identical results."""
        results = [calculate_sections(student_count=185, room_capacity=60) for _ in range(50)]
        first = results[0]
        for r in results[1:]:
            assert r.model_dump() == first.model_dump()

    def test_alphabetic_naming_helper(self):
        """Check alphabetic naming past 26."""
        assert get_alphabetic_section_name(0) == "A"
        assert get_alphabetic_section_name(25) == "Z"
        assert get_alphabetic_section_name(26) == "AA"


# ==============================================================================
# BATCH CALCULATION UNIT TESTS
# ==============================================================================
class TestBatchCalculation:
    def test_zero_students(self):
        """0 section students produces 0 batches."""
        res = calculate_batches(section_students=0, lab_capacity=30)
        assert res.calculated_batch_count == 0
        assert res.actual_batch_count == 0
        assert res.is_override is False
        assert len(res.batches) == 0

    def test_exact_division(self):
        """60 students with lab capacity 30 -> 2 batches (30, 30)."""
        res = calculate_batches(section_students=60, lab_capacity=30)
        assert res.calculated_batch_count == 2
        assert res.actual_batch_count == 2
        assert [b.name for b in res.batches] == ["B1", "B2"]
        assert [b.student_count for b in res.batches] == [30, 30]
        assert sum(b.student_count for b in res.batches) == 60

    def test_remainder_division(self):
        """65 students with lab capacity 30 -> 3 batches (30, 30, 5)."""
        res = calculate_batches(section_students=65, lab_capacity=30)
        assert res.calculated_batch_count == 3
        assert res.actual_batch_count == 3
        assert [b.name for b in res.batches] == ["B1", "B2", "B3"]
        assert [b.student_count for b in res.batches] == [30, 30, 5]
        assert sum(b.student_count for b in res.batches) == 65

    def test_capacity_equals_section_size(self):
        """30 students with lab capacity 30 -> 1 batch of 30."""
        res = calculate_batches(section_students=30, lab_capacity=30)
        assert res.calculated_batch_count == 1
        assert res.actual_batch_count == 1
        assert res.batches[0].name == "B1"
        assert res.batches[0].student_count == 30

    def test_capacity_one(self):
        """4 students with lab capacity 1 -> 4 batches of 1."""
        res = calculate_batches(section_students=4, lab_capacity=1)
        assert res.calculated_batch_count == 4
        assert [b.student_count for b in res.batches] == [1, 1, 1, 1]

    def test_invalid_lab_capacity_raises(self):
        """Lab capacity <= 0 must raise ValueError."""
        with pytest.raises(ValueError, match="Lab capacity must be greater than 0"):
            calculate_batches(section_students=60, lab_capacity=0)
        with pytest.raises(ValueError, match="Lab capacity must be greater than 0"):
            calculate_batches(section_students=60, lab_capacity=-5)

    def test_negative_students_raises(self):
        """Section students < 0 must raise ValueError."""
        with pytest.raises(ValueError, match="Section student count must be non-negative"):
            calculate_batches(section_students=-1, lab_capacity=30)

    def test_student_counts_sum_invariant(self):
        """Sum of batch student counts must equal section_students across varied inputs."""
        for total in [1, 15, 30, 45, 60, 65, 73, 100, 120]:
            for cap in [10, 15, 20, 25, 30, 40]:
                res = calculate_batches(section_students=total, lab_capacity=cap)
                assert sum(b.student_count for b in res.batches) == total

    def test_manual_batches_override(self):
        """Manual batch override with matching sum succeeds."""
        manual = [
            CalculatedBatchItem(name="Batch-Alpha", student_count=35),
            CalculatedBatchItem(name="Batch-Beta", student_count=25),
        ]
        res = calculate_batches(section_students=60, lab_capacity=30, manual_batches=manual)
        assert res.actual_batch_count == 2
        assert res.is_override is True
        assert res.batches == manual

    def test_manual_batches_mismatch_raises(self):
        """Manual batch override where sum does not equal section size must raise ValueError."""
        manual = [
            CalculatedBatchItem(name="B1", student_count=30),
            CalculatedBatchItem(name="B2", student_count=20),
        ]  # Sum = 50 != 60
        with pytest.raises(ValueError, match="does not match section students"):
            calculate_batches(section_students=60, lab_capacity=30, manual_batches=manual)
