from datetime import datetime
from typing import List, Optional, Dict, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.timetable import Timetable, TimetableVersion, TimetableSession
from app.schemas.contracts import TimetableSessionContract
from app.schemas.timetable import (
    VersionDiffResponse,
    VersionSessionDiff,
    TimetableVersionCreate,
)


class VersioningService:
    """
    Manages timetable versioning, snapshots, active version promotion/rollback,
    and granular diff comparisons between versions.
    """

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    async def get_versions_for_timetable(self, timetable_id: int) -> List[TimetableVersion]:
        if not self.db:
            return []
        stmt = (
            select(TimetableVersion)
            .where(TimetableVersion.timetable_id == timetable_id)
            .order_by(TimetableVersion.version_number.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_version_with_sessions(self, version_id: int) -> Optional[TimetableVersion]:
        if not self.db:
            return None
        stmt = (
            select(TimetableVersion)
            .where(TimetableVersion.id == version_id)
            .options(selectinload(TimetableVersion.sessions))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_new_version(
        self,
        timetable_id: int,
        sessions: List[TimetableSessionContract],
        notes: Optional[str] = None,
        make_active: bool = True,
    ) -> TimetableVersion:
        """
        Creates a new immutable TimetableVersion snapshot and writes session records.
        Automatically increments the version number.
        """
        existing_versions = await self.get_versions_for_timetable(timetable_id)
        next_version_num = (max([v.version_number for v in existing_versions], default=0)) + 1

        if make_active and self.db:
            # Deactivate previous versions of this timetable
            await self.db.execute(
                update(TimetableVersion)
                .where(TimetableVersion.timetable_id == timetable_id)
                .values(is_active=False)
            )

        new_version = TimetableVersion(
            timetable_id=timetable_id,
            version_number=next_version_num,
            is_active=make_active,
            notes=notes or f"Generated Version {next_version_num}",
            created_at=datetime.utcnow(),
        )

        if self.db:
            self.db.add(new_version)
            await self.db.flush()

            # Persist session snapshots
            for s in sessions:
                sess_record = TimetableSession(
                    version_id=new_version.id,
                    subject_id=s.subject_id,
                    faculty_id=s.faculty_id,
                    section_id=s.section_id,
                    batch_id=s.batch_id,
                    room_id=s.room_id,
                    lab_id=s.lab_id,
                    time_slot_id=s.time_slot_id,
                )
                self.db.add(sess_record)

            await self.db.commit()
            await self.db.refresh(new_version)
        else:
            new_version.id = 1

        return new_version

    async def set_active_version(self, timetable_id: int, version_id: int) -> Optional[TimetableVersion]:
        """
        Promotes/rolls back the active timetable version.
        """
        if not self.db:
            return None

        # Deactivate all versions for this timetable
        await self.db.execute(
            update(TimetableVersion)
            .where(TimetableVersion.timetable_id == timetable_id)
            .values(is_active=False)
        )

        # Activate target version
        target = await self.get_version_with_sessions(version_id)
        if target and target.timetable_id == timetable_id:
            target.is_active = True
            await self.db.commit()
            await self.db.refresh(target)
        return target

    async def restore_version_as_new(
        self,
        timetable_id: int,
        source_version_id: int,
        notes: Optional[str] = None,
    ) -> Optional[TimetableVersion]:
        """
        Restores a historical version by copying its sessions into a brand new version snapshot.
        Preserves immutability of historical versions.
        """
        source = await self.get_version_with_sessions(source_version_id)
        if not source or source.timetable_id != timetable_id:
            return None

        session_contracts = [
            TimetableSessionContract(
                subject_id=s.subject_id,
                faculty_id=s.faculty_id,
                section_id=s.section_id,
                batch_id=s.batch_id,
                room_id=s.room_id,
                lab_id=s.lab_id,
                time_slot_id=s.time_slot_id,
            )
            for s in (source.sessions or [])
        ]

        restore_notes = notes or f"Restored from Version {source.version_number}"
        return await self.create_new_version(
            timetable_id=timetable_id,
            sessions=session_contracts,
            notes=restore_notes,
            make_active=True,
        )

    def compute_version_diff(
        self,
        timetable_id: int,
        from_version: TimetableVersion,
        to_version: TimetableVersion,
    ) -> VersionDiffResponse:
        """
        Pure function computing granular differences between two versions of a timetable.
        """
        from_sessions = from_version.sessions or []
        to_sessions = to_version.sessions or []

        # Index sessions by (subject_id, section_id, batch_id)
        from_map: Dict[Tuple, TimetableSession] = {
            (s.subject_id, s.section_id, s.batch_id): s for s in from_sessions
        }
        to_map: Dict[Tuple, TimetableSession] = {
            (s.subject_id, s.section_id, s.batch_id): s for s in to_sessions
        }

        diffs: List[VersionSessionDiff] = []
        all_keys = set(from_map.keys()) | set(to_map.keys())

        for key in all_keys:
            s_from = from_map.get(key)
            s_to = to_map.get(key)

            if s_from and not s_to:
                diffs.append(
                    VersionSessionDiff(
                        subject_id=key[0],
                        section_id=key[1],
                        batch_id=key[2],
                        old_time_slot_id=s_from.time_slot_id,
                        old_room_id=s_from.room_id,
                        old_faculty_id=s_from.faculty_id,
                        diff_type="REMOVED",
                    )
                )
            elif s_to and not s_from:
                diffs.append(
                    VersionSessionDiff(
                        subject_id=key[0],
                        section_id=key[1],
                        batch_id=key[2],
                        new_time_slot_id=s_to.time_slot_id,
                        new_room_id=s_to.room_id,
                        new_faculty_id=s_to.faculty_id,
                        diff_type="ADDED",
                    )
                )
            elif s_from and s_to:
                is_changed = (
                    s_from.time_slot_id != s_to.time_slot_id
                    or s_from.room_id != s_to.room_id
                    or s_from.faculty_id != s_to.faculty_id
                )
                if is_changed:
                    diffs.append(
                        VersionSessionDiff(
                            subject_id=key[0],
                            section_id=key[1],
                            batch_id=key[2],
                            old_time_slot_id=s_from.time_slot_id,
                            new_time_slot_id=s_to.time_slot_id,
                            old_room_id=s_from.room_id,
                            new_room_id=s_to.room_id,
                            old_faculty_id=s_from.faculty_id,
                            new_faculty_id=s_to.faculty_id,
                            diff_type="MODIFIED",
                        )
                    )

        return VersionDiffResponse(
            timetable_id=timetable_id,
            from_version_number=from_version.version_number,
            to_version_number=to_version.version_number,
            total_sessions_from=len(from_sessions),
            total_sessions_to=len(to_sessions),
            total_differences=len(diffs),
            differences=diffs,
        )
