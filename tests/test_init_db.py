"""Tests for CineStats database initialisation."""
import unittest
import os
import tempfile
import sqlite3
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.db.init_db import init_db, get_connection, _create_tables


class TestInitDB(unittest.TestCase):
    """Test database initialisation and schema creation."""

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
        # Clean up WAL files if they exist
        for suffix in ["-wal", "-shm"]:
            p = self.db_path + suffix
            if os.path.exists(p):
                os.unlink(p)

    def test_creates_all_tables(self):
        """All 12+ tables should exist after init."""
        init_db(self.db_path)
        conn = get_connection(self.db_path)

        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = {t[0] for t in tables}

        expected = {
            "movies", "franchises", "daily_performance",
            "tv_series", "tv_episodes",
            "anime", "anime_seasons", "anime_episodes",
            "scrape_cache", "app_log",
            "user_preferences", "watchlist", "saved_comparisons",
            "match_overrides", "db_version",
        }

        for t in expected:
            self.assertIn(t, table_names, f"Table '{t}' missing from schema")

        conn.close()

    def test_wal_mode_enabled(self):
        """WAL journal mode should be enabled."""
        init_db(self.db_path)
        conn = get_connection(self.db_path)
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        self.assertEqual(mode.lower(), "wal")
        conn.close()

    def test_schema_version_recorded(self):
        """Schema version should be recorded in db_version."""
        init_db(self.db_path)
        conn = get_connection(self.db_path)
        row = conn.execute("SELECT version FROM db_version ORDER BY id DESC LIMIT 1").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 1)
        conn.close()

    def test_idempotent_init(self):
        """Running init_db twice should not error or duplicate."""
        init_db(self.db_path)
        init_db(self.db_path)  # should not raise
        conn = get_connection(self.db_path)
        versions = conn.execute("SELECT COUNT(*) FROM db_version").fetchone()[0]
        self.assertEqual(versions, 1, "Should not duplicate version entries")
        conn.close()

    def test_upsert_does_not_duplicate(self):
        """INSERT OR REPLACE should not create duplicates."""
        init_db(self.db_path)
        conn = get_connection(self.db_path)

        conn.execute("""
            INSERT INTO movies (title_normalized, title_display, source)
            VALUES ('test movie', 'Test Movie', 'test')
        """)
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
        self.assertEqual(count, 1)
        conn.close()


class TestGetConnection(unittest.TestCase):
    """Test database connection configuration."""

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
        for suffix in ["-wal", "-shm"]:
            p = self.db_path + suffix
            if os.path.exists(p):
                os.unlink(p)

    def test_foreign_keys_enabled(self):
        """Foreign keys should be enabled."""
        conn = get_connection(self.db_path)
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        self.assertEqual(fk, 1)
        conn.close()

    def test_row_factory(self):
        """Row factory should be sqlite3.Row."""
        conn = get_connection(self.db_path)
        self.assertEqual(conn.row_factory, sqlite3.Row)
        conn.close()


if __name__ == "__main__":
    unittest.main()
