from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.ui_generator.generator import ui_generator

router = APIRouter()

class UIRequest(BaseModel):
    idea: str

@router.post("/generate", status_code=status.HTTP_200_OK)
def generate_ui_design_blueprint(req: UIRequest, current_user: User = Depends(get_current_active_user)):
    """Generate professional UI design blueprints and layout hierarchies."""
    try:
        ui_blueprint = ui_generator.generate_ui_blueprint(req.idea)
        return ui_blueprint
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"UI Generation service failed: {str(e)}"
        )
