import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timetable import Timetable, TimetableVersion, TimetableSession, TimetableStatus
from app.models.academic import AcademicYear
from app.schemas.contracts import TimetableSessionContract
from app.services.versioning_service import VersioningService


def test_version_diff_calculation():
    service = VersioningService(db=None)

    # Version 1 sessions
    v1_sess = [
        TimetableSession(id=1, version_id=1, subject_id=101, section_id=1, batch_id=None, room_id=10, faculty_id=1, time_slot_id=1),
        TimetableSession(id=2, version_id=1, subject_id=102, section_id=1, batch_id=None, room_id=10, faculty_id=2, time_slot_id=2),
    ]
    v1 = TimetableVersion(id=1, timetable_id=100, version_number=1, is_active=False)
    v1.sessions = v1_sess

    # Version 2 sessions: Subject 101 moved to Slot 3 (MODIFIED), Subject 102 removed, Subject 103 added
    v2_sess = [
        TimetableSession(id=3, version_id=2, subject_id=101, section_id=1, batch_id=None, room_id=10, faculty_id=1, time_slot_id=3),
        TimetableSession(id=4, version_id=2, subject_id=103, section_id=1, batch_id=None, room_id=11, faculty_id=3, time_slot_id=4),
    ]
    v2 = TimetableVersion(id=2, timetable_id=100, version_number=2, is_active=True)
    v2.sessions = v2_sess

    diff = service.compute_version_diff(
        timetable_id=100,
        from_version=v1,
        to_version=v2,
    )

    assert diff.timetable_id == 100
    assert diff.from_version_number == 1
    assert diff.to_version_number == 2
    assert diff.total_sessions_from == 2
    assert diff.total_sessions_to == 2
    assert diff.total_differences == 3

    diff_types = {d.subject_id: d.diff_type for d in diff.differences}
    assert diff_types[101] == "MODIFIED"
    assert diff_types[102] == "REMOVED"
    assert diff_types[103] == "ADDED"


@pytest.mark.asyncio
async def test_version_restore_and_immutability(db_session: AsyncSession):
    # 1. Setup AcademicYear and Timetable
    ay = AcademicYear(name="2026-2027-Versioning", is_current=True)
    db_session.add(ay)
    await db_session.commit()
    await db_session.refresh(ay)

    tt = Timetable(academic_year_id=ay.id, name="Main Timetable", status=TimetableStatus.DRAFT)
    db_session.add(tt)
    await db_session.commit()
    await db_session.refresh(tt)

    service = VersioningService(db_session)

    # 2. Create Version 1
    v1_sessions = [
        TimetableSessionContract(
            subject_id=1,
            faculty_id=1,
            section_id=1,
            room_id=1,
            time_slot_id=1,
        )
    ]
    v1 = await service.create_new_version(tt.id, v1_sessions, notes="Initial version", make_active=True)
    assert v1.version_number == 1
    assert v1.is_active is True

    # 3. Create Version 2
    v2_sessions = [
        TimetableSessionContract(
            subject_id=1,
            faculty_id=1,
            section_id=1,
            room_id=2,
            time_slot_id=2,
        )
    ]
    v2 = await service.create_new_version(tt.id, v2_sessions, notes="Modified room & slot", make_active=True)
    assert v2.version_number == 2
    assert v2.is_active is True

    # Check v1 is no longer active
    v1_refreshed = await service.get_version_with_sessions(v1.id)
    assert v1_refreshed.is_active is False
    assert len(v1_refreshed.sessions) == 1
    assert v1_refreshed.sessions[0].room_id == 1  # immutable

    # 4. Restore Version 1 as a brand new Version 3
    v3 = await service.restore_version_as_new(tt.id, v1.id, notes="Restored v1 copy")
    assert v3 is not None
    assert v3.version_number == 3
    assert v3.is_active is True

    # Check v1 snapshot is STILL unchanged
    v1_check = await service.get_version_with_sessions(v1.id)
    assert v1_check.version_number == 1
    assert v1_check.is_active is False
    assert v1_check.sessions[0].room_id == 1


@pytest.mark.asyncio
async def test_api_version_endpoints(async_client: AsyncClient, db_session: AsyncSession):
    # Setup
    ay = AcademicYear(name="2026-2027-API-Vers", is_current=True)
    db_session.add(ay)
    await db_session.commit()
    await db_session.refresh(ay)

    tt = Timetable(academic_year_id=ay.id, name="API Timetable", status=TimetableStatus.DRAFT)
    db_session.add(tt)
    await db_session.commit()
    await db_session.refresh(tt)

    service = VersioningService(db_session)
    v1 = await service.create_new_version(
        tt.id,
        [TimetableSessionContract(subject_id=1, faculty_id=1, section_id=1, room_id=1, time_slot_id=1)],
        notes="v1",
    )
    v2 = await service.create_new_version(
        tt.id,
        [TimetableSessionContract(subject_id=1, faculty_id=1, section_id=1, room_id=2, time_slot_id=2)],
        notes="v2",
    )

    # 1. Get versions list
    res = await async_client.get(f"/api/v1/versions/{tt.id}")
    assert res.status_code == 200
    assert len(res.json()["data"]) == 2

    # 2. Get version detail
    res_det = await async_client.get(f"/api/v1/versions/{tt.id}/version/{v1.id}")
    assert res_det.status_code == 200
    assert res_det.json()["data"]["version_number"] == 1

    # 3. Diff
    res_diff = await async_client.get(f"/api/v1/versions/{tt.id}/diff?from_version_id={v1.id}&to_version_id={v2.id}")
    assert res_diff.status_code == 200
    assert res_diff.json()["data"]["total_differences"] >= 1

    # 4. Set Active
    res_act = await async_client.post(f"/api/v1/versions/{tt.id}/version/{v1.id}/set-active")
    assert res_act.status_code == 200
    assert res_act.json()["data"]["is_active"] is True

    # 5. Restore as New
    res_rest = await async_client.post(f"/api/v1/versions/{tt.id}/version/{v2.id}/restore")
    assert res_rest.status_code == 200
    assert res_rest.json()["data"]["version_number"] == 3
