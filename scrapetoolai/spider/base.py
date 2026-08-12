"""
Spider base class — Scrapy-style spider framework with stealth fetcher integration.

Usage:
    from scrapetoolai.spider import Spider

    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        fetcher = "auto"  # "http", "stealth", "browser", "auto"
        
        def parse(self, response):
            for item in response.css(".product"):
                yield {
                    "title": item.css_first("h2").text,
                    "price": item.css_first(".price").text,
                }
            next_page = response.css_first("a.next")
            if next_page:
                yield self.follow(next_page)
    
    MySpider.run(output="results.json")
"""

import json
import time
import csv
from pathlib import Path
from typing import Generator
from urllib.parse import urljoin


class Request:
    """A request to be processed by the spider engine."""
    def __init__(self, url: str, callback=None, meta: dict = None, priority: int = 0):
        self.url = url
        self.callback = callback
        self.meta = meta or {}
        self.priority = priority


class Spider:
    """
    Base spider class combining Scrapy's architecture with Scrapling's fetchers.
    
    Features from Scrapy:
    - start_urls and parse() callback pattern
    - yield items (dicts) and Request objects
    - link following with self.follow()
    - Output to JSON/CSV/JSONL
    
    Features from Scrapling:
    - Stealth fetcher integration (auto-escalation)
    - Adaptive selectors (survive site redesigns)
    - Anti-bot bypass built into the fetch layer
    """
    
    name: str = "unnamed"
    start_urls: list[str] = []
    fetcher: str = "auto"  # "http", "stealth", "browser", "auto"
    
    # Scrapy-style settings
    max_concurrent: int = 5
    download_delay: float = 1.0  # seconds between requests to same domain
    max_depth: int = 10
    max_pages: int = 1000
    respect_robots: bool = True
    
    def __init__(self):
        self._seen_urls: set = set()
        self._items: list = []
        self._queue: list = []
        self._stats = {"pages": 0, "items": 0, "errors": 0, "start_time": 0}
    
    def parse(self, response) -> Generator:
        """
        Override this method to extract data from responses.
        
        Yield:
        - dict: An extracted item (gets sent to pipeline)
        - Request: A new URL to crawl
        """
        raise NotImplementedError("Spider must implement parse()")
    
    def follow(self, element_or_url, callback=None, **kwargs) -> Request:
        """Create a Request to follow a link (like Scrapy's response.follow)."""
        if isinstance(element_or_url, str):
            url = element_or_url
        elif hasattr(element_or_url, 'attrib'):
            url = element_or_url.attrib.get("href", "")
        elif hasattr(element_or_url, 'get'):
            url = element_or_url.get("href", "")
        else:
            url = str(element_or_url)
        
        return Request(url=url, callback=callback or self.parse, **kwargs)
    
    @classmethod
    def run(cls, output: str = None, **kwargs):
        """Run the spider and optionally save results."""
        spider = cls()
        spider._run(**kwargs)
        
        if output:
            spider._save_output(output)
        
        return spider._items
    
    def _run(self, **kwargs):
        """Execute the spider crawl."""
        self._stats["start_time"] = time.time()
        
        # Seed the queue with start_urls
        for url in self.start_urls:
            self._queue.append(Request(url=url, callback=self.parse))
        
        print(f"[{self.name}] Starting crawl ({len(self.start_urls)} seed URLs, fetcher={self.fetcher})")
        
        while self._queue and self._stats["pages"] < self.max_pages:
            request = self._queue.pop(0)
            
            if request.url in self._seen_urls:
                continue
            self._seen_urls.add(request.url)
            
            try:
                response = self._fetch(request.url)
                self._stats["pages"] += 1
                
                # Process the response through the callback
                callback = request.callback or self.parse
                for result in callback(response):
                    if isinstance(result, dict):
                        self._items.append(result)
                        self._stats["items"] += 1
                    elif isinstance(result, Request):
                        # Resolve relative URLs
                        result.url = urljoin(request.url, result.url)
                        if result.url not in self._seen_urls:
                            self._queue.append(result)
                
                # Rate limiting
                time.sleep(self.download_delay)
                
            except Exception as e:
                self._stats["errors"] += 1
                print(f"[{self.name}] Error on {request.url}: {e}")
        
        elapsed = time.time() - self._stats["start_time"]
        print(f"[{self.name}] Done: {self._stats['pages']} pages, "
              f"{self._stats['items']} items, {self._stats['errors']} errors "
              f"in {elapsed:.1f}s")
    
    def _fetch(self, url: str):
        """Fetch a URL using the configured fetcher tier."""
        from scrapetoolai import fetch
        return fetch(url, tier=self.fetcher)
    
    def _save_output(self, path: str):
        """Save extracted items to file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.suffix == ".json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._items, f, indent=2, ensure_ascii=False)
        
        elif path.suffix == ".jsonl":
            with open(path, "w", encoding="utf-8") as f:
                for item in self._items:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        elif path.suffix == ".csv":
            if self._items:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=self._items[0].keys())
                    writer.writeheader()
                    writer.writerows(self._items)
        
        print(f"[{self.name}] Saved {len(self._items)} items to {path}")
