"""Pinterest export parser."""
from pathlib import Path
def ingest_pinterest(path: Path) -> dict:
    print("    Pinterest import: download your data from Settings → Privacy → Request data")
    return {"imported": 0, "duplicates": 0, "errors": 0}
