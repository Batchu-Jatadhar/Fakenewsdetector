"""
Sentence-BERT semantic similarity search engine.
Compares input text against known fact-checked claims.
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, List

from sentence_transformers import SentenceTransformer

INDEX_DIR = Path(__file__).resolve().parent / "models" / "claim-index"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class SemanticSimilarityEngine:
    def __init__(self):
        self.model = None
        self.embeddings = None
        self.metadata = None
        self._loaded = False

    def load(self):
        """Load Sentence-BERT model and claim index."""
        print("Loading Sentence-BERT model...")
        self.model = SentenceTransformer(MODEL_NAME)

        if INDEX_DIR.exists() and (INDEX_DIR / "embeddings.npy").exists():
            print(f"Loading claim index from {INDEX_DIR}")
            self.embeddings = np.load(str(INDEX_DIR / "embeddings.npy"))
            with open(INDEX_DIR / "metadata.json", "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            print(f"  Loaded {len(self.metadata)} claims")
        else:
            print("Claim index not found. Similarity search will use fallback scoring.")
            self.embeddings = None
            self.metadata = []

        self._loaded = True

    def find_similar(self, text: str, top_k: int = 5) -> List[Dict]:
        """
        Find the most similar known claims to the input text.

        Returns list of:
            {
                "claim": str,
                "label": int (0=real, 1=fake),
                "similarity": float (0-1),
                "source": str,
            }
        """
        if not self._loaded:
            self.load()

        if self.embeddings is None or len(self.metadata) == 0:
            return []

        # Encode the query
        query_embedding = self.model.encode([text[:1000]])[0]

        # Compute cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding) + 1e-8
        )

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "claim": self.metadata[idx]["text"][:200],
                "label": self.metadata[idx]["label"],
                "similarity": round(float(similarities[idx]), 4),
                "source": self.metadata[idx].get("source", "unknown"),
            })

        return results

    def compute_aggregate_score(self, text: str, top_k: int = 10) -> Dict:
        """
        Compute an aggregate fake-news score based on semantic similarity to known claims.

        Logic:
        - Find top-k similar claims
        - Weight their labels by similarity
        - If most similar claims are fake -> higher fake score
        - If most similar claims are real -> lower fake score

        Returns:
            {
                "sbert_fake_score": float (0-1),
                "top_matches": list,
                "avg_similarity": float,
            }
        """
        if not self._loaded:
            self.load()

        matches = self.find_similar(text, top_k=top_k)

        if not matches:
            return {
                "sbert_fake_score": 0.5,  # Uncertain when no index
                "top_matches": [],
                "avg_similarity": 0.0,
            }

        # Weighted score: similarity * label (1 for fake, 0 for real)
        weighted_fake = 0.0
        weight_sum = 0.0

        for match in matches:
            sim = max(match["similarity"], 0)  # Only positive similarities
            weighted_fake += sim * match["label"]
            weight_sum += sim

        sbert_fake_score = weighted_fake / weight_sum if weight_sum > 0 else 0.5

        avg_sim = np.mean([m["similarity"] for m in matches]) if matches else 0.0

        return {
            "sbert_fake_score": round(float(sbert_fake_score), 4),
            "top_matches": matches[:5],
            "avg_similarity": round(float(avg_sim), 4),
        }


# Singleton
_engine = None


def get_similarity_engine() -> SemanticSimilarityEngine:
    global _engine
    if _engine is None:
        _engine = SemanticSimilarityEngine()
        _engine.load()
    return _engine
