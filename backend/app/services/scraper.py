"""
Article text extraction from URLs.
"""
import httpx
from bs4 import BeautifulSoup
from typing import Optional


async def extract_article_text(url: str) -> str:
    """
    Extract article text content from a URL.

    Uses BeautifulSoup for HTML parsing with fallback strategies.
    """
    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; FakeNewsDetector/1.0; Research)"
            },
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text
    except Exception as e:
        raise ValueError(f"Failed to fetch URL: {str(e)}")

    soup = BeautifulSoup(html, "lxml")

    # Remove script, style, nav elements
    for element in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
        element.decompose()

    # Try to find article content using common selectors
    article_text = _extract_article_body(soup)

    if not article_text or len(article_text) < 50:
        # Fallback: get all paragraph text
        paragraphs = soup.find_all("p")
        article_text = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)

    if not article_text or len(article_text) < 50:
        # Final fallback: get body text
        body = soup.find("body")
        if body:
            article_text = body.get_text(separator=" ", strip=True)

    if not article_text:
        raise ValueError("Could not extract meaningful text from the URL")

    # Clean up
    article_text = " ".join(article_text.split())  # Normalize whitespace

    # Get title
    title = ""
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)

    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)

    if title:
        article_text = f"{title}. {article_text}"

    return article_text[:10000]  # Limit length


def _extract_article_body(soup: BeautifulSoup) -> Optional[str]:
    """Try to extract article body using common HTML patterns."""
    # Common article container selectors
    selectors = [
        ("article", {}),
        ("div", {"class": "article-body"}),
        ("div", {"class": "story-body"}),
        ("div", {"class": "post-content"}),
        ("div", {"class": "entry-content"}),
        ("div", {"class": "article-content"}),
        ("div", {"itemprop": "articleBody"}),
        ("div", {"role": "article"}),
    ]

    for tag, attrs in selectors:
        element = soup.find(tag, attrs)
        if element:
            paragraphs = element.find_all("p")
            if paragraphs:
                text = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
                if len(text) > 100:
                    return text

    return None
