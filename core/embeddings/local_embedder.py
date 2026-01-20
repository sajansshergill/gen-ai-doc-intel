from typing import List, Optional
import numpy as np

class LocalEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        # Lazy import to avoid segfault on module import
        from sentence_transformers import SentenceTransformer
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
    
    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model
        
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        # returns shape (n, dim)
        # Use smaller batches and normalize to save memory
        vecs = self.model.encode(
            texts, 
            normalize_embeddings=True,  # Normalize to save memory
            show_progress_bar=False,
            batch_size=min(8, len(texts))  # Smaller batches for free tier
        )
        return np.array(vecs, dtype="float32")
    
    def embed_query(self, text: str) -> np.ndarray:
        vec = self.model.encode(
            [text], 
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return np.array(vec[0], dtype="float32")