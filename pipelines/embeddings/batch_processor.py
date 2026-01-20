"""
Batch embedding processing pipeline.
Processes Chunks → EmbeddingRecords asynchronously.
"""
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime
import numpy as np

from core.models.artifacts import Chunk, EmbeddingRecord

if TYPE_CHECKING:
    from core.embeddings.local_embedder import LocalEmbedder


class BatchEmbeddingProcessor:
    """Process chunks in batches to create embeddings."""
    
    def __init__(self, batch_size: int = 8):  # Smaller default for free tier
        self.batch_size = batch_size
        self.embedder: Optional[Any] = None
    
    def _get_embedder(self):
        """Lazy initialization of embedder."""
        if self.embedder is None:
            from core.embeddings.local_embedder import LocalEmbedder
            self.embedder = LocalEmbedder()
        return self.embedder
    
    def process_chunks(
        self,
        chunks: List[Chunk],
        doc_id: str,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> List[EmbeddingRecord]:
        """
        Process chunks in batches to create embeddings.
        
        Args:
            chunks: List of Chunk artifacts
            doc_id: Document ID
            model_name: Embedding model name
        
        Returns:
            List of EmbeddingRecord artifacts
        """
        embedder = self._get_embedder()
        embeddings = []
        
        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            texts = [c.text for c in batch]
            
            # Generate embeddings
            vectors = embedder.embed_texts(texts)
            
            # Create EmbeddingRecord artifacts
            for j, chunk in enumerate(batch):
                embedding_record = EmbeddingRecord(
                    chunk_id=chunk.chunk_id,
                    doc_id=doc_id,
                    embedding=vectors[j].tolist(),
                    model_name=model_name,
                    dim=vectors.shape[1],
                    created_at=datetime.now(),
                    metadata={
                        "page_number": chunk.page_number,
                        "char_count": chunk.char_count
                    }
                )
                embeddings.append(embedding_record)
        
        return embeddings
    
    def process_single(self, chunk: Chunk, doc_id: str) -> EmbeddingRecord:
        """Process a single chunk."""
        embedder = self._get_embedder()
        vector = embedder.embed_query(chunk.text)
        
        return EmbeddingRecord(
            chunk_id=chunk.chunk_id,
            doc_id=doc_id,
            embedding=vector.tolist(),
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            dim=len(vector),
            created_at=datetime.now(),
            metadata={
                "page_number": chunk.page_number,
                "char_count": chunk.char_count
            }
        )
