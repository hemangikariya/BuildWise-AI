import json
from app.workflows.state_management import AgentState
from app.services.llm_service import LLMService
from app.rag.retrieval import retriever
from app.agents.business_analyst.agent import update_agent_status
from app.core.logging import agent_logger

def run_product_manager(state: AgentState) -> AgentState:
    version_id = state.get("version_id")
    prompt = state.get("input_prompt")
    agent_logger.info(f"Running Product Manager Agent for prompt: '{prompt}'")
    update_agent_status(version_id, "Product Manager", "RUNNING")
    
    # Retrieve RAG context if applicable
    context, citations = retriever.retrieve_context(f"Product requirements document user stories user personas team structure: {prompt}")
    
    system_instruction = (
        "You are an expert Product Manager. Your task is to analyze the project idea and previous analysis to generate:\n"
        "1. Product Requirements Document (PRD) details\n"
        "2. Detailed User Personas (minimum 2)\n"
        "3. User Stories (minimum 5 items, each with description and acceptance criteria)\n"
        "4. Recommended Team Structure (roles needed to build the product)\n\n"
        "Format your output strictly as a JSON object containing the keys:\n"
        "- 'prd_details': string description of core features and requirements\n"
        "- 'user_personas': list of objects with 'name', 'role', 'frustrations', 'goals'\n"
        "- 'user_stories': list of objects with 'title', 'as_a', 'i_want_to', 'so_that', 'acceptance_criteria' (list of strings)\n"
        "- 'team_structure': list of strings of suggested roles\n\n"
        f"Use the following retrieval context if relevant:\n{context}"
    )

    try:
        # Incorporate business analyst output if available
        biz_context = state.get("business_analysis", {})
        input_data = {
            "project_prompt": prompt,
            "business_analysis": biz_context
        }
        
        result = LLMService.generate_structured(
            prompt=json.dumps(input_data),
            system_instruction=system_instruction
        )
        
        state["product_requirements"] = {
            "prd_details": result.get("prd_details", ""),
            "user_personas": result.get("user_personas", []),
            "team_structure": result.get("team_structure", [])
        }
        state["user_stories"] = result.get("user_stories", [])
        
        update_agent_status(version_id, "Product Manager", "COMPLETED", output=str(result))
    except Exception as e:
        error_msg = f"Product Manager failed: {str(e)}"
        agent_logger.error(error_msg)
        update_agent_status(version_id, "Product Manager", "FAILED", error_message=error_msg)
        state["errors"].append(error_msg)
        
    return state
