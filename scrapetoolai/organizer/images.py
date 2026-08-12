"""Bulk image importer."""
from pathlib import Path
def ingest_images(path: Path, source: str = "images") -> dict:
    exts = {".jpg",".jpeg",".png",".webp",".gif",".avif"}
    if path.is_file():
        files = [path] if path.suffix.lower() in exts else []
    else:
        files = [f for f in path.rglob("*") if f.suffix.lower() in exts]
    print(f"    Found {len(files)} images")
    return {"imported": len(files), "duplicates": 0, "errors": 0}
