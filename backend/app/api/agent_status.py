from fastapi import APIRouter, HTTPException
from app.models import AgentStatus, AgentFeedback, AgentFeedbackResponse
from app.agent.agent import get_agent
from app.services.lesson_service import get_lesson_service
from app.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.get("/status", response_model=AgentStatus)
async def get_agent_status():
    """
    Get the current status of the AI agent.
    
    Returns:
    - Agent ID
    - Current status (ready, processing, error)
    - Current task (if any)
    - List of completed steps
    - Last updated timestamp
    
    This endpoint helps track the agent's reasoning process.
    """
    try:
        agent = get_agent()
        status = agent.get_status()
        
        return AgentStatus(
            agent_id=status["agent_id"],
            status=status["status"],
            current_task=status.get("current_task"),
            steps_completed=status["steps_completed"],
            last_updated=datetime.fromisoformat(status["last_updated"])
        )
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent status: {str(e)}"
        )

@router.post("/feedback", response_model=AgentFeedbackResponse, status_code=201)
async def submit_feedback(feedback: AgentFeedback):
    """
    Submit feedback for a generated lesson plan.
    
    This helps improve the agent's performance over time.
    
    Request body:
    ```json
    {
      "lesson_id": "uuid-of-lesson",
      "rating": 5,
      "feedback_text": "Very helpful and well-structured!",
      "helpful": true
    }
    ```
    
    Rating scale: 1-5 (1 = poor, 5 = excellent)
    """
    try:
        logger.info(f"Received feedback for lesson {feedback.lesson_id}")
        
        # Validate lesson exists
        lesson_service = get_lesson_service()
        lesson = lesson_service.get_lesson(feedback.lesson_id)
        
        if lesson is None:
            raise HTTPException(
                status_code=404,
                detail=f"Lesson with ID {feedback.lesson_id} not found"
            )
        
        # Save feedback
        result = lesson_service.save_feedback(
            lesson_id=feedback.lesson_id,
            rating=feedback.rating,
            feedback_text=feedback.feedback_text or "",
            helpful=feedback.helpful
        )
        
        return AgentFeedbackResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )