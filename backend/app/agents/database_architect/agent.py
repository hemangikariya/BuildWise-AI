import json
from app.workflows.state_management import AgentState
from app.services.llm_service import LLMService
from app.rag.retrieval import retriever
from app.agents.business_analyst.agent import update_agent_status
from app.core.logging import agent_logger

def run_database_architect(state: AgentState) -> AgentState:
    version_id = state.get("version_id")
    prompt = state.get("input_prompt")
    agent_logger.info(f"Running Database Architect Agent for prompt: '{prompt}'")
    update_agent_status(version_id, "Database Architect", "RUNNING")
    
    # Retrieve RAG context if applicable
    context, citations = retriever.retrieve_context(f"PostgreSQL database schema design foreign keys constraints indexes: {prompt}")
    
    system_instruction = (
        "You are a Senior Database Architect specializing in PostgreSQL. Your task is to design the relational database schema for the project.\n"
        "Generate:\n"
        "1. High-level Database Architecture overview (entities, relationships)\n"
        "2. Complete PostgreSQL DDL Schema (SQL queries to CREATE tables with correct types, Primary Keys, Foreign Keys, unique/check constraints, cascading rules, and indexes)\n"
        "3. Recommended performance optimization indexing strategies\n\n"
        "Format your output strictly as a JSON object containing the keys:\n"
        "- 'overview': string description of the entity relationships\n"
        "- 'schema_ddl': string containing raw DDL statements inside SQL formatting\n"
        "- 'indexing_strategy': string describing performance index choices\n\n"
        f"Use the following retrieval context if relevant:\n{context}"
    )

    try:
        input_data = {
            "project_prompt": prompt,
            "system_architecture": state.get("system_architecture", {}),
            "prd": state.get("product_requirements", {})
        }
        
        result = LLMService.generate_structured(
            prompt=json.dumps(input_data),
            system_instruction=system_instruction
        )
        
        state["database_design"] = {
            "overview": result.get("overview", ""),
            "schema_ddl": result.get("schema_ddl", ""),
            "indexing_strategy": result.get("indexing_strategy", "")
        }
        
        update_agent_status(version_id, "Database Architect", "COMPLETED", output=str(result))
    except Exception as e:
        error_msg = f"Database Architect failed: {str(e)}"
        agent_logger.error(error_msg)
        update_agent_status(version_id, "Database Architect", "FAILED", error_message=error_msg)
        state["errors"].append(error_msg)
        
    return state
