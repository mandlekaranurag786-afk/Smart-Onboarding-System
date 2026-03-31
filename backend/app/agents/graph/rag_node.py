"""
RAG Node for LangGraph - Handles policy queries in the chatbot workflow
"""
from typing import Dict, Any
import logging
from datetime import datetime

from app.agents.graph.state import OnboardingState
from app.rag.rag_service import get_rag_service

logger = logging.getLogger(__name__)


def policy_query_node(state: OnboardingState) -> Dict[str, Any]:
    """
    RAG Node: Policy Query Handler
    
    This node handles questions about company policies using RAG.
    Can be integrated into the chatbot workflow.
    """
    logger.info(f"[RAG Node] Processing policy query")
    
    # Get query from state (you can customize this based on your state structure)
    query = state.get('policy_query', '')
    
    if not query:
        return {
            "policy_answer": "No policy query provided",
            "policy_sources": [],
            "agent_results": [{
                "agent": "PolicyRAG",
                "status": "skipped",
                "reason": "No query provided",
                "timestamp": datetime.now().isoformat()
            }]
        }
    
    try:
        # Get RAG service
        rag_service = get_rag_service(documents_path="./documents")
        
        # Query policies
        result = rag_service.query(
            question=query,
            top_k=5,
            include_sources=True
        )
        
        logger.info(f"Policy query successful: {result['confidence']} confidence")
        
        return {
            "policy_answer": result['answer'],
            "policy_sources": result['sources'],
            "policy_confidence": result['confidence'],
            "agent_results": [{
                "agent": "PolicyRAG",
                "status": "success",
                "confidence": result['confidence'],
                "retrieved_chunks": result['retrieved_chunks'],
                "timestamp": datetime.now().isoformat()
            }]
        }
        
    except Exception as e:
        logger.error(f"Policy query failed: {e}")
        return {
            "policy_answer": "I encountered an error while searching company policies.",
            "policy_sources": [],
            "errors": [f"PolicyRAG: {str(e)}"],
            "agent_results": [{
                "agent": "PolicyRAG",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }]
        }
