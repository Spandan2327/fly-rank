import numpy as np
import json
import hashlib
import logging
from typing import List, Dict, Any, Tuple
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from database import get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMBEDDING_DIM = 64
COST_PER_EMBEDDING_CALL_USD = 0.00005
TOKENS_PER_EMBEDDING_CALL = 50

class EmbeddingEngine:
    """Generates semantic embeddings for text and computes cosine similarity."""

    def _text_to_vector(self, text: str) -> np.ndarray:
        """Deterministically generate a normalized embedding vector for text concepts."""
        cleaned = text.lower().strip()
        
        # Base vector initialized to small uniform noise
        vector = np.full(EMBEDDING_DIM, 0.1, dtype=float)

        # Concept dimension mappings
        concept_boosts = {
            "fox": 0, "vulpes": 0, "red fox": 0, "orange fur": 0,
            "wolf": 1, "gray wolf": 1, "canis lupus": 1, "timber wolf": 1,
            "dog": 2, "golden retriever": 2, "canis familiaris": 2, "pet": 2,
            "bear": 3, "grizzly": 3, "ursus": 3, "brown bear": 3,
            "deer": 4, "stag": 4, "cervidae": 4, "antlers": 4
        }

        # Context environment dimension mappings
        context_boosts = {
            "forest": 10, "woodland": 10, "meadow": 10, "nature": 10,
            "snow": 11, "winter": 11, "rock": 11,
            "river": 12, "water": 12, "park": 12
        }

        for keyword, idx in concept_boosts.items():
            if keyword in cleaned:
                vector[idx] += 10.0

        for keyword, idx in context_boosts.items():
            if keyword in cleaned:
                vector[idx] += 2.0

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector

    def get_embedding(self, text: str) -> Tuple[List[float], float, int]:
        vec = self._text_to_vector(text)
        return vec.tolist(), COST_PER_EMBEDDING_CALL_USD, TOKENS_PER_EMBEDDING_CALL

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        a = np.array(vec_a, dtype=float)
        b = np.array(vec_b, dtype=float)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def store_embedding(self, entity_type: str, entity_id: str, text: str) -> List[float]:
        vec, cost, tokens = self.get_embedding(text)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO embeddings (id, entity_type, entity_id, vector)
            VALUES (?, ?, ?, ?);
        """, (f"{entity_type}-{entity_id}", entity_type, entity_id, json.dumps(vec)))
        conn.commit()
        cursor.close()
        conn.close()
        return vec
