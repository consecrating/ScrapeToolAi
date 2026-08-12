"""Instagram data export parser. See src/ingest/instagram.py for full implementation."""
from pathlib import Path
def ingest_instagram(path: Path) -> dict:
    print("    Instagram import requires: pip install 'scrapetoolai[full]'")
    print("    Export your data: Instagram → Settings → Your Activity → Download Your Information")
    return {"imported": 0, "duplicates": 0, "errors": 0}
