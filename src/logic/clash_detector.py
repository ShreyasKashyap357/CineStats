"""
CineStats — Clash Detector
Section 5 of the v1.0 specification.

Identifies movies released on the same date and provides 
side-by-side performance comparisons.
"""
import sqlite3
import pandas as pd
from typing import List, Dict, Any

class ClashDetector:
    @staticmethod
    def get_clashing_movies(conn: sqlite3.Connection, movie_id: int) -> List[Dict[str, Any]]:
        """
        Given a movie ID, finds all other movies that released on the exact same date.
        Returns a list of dicts with basic performance info to display a clash comparison.
        """
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get target movie release date
        cursor.execute("SELECT release_date FROM movies WHERE id = ?", (movie_id,))
        row = cursor.fetchone()
        
        if not row or not row['release_date']:
            return []
            
        release_date = row['release_date']
        
        # Find clashes
        query = """
            SELECT 
                id, 
                title_display, 
                title_normalized,
                release_date, 
                language, 
                worldwide_gross_usd, 
                india_net_cr, 
                opening_weekend_usd,
                verdict
            FROM movies 
            WHERE release_date = ? AND id != ?
            ORDER BY worldwide_gross_usd DESC
        """
        
        cursor.execute(query, (release_date, movie_id))
        return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def find_all_major_clashes(conn: sqlite3.Connection, min_gross_usd: float = 10000000) -> pd.DataFrame:
        """
        Finds all historic dates where multiple major movies released simultaneously.
        Major is defined by the min_gross_usd threshold to filter out obscure indie clashes.
        Returns a DataFrame of clash dates and the participating movies.
        """
        query = """
            SELECT 
                release_date, 
                COUNT(id) as movie_count,
                GROUP_CONCAT(title_display, ' vs ') as clash_title,
                SUM(worldwide_gross_usd) as total_weekend_clash_usd
            FROM movies
            WHERE worldwide_gross_usd >= ? AND release_date IS NOT NULL
            GROUP BY release_date
            HAVING COUNT(id) > 1
            ORDER BY total_weekend_clash_usd DESC
        """
        return pd.read_sql(query, conn, params=(min_gross_usd,))
