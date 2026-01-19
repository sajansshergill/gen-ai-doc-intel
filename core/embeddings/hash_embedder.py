from typing import List
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer


class HashEmbedder:
    """
    Offline, no-download embedder using HashingVectorizer.
    Produces fixed-dim vectors suitable for FAISS.
    """
    def __init__(self, dim: int = 1024):
        self.dim = dim
        self.vec = HashingVectorizer(
            n_features=dim,
            alternate_sign=False,
            norm=None,          # we'll normalize ourselves
            lowercase=True,
            stop_words=None
        )

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        X = self.vec.transform(texts)            # sparse (n, dim)
        return X.toarray().astype("float32")

    def embed_query(self, text: str) -> np.ndarray:
        X = self.vec.transform([text])
        return X.toarray()[0].astype("float32")
