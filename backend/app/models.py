from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class LearnerProfile(BaseModel):
    age_group: Optional[str] = Field(None, description="e.g., '10-12', '13-15', 'adult'")
    difficulty_level: DifficultyLevel = Field(DifficultyLevel.INTERMEDIATE)
    prior_knowledge: Optional[str] = Field(None, description="Brief description of learner's background")
    learning_objectives: Optional[List[str]] = Field(None, description="Specific goals")

class LessonGenerateRequest(BaseModel):
    topic: str = Field(..., description="Main topic for the lesson")
    duration_minutes: int = Field(60, ge=15, le=180, description="Lesson duration in minutes")
    learner_profile: LearnerProfile = Field(default_factory=LearnerProfile)
    additional_context: Optional[str] = Field(None, description="Any additional requirements")

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    num_chunks: int
    num_pages: int
    status: str
    message: str

class LessonPlanSection(BaseModel):
    title: str
    content: str
    duration_minutes: Optional[int] = None

class LessonPlan(BaseModel):
    lesson_id: str
    topic: str
    difficulty_level: DifficultyLevel
    duration_minutes: int
    objectives: List[str]
    prerequisites: List[str]
    content_outline: List[LessonPlanSection]
    activities: List[str]
    assessments: List[str]
    resources: List[str]
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LessonGenerateResponse(BaseModel):
    lesson_id: str
    status: str
    message: str
    lesson_plan: Optional[LessonPlan] = None

class AgentStatus(BaseModel):
    agent_id: str
    status: str
    current_task: Optional[str] = None
    steps_completed: List[str]
    last_updated: datetime

class AgentFeedback(BaseModel):
    lesson_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
    helpful: bool = True

class AgentFeedbackResponse(BaseModel):
    message: str
    feedback_id: str