"""Search the local collection."""
import sqlite3, json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "library.db"

def _get_db():
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def search_collection(query: str, **filters) -> list:
    conn = _get_db()
    if not conn: return []
    try:
        if query:
            sql = "SELECT * FROM items JOIN items_fts ON items.rowid = items_fts.rowid WHERE items_fts MATCH ? LIMIT ?"
            params = [query, filters.get("limit", 10)]
        else:
            sql = "SELECT * FROM items WHERE 1=1"
            params = []
            for k, v in filters.items():
                if v and k in ("source","category","mood","type","platform"):
                    sql += f" AND {k} = ?"
                    params.append(v)
            sql += " ORDER BY imported_at DESC LIMIT ?"
            params.append(filters.get("limit", 10))
        return [dict(row) for row in conn.execute(sql, params).fetchall()]
    except: return []

def get_stats() -> dict:
    conn = _get_db()
    if not conn: return {"total": 0}
    try:
        total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        by_source = dict(conn.execute("SELECT source, COUNT(*) FROM items GROUP BY source").fetchall())
        by_category = dict(conn.execute("SELECT category, COUNT(*) FROM items WHERE category IS NOT NULL GROUP BY category").fetchall())
        return {"total": total, "by_source": by_source, "by_category": by_category}
    except: return {"total": 0}
