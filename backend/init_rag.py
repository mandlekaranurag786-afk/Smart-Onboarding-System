"""
Initialize RAG System - Index company policy documents

Run this script to index all PDF documents in the documents folder.
"""
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.rag.rag_service import get_rag_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Initialize RAG system by indexing documents"""
    logger.info("=" * 60)
    logger.info("RAG System Initialization")
    logger.info("=" * 60)
    
    # Get RAG service
    documents_path = "./documents"
    logger.info(f"Documents path: {documents_path}")
    
    rag_service = get_rag_service(documents_path=documents_path)
    
    # Check if documents exist
    docs_dir = Path(documents_path)
    if not docs_dir.exists():
        logger.error(f"Documents directory not found: {documents_path}")
        return
    
    pdf_files = list(docs_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    if not pdf_files:
        logger.warning("No PDF files found to index")
        return
    
    # Index documents
    logger.info("Starting document indexing...")
    result = rag_service.index_documents(force_reindex=True)
    
    logger.info("=" * 60)
    logger.info(f"Status: {result['status']}")
    logger.info(f"Documents indexed: {result['document_count']}")
    logger.info(f"Message: {result['message']}")
    logger.info("=" * 60)
    
    # Test query
    logger.info("\nTesting RAG system with sample query...")
    test_query = "What is the information security policy?"
    
    query_result = rag_service.query(test_query, top_k=3, include_sources=False)
    
    logger.info(f"\nTest Query: {test_query}")
    logger.info(f"Answer: {query_result['answer'][:200]}...")
    logger.info(f"Confidence: {query_result['confidence']}")
    
    logger.info("\n✅ RAG system initialized successfully!")
    logger.info("You can now query company policies through the API")


if __name__ == "__main__":
    main()
