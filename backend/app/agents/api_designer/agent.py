import json
from app.workflows.state_management import AgentState
from app.services.llm_service import LLMService
from app.rag.retrieval import retriever
from app.agents.business_analyst.agent import update_agent_status
from app.core.logging import agent_logger

def run_api_designer(state: AgentState) -> AgentState:
    version_id = state.get("version_id")
    prompt = state.get("input_prompt")
    agent_logger.info(f"Running API Designer Agent for prompt: '{prompt}'")
    update_agent_status(version_id, "API Designer", "RUNNING")
    
    # Retrieve RAG context if applicable
    context, citations = retriever.retrieve_context(f"FastAPI API design RESTful endpoints request response models: {prompt}")
    
    system_instruction = (
        "You are a Senior Backend Engineer and API Designer. Your task is to define the API contract for the project.\n"
        "Generate:\n"
        "1. REST API Design overview\n"
        "2. List of core API Endpoints (methods, paths, path parameters, query parameters, request bodies, success response formats, error status codes)\n"
        "3. Pydantic request/response schema descriptions\n\n"
        "Format your output strictly as a JSON object containing the keys:\n"
        "- 'overview': string\n"
        "- 'endpoints': list of objects with 'method', 'path', 'summary', 'request_body' (JSON string or description), 'response_body' (JSON string or description)\n"
        "- 'schema_definitions': string describing core models\n\n"
        f"Use the following retrieval context if relevant:\n{context}"
    )

    try:
        input_data = {
            "project_prompt": prompt,
            "database_design": state.get("database_design", {}),
            "prd": state.get("product_requirements", {})
        }
        
        result = LLMService.generate_structured(
            prompt=json.dumps(input_data),
            system_instruction=system_instruction
        )
        
        state["api_design"] = {
            "overview": result.get("overview", ""),
            "endpoints": result.get("endpoints", []),
            "schema_definitions": result.get("schema_definitions", "")
        }
        
        update_agent_status(version_id, "API Designer", "COMPLETED", output=str(result))
    except Exception as e:
        error_msg = f"API Designer failed: {str(e)}"
        agent_logger.error(error_msg)
        update_agent_status(version_id, "API Designer", "FAILED", error_message=error_msg)
        state["errors"].append(error_msg)
        
    return state
