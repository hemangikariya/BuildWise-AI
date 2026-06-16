import uuid
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.workflows.state_management import AgentState
from app.workflows.routing import route_after_judge
from app.agents.business_analyst.agent import run_business_analyst
from app.agents.product_manager.agent import run_product_manager
from app.agents.solution_architect.agent import run_solution_architect
from app.agents.database_architect.agent import run_database_architect
from app.agents.api_designer.agent import run_api_designer
from app.agents.security_agent.agent import run_security_agent
from app.agents.judge.agent import run_judge
from app.db.session import SessionLocal
from app.models.project import ProjectVersion
from app.pdf_generator.generator import pdf_builder
from app.core.logging import system_logger

# 1. Initialize StateGraph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("business_analyst", run_business_analyst)
workflow.add_node("product_manager", run_product_manager)
workflow.add_node("solution_architect", run_solution_architect)
workflow.add_node("database_architect", run_database_architect)
workflow.add_node("api_designer", run_api_designer)
workflow.add_node("security_agent", run_security_agent)
workflow.add_node("judge", run_judge)

# 3. Set entry point
workflow.set_entry_point("business_analyst")

# 4. Add Edges
workflow.add_edge("business_analyst", "product_manager")
workflow.add_edge("product_manager", "solution_architect")
workflow.add_edge("solution_architect", "database_architect")
workflow.add_edge("database_architect", "api_designer")
workflow.add_edge("api_designer", "security_agent")
workflow.add_edge("security_agent", "judge")

# 5. Add Conditional Router
def route_decision(state: AgentState) -> str:
    decision = route_after_judge(state)
    if decision == "continue":
        return END
    else:
        return "business_analyst"

workflow.add_conditional_edges(
    "judge",
    route_decision,
    {
        END: END,
        "business_analyst": "business_analyst"
    }
)

# Compile Graph
app_graph = workflow.compile()

# Runner Function
def run_cto_workflow(project_id: str, version_id: str, prompt: str) -> Dict[str, Any]:
    """Runs the multi-agent LangGraph workflow synchronously or as background task."""
    system_logger.info(f"Initiating CTO workflow for Project: {project_id}, Version: {version_id}")
    
    # Initialize state
    initial_state: AgentState = {
        "project_id": project_id,
        "version_id": version_id,
        "input_prompt": prompt,
        "business_analysis": {},
        "product_requirements": {},
        "user_stories": [],
        "system_architecture": {},
        "database_design": {},
        "api_design": {},
        "security_review": {},
        "judge_review": {},
        "errors": [],
        "retry_count": 0,
        "current_step": "business_analyst",
        "ui_blueprint": {},
        "branding_recommendations": {}
    }

    try:
        # Run state machine
        final_state = app_graph.invoke(initial_state)
        
        # Save output to Database
        db = SessionLocal()
        try:
            version = db.query(ProjectVersion).filter(ProjectVersion.id == uuid.UUID(version_id)).first()
            if version:
                compiled_blueprint = {
                    "business_analysis": final_state.get("business_analysis", {}),
                    "product_requirements": final_state.get("product_requirements", {}),
                    "user_stories": final_state.get("user_stories", []),
                    "system_architecture": final_state.get("system_architecture", {}),
                    "database_design": final_state.get("database_design", {}),
                    "api_design": final_state.get("api_design", {}),
                    "security_review": final_state.get("security_review", {})
                }
                version.output_data = compiled_blueprint
                db.commit()
                system_logger.info(f"CTO workflow successfully completed. Version {version_id} updated.")
                
                # Generate consultant-grade PDF
                try:
                    pdf_builder.generate_report(db, version_id)
                except Exception as pdf_err:
                    system_logger.error(f"Failed to generate PDF for version {version_id}: {str(pdf_err)}")
        finally:
            db.close()
            
        return final_state
    except Exception as e:
        system_logger.error(f"CTO workflow failed during orchestration execution: {str(e)}")
        # Log to AgentRuns
        from app.agents.business_analyst.agent import update_agent_status
        update_agent_status(version_id, "Orchestrator", "FAILED", error_message=str(e))
        raise e
