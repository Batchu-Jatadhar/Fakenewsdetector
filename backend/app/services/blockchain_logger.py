"""
Blockchain logging service for analysis results.

This is an optional, pluggable layer intended for anchoring analysis
metadata (not raw user content) on a blockchain or immutable ledger.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

import httpx

from app.config import settings


def _compute_analysis_hash(analysis_id: str, payload: Dict[str, Any]) -> str:
    """Compute a stable hash of the analysis result."""
    # Only include high-level fields in the hash to avoid leaking content
    to_hash = {
        "analysis_id": analysis_id,
        "fake_probability": payload.get("fake_probability"),
        "trust_score": payload.get("trust_score"),
        "roberta_score": payload.get("roberta_score"),
        "sbert_score": payload.get("sbert_score"),
        "confidence": payload.get("confidence"),
        "model_agreement": payload.get("model_agreement"),
        "source_credibility": payload.get("source_credibility"),
    }
    data = json.dumps(to_hash, sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


async def log_analysis_to_blockchain(
    analysis_id: str,
    payload: Dict[str, Any],
) -> None:
    """
    Log a summary of the analysis to a blockchain endpoint.

    This is best-effort: failures are swallowed so core analysis flow is not affected.
    """
    if not settings.blockchain_enabled or not settings.blockchain_endpoint:
        return

    try:
        record_hash = _compute_analysis_hash(analysis_id, payload)
        body = {
            "analysis_id": analysis_id,
            "hash": record_hash,
            "metadata": {
                "fake_probability": payload.get("fake_probability"),
                "trust_score": payload.get("trust_score"),
                "confidence": payload.get("confidence"),
                "model_agreement": payload.get("model_agreement"),
                "source_domain": (payload.get("source_credibility") or {}).get("domain"),
            },
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            # The concrete blockchain service is expected to expose a simple HTTP API.
            await client.post(settings.blockchain_endpoint, json=body)
    except Exception:
        # Do not let blockchain issues break core analysis
        return

