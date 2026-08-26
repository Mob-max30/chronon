import pytest
from datetime import datetime
from app.services.orchestration_service import OrchestrationService
from app.schemas.timetable import GenerationTriggerRequest
from app.models.timetable import GenerationStatus, GenerationRun
from app.schemas.contracts import (
    SchedulingInput,
    SubjectRequirement,
    SectionContract,
    TimeSlotContract,
    RoomContract,
    TimetableSessionContract,
)
from app.scheduling.fixtures import get_sample_scheduling_input, get_infeasible_fixture


@pytest.mark.asyncio
async def test_orchestration_service_success_flow():
    service = OrchestrationService(db=None)
    request = GenerationTriggerRequest(
        timetable_id=1,
        academic_year_id=1,
        semester_ids=[3],
        is_joint_first_year=False,
        triggered_by="test_user",
        notes="Automated test generation",
    )

    result = await service.orchestrate_generation(request, custom_input=get_sample_scheduling_input())

    assert result.generation_run.status == GenerationStatus.SUCCESS
    assert result.generation_run.timetable_id == 1
    assert result.validation_result is not None
    assert result.validation_result.is_valid is True
    assert result.total_sessions_generated > 0
    assert result.version is not None
    assert result.generation_run.quality_score is not None


@pytest.mark.asyncio
async def test_orchestration_service_infeasible_flow():
    service = OrchestrationService(db=None)
    request = GenerationTriggerRequest(
        timetable_id=1,
        academic_year_id=1,
        semester_ids=[3],
        is_joint_first_year=False,
    )

    infeasible_input = get_infeasible_fixture()

    result = await service.orchestrate_generation(request, custom_input=infeasible_input)

    assert result.generation_run.status in [GenerationStatus.INFEASIBLE, GenerationStatus.FAILED]


@pytest.mark.asyncio
async def test_orchestration_service_timeout_handling():
    service = OrchestrationService(db=None)
    request = GenerationTriggerRequest(
        timetable_id=1,
        academic_year_id=1,
        semester_ids=[3],
        max_solver_time_seconds=0,  # 0s forces immediate timeout check
    )

    result = await service.orchestrate_generation(request, custom_input=get_sample_scheduling_input())

    assert result.generation_run.status == GenerationStatus.TIMEOUT
    assert result.generation_run.conflict_summary["error"] == "SOLVER_TIMEOUT"


@pytest.mark.asyncio
async def test_orchestration_cancellation_flow():
    service = OrchestrationService(db=None)
    cancelled = await service.cancel_generation_run(9999)
    assert cancelled is None


@pytest.mark.asyncio
async def test_orchestration_structured_error_no_leaks():
    service = OrchestrationService(db=None)
    request = GenerationTriggerRequest(
        timetable_id=1,
        academic_year_id=1,
        semester_ids=[3],
    )

    class BrokenInput:
        pass

    result = await service.orchestrate_generation(request, custom_input=BrokenInput())  # type: ignore

    assert result.generation_run.status == GenerationStatus.FAILED
    assert "EXECUTION_EXCEPTION" in result.generation_run.conflict_summary["error"]
    assert "details" in result.generation_run.conflict_summary
    assert isinstance(result.generation_run.conflict_summary["details"], str)
