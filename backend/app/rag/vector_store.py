"""
Vector Store - ChromaDB integration for semantic search
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector embeddings and similarity search using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "company_policies"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embedding model
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Company policy documents"}
        )
        
        logger.info(f"Vector store initialized: {collection_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Add documents to vector store
        
        Args:
            documents: List of dicts with 'text' and 'metadata'
            
        Returns:
            Number of documents added
        """
        if not documents:
            logger.warning("No documents to add")
            return 0
        
        logger.info(f"Adding {len(documents)} documents to vector store...")
        
        # Prepare data
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        ids = [f"{doc['metadata']['source']}_{doc['metadata']['chunk_index']}" for doc in documents]
        
        # Generate embeddings
        embeddings = self.embed_texts(texts)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully added {len(documents)} documents")
        return len(documents)
    
    def search(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of results with text, metadata, and similarity score
        """
        logger.info(f"Searching for: {query}")
        
        # Generate query embedding
        query_embedding = self.embed_text(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity_score": 1 - results['distances'][0][i],  # Convert distance to similarity
                    "id": results['ids'][0][i]
                })
        
        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": self.persist_directory
        }
    
    def clear_collection(self):
        """Clear all documents from collection"""
        logger.warning(f"Clearing collection: {self.collection_name}")
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Company policy documents"}
        )
        logger.info("Collection cleared")
    
    def delete_by_source(self, source: str):
        """Delete all documents from a specific source"""
        logger.info(f"Deleting documents from source: {source}")
        self.collection.delete(where={"source": source})
