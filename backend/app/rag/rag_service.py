"""
RAG Service - Main interface for retrieval-augmented generation
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.rag.document_processor import DocumentProcessor
from app.rag.vector_store import VectorStore
from app.llm_client import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG service for company policy queries"""
    
    def __init__(self, documents_path: str = "./documents", persist_directory: str = "./chroma_db"):
        self.documents_path = documents_path
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore(persist_directory=persist_directory)
        self.llm = get_llm(temperature=0.2)
        
        logger.info("RAG Service initialized")
    
    def index_documents(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Index all documents in the documents directory
        
        Args:
            force_reindex: If True, clear existing index and reindex
            
        Returns:
            Indexing statistics
        """
        logger.info(f"Starting document indexing from: {self.documents_path}")
        
        # Check if already indexed
        stats = self.vector_store.get_collection_stats()
        if stats['document_count'] > 0 and not force_reindex:
            logger.info(f"Documents already indexed: {stats['document_count']} chunks")
            return {
                "status": "already_indexed",
                "document_count": stats['document_count'],
                "message": "Documents already indexed. Use force_reindex=True to reindex."
            }
        
        # Clear if force reindex
        if force_reindex:
            self.vector_store.clear_collection()
        
        # Process documents
        chunks = self.document_processor.process_directory(self.documents_path)
        
        if not chunks:
            logger.warning("No documents found to index")
            return {
                "status": "no_documents",
                "document_count": 0,
                "message": "No PDF documents found in directory"
            }
        
        # Add to vector store
        added_count = self.vector_store.add_documents(chunks)
        
        logger.info(f"Indexing complete: {added_count} chunks indexed")
        
        return {
            "status": "success",
            "document_count": added_count,
            "message": f"Successfully indexed {added_count} document chunks"
        }
    
    def query(self, question: str, top_k: int = 5, include_sources: bool = True) -> Dict[str, Any]:
        """
        Query the RAG system with a question
        
        Args:
            question: User's question
            top_k: Number of relevant chunks to retrieve
            include_sources: Whether to include source documents in response
            
        Returns:
            Dict with answer, sources, and metadata
        """
        logger.info(f"RAG Query: {question}")
        
        # Check if documents are indexed
        stats = self.vector_store.get_collection_stats()
        if stats['document_count'] == 0:
            return {
                "answer": "I don't have any company policy documents indexed yet. Please ask an administrator to index the documents first.",
                "sources": [],
                "confidence": "low",
                "error": "no_documents_indexed"
            }
        
        # Retrieve relevant documents
        search_results = self.vector_store.search(question, top_k=top_k)
        
        if not search_results:
            return {
                "answer": "I couldn't find any relevant information in the company policies to answer your question.",
                "sources": [],
                "confidence": "low"
            }
        
        # Build context from retrieved documents
        context = self._build_context(search_results)
        
        # Generate answer using LLM
        answer = self._generate_answer(question, context)
        
        # Prepare sources
        sources = []
        if include_sources:
            sources = self._format_sources(search_results)
        
        # Calculate confidence based on similarity scores
        avg_similarity = sum(r['similarity_score'] for r in search_results) / len(search_results)
        confidence = "high" if avg_similarity > 0.7 else "medium" if avg_similarity > 0.5 else "low"
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "retrieved_chunks": len(search_results)
        }
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context string from search results"""
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            policy_name = result['metadata'].get('policy_name', 'Unknown Policy')
            text = result['text']
            context_parts.append(f"[Source {i}: {policy_name}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using LLM with retrieved context"""
        
        system_prompt = """You are a helpful AI assistant for KONVERGE.AI company policies.

Your role:
- Answer questions about company policies accurately and clearly
- Use ONLY the information provided in the context
- If the context doesn't contain the answer, say so honestly
- Be concise but complete
- Cite specific policies when relevant
- Use a professional but friendly tone

Important:
- DO NOT make up information
- DO NOT provide information not in the context
- If unsure, acknowledge the limitation"""

        user_prompt = f"""Context from company policies:
{context}

Question: {question}

Please provide a clear, accurate answer based on the context above."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "I encountered an error while generating the answer. Please try again."
    
    def _format_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source information for response"""
        sources = []
        
        for result in search_results:
            sources.append({
                "policy_name": result['metadata'].get('policy_name', 'Unknown'),
                "source_file": result['metadata'].get('source', 'Unknown'),
                "chunk_index": result['metadata'].get('chunk_index', 0),
                "similarity_score": round(result['similarity_score'], 3),
                "excerpt": result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
            })
        
        return sources
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return self.vector_store.get_collection_stats()


# Singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service(documents_path: str = "./documents") -> RAGService:
    """Get or create RAG service singleton"""
    global _rag_service
    
    if _rag_service is None:
        _rag_service = RAGService(documents_path=documents_path)
    
    return _rag_service
