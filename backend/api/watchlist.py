from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from backend.database import get_db_context
from backend.logger import log_info, log_error

router = APIRouter()

class WatchlistItem(BaseModel):
    content_type: str  # "movie", "tv", "anime"
    content_id: int
    title: str
    poster_url: Optional[str] = None
    milestone: Optional[str] = None

@router.post("/add")
def add_to_watchlist(item: WatchlistItem):
    """Add an item to the watchlist."""
    try:
        with get_db_context() as db:
            # Create watchlist table if not exists
            db.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,
                    content_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    poster_url TEXT,
                    milestone TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if already exists
            existing = db.execute(
                "SELECT id FROM watchlist WHERE content_type = ? AND content_id = ?",
                (item.content_type, item.content_id)
            ).fetchone()
            
            if existing:
                return {"status": "exists", "message": "Item already in watchlist"}
            
            # Insert new item
            db.execute("""
                INSERT INTO watchlist (content_type, content_id, title, poster_url, milestone)
                VALUES (?, ?, ?, ?, ?)
            """, (item.content_type, item.content_id, item.title, item.poster_url, item.milestone))
            
            log_info(f"Added to watchlist: {item.content_type} {item.content_id}")
            return {"status": "success", "message": "Added to watchlist"}
    except Exception as e:
        log_error(f"Failed to add to watchlist: {e}")
        return {"status": "error", "message": str(e)}

@router.delete("/remove/{item_id}")
def remove_from_watchlist(item_id: int):
    """Remove an item from the watchlist."""
    try:
        with get_db_context() as db:
            db.execute("DELETE FROM watchlist WHERE id = ?", (item_id,))
            log_info(f"Removed from watchlist: {item_id}")
            return {"status": "success", "message": "Removed from watchlist"}
    except Exception as e:
        log_error(f"Failed to remove from watchlist: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/")
def get_watchlist():
    """Get all items in the watchlist."""
    try:
        with get_db_context() as db:
            # Ensure table exists
            db.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,
                    content_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    poster_url TEXT,
                    milestone TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            items = db.execute("""
                SELECT id, content_type, content_id, title, poster_url, milestone, added_at
                FROM watchlist
                ORDER BY added_at DESC
            """).fetchall()
            
            return {"items": [dict(item) for item in items]}
    except Exception as e:
        log_error(f"Failed to get watchlist: {e}")
        return {"status": "error", "message": str(e), "items": []}

@router.put("/milestone/{item_id}")
def update_milestone(item_id: int, milestone: str):
    """Update the milestone for a watchlist item."""
    try:
        with get_db_context() as db:
            db.execute(
                "UPDATE watchlist SET milestone = ? WHERE id = ?",
                (milestone, item_id)
            )
            log_info(f"Updated milestone for watchlist item {item_id}: {milestone}")
            return {"status": "success", "message": "Milestone updated"}
    except Exception as e:
        log_error(f"Failed to update milestone: {e}")
        return {"status": "error", "message": str(e)}
