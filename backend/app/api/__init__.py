from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.academic_years import router as academic_years_router
from app.api.branches import router as branches_router
from app.api.subjects import router as subjects_router
from app.api.faculty import router as faculty_router
from app.api.resources import router as resources_router
from app.api.generation import router as generation_router, runs_router as generation_runs_router
from app.api.timetables import router as timetables_router
from app.api.versions import router as versions_router
from app.api.documents import router as documents_router
from app.api.scheduling import router as scheduling_router

api_router = APIRouter()

# Attach health route at root level
api_router.include_router(health_router)

# Attach v1 endpoints
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(health_router)
v1_router.include_router(academic_years_router)
v1_router.include_router(branches_router)
v1_router.include_router(subjects_router)
v1_router.include_router(faculty_router)
v1_router.include_router(resources_router)
v1_router.include_router(generation_router)
v1_router.include_router(generation_runs_router)
v1_router.include_router(timetables_router)
v1_router.include_router(versions_router)
v1_router.include_router(documents_router)
v1_router.include_router(scheduling_router)

api_router.include_router(v1_router)

__all__ = ["api_router"]
