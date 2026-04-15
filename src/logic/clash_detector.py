"""
CineStats — Clash Detector
Section 5 of the v1.0 specification.

Two clash tiers:
  1. Direct Clash (Head-to-Head / Box Office Showdown): same release date.
  2. Release Clash (Box Office Clash / Crowded Release Window): releases
     within 14 days of each other.

Provides per-movie clash lookups and aggregate historic clash tables.
"""
import sqlite3
import pandas as pd
from typing import List, Dict, Any

# ── Constants ────────────────────────────────────────────────────────────────
DIRECT_CLASH_DAYS = 0      # exact same date
WINDOW_CLASH_DAYS = 14     # within 2 weeks

CLASH_TYPE_DIRECT = "direct_clash"       # aka Head-to-Head / Box Office Showdown
CLASH_TYPE_WINDOW = "release_clash"      # aka Crowded Release Window

_MOVIE_COLS = """
    id,
    title_display,
    title_normalized,
    release_date,
    language,
    worldwide_gross_usd,
    india_net_cr,
    opening_weekend_usd,
    verdict
"""


class ClashDetector:
    # ── Per-movie clash lookup ───────────────────────────────────────────────

    @staticmethod
    def get_clashing_movies(conn: sqlite3.Connection, movie_id: int,
                            window_days: int = WINDOW_CLASH_DAYS) -> List[Dict[str, Any]]:
        """
        Given a movie ID, finds all other movies whose release date falls
        within ``window_days`` of the target movie's release date.

        Each returned dict includes a ``clash_type`` field:
            - ``"direct_clash"``  — same release date
            - ``"release_clash"`` — within 1–``window_days`` days
        """
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT release_date FROM movies WHERE id = ?", (movie_id,))
        row = cursor.fetchone()

        if not row or not row['release_date']:
            return []

        release_date = row['release_date']

        query = f"""
            SELECT {_MOVIE_COLS},
                   ABS(JULIANDAY(release_date) - JULIANDAY(?)) AS day_diff
            FROM movies
            WHERE id != ?
              AND release_date IS NOT NULL
              AND ABS(JULIANDAY(release_date) - JULIANDAY(?)) <= ?
            ORDER BY day_diff ASC, worldwide_gross_usd DESC
        """
        cursor.execute(query, (release_date, movie_id, release_date, window_days))

        results = []
        for r in cursor.fetchall():
            d = dict(r)
            d['clash_type'] = (CLASH_TYPE_DIRECT
                               if int(d['day_diff']) == 0
                               else CLASH_TYPE_WINDOW)
            results.append(d)

        return results

    # ── Aggregate historic clashes ───────────────────────────────────────────

    @staticmethod
    def find_all_major_clashes(conn: sqlite3.Connection,
                               min_gross_usd: float = 10_000_000,
                               window_days: int = WINDOW_CLASH_DAYS) -> pd.DataFrame:
        """
        Finds all historic release windows where major films clashed.

        Returns a DataFrame with columns:
            release_date, movie_count, clash_title, total_weekend_clash_usd, clash_type
        """
        # Direct clashes — same date
        direct_df = pd.read_sql("""
            SELECT
                release_date,
                COUNT(id)                           AS movie_count,
                GROUP_CONCAT(title_display, ' vs ') AS clash_title,
                SUM(worldwide_gross_usd)            AS total_weekend_clash_usd
            FROM movies
            WHERE worldwide_gross_usd >= ? AND release_date IS NOT NULL
            GROUP BY release_date
            HAVING COUNT(id) > 1
            ORDER BY total_weekend_clash_usd DESC
        """, conn, params=(min_gross_usd,))
        direct_df['clash_type'] = CLASH_TYPE_DIRECT

        # Window clashes — different dates within window_days of each other
        # Self-join to find pairs; we take the earlier date as the anchor.
        window_df = pd.read_sql(f"""
            SELECT
                a.release_date                       AS release_date,
                a.title_display || ' vs ' || b.title_display AS clash_title,
                (COALESCE(a.worldwide_gross_usd, 0)
                 + COALESCE(b.worldwide_gross_usd, 0)) AS total_weekend_clash_usd,
                ABS(JULIANDAY(a.release_date) - JULIANDAY(b.release_date)) AS day_diff
            FROM movies a
            JOIN movies b
              ON a.id < b.id
             AND a.release_date != b.release_date
             AND ABS(JULIANDAY(a.release_date) - JULIANDAY(b.release_date)) <= {window_days}
            WHERE a.worldwide_gross_usd >= ?
              AND b.worldwide_gross_usd >= ?
              AND a.release_date IS NOT NULL
              AND b.release_date IS NOT NULL
            ORDER BY total_weekend_clash_usd DESC
        """, conn, params=(min_gross_usd, min_gross_usd))
        window_df['movie_count'] = 2
        window_df['clash_type'] = CLASH_TYPE_WINDOW

        combined = pd.concat([direct_df, window_df], ignore_index=True)
        combined.sort_values('total_weekend_clash_usd', ascending=False, inplace=True)
        return combined.reset_index(drop=True)
