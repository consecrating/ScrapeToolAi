#!/usr/bin/env python3
"""
ScrapeToolAi CLI — unified command interface.

Usage:
    scrapetool fetch <url> [--tier auto|http|stealth|browser] [--output file]
    scrapetool extract <url> --what "description of what to extract"
    scrapetool crawl <SpiderName> [--output file]
    scrapetool shell <url>
    scrapetool import <path> [--source instagram|pinterest|images|bookmarks]
    scrapetool search <query> [--category cat] [--source src] [--limit n]
    scrapetool sync-prompts
    scrapetool stats
    scrapetool mcp-server [--port 8080]
"""

import sys
import json
import argparse


def cmd_fetch(args):
    """Fetch a URL with stealth auto-escalation."""
    from scrapetoolai import fetch
    
    print(f"Fetching: {args.url} (tier={args.tier})")
    page = fetch(args.url, tier=args.tier)
    
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(page.html if hasattr(page, 'html') else str(page), encoding="utf-8")
        print(f"Saved to: {args.output}")
    else:
        # Print summary
        text = page.get_text() if hasattr(page, 'get_text') else str(page)
        print(f"Status: {page.status_code if hasattr(page, 'status_code') else 'OK'}")
        print(f"Length: {len(page.html if hasattr(page, 'html') else '')} chars")
        print(f"Text preview: {text[:500]}...")


def cmd_extract(args):
    """AI-powered extraction."""
    from scrapetoolai import smart_extract
    
    print(f"Extracting from: {args.url}")
    print(f"Looking for: {args.what}")
    results = smart_extract(args.url, args.what)
    
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Saved {len(results)} items to {args.output}")
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))


def cmd_crawl(args):
    """Run a spider."""
    # Try to import from prebuilt spiders
    spider_name = args.spider.lower()
    
    prebuilt = {
        "prompts": "scrapetoolai.spider.prebuilt.prompts.PromptSpider",
        "ecommerce": "scrapetoolai.spider.prebuilt.ecommerce.EcommerceSpider",
    }
    
    if spider_name in prebuilt:
        module_path, class_name = prebuilt[spider_name].rsplit(".", 1)
        import importlib
        mod = importlib.import_module(module_path)
        SpiderClass = getattr(mod, class_name)
    else:
        # Try to import from user's spiders/ directory
        try:
            sys.path.insert(0, ".")
            import importlib
            mod = importlib.import_module(f"spiders.{spider_name}")
            SpiderClass = None
            for attr in dir(mod):
                obj = getattr(mod, attr)
                if isinstance(obj, type) and hasattr(obj, 'parse') and obj.__name__ != 'Spider':
                    SpiderClass = obj
                    break
            if not SpiderClass:
                print(f"No spider class found in spiders/{spider_name}.py")
                return
        except ImportError:
            print(f"Spider '{spider_name}' not found. Available: {', '.join(prebuilt.keys())}")
            return
    
    SpiderClass.run(output=args.output)


def cmd_import(args):
    """Import personal data exports."""
    from pathlib import Path
    from scrapetoolai.organizer.importer import run_import
    
    path = Path(args.path)
    if not path.exists():
        print(f"Path not found: {path}")
        return
    
    run_import(path, force_source=args.source)


def cmd_search(args):
    """Search personal collection."""
    from scrapetoolai import search
    
    results = search(
        args.query,
        source=args.source,
        category=args.category,
        limit=args.limit,
    )
    
    if not results:
        print("No results. Run 'scrapetool import' or 'scrapetool sync-prompts' first.")
        return
    
    print(f"Found {len(results)} results:\n")
    for item in results:
        print(f"  [{item.get('source', '?')}] {item.get('title', 'Untitled')}")
        if item.get('prompt_text'):
            print(f"    {item['prompt_text'][:150]}...")
        elif item.get('description'):
            print(f"    {item['description'][:150]}...")
        print()


def cmd_sync_prompts(args):
    """Sync prompts from consecrating/Prompts repo."""
    from scrapetoolai.organizer.prompt_sync import sync_prompts
    sync_prompts()


def cmd_stats(args):
    """Show collection statistics."""
    from scrapetoolai.organizer.search import get_stats
    stats = get_stats()
    
    print(f"{'='*50}")
    print(f"  ScrapeToolAi Collection: {stats.get('total', 0)} items")
    print(f"{'='*50}")
    
    for section, data in stats.items():
        if section == "total":
            continue
        if data:
            print(f"\n  {section.replace('by_', 'By ').title()}:")
            for key, count in sorted(data.items(), key=lambda x: -x[1])[:10]:
                print(f"    {key:25s} {count:5d}")
    print()


def cmd_shell(args):
    """Interactive shell for exploring a page."""
    from scrapetoolai import fetch
    
    print(f"Fetching: {args.url}")
    page = fetch(args.url)
    print(f"Page loaded ({len(page.html) if hasattr(page, 'html') else 0} chars)")
    print(f"Available: page.css('.selector'), page.xpath('//path'), page.find_all('tag')")
    print(f"Type: page.get_text()[:500] to preview content")
    print()
    
    # Drop into interactive Python
    try:
        import IPython
        IPython.embed(header="ScrapeToolAi Shell — page object is ready")
    except ImportError:
        import code
        code.interact(local={"page": page, "fetch": fetch}, banner="ScrapeToolAi Shell (page ready)")


def cmd_mcp(args):
    """Start MCP server for AI agent integration."""
    print(f"Starting MCP server on port {args.port}...")
    print("Connect from Kiro, Claude, or Cursor using MCP protocol.")
    from scrapetoolai.mcp.server import start_server
    start_server(port=args.port)


def main():
    parser = argparse.ArgumentParser(prog="scrapetool", description="ScrapeToolAi — Super-advanced web scraping")
    subparsers = parser.add_subparsers(dest="command")

    # fetch
    p = subparsers.add_parser("fetch", help="Fetch a URL with stealth")
    p.add_argument("url")
    p.add_argument("--tier", default="auto", choices=["auto", "http", "stealth", "browser"])
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_fetch)

    # extract
    p = subparsers.add_parser("extract", help="AI-powered data extraction")
    p.add_argument("url")
    p.add_argument("--what", "-w", required=True, help="Describe what to extract")
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_extract)

    # crawl
    p = subparsers.add_parser("crawl", help="Run a spider")
    p.add_argument("spider", help="Spider name (prebuilt or from spiders/ dir)")
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_crawl)

    # shell
    p = subparsers.add_parser("shell", help="Interactive exploration shell")
    p.add_argument("url")
    p.set_defaults(func=cmd_shell)

    # import
    p = subparsers.add_parser("import", help="Import personal data exports")
    p.add_argument("path")
    p.add_argument("--source", choices=["instagram", "pinterest", "images", "magnific", "bookmarks"])
    p.set_defaults(func=cmd_import)

    # search
    p = subparsers.add_parser("search", help="Search your collection")
    p.add_argument("query")
    p.add_argument("--category", "-c")
    p.add_argument("--source", "-s")
    p.add_argument("--limit", "-l", type=int, default=10)
    p.set_defaults(func=cmd_search)

    # sync-prompts
    p = subparsers.add_parser("sync-prompts", help="Sync from Prompts repo")
    p.set_defaults(func=cmd_sync_prompts)

    # stats
    p = subparsers.add_parser("stats", help="Collection stats")
    p.set_defaults(func=cmd_stats)

    # mcp-server
    p = subparsers.add_parser("mcp-server", help="Start MCP server for AI integration")
    p.add_argument("--port", "-p", type=int, default=8080)
    p.set_defaults(func=cmd_mcp)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
