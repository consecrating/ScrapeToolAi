# ScrapeToolAi

**Super-advanced web scraping framework** combining the best active skills from [Scrapling](https://github.com/D4Vinci/Scrapling) and [Scrapy](https://github.com/scrapy/scrapy), plus AI-powered extraction and your personal data organization layer.

Built to actually work against Cloudflare, WAFs, and modern anti-bot systems.

---

## Why Not Just Use Scrapling or Scrapy Directly?

| Problem | Scrapy alone | Scrapling alone | **ScrapeToolAi** |
|---|---|---|---|
| Cloudflare bypass | ❌ Needs plugins | ✅ StealthyFetcher | ✅ Built-in, 3-tier auto-escalation |
| Site structure changes | ❌ Breaks | ✅ Adaptive selectors | ✅ + AI fallback when adaptive fails |
| Large-scale crawling | ✅ Spider framework | ❌ Single-page only | ✅ Spider framework + stealth fetchers |
| Data pipelines | ✅ Item pipelines | ❌ Manual | ✅ Pipelines + AI cleaning |
| Personal data organizer | ❌ | ❌ | ✅ Import Instagram/Pinterest/bookmarks |
| Prompt library sync | ❌ | ❌ | ✅ Syncs from consecrating/Prompts |
| AI integration | ❌ | ✅ MCP server | ✅ MCP + direct Kiro/ChatGPT/Grok |

---

## Active Skills Integrated

### From Scrapling (D4Vinci/Scrapling)
- **3-Tier Stealth Fetching** — Auto-escalates from fast HTTP → stealth Firefox → full Playwright based on protection level detected
- **Adaptive Element Tracking** — Selectors survive website restructures using similarity algorithms (no AI needed)
- **Anti-Bot Bypass** — Cloudflare Turnstile, WAFs, TLS fingerprint spoofing, canvas randomization, WebRTC blocking
- **Persistent Sessions** — Maintain login state across requests
- **Interactive Shell** — Live exploration and debugging

### From Scrapy (scrapy/scrapy)
- **Spider Framework** — Organized, reusable crawlers with start_urls, parse callbacks, and link following
- **Middleware Pipeline** — Request/response processing hooks (retry, redirect, proxy rotation, throttle)
- **Item Pipelines** — Data cleaning, validation, deduplication, and multi-format storage
- **Scheduler** — Priority queue with duplicate URL filtering
- **Feed Exports** — JSON, CSV, JSONL, XML output formats
- **Signals** — Event system for monitoring and extending behavior
- **AutoThrottle** — Adaptive request timing based on server response

### ScrapeToolAi Originals
- **AI-Powered Extraction** — Describe what you want in plain English, AI generates the selectors
- **Auto-Escalation** — Starts with fastest method, automatically escalates when blocked
- **Personal Data Organizer** — Import your Instagram/Pinterest/Magnific exports, categorize and index locally
- **Prompt Library Sync** — Direct integration with consecrating/Prompts (1,520+ prompts)
- **Platform Bridge** — Generate AI images directly from scraped inspiration

---

## Installation

```bash
# Core (HTTP fetching + parsing + organizer)
pip install -e .

# With stealth browsers (Cloudflare bypass)
pip install -e ".[stealth]"
scrapling install  # Install browser engines

# Full (everything including AI features)
pip install -e ".[full]"
```

### Requirements
- Python 3.10+
- For stealth: `scrapling[fetchers]` handles browser installation
- For AI extraction: OpenAI or Gemini API key (optional — rule-based works without)

---

## Quick Start

### 1. Stealth Scraping (Bypasses Cloudflare)

```python
from scrapetoolai import fetch

# Auto-escalates: HTTP → Stealth Firefox → Full Playwright
page = fetch("https://cloudflare-protected-site.com")

# Adaptive selectors — survive site redesigns
products = page.css(".product-card", adaptive=True)
for p in products:
    print(p.css_first(".title").text, p.css_first(".price").text)
```

### 2. Spider Crawling (Scrapy-style, with stealth)

```python
from scrapetoolai.spider import Spider

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/catalog"]
    
    # Uses StealthyFetcher automatically if Cloudflare detected
    fetcher = "auto"  # or "http", "stealth", "browser"
    
    def parse(self, response):
        for product in response.css(".product", adaptive=True):
            yield {
                "title": product.css_first("h2").text,
                "price": product.css_first(".price").text,
                "image": product.css_first("img").attrib["src"],
            }
        
        # Follow pagination
        next_page = response.css_first("a.next-page")
        if next_page:
            yield self.follow(next_page)

# Run it
ProductSpider.run(output="products.json")
```

### 3. AI-Powered Extraction (No selectors needed)

```python
from scrapetoolai import smart_extract

# Just describe what you want — AI figures out the selectors
results = smart_extract(
    url="https://any-restaurant-website.com/menu",
    extract="menu items with name, price, description, and dietary tags"
)
# Returns structured JSON automatically
```

### 4. Personal Data Import

```python
from scrapetoolai.organizer import import_data, search

# Import your platform exports
import_data("~/Downloads/instagram-export.zip")
import_data("~/Downloads/pinterest-board/")
import_data("~/Pictures/magnific-outputs/")

# Search across everything
results = search("golden hour portrait fashion")
```

### 5. CLI

```bash
# Scrape a URL (auto-detects protection level)
scrapetool fetch https://example.com --output page.json

# Run a spider
scrapetool crawl ProductSpider --output products.csv

# AI extraction
scrapetool extract https://restaurant.com/menu --what "menu items with prices"

# Import personal data
scrapetool import ~/Downloads/instagram-export.zip
scrapetool import ~/Pictures/saved-inspiration/

# Search your collection
scrapetool search "neon portrait editorial"

# Sync prompts
scrapetool sync-prompts

# Interactive shell (like Scrapling's)
scrapetool shell https://example.com

# Start MCP server (for Kiro/Claude/Cursor integration)
scrapetool mcp-server --port 8080
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  USER INTERFACE                                                  │
│  CLI │ Python API │ MCP Server (Kiro/Claude) │ REST API          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  ENGINE (async, event-driven — from Scrapy)                     │
│  Scheduler → Downloader → Spider → Pipeline → Export            │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  FETCHER LAYER (from Scrapling — 3-tier auto-escalation)        │
│                                                                  │
│  Tier 1: HTTPFetcher          Tier 2: StealthFetcher            │
│  • httpx async                • Modified Firefox                 │
│  • TLS fingerprint spoof      • Canvas randomization             │
│  • Stealth headers            • WebRTC blocking                  │
│  • Cookie persistence         • Cloudflare Turnstile bypass      │
│                                                                  │
│  Tier 3: BrowserFetcher       Auto-Escalation Logic:            │
│  • Full Playwright            • Try Tier 1 first (fastest)       │
│  • JS rendering               • If 403/challenge → Tier 2        │
│  • Infinite scroll             • If still blocked → Tier 3       │
│  • Login automation            • Cache which tier works per domain│
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  PARSER (from Scrapling — adaptive tracking)                    │
│  • CSS selectors  • XPath  • Text/regex search                  │
│  • Adaptive element tracking (survives site redesigns)          │
│  • AI selector generation (optional, when adaptive fails)       │
│  • Auto-selector from example data                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  DATA LAYER                                                      │
│  Item Pipelines │ SQLite Index │ Feed Exports │ AI Bridge       │
│  • Cleaning & validation  • Full-text search  • JSON/CSV/JSONL  │
│  • Deduplication          • Category tagging  • Prompt export   │
│  • Personal data import   • Color extraction  • Image gen bridge│
└─────────────────────────────────────────────────────────────────┘
```

---

## Middleware Stack (from Scrapy, enhanced)

```python
# config/settings.py — customize the pipeline
MIDDLEWARES = {
    "scrapetoolai.middleware.AutoEscalation": 100,    # Try fastest, escalate if blocked
    "scrapetoolai.middleware.ProxyRotation": 200,     # Rotate proxies per request
    "scrapetoolai.middleware.RetryMiddleware": 300,   # Retry with backoff
    "scrapetoolai.middleware.ThrottleMiddleware": 400, # Adaptive rate limiting
    "scrapetoolai.middleware.DedupFilter": 500,       # Skip duplicate URLs
    "scrapetoolai.middleware.CacheMiddleware": 600,   # Cache responses locally
}

PIPELINES = {
    "scrapetoolai.pipeline.CleanText": 100,          # Strip HTML, normalize whitespace
    "scrapetoolai.pipeline.ValidateSchema": 200,     # Type-check extracted fields
    "scrapetoolai.pipeline.Deduplicate": 300,        # Content-level dedup (not just URL)
    "scrapetoolai.pipeline.AIEnrich": 400,           # AI categorization (optional)
    "scrapetoolai.pipeline.SQLiteStore": 500,        # Index locally
    "scrapetoolai.pipeline.FeedExport": 600,         # JSON/CSV/JSONL output
}
```

---

## Pre-Built Spiders

| Spider | Target | What It Extracts |
|---|---|---|
| `PromptSpider` | consecrating/Prompts repo | All 1,520+ prompts indexed and searchable |
| `EcommerceSpider` | Any product listing | Name, price, image, description, reviews |
| `RestaurantSpider` | Restaurant websites | Menu items, prices, dietary info, location |
| `RealEstateSpider` | Property listings | Price, beds, baths, sqft, images, address |
| `SocialProfileSpider` | Public social profiles | Bio, post count, recent content |
| `JobListingSpider` | Job boards | Title, company, salary, requirements |
| `NewsSpider` | News sites | Headlines, body, author, date, category |

---

## MCP Server (AI Agent Integration)

Start the MCP server for direct integration with Kiro, Claude, or Cursor:

```bash
scrapetool mcp-server
```

Then in Kiro/Claude:
```
Scrape https://example.com and extract all product listings
Crawl this restaurant site and get the full menu
Import my Instagram export and find all fashion inspiration I saved
Search my collection for "moody neon portrait"
```

---

## Personal Data Organizer

Import your exported/saved content from any platform:

```bash
scrapetool import ~/Downloads/instagram-data.zip     # Instagram data download
scrapetool import ~/Downloads/pinterest-board.json   # Pinterest export
scrapetool import ~/Pictures/magnific/               # Magnific AI outputs
scrapetool import ~/bookmarks.html                   # Browser bookmarks
scrapetool import ~/Pictures/ai-generations/         # Any saved images
scrapetool sync-prompts                              # Fetch from Prompts repo
```

Everything is indexed locally in SQLite with full-text search, auto-categorization, color extraction, and mood detection.

---

## Project Structure

```
ScrapeToolAi/
├── README.md
├── LICENSE (MIT)
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── scrapetoolai/                  # Main package
│   ├── __init__.py                # Public API: fetch(), smart_extract(), search()
│   ├── fetchers/                  # 3-tier fetching (from Scrapling)
│   │   ├── http_fetcher.py        # Tier 1: Fast HTTP with TLS stealth
│   │   ├── stealth_fetcher.py     # Tier 2: Modified Firefox, Cloudflare bypass
│   │   ├── browser_fetcher.py     # Tier 3: Full Playwright automation
│   │   └── escalation.py          # Auto-escalation logic
│   ├── parser/                    # Adaptive parsing (from Scrapling)
│   │   ├── adaptive.py            # Element tracking via similarity
│   │   ├── selectors.py           # CSS + XPath + text search
│   │   └── ai_selector.py         # AI generates selectors when needed
│   ├── spider/                    # Spider framework (from Scrapy)
│   │   ├── base.py                # Spider base class
│   │   ├── engine.py              # Async event-driven engine
│   │   ├── scheduler.py           # URL queue with dedup
│   │   └── prebuilt/              # Ready-to-use spiders
│   │       ├── prompts.py         # consecrating/Prompts syncer
│   │       ├── ecommerce.py       # Generic product scraper
│   │       ├── restaurant.py      # Menu extraction
│   │       └── realestate.py      # Property listings
│   ├── middleware/                # Request/response pipeline (from Scrapy)
│   │   ├── escalation.py          # Auto-escalate on block
│   │   ├── proxy.py               # Proxy rotation
│   │   ├── retry.py               # Smart retry with backoff
│   │   ├── throttle.py            # Adaptive rate limiting
│   │   ├── cache.py               # Response caching
│   │   └── dedup.py               # URL deduplication
│   ├── pipeline/                  # Data processing (from Scrapy)
│   │   ├── clean.py               # Text cleaning
│   │   ├── validate.py            # Schema validation
│   │   ├── dedup.py               # Content dedup (perceptual hash)
│   │   ├── ai_enrich.py           # AI categorization
│   │   ├── store.py               # SQLite storage
│   │   └── export.py              # JSON/CSV/JSONL feeds
│   ├── organizer/                 # Personal data layer
│   │   ├── importer.py            # Platform-specific parsers
│   │   ├── instagram.py
│   │   ├── pinterest.py
│   │   ├── bookmarks.py
│   │   ├── images.py
│   │   └── search.py              # Full-text + category search
│   ├── ai/                        # AI features
│   │   ├── extractor.py           # smart_extract() — describe what you want
│   │   ├── selector_gen.py        # AI generates CSS/XPath from examples
│   │   └── bridge.py              # Feed results to image generators
│   ├── mcp/                       # MCP server for Kiro/Claude
│   │   └── server.py
│   └── cli/                       # Command-line interface
│       └── main.py
│
├── config/
│   ├── settings.py                # Default middleware/pipeline config
│   └── proxies.example.txt        # Proxy list template
│
├── spiders/                       # User's custom spiders go here
│   └── example_spider.py
│
├── data/                          # Local database (gitignored)
├── imports/                       # Drop exports here (gitignored)
└── output/                        # Scrape results (gitignored)
```

---

## Comparison with Other Tools

| Feature | Scrapy | Scrapling | BeautifulSoup | ScrapeToolAi |
|---|---|---|---|---|
| Cloudflare bypass | ❌ | ✅ | ❌ | ✅ |
| Adaptive selectors | ❌ | ✅ | ❌ | ✅ |
| Spider framework | ✅ | Basic | ❌ | ✅ |
| Middleware pipeline | ✅ | ❌ | ❌ | ✅ |
| Auto-escalation | ❌ | ❌ | ❌ | ✅ |
| AI extraction | ❌ | ❌ | ❌ | ✅ |
| Personal data organizer | ❌ | ❌ | ❌ | ✅ |
| MCP server (AI agents) | ❌ | ✅ | ❌ | ✅ |
| Prompt library sync | ❌ | ❌ | ❌ | ✅ |
| Docker ready | ✅ | ✅ | N/A | ✅ |

---

## Credits

- **Scrapling** by [D4Vinci](https://github.com/D4Vinci/Scrapling) — Stealth fetching, adaptive parsing, anti-bot bypass
- **Scrapy** by [Scrapy team](https://github.com/scrapy/scrapy) — Spider framework, middleware, pipelines, engine architecture
- **Mysha** from [consecrating/Prompts](https://github.com/consecrating/Prompts) — Prompt engineering system integration
