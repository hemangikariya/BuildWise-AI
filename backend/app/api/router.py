from fastapi import APIRouter
from app.api.v1 import auth, projects, logo_studio, ui_generator, reports, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(logo_studio.router, prefix="/logo-studio", tags=["Logo Studio"])
api_router.include_router(ui_generator.router, prefix="/ui-generator", tags=["UI Generator"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Operations"])
