"""
OpenRouter AI integration for enhanced natural language explanations.

This service is optional and only used if OPENROUTER_API_KEY is configured.
"""
from __future__ import annotations

from typing import Dict, Any

import httpx

from app.config import settings


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


async def enhance_explanation_with_openrouter(
    text: str,
    raw_explanation: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Optionally refine the reasoning with an LLM via OpenRouter.

    Returns an updated explanation dict. If OpenRouter is not configured or fails,
    returns the original explanation unchanged.
    """
    api_key = settings.openrouter_api_key
    if not api_key:
        return raw_explanation

    try:
        reasoning = raw_explanation.get("reasoning", "")
        prompt = (
            "You are an AI assistant helping users understand misinformation risk.\n\n"
            "Given the following article content and internal model explanation, rewrite the explanation so it is:\n"
            "- Simple and non-technical\n"
            "- Neutral and not alarmist\n"
            "- 3–5 sentences max\n\n"
            "Article content (truncated):\n"
            f"{text[:800]}\n\n"
            "Internal explanation:\n"
            f"{reasoning}\n\n"
            "Rewrite the explanation in plain language:"
        )

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                OPENROUTER_BASE_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.openrouter_model,
                    "messages": [
                        {"role": "system", "content": "You explain misinformation risk in clear, neutral language."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 200,
                    "temperature": 0.4,
                },
            )

        if response.status_code != 200:
            return raw_explanation

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            return raw_explanation

        content = choices[0]["message"]["content"]
        if not content:
            return raw_explanation

        updated = dict(raw_explanation)
        updated["reasoning"] = content.strip()
        return updated
    except Exception:
        return raw_explanation

