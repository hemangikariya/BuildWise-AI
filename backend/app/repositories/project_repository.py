import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectVersion, AIChat
from app.models.agent import AgentRun
from app.repositories.base import BaseRepository

class ProjectRepository(BaseRepository[Project]):
    def get_by_user(self, db: Session, user_id: uuid.UUID, *, skip: int = 0, limit: int = 100) -> List[Project]:
        return db.query(self.model).filter(self.model.user_id == user_id).offset(skip).limit(limit).all()

    def get_version(self, db: Session, version_id: uuid.UUID) -> Optional[ProjectVersion]:
        return db.query(ProjectVersion).filter(ProjectVersion.id == version_id).first()

    def get_versions(self, db: Session, project_id: uuid.UUID) -> List[ProjectVersion]:
        return db.query(ProjectVersion).filter(ProjectVersion.project_id == project_id).order_by(ProjectVersion.version_number.desc()).all()

    def create_version(self, db: Session, *, project_id: uuid.UUID, version_number: int, input_prompt: str) -> ProjectVersion:
        version = ProjectVersion(
            project_id=project_id,
            version_number=version_number,
            input_prompt=input_prompt,
            output_data={}
        )
        db.add(version)
        db.commit()
        db.refresh(version)
        return version

    def get_agent_runs(self, db: Session, version_id: uuid.UUID) -> List[AgentRun]:
        return db.query(AgentRun).filter(AgentRun.project_version_id == version_id).all()

    def get_chats(self, db: Session, project_id: uuid.UUID) -> List[AIChat]:
        return db.query(AIChat).filter(AIChat.project_id == project_id).order_by(AIChat.created_at.asc()).all()

project_repo = ProjectRepository(Project)
