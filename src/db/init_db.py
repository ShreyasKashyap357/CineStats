"""
CineStats — Database Initialisation & Schema Management
Section 17 of the v1.0 specification.

Creates all 12 tables, enables WAL mode, handles seed.db copy on cold start,
and runs schema migrations via the db_version table.
"""
import os
import shutil
import sqlite3
from constants import DB_PATH, SEED_DB_PATH, SCHEMA_VERSION


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Get a SQLite connection with WAL mode and foreign keys enabled."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def _create_tables(conn: sqlite3.Connection):
    """Create all CineStats tables if they don't exist."""
    conn.executescript("""
        -- Movies
        CREATE TABLE IF NOT EXISTS movies (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            title_normalized    TEXT NOT NULL,
            title_display       TEXT,
            release_date        DATE,
            origin_country      TEXT,
            language            TEXT,
            genre               TEXT,
            franchise_id        INTEGER REFERENCES franchises(id),
            worldwide_gross_usd REAL,
            domestic_gross_usd  REAL,
            foreign_gross_usd   REAL,
            india_net_cr        REAL,
            india_gross_cr      REAL,
            opening_weekend_usd REAL,
            theater_count       INTEGER,
            verdict             TEXT,
            days_in_release     INTEGER,
            runtime_mins        INTEGER,
            tmdb_id             INTEGER,
            bom_id              TEXT,
            sacnilk_id          TEXT,
            total_shows_sacnilk INTEGER,
            overseas_gross_cr   REAL,
            source              TEXT,
            match_confidence    REAL,
            last_updated        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Movie Regional Rollout (BOM)
        CREATE TABLE IF NOT EXISTS movie_rollout (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id            INTEGER REFERENCES movies(id),
            country_name        TEXT NOT NULL,
            region              TEXT,
            gross_usd           REAL,
            opening_usd         REAL,
            release_date        DATE,
            source_url          TEXT,
            UNIQUE(movie_id, country_name)
        );

        -- Scrape Jobs Queue
        CREATE TABLE IF NOT EXISTS scrape_jobs (
            id                  TEXT PRIMARY KEY,
            status              TEXT NOT NULL,
            module              TEXT NOT NULL,
            progress_pct        INTEGER DEFAULT 0,
            message             TEXT,
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Franchises (3-level hierarchy via self-reference)
        CREATE TABLE IF NOT EXISTS franchises (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            name                    TEXT NOT NULL,
            name_normalized         TEXT,
            parent_franchise_id     INTEGER REFERENCES franchises(id),
            franchise_type          TEXT,
            relationship_tag        TEXT,
            cumulative_worldwide_usd REAL,
            cumulative_india_net_cr REAL,
            first_release           DATE,
            latest_release          DATE,
            total_entries           INTEGER,
            last_updated            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Daily box office performance
        CREATE TABLE IF NOT EXISTS daily_performance (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id            INTEGER REFERENCES movies(id),
            date                DATE,
            daily_gross_usd     REAL,
            daily_india_net_cr  REAL,
            cumulative_gross_usd REAL,
            cumulative_india_net REAL,
            theater_count       INTEGER,
            UNIQUE(movie_id, date)
        );

        -- TV Series (also covers western_animation, cartoon)
        CREATE TABLE IF NOT EXISTS tv_series (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            title_normalized  TEXT NOT NULL,
            title_display     TEXT,
            origin_country    TEXT,
            network           TEXT,
            genre             TEXT,
            status            TEXT,
            premiere_date     DATE,
            total_seasons     INTEGER,
            total_episodes    INTEGER,
            avg_rating        REAL,
            content_type      TEXT,
            age_rating        TEXT,
            is_kodomomuke     INTEGER DEFAULT 0,
            tvmaze_id         INTEGER,
            tmdb_id           INTEGER,
            last_updated      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- TV Episodes
        CREATE TABLE IF NOT EXISTS tv_episodes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id       INTEGER REFERENCES tv_series(id),
            season          INTEGER,
            episode         INTEGER,
            title           TEXT,
            air_date        DATE,
            rating          REAL,
            us_viewers      REAL,
            india_trp       REAL,
            UNIQUE(series_id, season, episode)
        );

        -- Anime
        CREATE TABLE IF NOT EXISTS anime (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title_normalized TEXT NOT NULL,
            title_japanese  TEXT,
            title_english   TEXT,
            mal_id          INTEGER,
            anilist_id      INTEGER,
            mal_score       REAL,
            mal_rank        INTEGER,
            mal_popularity  INTEGER,
            mal_members     INTEGER,
            mal_favourites  INTEGER,
            anilist_score   REAL,
            anilist_popularity INTEGER,
            episodes        INTEGER,
            status          TEXT,
            demographic     TEXT,
            genre           TEXT,
            studio          TEXT,
            source_material TEXT,
            season          TEXT,
            season_year     INTEGER,
            origin_country  TEXT DEFAULT 'JP',
            poster_url      TEXT,
            last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Anime Seasons / Cours
        CREATE TABLE IF NOT EXISTS anime_seasons (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            anime_id        INTEGER REFERENCES anime(id),
            season_number   INTEGER,
            cour_number     INTEGER,
            title           TEXT,
            episodes_start  INTEGER,
            episodes_end    INTEGER,
            arc_name        TEXT,
            is_split        INTEGER DEFAULT 0,
            UNIQUE(anime_id, season_number, cour_number)
        );

        -- Anime Episodes
        CREATE TABLE IF NOT EXISTS anime_episodes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            anime_id        INTEGER REFERENCES anime(id),
            episode_number  INTEGER,
            title           TEXT,
            title_japanese  TEXT,
            air_date        DATE,
            mal_score       REAL,
            UNIQUE(anime_id, episode_number)
        );

        -- Scrape Cache (session-level)
        CREATE TABLE IF NOT EXISTS scrape_cache (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            source          TEXT NOT NULL,
            entity_key      TEXT NOT NULL,
            session_id      TEXT NOT NULL,
            scraped_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source, entity_key, session_id)
        );

        -- Application Event Log
        CREATE TABLE IF NOT EXISTS app_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            level           TEXT,
            event_type      TEXT,
            source          TEXT,
            entity_key      TEXT,
            message         TEXT,
            success         INTEGER
        );

        -- User Preferences (keyed by anonymous UUID)
        CREATE TABLE IF NOT EXISTS user_preferences (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_uuid       TEXT NOT NULL,
            pref_key        TEXT NOT NULL,
            pref_value      TEXT,
            updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_uuid, pref_key)
        );

        -- Watchlist
        CREATE TABLE IF NOT EXISTS watchlist (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_uuid       TEXT NOT NULL,
            entity_id       INTEGER NOT NULL,
            entity_type     TEXT NOT NULL,
            added_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            milestone_target REAL,
            notes           TEXT
        );

        -- Saved Comparisons
        CREATE TABLE IF NOT EXISTS saved_comparisons (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_uuid        TEXT NOT NULL,
            comparison_name  TEXT NOT NULL,
            comparison_type  TEXT,
            entity_ids       TEXT,
            entity_types     TEXT,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Match Overrides (manual title mapping)
        CREATE TABLE IF NOT EXISTS match_overrides (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            source_title            TEXT NOT NULL,
            source                  TEXT NOT NULL,
            target_title_normalized TEXT NOT NULL,
            target_entity_type      TEXT,
            notes                   TEXT,
            created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Schema Version Tracking
        CREATE TABLE IF NOT EXISTS db_version (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            version         INTEGER NOT NULL,
            applied_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description     TEXT
        );
    """)


