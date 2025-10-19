from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.config import get_settings
from app.api import documents, lessons, agent_status
from app.utils.logger import logger
import time

# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    # Educational Content Assistant API
    
    An AI-powered system that generates personalized lesson plans from educational documents.
    
    ## Features
    
    - **Document Processing**: Upload educational PDFs and build a searchable knowledge base
    - **AI Agent**: Multi-step reasoning agent that creates comprehensive lesson plans
    - **Personalization**: Adjusts content difficulty based on learner profiles
    - **Tool Usage**: Agent uses specialized tools for search, generation, and adjustment
    
    ## Workflow
    
    1. Upload educational documents via `/api/v1/documents/upload`
    2. Generate lesson plans via `/api/v1/lessons/generate`
    3. Retrieve lessons via `/api/v1/lessons/{lesson_id}`
    4. Monitor agent via `/api/v1/agent/status`
    5. Provide feedback via `/api/v1/agent/feedback`
    
    ## Agent Architecture
    
    The agent demonstrates multi-step reasoning:
    - Analyzes the request
    - Searches knowledge base for relevant content
    - Generates structured lesson plan
    - Adjusts difficulty level
    - Synthesizes final output
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"Status: {response.status_code} Time: {process_time:.3f}s"
    )
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc)
        }
    )

# Include routers
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(lessons.router, prefix=settings.API_V1_PREFIX)
app.include_router(agent_status.router, prefix=settings.API_V1_PREFIX)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Educational Content Assistant API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info("=" * 50)
    logger.info(f"API Documentation: http://localhost:8000/docs")
    logger.info(f"Agent Model: {settings.OPENAI_MODEL}")
    logger.info(f"Embedding Model: {settings.OPENAI_EMBEDDING_MODEL}")
    logger.info("=" * 50)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Educational Content Assistant API")