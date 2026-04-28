import sqlite3
from typing import Generator
from src.db.init_db import DB_PATH

import sqlite3
from typing import Generator
from contextlib import contextmanager
from src.db.init_db import DB_PATH

def get_db() -> sqlite3.Connection:
    """Returns a new connection with WAL config."""
    conn = sqlite3.connect(DB_PATH, timeout=15, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=15000")
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency."""
    conn = get_db()
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_db_context():
    """Context manager for backend queue worker."""
    conn = get_db()
    try:
        yield conn
    finally:
        conn.close()
