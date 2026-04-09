"""
CineStats — Scrape Cache Helpers
Session-level caching to prevent re-fetching the same entity within a session.
"""
import sqlite3
from datetime import datetime, timedelta


def check_cache(conn: sqlite3.Connection, source: str, entity_key: str,
                session_id: str) -> bool:
    """Check if an entity was already fetched in this session."""
    row = conn.execute(
        "SELECT 1 FROM scrape_cache WHERE source=? AND entity_key=? AND session_id=?",
        (source, entity_key, session_id)
    ).fetchone()
    return row is not None


def set_cache(conn: sqlite3.Connection, source: str, entity_key: str,
              session_id: str):
    """Mark an entity as fetched in this session."""
    conn.execute(
        """INSERT OR IGNORE INTO scrape_cache (source, entity_key, session_id)
           VALUES (?, ?, ?)""",
        (source, entity_key, session_id)
    )
    conn.commit()


def prune_cache(conn: sqlite3.Connection, days: int = 7):
    """Remove cache entries older than `days` days."""
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    conn.execute("DELETE FROM scrape_cache WHERE scraped_at < ?", (cutoff,))
    conn.commit()
