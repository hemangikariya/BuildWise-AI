import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_admin, get_db
from app.models.user import User
from app.models.agent import AgentRun
from app.models.logs import SystemLog, AuditLog
from app.models.rag import KnowledgeBase
from app.schemas.user import UserResponse
from app.schemas.system import SystemLogResponse, AuditLogResponse
from app.rag.ingestion import IngestionManager
from app.core.config import settings

router = APIRouter()

class UserStatusUpdate(BaseModel):
    is_active: bool

class IngestRequest(BaseModel):
    directory_path: Optional[str] = None

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Admin-only endpoint to retrieve all registered users."""
    return db.query(User).all()

@router.put("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: uuid.UUID,
    status_update: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Block or unblock a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot change their own active status")
        
    user.is_active = status_update.is_active
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Delete a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot delete their own account")
        
    db.delete(user)
    db.commit()
    return {"status": "success", "message": "User account deleted"}

@router.get("/agent-runs")
def list_agent_runs(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Monitor live or completed agent runs."""
    runs = db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(100).all()
    return [{
        "id": r.id,
        "project_version_id": r.project_version_id,
        "agent_name": r.agent_name,
        "status": r.status,
        "error_message": r.error_message,
        "created_at": r.created_at
    } for r in runs]

@router.get("/system-logs", response_model=List[SystemLogResponse])
def list_system_logs(level: Optional[str] = None, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Query system logs recorded in PostgreSQL."""
    query = db.query(SystemLog)
    if level:
        query = query.filter(SystemLog.level == level.upper())
    return query.order_by(SystemLog.created_at.desc()).limit(100).all()

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Query system activity audit logs."""
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()

@router.get("/knowledge-base")
def list_knowledge_entries(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """List knowledge base sources cataloged in database."""
    items = db.query(KnowledgeBase).all()
    return [{
        "id": item.id,
        "title": item.title,
        "file_path": item.file_path,
        "source_url": item.source_url,
        "created_at": item.created_at
    } for item in items]

@router.post("/knowledge-base/ingest", status_code=status.HTTP_200_OK)
def trigger_knowledge_ingestion(
    req: IngestRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Triggers loading and indexing of documentation directory in database and ChromaDB."""
    target_dir = req.directory_path or settings.KNOWLEDGE_BASE_DIR
    try:
        ingested = IngestionManager.ingest_directory(db, target_dir)
        return {
            "status": "success",
            "message": f"Successfully ingested {len(ingested)} documents from {target_dir}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
