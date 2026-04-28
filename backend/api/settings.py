from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from backend.database import get_db_context
from backend.logger import log_info, log_error

router = APIRouter()

class SettingsRequest(BaseModel):
    currency: str = "INR"
    country_lens: List[str] = ["Global", "India"]
    theme: str = "dark"
    expandable_threshold: int = 5
    pdf_always_expanded: bool = True

@router.post("/")
def save_settings(settings: SettingsRequest):
    """Save user settings to database."""
    try:
        with get_db_context() as db:
            # Check if settings table exists, create if not
            db.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency TEXT DEFAULT 'INR',
                    country_lens TEXT DEFAULT '["Global", "India"]',
                    theme TEXT DEFAULT 'dark',
                    expandable_threshold INTEGER DEFAULT 5,
                    pdf_always_expanded INTEGER DEFAULT 1,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Upsert settings (replace existing or insert new)
            db.execute("""
                INSERT INTO user_settings (currency, country_lens, theme, expandable_threshold, pdf_always_expanded)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    currency = excluded.currency,
                    country_lens = excluded.country_lens,
                    theme = excluded.theme,
                    expandable_threshold = excluded.expandable_threshold,
                    pdf_always_expanded = excluded.pdf_always_expanded,
                    last_updated = CURRENT_TIMESTAMP
            """, (
                settings.currency,
                str(settings.country_lens),
                settings.theme,
                settings.expandable_threshold,
                1 if settings.pdf_always_expanded else 0
            ))
            
            log_info(f"Settings saved: {settings.dict()}")
            return {"status": "success", "message": "Settings saved successfully"}
    except Exception as e:
        log_error(f"Failed to save settings: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/")
def get_settings():
    """Get current user settings."""
    try:
        with get_db_context() as db:
            # Ensure table exists
            db.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency TEXT DEFAULT 'INR',
                    country_lens TEXT DEFAULT '["Global", "India"]',
                    theme TEXT DEFAULT 'dark',
                    expandable_threshold INTEGER DEFAULT 5,
                    pdf_always_expanded INTEGER DEFAULT 1,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            row = db.execute("SELECT * FROM user_settings WHERE id = 1").fetchone()
            
            if row:
                import json
                return {
                    "currency": row["currency"],
                    "country_lens": json.loads(row["country_lens"]),
                    "theme": row["theme"],
                    "expandable_threshold": row["expandable_threshold"],
                    "pdf_always_expanded": bool(row["pdf_always_expanded"]),
                    "last_updated": row["last_updated"]
                }
            else:
                # Return defaults
                return {
                    "currency": "INR",
                    "country_lens": ["Global", "India"],
                    "theme": "dark",
                    "expandable_threshold": 5,
                    "pdf_always_expanded": True,
                    "last_updated": None
                }
    except Exception as e:
        log_error(f"Failed to get settings: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/cleanup")
def cleanup_database():
    """Clean up database - delete all data except settings."""
    try:
        with get_db_context() as db:
            # Get list of all tables
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [t["name"] for t in tables]
            
            # Tables to preserve (user_settings and system tables)
            preserve_tables = ["user_settings", "sqlite_sequence"]
            
            deleted_counts = {}
            
            for table in table_names:
                if table not in preserve_tables:
                    # Get count before deletion
                    count_result = db.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                    count = count_result["count"] if count_result else 0
                    
                    if count > 0:
                        # Delete all rows from table
                        db.execute(f"DELETE FROM {table}")
                        deleted_counts[table] = count
                        log_info(f"Cleared {count} rows from table: {table}")
            
            log_info(f"Database cleanup completed. Deleted counts: {deleted_counts}")
            return {
                "status": "success",
                "message": "Database cleaned successfully",
                "deleted_counts": deleted_counts
            }
    except Exception as e:
        log_error(f"Failed to cleanup database: {e}")
        return {"status": "error", "message": str(e)}
