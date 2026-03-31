"""
RAG API Endpoints - Company policy queries
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.rag.rag_service import get_rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["RAG"])


class PolicyQueryRequest(BaseModel):
    """Request model for policy queries"""
    question: str = Field(..., description="Question about company policies")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of relevant chunks to retrieve")
    include_sources: bool = Field(default=True, description="Include source documents in response")


class PolicyQueryResponse(BaseModel):
    """Response model for policy queries"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: str
    retrieved_chunks: int


class IndexRequest(BaseModel):
    """Request model for indexing documents"""
    force_reindex: bool = Field(default=False, description="Force reindexing even if documents exist")


class IndexResponse(BaseModel):
    """Response model for indexing"""
    status: str
    document_count: int
    message: str


class StatsResponse(BaseModel):
    """Response model for RAG statistics"""
    collection_name: str
    document_count: int
    persist_directory: str


@router.post("/query", response_model=PolicyQueryResponse)
async def query_policies(request: PolicyQueryRequest):
    """
    Query company policies using RAG
    
    This endpoint uses semantic search to find relevant policy information
    and generates a natural language answer.
    """
    try:
        rag_service = get_rag_service(documents_path="./documents")
        
        result = rag_service.query(
            question=request.question,
            top_k=request.top_k,
            include_sources=request.include_sources
        )
        
        return PolicyQueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Policy query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/index", response_model=IndexResponse)
async def index_documents(request: IndexRequest):
    """
    Index company policy documents
    
    This endpoint processes all PDF files in the documents directory
    and creates vector embeddings for semantic search.
    """
    try:
        rag_service = get_rag_service(documents_path="./documents")
        
        result = rag_service.index_documents(force_reindex=request.force_reindex)
        
        return IndexResponse(**result)
        
    except Exception as e:
        logger.error(f"Document indexing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_rag_stats():
    """
    Get RAG system statistics
    
    Returns information about indexed documents and vector store status.
    """
    try:
        rag_service = get_rag_service(documents_path="./documents")
        
        stats = rag_service.get_stats()
        
        return StatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@router.get("/health")
async def rag_health_check():
    """
    Health check for RAG system
    """
    try:
        rag_service = get_rag_service(documents_path="./documents")
        stats = rag_service.get_stats()
        
        return {
            "status": "healthy",
            "documents_indexed": stats['document_count'],
            "ready": stats['document_count'] > 0
        }
        
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
