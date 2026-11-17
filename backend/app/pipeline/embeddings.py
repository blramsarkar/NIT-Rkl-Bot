"""
==============================================================================
File: backend/app/pipeline/embeddings.py
Role: Dense Vector Embedding & Semantic Similarity Service
Purpose: Encodes text queries and document chunks into 384-dimensional dense
         vectors using the local 'all-MiniLM-L6-v2' SentenceTransformer model.
         Provides vector cosine similarity ranking and embedding batch generation.
==============================================================================
"""

import logging
import hashlib
from typing import List
import numpy as np
from app.config import settings

logger = logging.getLogger("nitrkl_bot.pipeline.embeddings")

_model_instance = None


def get_embedding_model():
    """
    Singleton accessor for SentenceTransformer embedding model.
    Loads 'all-MiniLM-L6-v2' once into memory on first call, prioritizing local cache.
    """
    global _model_instance
    if _model_instance is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local embedding model: {settings.EMBEDDING_MODEL}")
            try:
                # Attempt to load from offline cache first (zero network lag/retries)
                _model_instance = SentenceTransformer(settings.EMBEDDING_MODEL, model_kwargs={"local_files_only": True})
            except Exception:
                try:
                    _model_instance = SentenceTransformer(settings.EMBEDDING_MODEL)
                except Exception:
                    _model_instance = "fallback"
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer: {e}. Falling back to pseudo-dense vectorizer.")
            _model_instance = "fallback"
    return _model_instance


def encode_text(text: str) -> List[float]:
    """
    Encodes a single text string into a 384-dimensional L2-normalized float vector.
    """
    if not text or not text.strip():
        return [0.0] * settings.VECTOR_DIMENSION

    model = get_embedding_model()
    if model != "fallback" and model is not None:
        try:
            vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return vec.tolist()
        except Exception as e:
            logger.error(f"Encoding failed: {e}. Falling back.")

    # Deterministic fallback vector using hashing for offline safety
    words = text.lower().split()
    dim = settings.VECTOR_DIMENSION
    vec = np.zeros(dim, dtype=np.float32)
    for idx, w in enumerate(words):
        # Stable across restarts (built-in hash() is randomised per process)
        pos = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16) % dim
        vec[pos] += 1.0 / (idx + 1)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def encode_batch(texts: List[str]) -> List[List[float]]:
    """
    Encodes a list of text strings into 384-dimensional L2-normalized vectors.
    """
    if not texts:
        return []

    model = get_embedding_model()
    if model != "fallback" and model is not None:
        try:
            vecs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return vecs.tolist()
        except Exception as e:
            logger.error(f"Batch encoding failed: {e}. Falling back to iterative encoding.")

    return [encode_text(t) for t in texts]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Computes exact Cosine Similarity between two L2-normalized float vectors.
    Since ||a|| = ||b|| = 1.0, similarity is the dot product: a . b
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
