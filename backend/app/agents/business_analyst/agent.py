import uuid
from typing import Dict, Any
from app.workflows.state_management import AgentState
from app.services.llm_service import LLMService
from app.rag.retrieval import retriever
from app.db.session import SessionLocal
from app.models.agent import AgentRun
from app.core.logging import agent_logger

def update_agent_status(version_id: str, agent_name: str, status: str, output: str = None, error_message: str = None):
    """Helper to update AgentRun status in PostgreSQL for live SSE tracking."""
    db = SessionLocal()
    try:
        run = db.query(AgentRun).filter(
            AgentRun.project_version_id == uuid.UUID(version_id),
            AgentRun.agent_name == agent_name
        ).first()
        if not run:
            run = AgentRun(
                project_version_id=uuid.UUID(version_id),
                agent_name=agent_name,
                status=status,
                output=output,
                error_message=error_message
            )
            db.add(run)
        else:
            run.status = status
            if output:
                run.output = output
            if error_message:
                run.error_message = error_message
        db.commit()
    except Exception as e:
        db.rollback()
        agent_logger.error(f"Failed to update agent status in DB: {str(e)}")
    finally:
        db.close()

def run_business_analyst(state: AgentState) -> AgentState:
    version_id = state.get("version_id")
    prompt = state.get("input_prompt")
    agent_logger.info(f"Running Business Analyst Agent for prompt: '{prompt}'")
    update_agent_status(version_id, "Business Analyst", "RUNNING")
    
    # Retrieve RAG context if applicable
    context, citations = retriever.retrieve_context(f"Business analysis market fit competitors cost estimation for: {prompt}")
    
    system_instruction = (
        "You are a Senior Business Analyst. Your task is to analyze the user's project idea and generate:\n"
        "1. Executive Summary\n"
        "2. Business Analysis (market fit, revenue model, competitor analysis)\n"
        "3. Cost Estimation (infra, development, third-party)\n"
        "4. Risk Assessment (list of potential business risks and mitigation strategies)\n\n"
        "Format your output strictly as a JSON object containing the keys: "
        "'executive_summary', 'market_fit', 'revenue_model', 'competitors', 'cost_estimation', 'risks'.\n"
        f"Use the following retrieval context if relevant:\n{context}"
    )

    try:
        result = LLMService.generate_structured(
            prompt=f"Project Idea: {prompt}",
            system_instruction=system_instruction
        )
        
        # Parse and save outputs to state
        state["business_analysis"] = {
            "executive_summary": result.get("executive_summary", ""),
            "market_fit": result.get("market_fit", ""),
            "revenue_model": result.get("revenue_model", ""),
            "competitor_analysis": result.get("competitors", [])
        }
        state["cost_estimation"] = result.get("cost_estimation", {})
        # Map risks to state or format as needed
        state["technical_documentation"] = state.get("technical_documentation") or {}
        state["technical_documentation"]["risks"] = result.get("risks", [])
        
        update_agent_status(version_id, "Business Analyst", "COMPLETED", output=str(result))
    except Exception as e:
        error_msg = f"Business Analyst failed: {str(e)}"
        agent_logger.error(error_msg)
        update_agent_status(version_id, "Business Analyst", "FAILED", error_message=error_msg)
        state["errors"].append(error_msg)
        
    return state
