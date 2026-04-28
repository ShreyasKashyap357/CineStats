from fastapi import APIRouter
from backend.database import get_db_context
from backend.logger import log_info, log_error, get_logger
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()
logger = get_logger("logs-api")

@router.post("/client")
def receive_client_logs(logs: List[Dict[str, Any]]):
    """Receive client-side logs from frontend and store them."""
    try:
        with get_db_context() as db:
            # Check if app_log table exists
            table_check = db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='app_log'
            """).fetchone()
            
            if not table_check:
                logger.warning("app_log table does not exist, skipping client log storage")
                return {"status": "skipped", "message": "app_log table does not exist"}
            
            # Insert client logs
            for log_entry in logs:
                db.execute("""
                    INSERT INTO app_log (timestamp, level, event_type, source, entity_key, message, success)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_entry.get('timestamp', datetime.utcnow().isoformat()),
                    log_entry.get('level', 'INFO'),
                    'client_log',
                    log_entry.get('source', 'frontend'),
                    '',
                    log_entry.get('message', ''),
                    1
                ))
            
            db.commit()
            logger.info(f"Received {len(logs)} client logs")
            return {"status": "success", "count": len(logs)}
    except Exception as e:
        log_error(f"Failed to store client logs: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/")
def get_logs(limit: int = 100, offset: int = 0):
    """Get recent app_log entries."""
    try:
        with get_db_context() as db:
            # Check if app_log table exists
            table_check = db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='app_log'
            """).fetchone()
            
            if not table_check:
                return {"logs": [], "total": 0, "message": "app_log table does not exist"}
            
            # Get logs
            logs = db.execute("""
                SELECT * FROM app_log
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
            
            # Get total count
            total = db.execute("SELECT COUNT(*) FROM app_log").fetchone()[0]
            
            return {
                "logs": [dict(log) for log in logs],
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        log_error(f"Failed to fetch logs: {e}")
        return {"logs": [], "total": 0, "error": str(e)}
