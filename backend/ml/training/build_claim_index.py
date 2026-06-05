"""
Build a Sentence-BERT claim index for semantic similarity search.
Encodes known fact-checked claims and saves embeddings + metadata for fast retrieval.

Usage:
    python -m ml.training.build_claim_index
"""
import json
import numpy as np
from pathlib import Path

from sentence_transformers import SentenceTransformer

from ml.training.download_datasets import prepare_all_datasets

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR = Path(__file__).resolve().parent.parent / "models" / "claim-index"


def build_claim_index():
    """Build semantic similarity index from fact-checked claims."""
    print("Building Sentence-BERT claim index...")

    # Load data
    data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "processed"
    if not (data_dir / "train.json").exists():
        print("Datasets not found. Preparing...")
        prepare_all_datasets()

    with open(data_dir / "train.json", "r", encoding="utf-8") as f:
        train_data = json.load(f)

    # Use a subset of claims for the index (unique short claims work best)
    claims = []
    seen = set()
    for item in train_data:
        text = item["text"][:500]  # Limit length
        if text not in seen and len(text) > 20:
            claims.append({
                "text": text,
                "label": item["label"],  # 0=real, 1=fake
                "source": item.get("source", "unknown"),
            })
            seen.add(text)

    # Limit index size for performance
    max_claims = 5000
    if len(claims) > max_claims:
        # Keep balanced set
        real_claims = [c for c in claims if c["label"] == 0][:max_claims // 2]
        fake_claims = [c for c in claims if c["label"] == 1][:max_claims // 2]
        claims = real_claims + fake_claims

    print(f"  Encoding {len(claims)} claims...")

    # Load model and encode
    model = SentenceTransformer(MODEL_NAME)
    texts = [c["text"] for c in claims]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    # Save index
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    np.save(str(INDEX_DIR / "embeddings.npy"), embeddings)

    metadata = [{"text": c["text"], "label": c["label"], "source": c["source"]} for c in claims]
    with open(INDEX_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"  Saved {len(claims)} claim embeddings to {INDEX_DIR}")
    print(f"  Embedding shape: {embeddings.shape}")

    return embeddings, metadata


if __name__ == "__main__":
    build_claim_index()
