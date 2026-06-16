import json
from app.workflows.state_management import AgentState
from app.services.llm_service import LLMService
from app.rag.retrieval import retriever
from app.agents.business_analyst.agent import update_agent_status
from app.core.logging import agent_logger

def run_security_agent(state: AgentState) -> AgentState:
    version_id = state.get("version_id")
    prompt = state.get("input_prompt")
    agent_logger.info(f"Running Security Agent for prompt: '{prompt}'")
    update_agent_status(version_id, "Security Agent", "RUNNING")
    
    # Retrieve RAG context if applicable
    context, citations = retriever.retrieve_context(f"Web application security JWT authentication RBAC rate limiting OWASP: {prompt}")
    
    system_instruction = (
        "You are a Senior Security Engineer and Security Architect. Your task is to perform a security review for the project.\n"
        "Generate:\n"
        "1. Security Strategy overview (encryption, TLS, storage security)\n"
        "2. Authentication & Authorization Review (JWT, Refresh tokens, RBAC permissions check)\n"
        "3. OWASP Top 10 Mitigation strategies (SQL Injection, XSS, CSRF, input validation)\n"
        "4. Risk & Compliance recommendations (e.g. GDPR, HIPAA if applicable)\n\n"
        "Format your output strictly as a JSON object containing the keys:\n"
        "- 'security_strategy': string\n"
        "- 'auth_review': string\n"
        "- 'owasp_mitigation': string\n"
        "- 'compliance_recommendations': string\n\n"
        f"Use the following retrieval context if relevant:\n{context}"
    )

    try:
        input_data = {
            "project_prompt": prompt,
            "api_design": state.get("api_design", {}),
            "database_design": state.get("database_design", {})
        }
        
        result = LLMService.generate_structured(
            prompt=json.dumps(input_data),
            system_instruction=system_instruction
        )
        
        state["security_review"] = {
            "strategy": result.get("security_strategy", ""),
            "auth_review": result.get("auth_review", ""),
            "owasp_mitigation": result.get("owasp_mitigation", ""),
            "compliance": result.get("compliance_recommendations", "")
        }
        
        update_agent_status(version_id, "Security Agent", "COMPLETED", output=str(result))
    except Exception as e:
        error_msg = f"Security Agent failed: {str(e)}"
        agent_logger.error(error_msg)
        update_agent_status(version_id, "Security Agent", "FAILED", error_message=error_msg)
        state["errors"].append(error_msg)
        
    return state
