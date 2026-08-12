"""Auto-detect source type from file/folder."""
import zipfile, json
from pathlib import Path

def detect_source(path: Path) -> str:
    path = Path(path)
    if path.suffix == ".zip":
        try:
            with zipfile.ZipFile(path) as zf:
                names = " ".join(zf.namelist()[:50])
                if "saved_posts" in names or "liked_posts" in names or "media/posts" in names:
                    return "instagram"
                if "tweet" in names:
                    return "twitter"
                if "pins" in names:
                    return "pinterest"
        except: pass
        return "images"
    if path.suffix == ".json":
        try:
            data = json.loads(path.read_text()[:5000])
            if isinstance(data, dict):
                if "board" in data or "pins" in data: return "pinterest"
                if "saved_media" in data: return "instagram"
        except: pass
        return "generic"
    if path.suffix in (".html", ".htm"):
        text = path.read_text(errors="ignore")[:1000]
        if "NETSCAPE-Bookmark" in text: return "bookmarks"
    if path.is_dir():
        children = [c.name.lower() for c in path.iterdir()]
        if "saved_posts" in children or "media" in children: return "instagram"
        img_exts = {".jpg",".jpeg",".png",".webp",".gif"}
        imgs = [c for c in path.iterdir() if c.suffix.lower() in img_exts]
        if len(imgs) > 3: return "images"
    if path.suffix.lower() in (".jpg",".jpeg",".png",".webp",".gif"):
        return "images"
    return "generic"
