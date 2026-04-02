"""
Test RAG System - Comprehensive testing of policy query functionality
"""
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.rag.rag_service import get_rag_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_rag_system():
    """Test RAG system with various queries"""
    
    print("=" * 80)
    print("RAG SYSTEM TEST")
    print("=" * 80)
    
    # Initialize RAG service
    rag_service = get_rag_service(documents_path="./documents")
    
    # Get stats
    stats = rag_service.get_stats()
    print(f"\n📊 RAG Statistics:")
    print(f"   Collection: {stats['collection_name']}")
    print(f"   Documents indexed: {stats['document_count']}")
    print(f"   Storage: {stats['persist_directory']}")
    
    if stats['document_count'] == 0:
        print("\n⚠️  No documents indexed. Run 'python init_rag.py' first.")
        return
    
    # Test queries
    test_queries = [
        "What is the information security policy?",
        "What are the password requirements?",
        "Can I work remotely?",
        "What is the BYOD policy?",
        "How should I handle security incidents?",
        "What are the email communication guidelines?",
        "What is the social media policy?",
        "How do I manage software licenses?"
    ]
    
    print("\n" + "=" * 80)
    print("TESTING QUERIES")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─' * 80}")
        print(f"Query {i}: {query}")
        print(f"{'─' * 80}")
        
        result = rag_service.query(
            question=query,
            top_k=3,
            include_sources=True
        )
        
        print(f"\n📝 Answer:")
        print(f"   {result['answer'][:300]}...")
        
        print(f"\n📊 Metadata:")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Retrieved chunks: {result['retrieved_chunks']}")
        
        print(f"\n📚 Sources:")
        for j, source in enumerate(result['sources'][:2], 1):
            print(f"   {j}. {source['policy_name']} (similarity: {source['similarity_score']:.3f})")
    
    print("\n" + "=" * 80)
    print("✅ RAG SYSTEM TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_rag_system()
