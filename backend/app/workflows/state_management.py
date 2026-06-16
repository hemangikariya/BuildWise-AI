from typing import Any, Dict, List, TypedDict

class AgentState(TypedDict):
    project_id: str
    version_id: str
    input_prompt: str
    
    # Outputs from agents
    business_analysis: Dict[str, Any]
    product_requirements: Dict[str, Any]
    user_stories: List[Dict[str, Any]]
    system_architecture: Dict[str, Any]
    database_design: Dict[str, Any]
    api_design: Dict[str, Any]
    security_review: Dict[str, Any]
    cost_estimation: Dict[str, Any]
    scalability_planning: Dict[str, Any]
    deployment_plan: Dict[str, Any]
    technical_documentation: Dict[str, Any]
    ui_blueprint: Dict[str, Any]
    branding_recommendations: Dict[str, Any]
    
    # Judge review status
    judge_review: Dict[str, Any]
    
    # Control variables
    errors: List[str]
    retry_count: int
    current_step: str
