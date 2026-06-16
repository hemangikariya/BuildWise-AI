from typing import Literal
from app.workflows.state_management import AgentState
from app.core.logging import agent_logger

def route_after_judge(state: AgentState) -> Literal["continue", "correct"]:
    """Determines whether the workflow should complete or loop back to correct failing agents."""
    review = state.get("judge_review", {})
    approved = review.get("approved", True)
    retry_count = state.get("retry_count", 0)

    if approved:
        agent_logger.info("Judge Agent approved technical plan. Completing workflow.")
        return "continue"
        
    if retry_count >= 3:
        agent_logger.warning("Judge Agent rejected technical plan, but retry limit (3) reached. Forcing completion.")
        return "continue"
        
    feedbacks = review.get("feedbacks", [])
    agent_logger.info(f"Judge Agent rejected plan. Feedbacks: {feedbacks}. Looping back to correct plans. Attempt {retry_count + 1}/3")
    return "correct"