def _record_version(conn: sqlite3.Connection, version: int, description: str):
    """Record a schema version in the db_version table."""
    conn.execute(
        "INSERT INTO db_version (version, description) VALUES (?, ?)",
        (version, description)
    )
    conn.commit()


def _get_current_version(conn: sqlite3.Connection) -> int:
    """Get the current schema version, or 0 if no versions recorded."""
    try:
        row = conn.execute(
            "SELECT MAX(version) FROM db_version"
        ).fetchone()
        return row[0] if row and row[0] else 0
    except sqlite3.OperationalError:
        return 0


def init_db(db_path: str = DB_PATH):
    """Initialise the CineStats database.
    
    On cold start (db doesn't exist):
      - If seed.db exists, copy it as the starting database.
      - Otherwise, create fresh and apply full schema.
    
    On warm start (db exists):
      - Check schema version and run any pending migrations.
    """
    cold_start = not os.path.exists(db_path)

    if cold_start and os.path.exists(SEED_DB_PATH):
        shutil.copy2(SEED_DB_PATH, db_path)
        print(f"[CineStats] Cold start: copied {SEED_DB_PATH} → {db_path}")

    conn = get_connection(db_path)
    try:
        _create_tables(conn)

        current = _get_current_version(conn)
        
        # Apply v1 Migration
        if current < 1:
            _record_version(conn, 1, "v1: Initial schema — all 12 tables")
            print("[CineStats] Schema v1 applied.")
            current = 1
            
        # Apply v2 Migration
        if current < 2:
            print("[CineStats] Applying Schema v2 migrations...")
            try:
                conn.execute("ALTER TABLE movies ADD COLUMN bom_id TEXT")
                conn.execute("ALTER TABLE movies ADD COLUMN sacnilk_id TEXT")
                conn.execute("ALTER TABLE movies ADD COLUMN total_shows_sacnilk INTEGER")
                conn.execute("ALTER TABLE movies ADD COLUMN overseas_gross_cr   REAL")
                conn.execute("ALTER TABLE movie_rollout ADD COLUMN source_url TEXT")
            except sqlite3.OperationalError as e:
                pass
                
        # Apply v3 Migration
        if current < 3:
            print("[CineStats] Applying Schema v3 migrations...")
            try:
                conn.execute("ALTER TABLE movie_rollout ADD COLUMN source_url TEXT")
            except sqlite3.OperationalError:
                pass
                
        # Apply v4 Migration
        if current < 4:
            print("[CineStats] Applying Schema v4 migrations (Records & Franchises)...")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS franchises (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT NOT NULL,
                    type        TEXT NOT NULL, -- 'brand', 'franchise', 'genre'
                    url         TEXT UNIQUE
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS movie_franchises (
                    movie_id        INTEGER REFERENCES movies(id),
                    franchise_id    INTEGER REFERENCES franchises(id),
                    UNIQUE(movie_id, franchise_id)
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    title       TEXT NOT NULL,
                    category    TEXT,
                    source      TEXT,
                    url         TEXT UNIQUE
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS record_entries (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id       INTEGER REFERENCES records(id),
                    rank            INTEGER,
                    movie_title     TEXT,
                    primary_value   TEXT,
                    metadata_json   TEXT,
                    UNIQUE(record_id, rank, movie_title)
                );
            """)
                
            _record_version(conn, 4, "v4: Added franchises, movie_franchises, records, and record_entries tables")
            print("[CineStats] Schema v4 applied.")
            current = 4

        if current < 5:
            # v5: Add source_url to movie_rollout if missing
            try:
                conn.execute("ALTER TABLE movie_rollout ADD COLUMN source_url TEXT;")
            except sqlite3.OperationalError:
                pass # Column already exists
                
            _record_version(conn, 5, "v5: Added source_url to movie_rollout")
            print("[CineStats] Schema v5 applied.")
            current = 5

        if current < 6:
            # v6: Add anime_arcs, deep metadata, and fix franchises
            conn.execute("""
                CREATE TABLE IF NOT EXISTS anime_arcs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE,
                    arc_name TEXT NOT NULL,
                    episode_start INTEGER NOT NULL,
                    episode_end INTEGER NOT NULL,
                    source_chapter_start INTEGER,
                    source_chapter_end INTEGER
                );
            """)
            
            # Movies metadata
            for col in ["director", "producer", "studio", "cast_json", "poster_url"]:
                try: conn.execute(f"ALTER TABLE movies ADD COLUMN {col} TEXT;")
                except sqlite3.OperationalError: pass
                
            # TV metadata
            for col in ["director", "producer", "studio", "cast_json"]:
                try: conn.execute(f"ALTER TABLE tv_series ADD COLUMN {col} TEXT;")
                except sqlite3.OperationalError: pass
                
            # Franchises fixes
            for col in ["type", "url", "source"]:
                try: conn.execute(f"ALTER TABLE franchises ADD COLUMN {col} TEXT;")
                except sqlite3.OperationalError: pass

            _record_version(conn, 6, "v6: Added anime_arcs, deep metadata, and franchises fixes")
            print("[CineStats] Schema v6 applied.")
            current = 6

        if current < 7:
            # v7: Add UNIQUE index on franchises.url, poster_url to tv_series
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_franchises_url ON franchises(url) WHERE url IS NOT NULL;")
            try: conn.execute("ALTER TABLE tv_series ADD COLUMN poster_url TEXT;")
            except sqlite3.OperationalError: pass
            
            _record_version(conn, 7, "v7: franchises.url UNIQUE index, tv_series.poster_url")
            print("[CineStats] Schema v7 applied.")
            current = 7

        if current < 8:
            # v8: Add overview
            for t in ["movies", "tv_series", "anime"]:
                try: conn.execute(f"ALTER TABLE {t} ADD COLUMN overview TEXT;")
                except sqlite3.OperationalError: pass
            
            _record_version(conn, 8, "v8: Added overview to media tables")
            print("[CineStats] Schema v8 applied.")
            current = 8

        print(f"[CineStats] Schema up to date (v{current}).")

        conn.commit()
    finally:
        conn.close()

    return db_path


if __name__ == "__main__":
    init_db()
    print("[CineStats] Database initialisation complete.")
