"""
Ensemble scoring: combines RoBERTa classifier and Sentence-BERT similarity scores.
"""
from typing import Dict


# Configurable weights
ROBERTA_WEIGHT = 0.65
SBERT_WEIGHT = 0.35


def ensemble_score(roberta_result: Dict, sbert_result: Dict) -> Dict:
    """
    Combine RoBERTa classification and SBERT similarity into a final score.

    Args:
        roberta_result: Output from RoBERTaClassifier.predict()
        sbert_result: Output from SemanticSimilarityEngine.compute_aggregate_score()

    Returns:
        {
            "fake_probability": float (0-1),
            "trust_score": float (0-1),
            "confidence": float (0-1),
            "roberta_score": float,
            "sbert_score": float,
            "model_agreement": bool,
        }
    """
    roberta_fake = roberta_result["fake_prob"]
    roberta_confidence = roberta_result["confidence"]
    sbert_fake = sbert_result["sbert_fake_score"]

    # Weighted ensemble
    fake_probability = (ROBERTA_WEIGHT * roberta_fake) + (SBERT_WEIGHT * sbert_fake)
    trust_score = 1.0 - fake_probability

    # Confidence: average of RoBERTa confidence and how decisive SBERT is
    sbert_decisiveness = abs(sbert_fake - 0.5) * 2  # 0 when uncertain, 1 when decisive
    confidence = (roberta_confidence + sbert_decisiveness) / 2

    # Check if models agree
    roberta_says_fake = roberta_fake > 0.5
    sbert_says_fake = sbert_fake > 0.5
    model_agreement = roberta_says_fake == sbert_says_fake

    # Boost confidence if models agree, reduce if they disagree
    if model_agreement:
        confidence = min(confidence * 1.1, 1.0)
    else:
        confidence = confidence * 0.8

    return {
        "fake_probability": round(fake_probability, 4),
        "trust_score": round(trust_score, 4),
        "confidence": round(confidence, 4),
        "roberta_score": round(roberta_fake, 4),
        "sbert_score": round(sbert_fake, 4),
        "model_agreement": model_agreement,
    }
