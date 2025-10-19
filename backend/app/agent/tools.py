from langchain.tools import Tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import get_settings
from app.utils.logger import logger
from typing import List, Dict, Any
import json

settings = get_settings()

class KnowledgeBaseSearchTool:
    """Tool 1: Search relevant content from the knowledge base"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=settings.OPENAI_EMBEDDING_MODEL)
        
    def search(self, query: str, k: int = 5) -> str:
        """Search the knowledge base for relevant content"""
        try:
            logger.info(f"Searching knowledge base for: {query}")
            
            # Load FAISS index
            vectorstore = FAISS.load_local(
                settings.FAISS_INDEX_PATH,
                self.embeddings
            )
            
            # Retrieve relevant documents
            docs = vectorstore.similarity_search(query, k=k)
            
            # Format results
            results = []
            for i, doc in enumerate(docs, 1):
                results.append(f"Source {i}:\n{doc.page_content}\n")
            
            output = "\n---\n".join(results)
            logger.info(f"Found {len(docs)} relevant documents")
            
            return output if output else "No relevant content found in knowledge base."
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return f"Error searching knowledge base: {str(e)}"

class LessonPlanGeneratorTool:
    """Tool 2: Generate structured lesson plans"""
    
    def generate_structure(self, input_str: str) -> str:
        """Generate a structured lesson plan outline"""
        try:
            logger.info(f"Generating lesson structure")
            
            # Parse input if it's JSON
            if isinstance(input_str, str) and input_str.strip().startswith('{'):
                input_data = json.loads(input_str)
                topic = input_data.get('topic', 'Unknown')
                duration = int(input_data.get('duration', '60').replace(' minutes', ''))
                difficulty = input_data.get('difficulty', 'intermediate')
                context = input_data.get('context', '')
            else:
                # Fallback: treat as topic
                topic = input_str
                duration = 60
                difficulty = 'intermediate'
                context = ''
            
            # This returns a structured template that the agent can fill
            structure = {
                "topic": topic,
                "duration_minutes": duration,
                "difficulty_level": difficulty,
                "structure": {
                    "objectives": "List 3-5 clear learning objectives that students should achieve",
                    "prerequisites": "List prerequisite knowledge or skills needed",
                    "content_outline": [
                        {
                            "section": "Introduction",
                            "duration": f"{int(duration * 0.1)} minutes",
                            "description": "Hook and overview"
                        },
                        {
                            "section": "Main Content",
                            "duration": f"{int(duration * 0.5)} minutes",
                            "description": "Core concepts and explanations"
                        },
                        {
                            "section": "Activities",
                            "duration": f"{int(duration * 0.25)} minutes",
                            "description": "Hands-on practice"
                        },
                        {
                            "section": "Assessment & Conclusion",
                            "duration": f"{int(duration * 0.15)} minutes",
                            "description": "Review and evaluation"
                        }
                    ],
                    "activities": "Suggest 3-5 engaging activities appropriate for the difficulty level",
                    "assessments": "Suggest assessment methods to measure learning outcomes",
                    "resources": "List recommended resources and materials"
                },
                "context": context
            }
            
            return json.dumps(structure, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating lesson structure: {e}")
            return f"Error: {str(e)}"

class DifficultyAdjusterTool:
    """Tool 3: Adjust difficulty level based on learner profile"""
    
    def adjust_content(self, input_str: str) -> str:
        """Adjust content difficulty level"""
        try:
            logger.info(f"Adjusting content difficulty")
            
            # Parse input if it's JSON
            if isinstance(input_str, str) and input_str.strip().startswith('{'):
                input_data = json.loads(input_str)
                content = input_data.get('content', '')
                current_level = input_data.get('current_level', 'intermediate')
                target_level = input_data.get('target_level', 'intermediate')
                age_group = input_data.get('age_group', '')
            else:
                # Fallback
                content = input_str
                current_level = 'intermediate'
                target_level = 'intermediate'
                age_group = ''
            
            guidance = {
                "beginner": {
                    "vocabulary": "Use simple, everyday language. Avoid jargon.",
                    "concepts": "Break down into small, digestible pieces. Use concrete examples.",
                    "activities": "Provide step-by-step guidance. Include visual aids.",
                    "examples": "Use familiar, real-world examples."
                },
                "intermediate": {
                    "vocabulary": "Introduce technical terms with clear definitions.",
                    "concepts": "Build on foundational knowledge. Show connections.",
                    "activities": "Encourage some independent problem-solving.",
                    "examples": "Mix familiar and novel examples."
                },
                "advanced": {
                    "vocabulary": "Use technical terminology appropriately.",
                    "concepts": "Explore complex relationships and abstract ideas.",
                    "activities": "Encourage critical thinking and application.",
                    "examples": "Use challenging, real-world scenarios."
                }
            }
            
            adjustment_guide = {
                "original_content": content,
                "current_level": current_level,
                "target_level": target_level,
                "age_group": age_group,
                "adjustment_guidelines": guidance.get(target_level.lower(), guidance["intermediate"]),
                "instructions": f"Rewrite the content to match {target_level} level, considering the age group: {age_group}"
            }
            
            return json.dumps(adjustment_guide, indent=2)
            
        except Exception as e:
            logger.error(f"Error adjusting difficulty: {e}")
            return f"Error: {str(e)}"

# Define LangChain tools
def create_agent_tools() -> List[Tool]:
    """Create the list of tools for the agent"""
    
    # Lazy initialization - create instances only when needed
    kb_search = KnowledgeBaseSearchTool()
    lesson_generator = LessonPlanGeneratorTool()
    difficulty_adjuster = DifficultyAdjusterTool()
    
    tools = [
        Tool(
            name="search_knowledge_base",
            func=kb_search.search,
            description=(
                "Search the knowledge base for relevant educational content. "
                "Input should be a clear search query related to the lesson topic. "
                "Returns relevant excerpts from uploaded educational materials."
            )
        ),
        Tool(
            name="generate_lesson_structure",
            func=lesson_generator.generate_structure,
            description=(
                "Generate a structured lesson plan template. "
                "Input should be a JSON string with: topic, duration, difficulty, and optional context. "
                "Returns a structured template for creating comprehensive lesson plans."
            )
        ),
        Tool(
            name="adjust_difficulty",
            func=difficulty_adjuster.adjust_content,
            description=(
                "Adjust content difficulty level for different learners. "
                "Input should be a JSON string with: content, current_level, target_level, and age_group. "
                "Returns guidelines for adjusting content to the appropriate difficulty level."
            )
        )
    ]
    
    return tools