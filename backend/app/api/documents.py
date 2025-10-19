from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.models import DocumentUploadResponse
from app.services.document_service import get_document_service
from app.utils.logger import logger
from typing import Dict, Any

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF file to upload")
):
    """
    Upload and process an educational document.
    
    The document will be:
    1. Validated (PDF format)
    2. Split into chunks
    3. Embedded using OpenAI embeddings
    4. Stored in FAISS vector database
    
    This enables the agent to search and retrieve relevant content.
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Validate file size (max 50MB)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 50MB limit"
        )
    
    try:
        logger.info(f"Received upload request for file: {file.filename}")
        
        # Process document
        document_service = get_document_service()
        result = await document_service.process_document(content, file.filename)
        
        return DocumentUploadResponse(**result)
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_index_stats():
    """
    Get statistics about the current knowledge base.
    
    Returns information about:
    - Number of indexed documents
    - Total vectors in the database
    - Index size
    """
    try:
        document_service = get_document_service()
        stats = document_service.get_index_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting index stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve stats: {str(e)}"
        )