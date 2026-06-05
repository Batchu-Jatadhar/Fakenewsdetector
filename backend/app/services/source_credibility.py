"""
Source credibility analysis service.

Uses NewsAPI metadata and simple heuristics to estimate source credibility for a given URL domain.
"""
from __future__ import annotations

from typing import Dict, Optional
from urllib.parse import urlparse

import httpx

from app.config import settings


def _extract_domain(url: str) -> Optional[str]:
  parsed = urlparse(url)
  host = parsed.netloc.lower()
  if host.startswith("www."):
      host = host[4:]
  return host or None


async def get_source_credibility(source_url: Optional[str]) -> Dict:
  """
  Compute a basic credibility profile for the source domain.

  Returns a dict like:
      {
          "domain": str,
          "credibility_score": float (0-1),
          "category": Optional[str],
          "country": Optional[str],
          "description": Optional[str],
      }
  """
  if not source_url:
      return {}

  domain = _extract_domain(source_url)
  if not domain:
      return {}

  # If NewsAPI key not configured, return a heuristic-only score
  if not settings.newsapi_key:
      return {
          "domain": domain,
          "credibility_score": 0.5,
          "category": None,
          "country": None,
          "description": None,
      }

  try:
      async with httpx.AsyncClient(timeout=10.0) as client:
          # NewsAPI "sources" endpoint gives metadata about known outlets
          response = await client.get(
              "https://newsapi.org/v2/top-headlines/sources",
              params={
                  "apiKey": settings.newsapi_key,
                  "language": "en",
              },
          )
          if response.status_code != 200:
              raise RuntimeError(f"NewsAPI error: {response.status_code}")

          data = response.json()
          sources = data.get("sources", [])

          # Try to match domain to a known NewsAPI source (by name or URL host)
          matched = None
          for src in sources:
              url = src.get("url") or ""
              src_domain = _extract_domain(url) or ""
              if domain == src_domain:
                  matched = src
                  break

          if not matched:
              # Unknown outlet: assign a neutral but slightly lower score
              return {
                  "domain": domain,
                  "credibility_score": 0.5,
                  "category": None,
                  "country": None,
                  "description": None,
              }

          # Basic scoring heuristic: treat recognized outlets as more credible
          base_score = 0.8
          category = matched.get("category")
          country = matched.get("country")

          # Penalize "entertainment" or "sports" slightly as they are often less hard-news
          if category in {"entertainment", "sports"}:
              base_score -= 0.1

          return {
              "domain": domain,
              "credibility_score": max(min(base_score, 1.0), 0.0),
              "category": category,
              "country": country,
              "description": matched.get("description"),
          }
  except Exception:
      # Fail open with a neutral score if NewsAPI call fails
      return {
          "domain": domain,
          "credibility_score": 0.5,
          "category": None,
          "country": None,
          "description": None,
      }

