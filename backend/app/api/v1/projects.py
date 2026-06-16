import asyncio
import json
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_active_user, get_db
from app.models.user import User
from app.models.project import Project, ProjectVersion, AIChat
from app.models.agent import AgentRun
from app.repositories.project_repository import project_repo
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectVersionResponse, AIChatCreate, AIChatResponse
from app.workflows.orchestration import run_cto_workflow
from app.services.llm_service import LLMService
from app.rag.retrieval import retriever
from app.core.logging import api_logger

router = APIRouter()

@router.get("", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """List all projects belonging to the logged-in user."""
    return project_repo.get_by_user(db, user_id=current_user.id)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create a new project workspace."""
    project = Project(
        user_id=current_user.id,
        title=project_in.title,
        description=project_in.description
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(project_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete project and cascading children."""
    project = project_repo.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    project_repo.remove(db, id=project_id)
    return {"status": "success", "message": "Project deleted"}

@router.get("/{project_id}/versions", response_model=List[ProjectVersionResponse])
def get_project_versions(project_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Retrieve all technical plans/versions of a project."""
    project = project_repo.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project_repo.get_versions(db, project_id=project_id)

@router.get("/{project_id}/versions/{version_id}", response_model=ProjectVersionResponse)
def get_project_version(project_id: uuid.UUID, version_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Retrieve a specific compiled blueprint version."""
    project = project_repo.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    version = project_repo.get_version(db, version_id=version_id)
    if not version or version.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return version

@router.post("/{project_id}/generate", status_code=status.HTTP_202_ACCEPTED)
def generate_technical_plan(
    project_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Starts the multi-agent generation of the technical plan as a background task."""
    project = project_repo.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Calculate version number
    versions = project_repo.get_versions(db, project_id=project_id)
    next_ver = len(versions) + 1
    
    # Create ProjectVersion
    version = project_repo.create_version(
        db,
        project_id=project_id,
        version_number=next_ver,
        input_prompt=project.description or project.title
    )
    
    # Pre-seed AgentRuns in DB as PENDING
    agents = [
        "Business Analyst",
        "Product Manager",
        "Solution Architect",
        "Database Architect",
        "API Designer",
        "Security Agent",
        "Judge Agent"
    ]
    for agent_name in agents:
        run = AgentRun(
            project_version_id=version.id,
            agent_name=agent_name,
            status="PENDING"
        )
        db.add(run)
    db.commit()
    
    # Add orchestrator to background tasks
    background_tasks.add_task(
        run_cto_workflow,
        project_id=str(project_id),
        version_id=str(version.id),
        prompt=project.description or project.title
    )
    
    return {"status": "initiated", "version_id": version.id}

@router.get("/{project_id}/versions/{version_id}/stream")
def stream_generation_progress(
    project_id: uuid.UUID,
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """SSE endpoint streaming live agent run progress updates to the frontend."""
    project = project_repo.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    async def event_generator():
        # Keep tracking status of agent runs
        completed_agents = set()
        total_agents = 7
        
        while True:
            # Open separate db session for thread safety in async loop
            from app.db.session import SessionLocal
            session = SessionLocal()
            try:
                runs = session.query(AgentRun).filter(AgentRun.project_version_id == version_id).all()
                if not runs:
                    yield {"event": "error", "data": "No runs found"}
                    break
                    
                update_list = []
                finished_count = 0
                failed_any = False
                
                for run in runs:
                    update_list.append({
                        "agent": run.agent_name,
                        "status": run.status,
                        "error": run.error_message
                    })
                    if run.status in ["COMPLETED", "FAILED"]:
                        finished_count += 1
                    if run.status == "FAILED":
                        failed_any = True

                progress = float(finished_count) / total_agents
                
                yield {
                    "event": "progress",
                    "data": json.dumps({
                        "progress": progress,
                        "agents": update_list
                    })
                }

                # Terminate condition
                if finished_count == total_agents or failed_any:
                    # Stream one last confirmation
                    version = session.query(ProjectVersion).filter(ProjectVersion.id == version_id).first()
                    has_output = version and version.output_data and len(version.output_data) > 0
                    yield {
                        "event": "complete" if has_output else "failed",
                        "data": json.dumps({
                            "progress": 1.0 if has_output else progress,
                            "completed": has_output
                        })
                    }
                    break
            except Exception as e:
                api_logger.error(f"SSE generator thread error: {str(e)}")
                yield {"event": "error", "data": str(e)}
                break
            finally:
                session.close()
            
            await asyncio.sleep(2.0)
            
    return EventSourceResponse(event_generator())

@router.post("/{project_id}/chat", response_model=AIChatResponse)
def cto_consultation(
    project_id: uuid.UUID,
    chat_in: AIChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Allows the user to text and get tech feedback from a virtual CTO (combining RAG + project spec context)."""
    project = project_repo.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Add user message
    user_chat = AIChat(
        project_id=project_id,
        user_id=current_user.id,
        role="user",
        message=chat_in.message
    )
    db.add(user_chat)
    db.commit()
    db.refresh(user_chat)

    # Get latest blueprint output to contextualize LLM responses
    latest_version = db.query(ProjectVersion).filter(ProjectVersion.project_id == project_id).order_by(ProjectVersion.version_number.desc()).first()
    blueprint_context = json.dumps(latest_version.output_data) if latest_version else "No technical plan has been generated yet."

    # RAG search for the chat topic
    rag_context, citations = retriever.retrieve_context(chat_in.message)

    # Call LLM
    system_instruction = (
        "You are BuildWise AI's Virtual CTO. You are consulting the user on their project.\n"
        "Here is the project background / technical blueprint we have generated so far:\n"
        f"{blueprint_context}\n\n"
        "Here is the design documentation context retrieved from our Knowledge Base:\n"
        f"{rag_context}\n\n"
        "Provide professional, concrete architectural advice, answering their question directly. Do not hallucinate claims."
    )

    try:
        cto_response = LLMService.generate(prompt=chat_in.message, system_instruction=system_instruction)
        
        # Add assistant message
        assistant_chat = AIChat(
            project_id=project_id,
            user_id=current_user.id,
            role="assistant",
            message=cto_response
        )
        db.add(assistant_chat)
        db.commit()
        db.refresh(assistant_chat)
        return assistant_chat
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"CTO failed to consult: {str(e)}")

@router.get("/{project_id}/chats", response_model=List[AIChatResponse])
def get_chat_history(project_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """List chat history with the CTO for a project."""
    project = project_repo.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project_repo.get_chats(db, project_id=project_id)
