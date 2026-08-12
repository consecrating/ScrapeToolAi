"""Sync prompts from consecrating/Prompts repo."""
import re, json, time, hashlib
from pathlib import Path
from urllib.request import urlopen, Request

REPO = "consecrating/Prompts"
RAW = f"https://raw.githubusercontent.com/{REPO}/main"
CATEGORIES = ["portrait","fashion-editorial","cinematic","product","travel-landscape",
    "street-photography","fantasy-conceptual","fitness-athletic","food-culinary",
    "architecture-interior","lifestyle","nature-wildlife","night-neon","vintage-retro",
    "surreal","underwater","swimwear-beachwear","lingerie-intimate","boudoir-artistic",
    "cultural-fashion","festival-posters","instagram-business","real-estate","hotels",
    "restaurants","digital-marketing","youtube-thumbnails","youtube-blog-thumbnails",
    "website-banners","modern-youth-fashion"]

def sync_prompts():
    print(f"Syncing from github.com/{REPO}...")
    total = 0
    for cat in CATEGORIES:
        try:
            url = f"{RAW}/prompts/{cat}/prompts.md"
            req = Request(url, headers={"User-Agent": "ScrapeToolAi/1.0"})
            content = urlopen(req, timeout=10).read().decode()
            count = content.count("## ")
            total += count
            print(f"  {cat}: {count} prompts")
            time.sleep(0.3)
        except Exception as e:
            print(f"  {cat}: error ({e})")
    print(f"\nTotal: {total} prompts synced from {REPO}")
