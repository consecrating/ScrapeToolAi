"""
ScrapeToolAi — Super-advanced web scraping framework.

Combines Scrapling's stealth fetching + adaptive parsing with Scrapy's
spider architecture + middleware pipelines, plus AI-powered extraction
and personal data organization.

Quick usage:
    from scrapetoolai import fetch, smart_extract, search

    # Stealth fetch (auto-escalates on Cloudflare)
    page = fetch("https://protected-site.com")
    
    # AI extraction (no selectors needed)
    data = smart_extract("https://site.com/menu", "menu items with prices")
    
    # Search your personal collection
    results = search("golden hour portrait")
"""

__version__ = "1.0.0"


def fetch(url: str, *, tier: str = "auto", headless: bool = True, **kwargs):
    """
    Fetch a URL with automatic anti-bot escalation.
    
    Tiers:
        "auto" — Start with HTTP, escalate to stealth/browser if blocked
        "http" — Fast HTTP with TLS fingerprint spoofing
        "stealth" — Modified Firefox, bypasses Cloudflare
        "browser" — Full Playwright automation
    
    Returns an AdaptivePage object with CSS/XPath selectors and adaptive tracking.
    """
    from .fetchers.escalation import auto_fetch
    return auto_fetch(url, tier=tier, headless=headless, **kwargs)


def smart_extract(url: str, intent: str, **kwargs) -> list[dict]:
    """
    AI-powered extraction — describe what you want in plain English.
    
    Example:
        data = smart_extract(
            "https://restaurant.com/menu",
            "menu items with name, price, description, and dietary tags"
        )
    
    Requires: OPENAI_API_KEY or GOOGLE_AI_KEY in environment.
    Falls back to heuristic extraction without AI keys.
    """
    from .ai.extractor import extract_with_ai
    return extract_with_ai(url, intent, **kwargs)


def search(query: str, **filters) -> list[dict]:
    """
    Search your personal data collection (imported Instagram, Pinterest, etc.).
    
    Filters: source, category, mood, type, platform, limit
    """
    from .organizer.search import search_collection
    return search_collection(query, **filters)
