import sys
import json
from app.scheduling.fixtures import get_sample_scheduling_input, get_infeasible_fixture
from app.scheduling.generators import generate_single
from app.validation.validator import IndependentTimetableValidator


def run_demo():
    print("=" * 80)
    print(" CHRONON TIMETABLE SCHEDULER & INDEPENDENT VALIDATOR DEMO ")
    print("=" * 80)

    # 1. Load basic fixture A
    print("\n[1] Loading Basic Valid Fixture A...")
    fixture_a = get_sample_scheduling_input()
    print(f"    - Academic Year ID: {fixture_a.academic_year_id}")
    print(f"    - Sections: {len(fixture_a.sections)}")
    print(f"    - Rooms: {len(fixture_a.rooms)}")
    print(f"    - Time Slots: {len(fixture_a.time_slots)}")
    print(f"    - Subjects: {len(fixture_a.subjects)}")

    # 2. Run generate_single()
    print("\n[2] Executing CP-SAT Scheduler Pipeline (generate_single)...")
    result = generate_single(fixture_a)

    print(f"\n    ---> Solver Status: {result.status}")
    print(f"    ---> Is Valid: {result.is_valid}")
    print(f"    ---> Is Optimal: {result.is_optimal}")
    print(f"    ---> Total Sessions Scheduled: {len(result.sessions)}")
    print(f"    ---> Execution Time: {result.execution_time_seconds} seconds")

    if result.quality:
        print("\n[3] Quality Score Breakdown:")
        print(f"    - Overall Score: {result.quality.overall_score}/100")
        print(f"    - Distribution Score: {result.quality.distribution_score}")
        print(f"    - Student Gap Score: {result.quality.student_gap_score}")
        print(f"    - Faculty Gap Score: {result.quality.faculty_gap_score}")
        print(f"    - Workload Balance Score: {result.quality.workload_balance_score}")

    print("\n[4] First 5 Scheduled Sessions:")
    for sess in result.sessions[:5]:
        print(f"    - Session #{sess.id}: Subj={sess.subject_id}, Fac={sess.faculty_id}, Sec={sess.section_id}, Room={sess.room_id}, Slot={sess.time_slot_id}")

    print("\n[5] Testing Independent Validator Isolation...")
    validator = IndependentTimetableValidator(result.sessions, fixture_a)
    val_res = validator.validate()
    print(f"    - Validator Pass: {val_res.is_valid}")
    print(f"    - Total Hard Violations: {val_res.total_hard_violations}")

    # 6. Test Infeasible Fixture G
    print("\n[6] Testing Infeasible Fixture G (Impossible Constraints)...")
    infeasible_input = get_infeasible_fixture()
    inf_result = generate_single(infeasible_input)
    print(f"    - Solver Status: {inf_result.status}")
    print(f"    - Is Valid: {inf_result.is_valid}")
    print(f"    - Message: {inf_result.message}")

    print("\n" + "=" * 80)
    print(" DEMO COMPLETED SUCCESSFULLY ")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
