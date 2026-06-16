import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict

# AIChat Schemas
class AIChatCreate(BaseModel):
    message: str

class AIChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    message: str
    created_at: datetime

# AgentRun Schemas
class AgentRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    agent_name: str
    status: str
    output: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# ProjectVersion Schemas
class ProjectVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    version_number: int
    input_prompt: str
    output_data: Optional[Dict[str, Any]] = None
    created_at: datetime

# Project Schemas
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
