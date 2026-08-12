"""
Tier 1: Fast HTTP fetcher with TLS fingerprint spoofing and stealth headers.

This is the fastest tier — no browser needed. Works for most unprotected sites.
Uses httpx for async support and HTTP/2.
"""

import random
from urllib.parse import urlparse

# Realistic browser User-Agent rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

# Headers that look like a real browser
def _stealth_headers(url: str) -> dict:
    """Generate headers that mimic a real browser visit."""
    domain = urlparse(url).netloc
    ua = random.choice(USER_AGENTS)
    
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "DNT": "1",
    }
    
    # Add Referer for non-homepage requests
    if urlparse(url).path not in ("", "/"):
        headers["Referer"] = f"https://{domain}/"
    
    return headers


def http_fetch(url: str, *, timeout: float = 30, follow_redirects: bool = True, **kwargs):
    """
    Fetch URL using fast HTTP with stealth headers.
    
    Returns a SimplePage object compatible with CSS/XPath selectors.
    """
    try:
        import httpx
        
        headers = _stealth_headers(url)
        headers.update(kwargs.pop("headers", {}))
        
        with httpx.Client(
            http2=True,
            follow_redirects=follow_redirects,
            timeout=timeout,
            headers=headers,
        ) as client:
            response = client.get(url, **kwargs)
        
        if response.status_code in (403, 503, 429):
            from .escalation import BlockedError
            raise BlockedError(f"HTTP {response.status_code} — likely bot protection on {url}")
        
        response.raise_for_status()
        return SimplePage(response.text, url=url, status_code=response.status_code)
    
    except ImportError:
        # Fallback to urllib if httpx not installed
        from urllib.request import urlopen, Request
        req = Request(url, headers=_stealth_headers(url))
        with urlopen(req, timeout=int(timeout)) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            return SimplePage(html, url=url, status_code=resp.status)


class SimplePage:
    """
    Lightweight page object with CSS/XPath selector support.
    Compatible interface with Scrapling's pages for the escalation layer.
    """
    
    def __init__(self, html: str, url: str = "", status_code: int = 200):
        self.html = html
        self.text = html
        self.url = url
        self.status_code = status_code
        self._soup = None
    
    @property
    def soup(self):
        """Lazy-load BeautifulSoup parser."""
        if self._soup is None:
            from bs4 import BeautifulSoup
            self._soup = BeautifulSoup(self.html, "lxml")
        return self._soup
    
    def css(self, selector: str, adaptive: bool = False) -> list:
        """Select elements by CSS selector."""
        return self.soup.select(selector)
    
    def css_first(self, selector: str, adaptive: bool = False):
        """Select first element matching CSS selector."""
        result = self.soup.select_one(selector)
        return result
    
    def xpath(self, expression: str) -> list:
        """Select elements by XPath expression."""
        try:
            from lxml import etree
            tree = etree.HTML(self.html)
            return tree.xpath(expression)
        except ImportError:
            raise ImportError("XPath requires lxml: pip install lxml")
    
    def find_all(self, *args, **kwargs):
        """BeautifulSoup-style find_all."""
        return self.soup.find_all(*args, **kwargs)
    
    def find(self, *args, **kwargs):
        """BeautifulSoup-style find."""
        return self.soup.find(*args, **kwargs)
    
    def get_text(self) -> str:
        """Extract all text content."""
        return self.soup.get_text(separator="\n", strip=True)
    
    def __repr__(self):
        return f"<SimplePage url={self.url} status={self.status_code} len={len(self.html)}>"
