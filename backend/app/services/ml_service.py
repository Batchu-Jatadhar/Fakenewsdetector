"""
ML Service: Orchestrates the full analysis pipeline.
"""
import asyncio
import hashlib
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from ml.roberta_classifier import get_classifier
from ml.semantic_similarity import get_similarity_engine
from ml.ensemble import ensemble_score
from ml.explainer import generate_explanation
from app.services.fact_check_service import check_facts
from app.services.cache_service import get_cached_result, cache_result
from app.services.source_credibility import get_source_credibility
from app.services.openrouter_ai import enhance_explanation_with_openrouter
from app.services.blockchain_logger import log_analysis_to_blockchain


async def run_analysis_pipeline(
    text: str,
    analysis_id: str,
    db: AsyncSession,
    source_url: str | None = None,
) -> Dict:
    """
    Run the full ML analysis pipeline on input text.

    Steps:
    1. Check cache
    2. Run RoBERTa classifier
    3. Run Sentence-BERT similarity search
    4. Compute ensemble score
    5. Generate explanation (+ optional OpenRouter refinement)
    6. Run fact-check verification
    7. Compute source credibility (if URL available)
    8. Optionally log a hash of the result to a blockchain endpoint
    9. Cache and return results
    """
    # Check cache first
    text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
    cached = await get_cached_result(text_hash)
    if cached:
        return cached

    # Run ML models (synchronous operations wrapped for async)
    loop = asyncio.get_event_loop()

    # Run both models concurrently
    roberta_task = loop.run_in_executor(None, _run_roberta, text)
    sbert_task = loop.run_in_executor(None, _run_sbert, text)

    roberta_result, sbert_result = await asyncio.gather(roberta_task, sbert_task)

    # Ensemble scoring
    scores = ensemble_score(roberta_result, sbert_result)

    # Generate explanation (local)
    explanation = await loop.run_in_executor(
        None, generate_explanation, text, scores, sbert_result.get("top_matches", [])
    )

    # Optionally refine explanation with OpenRouter AI
    explanation = await enhance_explanation_with_openrouter(text, explanation)

    # External fact-check verification
    fact_checks = await check_facts(text[:500])

    # Source credibility (if URL is available)
    source_credibility = await get_source_credibility(source_url)

    result = {
        "fake_probability": scores["fake_probability"],
        "trust_score": scores["trust_score"],
        "roberta_score": scores["roberta_score"],
        "sbert_score": scores["sbert_score"],
        "confidence": scores["confidence"],
        "explanation": explanation,
        "fact_checks": fact_checks,
        "model_agreement": scores["model_agreement"],
        "source_credibility": source_credibility,
    }

    # Fire-and-forget blockchain logging (does not block or raise)
    try:
        loop.create_task(log_analysis_to_blockchain(analysis_id, result))
    except RuntimeError:
        # Event loop might not be available in some contexts; ignore
        pass

    # Cache the result
    await cache_result(text_hash, result)

    return result


def _run_roberta(text: str) -> Dict:
    classifier = get_classifier()
    return classifier.predict(text)


def _run_sbert(text: str) -> Dict:
    engine = get_similarity_engine()
    return engine.compute_aggregate_score(text)
