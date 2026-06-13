from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.profile import router as profile_router
from backend.app.api.v1.projects import router as projects_router
from backend.app.api.v1.ai import router as ai_router
from backend.app.api.v1.jd import router as jd_router
from backend.app.api.v1.resume import router as resume_router
from backend.app.api.v1.ats import router as ats_router
from backend.app.api.v1.cover import router as cover_router
from backend.app.api.v1.templates import router as templates_router
from backend.app.api.v1.admin import router as admin_router
from backend.app.api.v1.billing import router as billing_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(profile_router, prefix="/profile", tags=["profile"])
router.include_router(projects_router, prefix="/projects", tags=["projects"])
router.include_router(ai_router, prefix="/ai", tags=["ai"])
router.include_router(jd_router, prefix="/jd", tags=["jd"])
router.include_router(resume_router, prefix="/resume", tags=["resume"])
router.include_router(ats_router, prefix="/ats", tags=["ats"])
router.include_router(cover_router, prefix="/cover", tags=["cover"])
router.include_router(templates_router, prefix="/templates", tags=["templates"])
router.include_router(admin_router, prefix="/admin", tags=["admin"])
router.include_router(billing_router, prefix="/billing", tags=["billing"])
