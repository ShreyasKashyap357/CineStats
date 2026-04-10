"""
CineStats — Mover Calculator
Section 5 of the v1.0 specification.

Calculates the largest day-over-day or week-over-week 
percentage changes (gainers and losers) in box office performance.
"""
import sqlite3
import pandas as pd

class MoverCalculator:
    @staticmethod
    def get_daily_movers(conn: sqlite3.Connection, date: str, min_gross: float = 100000) -> pd.DataFrame:
        """
        Calculates day-over-day percentage changes for movies on a given date.
        Restricts to movies that excerpt a minimum gross to avoid tiny movies causing 1000% swings.
        Returns a DataFrame sorted by % change.
        """
        # We need the performance for 'date' and the day before.
        # Joining the daily_performance table on itself with a 1-day offset.
        query = """
            WITH CurrentDay AS (
                SELECT movie_id, daily_gross_usd, date
                FROM daily_performance
                WHERE date = ? AND daily_gross_usd >= ?
            ),
            PreviousDay AS (
                SELECT movie_id, daily_gross_usd as prev_gross
                FROM daily_performance
                WHERE date = date(?, '-1 day')
            )
            SELECT 
                m.title_display,
                c.daily_gross_usd,
                p.prev_gross,
                ((c.daily_gross_usd - p.prev_gross) / p.prev_gross) * 100 as pct_change
            FROM CurrentDay c
            JOIN PreviousDay p ON c.movie_id = p.movie_id
            JOIN movies m ON c.movie_id = m.id
            WHERE p.prev_gross > 0
            ORDER BY pct_change DESC
        """
        df = pd.read_sql(query, conn, params=(date, min_gross, date))
        return df

    @staticmethod
    def get_top_gainers_and_losers(conn: sqlite3.Connection, date: str, limit: int = 5, min_gross: float = 100000) -> dict:
        """Helper to get top N gainers and bottom N losers for a specific date."""
        df = MoverCalculator.get_daily_movers(conn, date, min_gross)
        
        if df.empty:
            return {'gainers': pd.DataFrame(), 'losers': pd.DataFrame()}
            
        gainers = df[df['pct_change'] > 0].head(limit)
        losers = df[df['pct_change'] < 0].tail(limit).sort_values('pct_change', ascending=True)
        
        return {'gainers': gainers, 'losers': losers}
