"""
Auto-escalation fetcher — the core innovation combining Scrapling's 3-tier approach
with intelligent domain-level caching of which tier works.

Flow:
  1. Check domain cache — if we know this domain needs stealth, skip HTTP
  2. Try Tier 1 (HTTP) — fastest, works for most unprotected sites
  3. If 403/challenge detected → Try Tier 2 (Stealth Firefox) — Cloudflare bypass
  4. If still blocked → Try Tier 3 (Full Playwright) — last resort
  5. Cache the working tier for this domain (expires after 1 hour)
"""

import time
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

# Domain tier cache — remembers which tier works per domain
_TIER_CACHE_FILE = Path(__file__).parent.parent.parent / "data" / ".tier_cache.json"
_tier_cache: dict = {}


def auto_fetch(url: str, *, tier: str = "auto", headless: bool = True, **kwargs):
    """
    Fetch URL with automatic escalation through stealth tiers.
    
    Returns a parsed page object (AdaptivePage) with CSS/XPath/text selectors.
    """
    if tier != "auto":
        return _fetch_with_tier(url, tier, headless=headless, **kwargs)
    
    domain = urlparse(url).netloc
    cached_tier = _get_cached_tier(domain)
    
    if cached_tier:
        try:
            return _fetch_with_tier(url, cached_tier, headless=headless, **kwargs)
        except (BlockedError, FetchError):
            # Cache was wrong, escalate
            _clear_cached_tier(domain)
    
    # Escalation ladder
    tiers = ["http", "stealth", "browser"]
    last_error = None
    
    for t in tiers:
        try:
            result = _fetch_with_tier(url, t, headless=headless, **kwargs)
            _cache_tier(domain, t)
            return result
        except BlockedError as e:
            last_error = e
            continue
        except FetchError as e:
            last_error = e
            continue
    
    raise FetchError(f"All tiers failed for {url}. Last error: {last_error}")


def _fetch_with_tier(url: str, tier: str, *, headless: bool = True, **kwargs):
    """Attempt fetch with a specific tier."""
    
    if tier == "http":
        from .http_fetcher import http_fetch
        return http_fetch(url, **kwargs)
    
    elif tier == "stealth":
        try:
            from scrapling.fetchers import StealthyFetcher
            page = StealthyFetcher.get(url, headless=headless, **kwargs)
            if _is_blocked(page):
                raise BlockedError(f"Stealth fetch blocked for {url}")
            return page
        except ImportError:
            raise FetchError(
                "StealthyFetcher requires: pip install 'scrapetoolai[stealth]' && scrapling install"
            )
    
    elif tier == "browser":
        try:
            from scrapling.fetchers import DynamicFetcher
            page = DynamicFetcher.get(url, headless=headless, **kwargs)
            if _is_blocked(page):
                raise BlockedError(f"Browser fetch blocked for {url}")
            return page
        except ImportError:
            raise FetchError(
                "DynamicFetcher requires: pip install 'scrapetoolai[stealth]' && scrapling install"
            )
    
    raise ValueError(f"Unknown tier: {tier}. Use: http, stealth, browser, auto")


def _is_blocked(page) -> bool:
    """Detect if the response is a block/challenge page."""
    if hasattr(page, 'status_code'):
        if page.status_code in (403, 503, 429):
            return True
    
    # Check for common challenge signatures
    text = ""
    if hasattr(page, 'text'):
        text = page.text[:2000] if page.text else ""
    elif hasattr(page, 'html'):
        text = page.html[:2000] if page.html else ""
    
    block_signatures = [
        "Just a moment...",  # Cloudflare
        "Checking your browser",  # Cloudflare
        "Access denied",
        "Please verify you are a human",
        "Enable JavaScript and cookies",
        "Attention Required",
        "_cf_chl_opt",  # Cloudflare challenge
        "challenges.cloudflare.com",
    ]
    
    for sig in block_signatures:
        if sig.lower() in text.lower():
            return True
    
    return False


# --- Tier caching ---

def _get_cached_tier(domain: str) -> str | None:
    """Get cached tier for domain if still valid (1 hour TTL)."""
    _load_cache()
    entry = _tier_cache.get(domain)
    if entry and time.time() - entry["time"] < 3600:
        return entry["tier"]
    return None


def _cache_tier(domain: str, tier: str):
    """Cache which tier worked for a domain."""
    _tier_cache[domain] = {"tier": tier, "time": time.time()}
    _save_cache()


def _clear_cached_tier(domain: str):
    """Clear cache for a domain."""
    _tier_cache.pop(domain, None)
    _save_cache()


def _load_cache():
    """Load tier cache from disk."""
    global _tier_cache
    if _tier_cache:
        return
    try:
        if _TIER_CACHE_FILE.exists():
            _tier_cache = json.loads(_TIER_CACHE_FILE.read_text())
    except Exception:
        _tier_cache = {}


def _save_cache():
    """Persist tier cache to disk."""
    try:
        _TIER_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _TIER_CACHE_FILE.write_text(json.dumps(_tier_cache))
    except Exception:
        pass


# --- Exceptions ---

class FetchError(Exception):
    """General fetch failure."""
    pass


class BlockedError(FetchError):
    """Request was blocked by anti-bot system."""
    pass
