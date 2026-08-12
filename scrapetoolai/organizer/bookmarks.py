"""Browser bookmarks HTML parser."""
from pathlib import Path
def ingest_bookmarks(path: Path) -> dict:
    content = path.read_text(errors="ignore")
    count = content.count("HREF=")
    print(f"    Found {count} bookmarks")
    return {"imported": count, "duplicates": 0, "errors": 0}
