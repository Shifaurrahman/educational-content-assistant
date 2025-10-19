from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage
from app.agent.tools import create_agent_tools
from app.config import get_settings
from app.utils.logger import logger
from app.models import LessonGenerateRequest, LessonPlan, LessonPlanSection, DifficultyLevel
from typing import Dict, Any, List
import json
from datetime import datetime
import uuid

settings = get_settings()

class EducationalAgent:
    """
    Main agent that orchestrates lesson plan generation with multi-step reasoning.
    
    Agent workflow:
    1. Analyze the request (topic, difficulty, duration)
    2. Search knowledge base for relevant content
    3. Generate lesson structure
    4. Adjust difficulty if needed
    5. Synthesize final lesson plan
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.AGENT_TEMPERATURE
        )
        self.tools = create_agent_tools()
        self.agent_executor = self._create_agent()
        self.agent_id = str(uuid.uuid4())
        self.steps_completed = []
        
    def _create_agent(self) -> AgentExecutor:
        """Create the agent with tools and prompt template"""
        
        # System prompt that defines agent behavior
        system_prompt = """You are an expert educational content designer and AI agent specialized in creating personalized lesson plans.

Your capabilities:
1. Search educational knowledge bases for relevant content
2. Generate structured, comprehensive lesson plans
3. Adjust content difficulty based on learner profiles

Your task is to create high-quality, pedagogically sound lesson plans by:
- Analyzing the user's request carefully
- Searching the knowledge base for relevant educational content
- Generating a well-structured lesson plan with clear objectives
- Adjusting the difficulty level to match the learner profile
- Providing practical activities and assessments

**CRITICAL: Always cite your sources and reference the educational materials.**
- When using information from the knowledge base, acknowledge it (e.g., "According to the source material...")
- In the resources section, explicitly mention "Course materials from uploaded documents"
- Reference specific concepts that came from the knowledge base

Always think step-by-step and use your tools strategically. 

When creating lesson plans, ensure they include:
- Clear learning objectives (what students will be able to do)
- Prerequisites (what students should know beforehand)
- Content outline (structured sections with timing)
- Engaging activities (hands-on, interactive)
- Assessment methods (how to measure learning)
- Resources and materials needed

