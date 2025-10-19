from app.models import LessonPlan, LessonGenerateRequest
from app.agent.agent import get_agent
from app.config import get_settings
from app.utils.logger import logger
from app.utils.evaluation import get_evaluator
from pathlib import Path
import json
from typing import Optional, Dict, Any
import uuid

settings = get_settings()

class LessonService:
    """Service for managing lesson plan generation and storage"""
    
    def __init__(self):
        # Ensure lessons directory exists
        Path(settings.LESSONS_DIR).mkdir(parents=True, exist_ok=True)
        self.agent = get_agent()
    
    async def generate_lesson(self, request: LessonGenerateRequest) -> Dict[str, Any]:
        """
        Generate a lesson plan using the AI agent.
        This is where the agentic system does its work.
        """
        try:
            logger.info(f"Generating lesson for topic: {request.topic}")
            
            # Use the agent to generate the lesson
            result = self.agent.generate_lesson(request)
            
            if not result["success"]:
                raise Exception(result.get("error", "Unknown error in lesson generation"))
            
            lesson_plan = result["lesson_plan"]
            
            # Evaluate the lesson plan
            evaluator = get_evaluator()
            search_results = self._extract_search_results(result.get("intermediate_steps", []))
            agent_steps = result.get("agent_steps", [])
            
            logger.info(f"Evaluating lesson with {len(search_results)} search results and {len(agent_steps)} agent steps")
            
            evaluation_metrics = evaluator.evaluate_lesson(
                lesson_plan=lesson_plan.dict(),
                search_results=search_results,
                agent_steps=agent_steps
            )
            
            # Add metrics to lesson metadata
            if not isinstance(lesson_plan.metadata, dict):
                lesson_plan.metadata = {}
            lesson_plan.metadata["evaluation_metrics"] = evaluation_metrics
            
            # Save lesson plan to disk
            self._save_lesson(lesson_plan)
            
            logger.info(f"Successfully generated lesson {lesson_plan.lesson_id} with quality score: {evaluation_metrics.get('quality_score', 0):.2f}")
            
            return {
                "lesson_id": lesson_plan.lesson_id,
                "status": "completed",
                "message": "Lesson plan generated successfully",
                "lesson_plan": lesson_plan,
                "evaluation_metrics": evaluation_metrics
            }
            
        except Exception as e:
            logger.error(f"Error generating lesson: {e}", exc_info=True)
            return {
                "lesson_id": str(uuid.uuid4()),
                "status": "failed",
                "message": f"Failed to generate lesson: {str(e)}",
                "lesson_plan": None,
                "evaluation_metrics": None
            }
    
    def _extract_search_results(self, intermediate_steps: list) -> list:
        """Extract search results from agent's intermediate steps"""
        search_results = []
        try:
            for step in intermediate_steps:
                if isinstance(step, tuple) and len(step) >= 2:
                    action, observation = step[0], step[1]
                    # Check if this was a search tool call
                    if hasattr(action, 'tool') and 'search' in action.tool.lower():
                        search_results.append(str(observation))
            logger.info(f"Extracted {len(search_results)} search results from intermediate steps")
        except Exception as e:
            logger.error(f"Error extracting search results: {e}")
        
        return search_results
    
    def get_lesson(self, lesson_id: str) -> Optional[LessonPlan]:
        """Retrieve a lesson plan by ID"""
        try:
            lesson_file = Path(settings.LESSONS_DIR) / f"{lesson_id}.json"
            
            if not lesson_file.exists():
                logger.warning(f"Lesson {lesson_id} not found")
                return None
            
            with open(lesson_file, "r") as f:
                lesson_data = json.load(f)
            
            lesson_plan = LessonPlan(**lesson_data)
            logger.info(f"Retrieved lesson {lesson_id}")
            
            return lesson_plan
            
        except Exception as e:
            logger.error(f"Error retrieving lesson {lesson_id}: {e}")
            return None
    
    def _save_lesson(self, lesson_plan: LessonPlan):
        """Save lesson plan to disk"""
        try:
            lesson_file = Path(settings.LESSONS_DIR) / f"{lesson_plan.lesson_id}.json"
            
            with open(lesson_file, "w") as f:
                json.dump(lesson_plan.dict(), f, indent=2, default=str)
            
            logger.info(f"Saved lesson {lesson_plan.lesson_id} to {lesson_file}")
            
        except Exception as e:
            logger.error(f"Error saving lesson {lesson_plan.lesson_id}: {e}")
            raise
    
    def list_lessons(self, limit: int = 10) -> list[Dict[str, Any]]:
        """List all saved lessons"""
        try:
            lessons_dir = Path(settings.LESSONS_DIR)
            lesson_files = sorted(
                lessons_dir.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:limit]
            
            lessons = []
            for lesson_file in lesson_files:
                try:
                    with open(lesson_file, "r") as f:
                        lesson_data = json.load(f)
                    
                    lessons.append({
                        "lesson_id": lesson_data["lesson_id"],
                        "topic": lesson_data["topic"],
                        "difficulty_level": lesson_data["difficulty_level"],
                        "created_at": lesson_data["created_at"],
                        "quality_score": lesson_data.get("metadata", {}).get("evaluation_metrics", {}).get("quality_score", "N/A")
                    })
                except Exception as e:
                    logger.warning(f"Failed to read lesson file {lesson_file}: {e}")
                    continue
            
            return lessons
            
        except Exception as e:
            logger.error(f"Error listing lessons: {e}")
            return []
    
    def save_feedback(self, lesson_id: str, rating: int, feedback_text: str, helpful: bool) -> Dict[str, Any]:
        """Save user feedback for a lesson"""
        try:
            feedback_id = str(uuid.uuid4())
            feedback_dir = Path(settings.LESSONS_DIR) / "feedback"
            feedback_dir.mkdir(exist_ok=True)
            feedback_file = feedback_dir / f"{feedback_id}.json"
            
            from datetime import datetime
            feedback_data = {
                "feedback_id": feedback_id,
                "lesson_id": lesson_id,
                "rating": rating,
                "feedback_text": feedback_text,
                "helpful": helpful,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(feedback_file, "w") as f:
                json.dump(feedback_data, f, indent=2)
            
            logger.info(f"Saved feedback {feedback_id} for lesson {lesson_id}")
            
            return {
                "message": "Feedback saved successfully",
                "feedback_id": feedback_id
            }
            
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            raise

# Global service instance
_lesson_service = None

def get_lesson_service() -> LessonService:
    """Get or create lesson service instance"""
    global _lesson_service
    if _lesson_service is None:
        _lesson_service = LessonService()
    return _lesson_service