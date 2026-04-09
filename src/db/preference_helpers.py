"""
CineStats — User Preference Helpers
CRUD for user_preferences, watchlist, and saved_comparisons tables.
Keyed by anonymous UUID (Section 3.6).
"""
import sqlite3
from datetime import datetime
from typing import Optional
import json


# ── User Preferences ────────────────────────────────────────────────────────

def get_pref(conn: sqlite3.Connection, user_uuid: str,
             pref_key: str, default: str = None) -> Optional[str]:
    """Get a single preference value."""
    row = conn.execute(
        "SELECT pref_value FROM user_preferences WHERE user_uuid=? AND pref_key=?",
        (user_uuid, pref_key)
    ).fetchone()
    return row[0] if row else default


def set_pref(conn: sqlite3.Connection, user_uuid: str,
             pref_key: str, pref_value: str):
    """Set a single preference value."""
    conn.execute("""
        INSERT INTO user_preferences (user_uuid, pref_key, pref_value, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_uuid, pref_key) DO UPDATE SET
            pref_value=excluded.pref_value,
            updated_at=excluded.updated_at
    """, (user_uuid, pref_key, pref_value, datetime.utcnow().isoformat()))
    conn.commit()


def get_all_prefs(conn: sqlite3.Connection, user_uuid: str) -> dict:
    """Get all preferences for a user as a dict."""
    rows = conn.execute(
        "SELECT pref_key, pref_value FROM user_preferences WHERE user_uuid=?",
        (user_uuid,)
    ).fetchall()
    return {row[0]: row[1] for row in rows}


# ── Watchlist ────────────────────────────────────────────────────────────────

def add_to_watchlist(conn: sqlite3.Connection, user_uuid: str, entity_id: int,
                     entity_type: str, milestone_target: float = None,
                     notes: str = None) -> int:
    """Add an entity to the user's watchlist."""
    conn.execute("""
        INSERT INTO watchlist (user_uuid, entity_id, entity_type,
                             milestone_target, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (user_uuid, entity_id, entity_type, milestone_target, notes))
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def remove_from_watchlist(conn: sqlite3.Connection, user_uuid: str,
                          entity_id: int, entity_type: str):
    """Remove an entity from the user's watchlist."""
    conn.execute(
        "DELETE FROM watchlist WHERE user_uuid=? AND entity_id=? AND entity_type=?",
        (user_uuid, entity_id, entity_type)
    )
    conn.commit()


def get_watchlist(conn: sqlite3.Connection, user_uuid: str,
                  entity_type: str = None) -> list:
    """Get the user's watchlist, optionally filtered by type."""
    if entity_type:
        rows = conn.execute(
            "SELECT * FROM watchlist WHERE user_uuid=? AND entity_type=? ORDER BY added_at DESC",
            (user_uuid, entity_type)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM watchlist WHERE user_uuid=? ORDER BY added_at DESC",
            (user_uuid,)
        ).fetchall()
    return [dict(r) for r in rows]


def is_in_watchlist(conn: sqlite3.Connection, user_uuid: str,
                    entity_id: int, entity_type: str) -> bool:
    """Check if an entity is in the user's watchlist."""
    row = conn.execute(
        "SELECT 1 FROM watchlist WHERE user_uuid=? AND entity_id=? AND entity_type=?",
        (user_uuid, entity_id, entity_type)
    ).fetchone()
    return row is not None


# ── Saved Comparisons ────────────────────────────────────────────────────────

def save_comparison(conn: sqlite3.Connection, user_uuid: str,
                    comparison_name: str, comparison_type: str,
                    entity_ids: list, entity_types: list = None) -> int:
    """Save a comparison configuration."""
    conn.execute("""
        INSERT INTO saved_comparisons
            (user_uuid, comparison_name, comparison_type, entity_ids, entity_types)
        VALUES (?, ?, ?, ?, ?)
    """, (user_uuid, comparison_name, comparison_type,
          json.dumps(entity_ids), json.dumps(entity_types or [])))
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def get_saved_comparisons(conn: sqlite3.Connection, user_uuid: str) -> list:
    """Get all saved comparisons for a user."""
    rows = conn.execute(
        "SELECT * FROM saved_comparisons WHERE user_uuid=? ORDER BY created_at DESC",
        (user_uuid,)
    ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["entity_ids"] = json.loads(d["entity_ids"]) if d["entity_ids"] else []
        d["entity_types"] = json.loads(d["entity_types"]) if d["entity_types"] else []
        result.append(d)
    return result


def delete_comparison(conn: sqlite3.Connection, comparison_id: int,
                      user_uuid: str):
    """Delete a saved comparison."""
    conn.execute(
        "DELETE FROM saved_comparisons WHERE id=? AND user_uuid=?",
        (comparison_id, user_uuid)
    )
    conn.commit()
