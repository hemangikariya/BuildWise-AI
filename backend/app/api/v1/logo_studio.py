from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.logo_studio.generator import logo_studio

router = APIRouter()

class LogoRequest(BaseModel):
    idea: str

@router.post("/generate", status_code=status.HTTP_200_OK)
def generate_logo_suite(req: LogoRequest, current_user: User = Depends(get_current_active_user)):
    """Generate professional brand design suggestions and SVG vector code."""
    try:
        brand_data = logo_studio.generate_branding_package(req.idea)
        return brand_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Logo Generation service failed: {str(e)}"
        )
