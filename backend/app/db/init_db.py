import asyncio
import logging
from datetime import date, time
from sqlalchemy import select

from app.db.base import Base
from app.db.session import get_engine, get_session_factory
from app.models.academic import (
    Institution,
    InstitutionType,
    AcademicYear,
    Scheme,
    Branch,
    Stream,
    Semester,
    TermType,
    Subject,
    SubjectType,
    Faculty,
    FacultySubject,
    CycleGroup,
)
from app.models.resources import (
    Room,
    Lab,
    Section,
    Batch,
    SlotConfig,
    TimeSlot,
    SlotType,
)

logger = logging.getLogger("chronon.init_db")


async def init_db():
    """Create all tables and seed standard VTU baseline data if empty."""
    engine = get_engine()
    if engine is None:
        return

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed baseline records if needed
    factory = get_session_factory()
    if factory is None:
        return

    async with factory() as session:
        # Check if already seeded
        res = await session.execute(select(AcademicYear))
        if res.scalars().first() is not None:
            return  # Already seeded

        try:
            # 1. Institution
            inst = Institution(
                name="B.M.S. College of Engineering",
                code="BMSCE",
                type=InstitutionType.VTU_AFFILIATED,
            )
            session.add(inst)
            await session.flush()

            # 2. Academic Year
            ay = AcademicYear(
                name="2026-2027",
                is_current=True,
                start_date=date(2026, 8, 1),
                end_date=date(2027, 6, 30),
            )
            session.add(ay)
            await session.flush()

            # 3. Scheme
            scheme = Scheme(
                name="2022 Scheme",
                year=2022,
                institution_id=inst.id,
            )
            session.add(scheme)
            await session.flush()

            # 4. Semesters (1 to 8)
            semesters = []
            for num in range(1, 9):
                sem = Semester(
                    scheme_id=scheme.id,
                    number=num,
                    term_type=TermType.ODD if num % 2 == 1 else TermType.EVEN,
                )
                session.add(sem)
                semesters.append(sem)
            await session.flush()

            # 5. First-Year Streams
            stream_cse = Stream(
                name="Computer Science & Engineering Stream",
                code="CSE-STR",
                institution_id=inst.id,
                physics_group_count=3,
                chemistry_group_count=3,
            )
            stream_mech = Stream(
                name="Mechanical & Civil Stream",
                code="ME-STR",
                institution_id=inst.id,
                physics_group_count=1,
                chemistry_group_count=1,
            )
            session.add_all([stream_cse, stream_mech])
            await session.flush()

            # 6. Branches
            b_cse = Branch(name="Computer Science & Engineering", code="CSE", student_count=180, stream_id=stream_cse.id, institution_id=inst.id)
            b_ise = Branch(name="Information Science & Engineering", code="ISE", student_count=120, stream_id=stream_cse.id, institution_id=inst.id)
            b_aiml = Branch(name="Artificial Intelligence & Machine Learning", code="AIML", student_count=60, stream_id=stream_cse.id, institution_id=inst.id)
            b_me = Branch(name="Mechanical Engineering", code="ME", student_count=60, stream_id=stream_mech.id, institution_id=inst.id)
            b_cv = Branch(name="Civil Engineering", code="CV", student_count=60, stream_id=stream_mech.id, institution_id=inst.id)
            session.add_all([b_cse, b_ise, b_aiml, b_me, b_cv])
            await session.flush()

            # 7. Subjects (Sem 1 & Sem 3)
            sem1 = semesters[0]
            sem3 = semesters[2]

            sub_math1 = Subject(code="22MATS11", name="Mathematics-I for CSE", semester_id=sem1.id, subject_type=SubjectType.THEORY, weekly_hours=4, credits=4, is_first_year=True, stream_id=stream_cse.id)
            sub_phy = Subject(code="22PHYS12", name="Physics for CSE Stream", semester_id=sem1.id, subject_type=SubjectType.THEORY, weekly_hours=4, credits=4, is_first_year=True, stream_id=stream_cse.id, cycle_group=CycleGroup.PHYSICS)
            sub_phylab = Subject(code="22PHYL16", name="Physics Laboratory", semester_id=sem1.id, subject_type=SubjectType.LAB, weekly_hours=2, credits=1, is_first_year=True, stream_id=stream_cse.id, cycle_group=CycleGroup.PHYSICS)
            sub_chem = Subject(code="22CHEM12", name="Chemistry for CSE Stream", semester_id=sem1.id, subject_type=SubjectType.THEORY, weekly_hours=4, credits=4, is_first_year=True, stream_id=stream_cse.id, cycle_group=CycleGroup.CHEMISTRY)

            sub_dsa = Subject(code="21CS32", name="Data Structures and Applications", semester_id=sem3.id, subject_type=SubjectType.THEORY, weekly_hours=4, credits=4, is_first_year=False)
            sub_dsalab = Subject(code="21CSL381", name="Data Structures Laboratory", semester_id=sem3.id, subject_type=SubjectType.LAB, weekly_hours=2, credits=1, is_first_year=False)
            sub_ade = Subject(code="21CS33", name="Analog and Digital Electronics", semester_id=sem3.id, subject_type=SubjectType.THEORY, weekly_hours=3, credits=3, is_first_year=False)
            sub_co = Subject(code="21CS34", name="Computer Organization & Architecture", semester_id=sem3.id, subject_type=SubjectType.THEORY, weekly_hours=3, credits=3, is_first_year=False)
            sub_math3 = Subject(code="21MAT31", name="Transform Calculus & Numerical Techniques", semester_id=sem3.id, subject_type=SubjectType.THEORY, weekly_hours=3, credits=3, is_first_year=False)

            session.add_all([sub_math1, sub_phy, sub_phylab, sub_chem, sub_dsa, sub_dsalab, sub_ade, sub_co, sub_math3])
            await session.flush()

            # 8. Faculty
            f_gowda = Faculty(name="Dr. H. S. Guruprasad", employee_code="EMP001", email="guruprasad@bmsce.ac.in", department="CSE", designation="Professor", max_weekly_hours=18, is_active=True, institution_id=inst.id)
            f_anita = Faculty(name="Dr. Anita Kanavalli", employee_code="EMP002", email="anita.cse@bmsce.ac.in", department="CSE", designation="Associate Professor", max_weekly_hours=18, is_active=True, institution_id=inst.id)
            f_kavitha = Faculty(name="Prof. Kavitha Sooda", employee_code="EMP003", email="kavitha.cse@bmsce.ac.in", department="CSE", designation="Assistant Professor", max_weekly_hours=20, is_active=True, institution_id=inst.id)
            f_math = Faculty(name="Dr. Sujatha N.", employee_code="EMP004", email="sujatha.math@bmsce.ac.in", department="Mathematics", designation="Associate Professor", max_weekly_hours=18, is_active=True, institution_id=inst.id)
            session.add_all([f_gowda, f_anita, f_kavitha, f_math])
            await session.flush()

            # Faculty subject mappings
            m1 = FacultySubject(faculty_id=f_gowda.id, subject_id=sub_dsa.id, preference_rank=1, is_primary=True)
            m2 = FacultySubject(faculty_id=f_anita.id, subject_id=sub_dsalab.id, preference_rank=1, is_primary=True)
            m3 = FacultySubject(faculty_id=f_kavitha.id, subject_id=sub_ade.id, preference_rank=1, is_primary=True)
            m4 = FacultySubject(faculty_id=f_math.id, subject_id=sub_math3.id, preference_rank=1, is_primary=True)
            session.add_all([m1, m2, m3, m4])

            # 9. Rooms & Labs
            r1 = Room(name="LH-301", building="Academic Block 3", capacity=70, institution_id=inst.id)
            r2 = Room(name="LH-302", building="Academic Block 3", capacity=70, institution_id=inst.id)
            r3 = Room(name="LH-303", building="Academic Block 3", capacity=70, institution_id=inst.id)
            l1 = Lab(name="Data Structures Lab", building="Computing Block", capacity=35, count=1, lab_type="COMPUTER", institution_id=inst.id)
            l2 = Lab(name="Systems & Hardware Lab", building="Computing Block", capacity=35, count=1, lab_type="COMPUTER", institution_id=inst.id)
            session.add_all([r1, r2, r3, l1, l2])
            await session.flush()

            # 10. Sections & Batches for 3rd Sem CSE
            sec_a = Section(name="A", branch_id=b_cse.id, semester_id=sem3.id, student_count=60, room_id=r1.id)
            sec_b = Section(name="B", branch_id=b_cse.id, semester_id=sem3.id, student_count=60, room_id=r2.id)
            session.add_all([sec_a, sec_b])
            await session.flush()

            b1_a = Batch(name="A1", section_id=sec_a.id, student_count=30, lab_id=l1.id)
            b2_a = Batch(name="A2", section_id=sec_a.id, student_count=30, lab_id=l1.id)
            b1_b = Batch(name="B1", section_id=sec_b.id, student_count=30, lab_id=l2.id)
            b2_b = Batch(name="B2", section_id=sec_b.id, student_count=30, lab_id=l2.id)
            session.add_all([b1_a, b2_a, b1_b, b2_b])

            # 11. Time Slots (5 days x 6 periods)
            slot_config = SlotConfig(
                institution_id=inst.id,
                name="Standard VTU 6-Period Day",
                day_start_time=time(9, 0),
                day_end_time=time(16, 30),
            )
            session.add(slot_config)
            await session.flush()

            slots = []
            slot_times = [
                (time(9, 0), time(9, 55)),
                (time(9, 55), time(10, 50)),
                (time(11, 5), time(12, 0)),
                (time(12, 0), time(12, 55)),
                (time(13, 40), time(14, 35)),
                (time(14, 35), time(15, 30)),
            ]
            for day in range(5):  # 0=Monday to 4=Friday
                for p_idx, (st, et) in enumerate(slot_times, 1):
                    ts = TimeSlot(
                        day_of_week=day,
                        period_index=p_idx,
                        start_time=st,
                        end_time=et,
                        slot_type=SlotType.THEORY,
                    )
                    slots.append(ts)
            session.add_all(slots)

            await session.commit()
            print("Database baseline seeded successfully.")
        except Exception as e:
            await session.rollback()
            print(f"Failed to seed database: {e}")


if __name__ == "__main__":
    asyncio.run(init_db())
