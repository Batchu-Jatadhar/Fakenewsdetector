"""
Explanation generator for fake news detection results.
Uses attention weights and heuristic patterns to identify suspicious content.
"""
import re
from typing import Dict, List, Optional

from ml.roberta_classifier import get_classifier


# Suspicious patterns commonly found in misinformation
SUSPICIOUS_PATTERNS = [
    (r"\b(BREAKING|SHOCKING|URGENT|EXPOSED|BOMBSHELL|ALERT)\b", "Sensationalist language"),
    (r"\b(they don'?t want you to know|wake up|open your eyes)\b", "Conspiratorial framing", re.IGNORECASE),
    (r"[A-Z]{5,}", "Excessive capitalization"),
    (r"!{3,}", "Excessive exclamation marks"),
    (r"\b(miracle|cure|secret|banned|censored)\b", "Clickbait/sensationalist terms", re.IGNORECASE),
    (r"\b(100%|guaranteed|proven|undeniable)\b", "Absolute claims", re.IGNORECASE),
    (r"\b(share before|share this|going viral)\b", "Urgency manipulation", re.IGNORECASE),
    (r"\b(mainstream media|MSM|big pharma|deep state|elites)\b", "Conspiracy terminology", re.IGNORECASE),
    (r"\b(doctors hate|one weird trick|you won'?t believe)\b", "Clickbait patterns", re.IGNORECASE),
    (r"\b(exposed|revealed|leaked|whistleblower)\b.*!", "Dramatic revelation claims", re.IGNORECASE),
]


def generate_explanation(
    text: str,
    ensemble_result: Dict,
    sbert_matches: List[Dict],
) -> Dict:
    """
    Generate human-readable explanation for the analysis result.

    Returns:
        {
            "reasoning": str,
            "suspicious_phrases": [{"text": str, "start": int, "end": int, "reason": str}],
        }
    """
    suspicious_phrases = []

    # Pattern-based detection
    for pattern_info in SUSPICIOUS_PATTERNS:
        if len(pattern_info) == 3:
            pattern, reason, flags = pattern_info
        else:
            pattern, reason = pattern_info
            flags = 0

        for match in re.finditer(pattern, text, flags):
            suspicious_phrases.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "reason": reason,
            })

    # Try attention-based detection
    try:
        classifier = get_classifier()
        attention_data = classifier.get_attention_weights(text)
        if attention_data:
            token_attentions = attention_data["token_attentions"]
            # Find tokens with high attention that might be suspicious
            if token_attentions:
                attention_values = [att for _, att in token_attentions]
                if attention_values:
                    mean_att = sum(attention_values) / len(attention_values)
                    std_att = (sum((a - mean_att) ** 2 for a in attention_values) / len(attention_values)) ** 0.5

                    threshold = mean_att + 2 * std_att
                    high_attention_tokens = [
                        tok for tok, att in token_attentions
                        if att > threshold and not tok.startswith("Ġ") or len(tok) > 3
                    ]

                    if high_attention_tokens:
                        for token in high_attention_tokens[:5]:
                            clean_token = token.replace("Ġ", "")
                            idx = text.lower().find(clean_token.lower())
                            if idx >= 0:
                                suspicious_phrases.append({
                                    "text": text[idx:idx + len(clean_token)],
                                    "start": idx,
                                    "end": idx + len(clean_token),
                                    "reason": "High model attention",
                                })
    except Exception:
        pass  # Attention analysis is optional

    # Deduplicate overlapping phrases
    suspicious_phrases = _deduplicate_phrases(suspicious_phrases)

    # Generate reasoning text
    reasoning = _build_reasoning(ensemble_result, sbert_matches, suspicious_phrases)

    return {
        "reasoning": reasoning,
        "suspicious_phrases": suspicious_phrases[:10],  # Limit to top 10
    }


def _deduplicate_phrases(phrases: List[Dict]) -> List[Dict]:
    """Remove overlapping phrase detections."""
    if not phrases:
        return []

    sorted_phrases = sorted(phrases, key=lambda p: p["start"])
    result = [sorted_phrases[0]]

    for phrase in sorted_phrases[1:]:
        if phrase["start"] >= result[-1]["end"]:
            result.append(phrase)

    return result


def _build_reasoning(
    ensemble_result: Dict,
    sbert_matches: List[Dict],
    suspicious_phrases: List[Dict],
) -> str:
    """Build a human-readable reasoning explanation."""
    fake_prob = ensemble_result["fake_probability"]
    confidence = ensemble_result["confidence"]
    agreement = ensemble_result["model_agreement"]

    parts = []

    # Overall assessment
    if fake_prob > 0.7:
        parts.append(f"This content has a HIGH probability of being misinformation (fake probability: {fake_prob:.0%}).")
    elif fake_prob > 0.4:
        parts.append(f"This content shows MIXED signals requiring careful evaluation (fake probability: {fake_prob:.0%}).")
    else:
        parts.append(f"This content appears to be LIKELY CREDIBLE (fake probability: {fake_prob:.0%}).")

    # Model agreement
    if agreement:
        parts.append(f"Both the language analysis model and semantic similarity engine agree on this assessment (confidence: {confidence:.0%}).")
    else:
        parts.append(f"The language analysis and semantic similarity models show some disagreement, suggesting this content has mixed characteristics (confidence: {confidence:.0%}).")

    # RoBERTa analysis
    roberta_score = ensemble_result["roberta_score"]
    if roberta_score > 0.6:
        parts.append("The RoBERTa language model detected patterns in writing style and content structure commonly associated with misinformation.")
    elif roberta_score < 0.3:
        parts.append("The RoBERTa language model found the writing style and content structure consistent with credible reporting.")

    # SBERT analysis
    sbert_score = ensemble_result["sbert_score"]
    if sbert_matches:
        fake_matches = [m for m in sbert_matches if m["label"] == 1 and m["similarity"] > 0.5]
        real_matches = [m for m in sbert_matches if m["label"] == 0 and m["similarity"] > 0.5]

        if fake_matches:
            parts.append(f"The content is semantically similar to {len(fake_matches)} known misinformation claim(s) in our database.")
        if real_matches:
            parts.append(f"The content also shows similarity to {len(real_matches)} verified credible source(s).")

    # Suspicious patterns
    if suspicious_phrases:
        reasons = list(set(p["reason"] for p in suspicious_phrases))
        parts.append(f"Detected {len(suspicious_phrases)} potentially suspicious element(s): {', '.join(reasons[:3])}.")

    return " ".join(parts)
