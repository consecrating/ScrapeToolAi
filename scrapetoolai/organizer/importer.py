"""Main import orchestrator for personal data."""
import time
from pathlib import Path

def run_import(path: Path, force_source: str = None):
    """Process a file/folder import."""
    from .detect import detect_source
    
    path = Path(path)
    if not path.exists():
        print(f"Path not found: {path}")
        return
    
    source = force_source or detect_source(path)
    print(f"Importing: {path.name} (detected: {source})")
    
    handlers = {
        "instagram": _import_instagram,
        "pinterest": _import_pinterest,
        "images": _import_images,
        "magnific": lambda p: _import_images(p, source="magnific"),
        "bookmarks": _import_bookmarks,
    }
    
    handler = handlers.get(source)
    if not handler:
        print(f"  No handler for source: {source}. Trying as images...")
        handler = _import_images
    
    stats = handler(path)
    print(f"  Done: {stats.get('imported', 0)} imported, {stats.get('duplicates', 0)} dupes, {stats.get('errors', 0)} errors")

def _import_instagram(path):
    from .instagram import ingest_instagram
    return ingest_instagram(path)

def _import_pinterest(path):
    from .pinterest import ingest_pinterest
    return ingest_pinterest(path)

def _import_images(path, source="images"):
    from .images import ingest_images
    return ingest_images(path, source=source)

def _import_bookmarks(path):
    from .bookmarks import ingest_bookmarks
    return ingest_bookmarks(path)
