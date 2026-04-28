from fastapi import APIRouter
from typing import Optional
from backend.database import get_db_context
from backend.logger import log_info, log_error

router = APIRouter()

@router.get("/analyze/{release_date}")
def analyze_clash(release_date: str):
    """Find all movies released on the same date for clash analysis."""
    try:
        with get_db_context() as db:
            # Query all movies with the same release date
            movies = db.execute("""
                SELECT id, title_display, release_date, worldwide_gross_usd, 
                       india_net_cr, origin_country, genre, verdict, poster_url
                FROM movies
                WHERE release_date = ?
                ORDER BY worldwide_gross_usd DESC NULLS LAST
            """, (release_date,)).fetchall()
            
            return {
                "release_date": release_date,
                "movies": [dict(movie) for movie in movies],
                "count": len(movies)
            }
    except Exception as e:
        log_error(f"Failed to analyze clash for {release_date}: {e}")
        return {"release_date": release_date, "movies": [], "count": 0, "error": str(e)}

@router.get("/recent-clashes")
def get_recent_clashes(limit: int = 10):
    """Get recent dates with multiple movie releases."""
    try:
        with get_db_context() as db:
            # Find dates with 2+ movie releases
            clashes = db.execute("""
                SELECT release_date, COUNT(*) as movie_count
                FROM movies
                WHERE release_date IS NOT NULL
                GROUP BY release_date
                HAVING COUNT(*) >= 2
                ORDER BY release_date DESC
                LIMIT ?
            """, (limit,)).fetchall()
            
            return {
                "clashes": [dict(clash) for clash in clashes]
            }
    except Exception as e:
        log_error(f"Failed to get recent clashes: {e}")
        return {"clashes": [], "error": str(e)}
