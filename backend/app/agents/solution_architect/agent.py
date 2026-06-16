import json
from app.workflows.state_management import AgentState
from app.services.llm_service import LLMService
from app.rag.retrieval import retriever
from app.agents.business_analyst.agent import update_agent_status
from app.core.logging import agent_logger

def run_solution_architect(state: AgentState) -> AgentState:
    version_id = state.get("version_id")
    prompt = state.get("input_prompt")
    agent_logger.info(f"Running Solution Architect Agent for prompt: '{prompt}'")
    update_agent_status(version_id, "Solution Architect", "RUNNING")
    
    # Retrieve RAG context if applicable
    context, citations = retriever.retrieve_context(f"System architecture design patterns deployment strategy scalability plan: {prompt}")
    
    system_instruction = (
        "You are a Principal Software Architect. Your task is to analyze the project requirements and generate:\n"
        "1. High-level System Architecture overview\n"
        "2. Mermaid sequence or architecture diagram syntax (valid Markdown Mermaid code block)\n"
        "3. Deployment Strategy (Docker, Cloud Providers like AWS/GCP, CI/CD pipeline)\n"
        "4. Scalability Plan (Horizontal scaling, Caching, DB replicas)\n"
        "5. Technical Implementation Roadmap (Phase 1, Phase 2, etc.)\n\n"
        "Format your output strictly as a JSON object containing the keys:\n"
        "- 'architecture_overview': string\n"
        "- 'mermaid_diagram': string (contain ONLY valid mermaid diagram code starting with graph, sequenceDiagram, etc.)\n"
        "- 'deployment_strategy': string\n"
        "- 'scalability_plan': string\n"
        "- 'implementation_roadmap': list of objects with 'phase', 'milestone', 'description'\n\n"
        f"Use the following retrieval context if relevant:\n{context}"
    )

    try:
        input_data = {
            "project_prompt": prompt,
            "prd": state.get("product_requirements", {}),
            "business_analysis": state.get("business_analysis", {})
        }
        
        result = LLMService.generate_structured(
            prompt=json.dumps(input_data),
            system_instruction=system_instruction
        )
        
        state["system_architecture"] = {
            "overview": result.get("architecture_overview", ""),
            "diagram": result.get("mermaid_diagram", "")
        }
        state["deployment_plan"] = {
            "strategy": result.get("deployment_strategy", "")
        }
        state["scalability_planning"] = {
            "plan": result.get("scalability_plan", "")
        }
        
        state["technical_documentation"] = state.get("technical_documentation") or {}
        state["technical_documentation"]["roadmap"] = result.get("implementation_roadmap", [])
        
        update_agent_status(version_id, "Solution Architect", "COMPLETED", output=str(result))
    except Exception as e:
        error_msg = f"Solution Architect failed: {str(e)}"
        agent_logger.error(error_msg)
        update_agent_status(version_id, "Solution Architect", "FAILED", error_message=error_msg)
        state["errors"].append(error_msg)
        
    return state