Be thorough, pedagogically sound, and learner-focused."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=settings.AGENT_MAX_ITERATIONS,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        
        return agent_executor
    
    def _format_request_for_agent(self, request: LessonGenerateRequest) -> str:
        """Format the lesson request into a clear prompt for the agent"""
        
        prompt = f"""Please create a comprehensive lesson plan with the following specifications:

Topic: {request.topic}
Duration: {request.duration_minutes} minutes
Difficulty Level: {request.learner_profile.difficulty_level.value}
Age Group: {request.learner_profile.age_group or 'Not specified'}
Prior Knowledge: {request.learner_profile.prior_knowledge or 'Not specified'}

"""
        if request.learner_profile.learning_objectives:
            prompt += f"\nSpecific Learning Objectives:\n"
            for obj in request.learner_profile.learning_objectives:
                prompt += f"- {obj}\n"
        
        if request.additional_context:
            prompt += f"\nAdditional Context: {request.additional_context}\n"
        
        prompt += """
Please follow these steps:
1. Search the knowledge base for relevant content about this topic
2. Generate a structured lesson plan template
3. If needed, adjust the content difficulty to match the learner profile
4. Create a comprehensive lesson plan with all required sections

Provide the final lesson plan in a clear, structured format."""
        
        return prompt
    
    def generate_lesson(self, request: LessonGenerateRequest) -> Dict[str, Any]:
        """
        Main method to generate a lesson plan using the agent.
        Demonstrates multi-step reasoning.
        """
        try:
            logger.info(f"Agent {self.agent_id} starting lesson generation for topic: {request.topic}")
            self.steps_completed = []
            
            # Step 1: Format request
            self.steps_completed.append("Analyzed request and formatted prompt")
            agent_prompt = self._format_request_for_agent(request)
            
            # Step 2: Execute agent
            logger.info("Agent executing with tools...")
            result = self.agent_executor.invoke({
                "input": agent_prompt
            })
            
            # Log intermediate steps
            if "intermediate_steps" in result:
                for step in result["intermediate_steps"]:
                    action, observation = step
                    self.steps_completed.append(f"Used tool: {action.tool}")
                    logger.info(f"Tool used: {action.tool}")
                    logger.debug(f"Tool input: {action.tool_input}")
            
            # Step 3: Parse agent output
            self.steps_completed.append("Generated lesson plan content")
            agent_output = result["output"]
            
            # Step 4: Structure the lesson plan
            lesson_plan = self._structure_lesson_plan(
                agent_output=agent_output,
                request=request
            )
            
            self.steps_completed.append("Structured and finalized lesson plan")
            logger.info(f"Agent {self.agent_id} completed lesson generation")
            
            return {
                "success": True,
                "lesson_plan": lesson_plan,
                "agent_steps": self.steps_completed,
                "intermediate_steps": result.get("intermediate_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Error in agent lesson generation: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "agent_steps": self.steps_completed
            }
    
    def _structure_lesson_plan(
        self, 
        agent_output: str, 
        request: LessonGenerateRequest
    ) -> LessonPlan:
        """
        Structure the agent's output into a proper LessonPlan object.
        Uses LLM to parse and structure the output.
        """
        
        structure_prompt = f"""Given the following lesson plan content, extract and structure it into a JSON format.

Lesson Content:
{agent_output}

Original Request:
- Topic: {request.topic}
- Duration: {request.duration_minutes} minutes
- Difficulty: {request.learner_profile.difficulty_level.value}

IMPORTANT: Ensure the lesson plan references the source materials appropriately.
- In content sections, use phrases like "Based on the course material..." or "According to the documentation..."
- In the resources section, include "Educational documents and course materials"
- Make it clear that content is derived from uploaded educational resources

Please extract and format as JSON with these exact fields:
{{
  "objectives": ["list of learning objectives"],
  "prerequisites": ["list of prerequisite knowledge/skills"],
  "content_outline": [
    {{"title": "section name", "content": "section description (reference sources where applicable)", "duration_minutes": 15}}
  ],
  "activities": ["list of activities"],
  "assessments": ["list of assessment methods"],
  "resources": ["list of resources and materials - MUST include reference to uploaded course materials"]
}}

Ensure all lists have at least 3 items. Be specific and detailed.
Return ONLY the JSON, no other text."""

        try:
            response = self.llm.invoke([HumanMessage(content=structure_prompt)])
            
            # Parse JSON from response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            structured_data = json.loads(content)
            
            # Create LessonPlan object
            lesson_plan = LessonPlan(
                lesson_id=str(uuid.uuid4()),
                topic=request.topic,
                difficulty_level=request.learner_profile.difficulty_level,
                duration_minutes=request.duration_minutes,
                objectives=structured_data.get("objectives", []),
                prerequisites=structured_data.get("prerequisites", []),
                content_outline=[
                    LessonPlanSection(**section) 
                    for section in structured_data.get("content_outline", [])
                ],
                activities=structured_data.get("activities", []),
                assessments=structured_data.get("assessments", []),
                resources=structured_data.get("resources", []),
                created_at=datetime.now(),
                metadata={
                    "agent_id": self.agent_id,
                    "learner_profile": request.learner_profile.dict(),
                    "additional_context": request.additional_context
                }
            )
            
            return lesson_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse structured output: {e}")
            # Fallback: create a basic lesson plan
            return self._create_fallback_lesson_plan(agent_output, request)
    
    def _create_fallback_lesson_plan(
        self, 
        content: str, 
        request: LessonGenerateRequest
    ) -> LessonPlan:
        """Create a basic lesson plan if structuring fails"""
        
        return LessonPlan(
            lesson_id=str(uuid.uuid4()),
            topic=request.topic,
            difficulty_level=request.learner_profile.difficulty_level,
            duration_minutes=request.duration_minutes,
            objectives=["Complete the lesson content"],
            prerequisites=["Basic understanding of the topic"],
            content_outline=[
                LessonPlanSection(
                    title="Lesson Content",
                    content=content,
                    duration_minutes=request.duration_minutes
                )
            ],
            activities=["Review the content", "Practice exercises"],
            assessments=["Knowledge check", "Practical application"],
            resources=["Course materials"],
            created_at=datetime.now(),
            metadata={"fallback": True}
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "status": "ready",
            "steps_completed": self.steps_completed,
            "last_updated": datetime.now().isoformat()
        }

# Global agent instance (in production, use proper state management)
_agent_instance = None

def get_agent() -> EducationalAgent:
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = EducationalAgent()
    return _agent_instance