from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from app.config import get_settings
from app.utils.logger import logger
from pathlib import Path
import uuid
import shutil
from typing import Dict, Any

settings = get_settings()

class DocumentService:
    """Service for handling document upload and processing"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=settings.OPENAI_EMBEDDING_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        # Ensure directories exist
        Path(settings.FAISS_INDEX_PATH).mkdir(parents=True, exist_ok=True)
        Path("temp").mkdir(exist_ok=True)
    
    async def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process uploaded document and add to vector store.
        Supports streaming indexing.
        """
        document_id = str(uuid.uuid4())
        temp_file_path = f"temp/{document_id}_{filename}"
        
        try:
            logger.info(f"Processing document: {filename} (ID: {document_id})")
            
            # Save uploaded file temporarily
            with open(temp_file_path, "wb") as f:
                f.write(file_content)
            
            # Load PDF
            loader = PyPDFLoader(temp_file_path)
            pages = loader.load()
            
            logger.info(f"Loaded {len(pages)} pages from {filename}")
            
            # Split into chunks
            texts = self.text_splitter.split_documents(pages)
            
            logger.info(f"Split into {len(texts)} chunks")
            
            # Create or load existing vector store
            vectorstore = await self._get_or_create_vectorstore()
            
            # Add documents to vector store
            vectorstore.add_documents(texts)
            
            # Save updated vector store
            vectorstore.save_local(settings.FAISS_INDEX_PATH)
            
            logger.info(f"Successfully indexed document {document_id}")
            
            return {
                "document_id": document_id,
                "filename": filename,
                "num_chunks": len(texts),
                "num_pages": len(pages),
                "status": "completed",
                "message": f"Document '{filename}' successfully processed and indexed"
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}", exc_info=True)
            raise Exception(f"Failed to process document: {str(e)}")
            
        finally:
            # Clean up temporary file
            try:
                Path(temp_file_path).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")
    
    async def _get_or_create_vectorstore(self) -> FAISS:
        """Get existing vector store or create a new one"""
        index_path = Path(settings.FAISS_INDEX_PATH)
        
        # Check if index exists
        if (index_path / "index.faiss").exists():
            logger.info("Loading existing FAISS index")
            try:
                vectorstore = FAISS.load_local(
                    settings.FAISS_INDEX_PATH,
                    self.embeddings
                )
                return vectorstore
            except Exception as e:
                logger.warning(f"Failed to load existing index, creating new one: {e}")
        
        # Create new vector store with a dummy document
        logger.info("Creating new FAISS index")
        from langchain.schema import Document
        dummy_doc = Document(page_content="Initialization document", metadata={"init": True})
        vectorstore = FAISS.from_documents([dummy_doc], self.embeddings)
        
        return vectorstore
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current vector store"""
        try:
            index_path = Path(settings.FAISS_INDEX_PATH)
            
            if not (index_path / "index.faiss").exists():
                return {
                    "exists": False,
                    "message": "No documents indexed yet"
                }
            
            vectorstore = FAISS.load_local(
                settings.FAISS_INDEX_PATH,
                self.embeddings
            )
            
            return {
                "exists": True,
                "num_vectors": vectorstore.index.ntotal,
                "index_size_mb": round(
                    (index_path / "index.faiss").stat().st_size / (1024 * 1024), 
                    2
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {
                "exists": False,
                "error": str(e)
            }

# Global service instance
_document_service = None

def get_document_service() -> DocumentService:
    """Get or create document service instance"""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service