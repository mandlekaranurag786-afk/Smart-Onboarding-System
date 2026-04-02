"""
Document Processor - Extracts and chunks PDF documents
"""
import logging
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process PDF documents for RAG"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return ""
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for period, question mark, or exclamation
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def process_document(self, pdf_path: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Process a PDF document into chunks with metadata
        
        Returns:
            List of dicts with 'text' and 'metadata'
        """
        logger.info(f"Processing document: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"No text extracted from {pdf_path}")
            return []
        
        # Chunk text
        chunks = self.chunk_text(text)
        logger.info(f"Created {len(chunks)} chunks from {pdf_path}")
        
        # Add metadata to each chunk
        file_name = Path(pdf_path).name
        policy_name = file_name.replace('.pdf', '').replace('_', ' ')
        
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "source": file_name,
                "policy_name": policy_name,
                "chunk_index": i,
                "total_chunks": len(chunks),
                **(metadata or {})
            }
            processed_chunks.append({
                "text": chunk,
                "metadata": chunk_metadata
            })
        
        return processed_chunks
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Process all PDF files in a directory"""
        directory = Path(directory_path)
        all_chunks = []
        
        pdf_files = list(directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")
        
        for pdf_file in pdf_files:
            chunks = self.process_document(str(pdf_file))
            all_chunks.extend(chunks)
        
        logger.info(f"Total chunks processed: {len(all_chunks)}")
        return all_chunks
