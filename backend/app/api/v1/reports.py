import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_active_user, get_db
from app.models.user import User
from app.models.rag import Report
from app.pdf_generator.generator import pdf_builder

router = APIRouter()

@router.get("/{version_id}/pdf")
def download_pdf_report(
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Download compiled consultant-grade PDF report."""
    report = db.query(Report).filter(Report.project_version_id == version_id).first()
    
    if not report:
        # Build it dynamically if it doesn't exist yet but technical data is compiled
        try:
            pdf_path = pdf_builder.generate_report(db, str(version_id))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report PDF has not been compiled yet or failed: {str(e)}"
            )
    else:
        pdf_path = report.pdf_path

    if not os.path.exists(pdf_path):
        # File deleted or missing on disk, regenerate
        try:
            pdf_path = pdf_builder.generate_report(db, str(version_id))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to regenerate missing PDF: {str(e)}"
            )

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path)
    )
