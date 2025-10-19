from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Educational Content Assistant"
    VERSION: str = "1.0.0"
    
    # OpenAI Settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # GROQ Settings (Optional)
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Vector Store Settings
    FAISS_INDEX_PATH: str = "data/faiss_index"
    
    # Document Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Lesson Storage
    LESSONS_DIR: str = "data/lessons"
    
    # Agent Settings
    AGENT_MAX_ITERATIONS: int = 10
    AGENT_TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env

@lru_cache()
def get_settings() -> Settings:
    return Settings()