"""
Services module for business logic, deterministic calculations, orchestration, and view assembly.
"""
from app.services.academic_service import AcademicService
from app.services.ingestion_service import IngestionService
from app.services.versioning_service import VersioningService
from app.services.orchestration_service import OrchestrationService
from app.services.pipeline_service import build_scheduling_input_from_db
from app.services.resource_calc import (
    calculate_sections,
    calculate_batches,
    generate_time_slots,
    validate_availability_windows,
    SectionCalculationResult,
    BatchCalculationResult,
    SlotConfigInput,
    GeneratedTimeSlot,
)
from app.services.timetable_view import build_timetable_matrix, export_timetable_csv

__all__ = [
    "AcademicService",
    "IngestionService",
    "VersioningService",
    "OrchestrationService",
    "build_scheduling_input_from_db",
    "calculate_sections",
    "calculate_batches",
    "generate_time_slots",
    "validate_availability_windows",
    "SectionCalculationResult",
    "BatchCalculationResult",
    "SlotConfigInput",
    "GeneratedTimeSlot",
    "build_timetable_matrix",
    "export_timetable_csv",
]
