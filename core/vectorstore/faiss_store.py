import os
import json
from typing import List, Dict, Any, Optional

import numpy as np

try:
    import faiss
except ImportError as e:
    raise RuntimeError("faiss is not installed. Run: pip install faiss-cpu") from e

class FaissStore:
    """
    Simple local FAISS index with JSON metadata persistence.
    Stores vectors + metadata aligned by row index.
    """
    
    def __init__(self, index_dir: str, dim: int):
        self.index_dir = index_dir
        self.dim = dim
        os.makedirs(index_dir, exist_ok=True)
        
        self.index_path = os.path.join(index_dir, "index.faiss")
        self.meta_path = os.path.join(index_dir, "meta.json")
        
        self.index = None
        self.meta: List[Dict[str, Any]] = []
        
        self.load_or_init()
        
    def load_or_init(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.meta = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(self.dim) # cosine similarity after normalization
            self.meta = []
            
    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)
            
    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
        return vectors / norms
    
    def add(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]]):
        """
        vectors shape: (n, dim)
        metadatas length: n
        """
        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            raise ValueError(f"Expected vectors of shape (n, {self.dim}), got {vectors.shape}")
        
        if len(metadatas) != vectors.shape[0]:
            raise ValueError("metadatas length must match number of vectors")
        
        vectors = vectors.astype("float32")
        vectors = self._normalize(vectors)
        
        self.index.add(vectors)
        self.meta.extend(metadatas)
        self.save()
        
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        query_vector shape: (dim, ) or (1, dim)
        returns list of meta dicts with score
        """
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
            
        query_vector = query_vector.astype("float32")
        query_vector = self._normalize(query_vector)
        
        scores, idxs = self.index.search(query_vector, top_k)
        scores = scores[0].tolist()
        idxs = idxs[0].tolist()
        
        results = []
        for score, idx in zip(scores, idxs):
            if idx == -1:
                continue
            m = dict(self.meta[idx])
            m["score"] = float(score)
            results.append(m)
            
        return results