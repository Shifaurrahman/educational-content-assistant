from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models import (
    LessonGenerateRequest, 
    LessonGenerateResponse, 
    LessonPlan,
    AgentFeedback,
    AgentFeedbackResponse
)
from app.services.lesson_service import get_lesson_service
from app.utils.logger import logger
from typing import List, Dict, Any

router = APIRouter(prefix="/lessons", tags=["Lessons"])

@router.post("/generate", response_model=LessonGenerateResponse, status_code=201)
async def generate_lesson(request: LessonGenerateRequest):
    """
    Generate a personalized lesson plan using the AI agent.
    
    The agent will:
    1. Analyze your request (topic, difficulty, duration, learner profile)
    2. Search the knowledge base for relevant educational content
    3. Generate a structured lesson plan with objectives, activities, and assessments
    4. Adjust difficulty based on the learner profile
    
    This endpoint demonstrates multi-step reasoning and tool usage.
    
    Example request:
    ```json
    {
      "topic": "Introduction to Photosynthesis",
      "duration_minutes": 60,
      "learner_profile": {
        "age_group": "13-15",
        "difficulty_level": "intermediate",
        "prior_knowledge": "Basic biology concepts",
        "learning_objectives": [
          "Understand the process of photosynthesis",
          "Identify the key components involved"
        ]
      },
      "additional_context": "Focus on practical experiments"
    }
    ```
    """
    try:
        logger.info(f"Received lesson generation request for topic: {request.topic}")
        
        lesson_service = get_lesson_service()
        result = await lesson_service.generate_lesson(request)
        
        return LessonGenerateResponse(**result)
        
    except Exception as e:
        logger.error(f"Error generating lesson: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate lesson: {str(e)}"
        )

@router.get("/{lesson_id}", response_model=LessonPlan)
async def get_lesson(lesson_id: str):
    """
    Retrieve a previously generated lesson plan by ID.
    
    Returns the complete lesson plan with all sections:
    - Learning objectives
    - Prerequisites
    - Content outline
    - Activities
    - Assessments
    - Resources
    """
    try:
        lesson_service = get_lesson_service()
        lesson = lesson_service.get_lesson(lesson_id)
        
        if lesson is None:
            raise HTTPException(
                status_code=404,
                detail=f"Lesson with ID {lesson_id} not found"
            )
        
        return lesson
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve lesson: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
async def list_lessons(limit: int = 10):
    """
    List all generated lesson plans (most recent first).
    
    Query parameters:
    - limit: Maximum number of lessons to return (default: 10)
    """
    try:
        lesson_service = get_lesson_service()
        lessons = lesson_service.list_lessons(limit=limit)
        return lessons
        
    except Exception as e:
        logger.error(f"Error listing lessons: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list lessons: {str(e)}"
        )