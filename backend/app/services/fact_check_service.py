"""
Fact-check verification service.
Integrates Google Fact Check Tools API and NewsAPI with mock fallbacks.
"""
import httpx
from typing import List, Dict
from app.config import settings


async def check_facts(text: str) -> List[Dict]:
    """
    Check facts using external APIs with mock fallbacks.

    Returns list of fact-check results:
        {
            "source": str,
            "claim_text": str,
            "verdict": str,
            "publisher": str,
            "url": str,
        }
    """
    results = []

    # Google Fact Check API
    google_results = await _google_fact_check(text)
    results.extend(google_results)

    # NewsAPI for related articles
    news_results = await _newsapi_check(text)
    results.extend(news_results)

    # If no API keys configured, use mock data
    if not results:
        results = _get_mock_fact_checks(text)

    return results


async def _google_fact_check(text: str) -> List[Dict]:
    """Query Google Fact Check Tools API."""
    if not settings.google_factcheck_api_key:
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://factchecktools.googleapis.com/v1alpha1/claims:search",
                params={
                    "query": text[:200],
                    "key": settings.google_factcheck_api_key,
                    "languageCode": "en",
                },
            )
            if response.status_code == 200:
                data = response.json()
                results = []
                for claim in data.get("claims", [])[:5]:
                    for review in claim.get("claimReview", []):
                        results.append({
                            "source": "google_factcheck",
                            "claim_text": claim.get("text", ""),
                            "verdict": review.get("textualRating", "Unknown"),
                            "publisher": review.get("publisher", {}).get("name", "Unknown"),
                            "url": review.get("url", ""),
                        })
                return results
    except Exception:
        pass

    return []


async def _newsapi_check(text: str) -> List[Dict]:
    """Query NewsAPI for related articles from trusted sources."""
    if not settings.newsapi_key:
        return []

    try:
        # Extract key phrases for search
        words = text.split()[:10]
        query = " ".join(words)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "apiKey": settings.newsapi_key,
                    "language": "en",
                    "sortBy": "relevancy",
                    "pageSize": 5,
                },
            )
            if response.status_code == 200:
                data = response.json()
                results = []
                for article in data.get("articles", [])[:5]:
                    results.append({
                        "source": "newsapi",
                        "claim_text": article.get("title", ""),
                        "verdict": "Related Article",
                        "publisher": article.get("source", {}).get("name", "Unknown"),
                        "url": article.get("url", ""),
                    })
                return results
    except Exception:
        pass

    return []


def _get_mock_fact_checks(text: str) -> List[Dict]:
    """Return mock fact-check results for demonstration purposes."""
    text_lower = text.lower()

    mock_database = [
        {
            "keywords": ["vaccine", "covid", "5g", "microchip", "pfizer", "moderna"],
            "checks": [
                {
                    "source": "mock",
                    "claim_text": "COVID-19 vaccines contain microchips for tracking",
                    "verdict": "False",
                    "publisher": "Reuters Fact Check",
                    "url": "https://example.com/factcheck/vaccines-microchips",
                },
                {
                    "source": "mock",
                    "claim_text": "5G technology is linked to COVID-19 spread",
                    "verdict": "False",
                    "publisher": "AP Fact Check",
                    "url": "https://example.com/factcheck/5g-covid",
                },
            ],
        },
        {
            "keywords": ["election", "stolen", "fraud", "ballot", "voting machine"],
            "checks": [
                {
                    "source": "mock",
                    "claim_text": "Widespread voter fraud changed election outcomes",
                    "verdict": "False",
                    "publisher": "PolitiFact",
                    "url": "https://example.com/factcheck/election-fraud",
                },
            ],
        },
        {
            "keywords": ["climate", "hoax", "global warming", "carbon"],
            "checks": [
                {
                    "source": "mock",
                    "claim_text": "Climate change is a hoax created by scientists",
                    "verdict": "False",
                    "publisher": "Snopes",
                    "url": "https://example.com/factcheck/climate-hoax",
                },
            ],
        },
        {
            "keywords": ["cure", "cancer", "miracle", "pharma", "secret treatment"],
            "checks": [
                {
                    "source": "mock",
                    "claim_text": "A secret cure for cancer is being hidden by pharmaceutical companies",
                    "verdict": "False",
                    "publisher": "FactCheck.org",
                    "url": "https://example.com/factcheck/cancer-cure",
                },
            ],
        },
        {
            "keywords": ["moon", "landing", "nasa", "fake", "hoax"],
            "checks": [
                {
                    "source": "mock",
                    "claim_text": "The Apollo moon landings were faked by NASA",
                    "verdict": "False",
                    "publisher": "Snopes",
                    "url": "https://example.com/factcheck/moon-landing",
                },
            ],
        },
    ]

    results = []
    for entry in mock_database:
        if any(kw in text_lower for kw in entry["keywords"]):
            results.extend(entry["checks"])

    # Always add a general reference
    if not results:
        results.append({
            "source": "mock",
            "claim_text": "General credibility assessment based on content analysis",
            "verdict": "Requires Further Verification",
            "publisher": "AI Analysis Engine",
            "url": "",
        })

    return results[:5]
