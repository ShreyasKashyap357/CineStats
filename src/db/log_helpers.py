"""
CineStats — App Log Helpers
Structured event logging to app_log table in SQLite.
"""
import sqlite3
from datetime import datetime, timedelta


def log_event(conn: sqlite3.Connection, level: str, event_type: str,
              source: str = "", entity_key: str = "", message: str = "",
              success: int = 1):
    """Log an event to the app_log table.
    
    Args:
        level: 'INFO', 'WARNING', 'ERROR'
        event_type: 'scrape', 'api_call', 'poster_fetch', 'pdf_export',
                    'user_action', 'error', 'rate_limit'
        source: module name (e.g. 'bom_scraper', 'tmdb_client')
        entity_key: entity identifier (e.g. movie title)
        message: human-readable description
        success: 1 for success, 0 for failure
    """
    conn.execute("""
        INSERT INTO app_log (timestamp, level, event_type, source, entity_key, message, success)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), level, event_type, source,
          entity_key, message, success))
    conn.commit()


def get_recent_events(conn: sqlite3.Connection, limit: int = 50,
                      event_type: str = None) -> list:
    """Get recent log entries, optionally filtered by event_type."""
    if event_type:
        rows = conn.execute(
            "SELECT * FROM app_log WHERE event_type=? ORDER BY timestamp DESC LIMIT ?",
            (event_type, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM app_log ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_recently_added(conn: sqlite3.Connection, limit: int = 10) -> list:
    """Get recently scraped/fetched entities for 'What's New' section."""
    rows = conn.execute("""
        SELECT entity_key, source, timestamp
        FROM app_log
        WHERE event_type IN ('scrape', 'api_call') AND success=1
              AND entity_key IS NOT NULL AND entity_key != ''
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,)).fetchall()
    return [dict(r) for r in rows]


def prune_log(conn: sqlite3.Connection, days: int = 90):
    """Remove log entries older than `days` days."""
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    conn.execute("DELETE FROM app_log WHERE timestamp < ?", (cutoff,))
    conn.commit()
