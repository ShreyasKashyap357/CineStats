from fastapi import APIRouter
from typing import Optional
from backend.database import get_db_context
from backend.logger import log_info, log_error

router = APIRouter()

@router.get("/context/{movie_id}")
def get_verdict_context(movie_id: int):
    """Get verdict context by comparing to similar films."""
    try:
        with get_db_context() as db:
            # Get the source movie
            source = db.execute("""
                SELECT id, title_display, genre, origin_country, verdict, 
                       worldwide_gross_usd, vote_average, release_date
                FROM movies WHERE id = ?
            """, (movie_id,)).fetchone()
            
            if not source:
                return {"context": [], "source": None}
            
            source = dict(source)
            
            # Find similar films (same genre, same country, similar release year)
            similar = db.execute("""
                SELECT id, title_display, genre, origin_country, verdict, 
                       worldwide_gross_usd, vote_average, release_date
                FROM movies
                WHERE id != ?
                  AND (genre = ? OR origin_country = ?)
                  AND release_date IS NOT NULL
                ORDER BY 
                    CASE 
                        WHEN genre = ? AND origin_country = ? THEN 0
                        WHEN genre = ? THEN 1
                        WHEN origin_country = ? THEN 2
                        ELSE 3
                    END,
                    worldwide_gross_usd DESC
                LIMIT 10
            """, (movie_id, source.get("genre"), source.get("origin_country"), 
                  source.get("genre"), source.get("origin_country"),
                  source.get("genre"), source.get("origin_country"))).fetchall()
            
            similar_movies = [dict(s) for s in similar]
            
            # Calculate verdict statistics
            verdict_counts = {}
            for movie in similar_movies:
                verdict = movie.get("verdict", "Unknown")
                verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
            
            # Determine most common verdict
            most_common = max(verdict_counts.items(), key=lambda x: x[1]) if verdict_counts else (None, 0)
            
            return {
                "source": source,
                "similar_movies": similar_movies,
                "verdict_distribution": verdict_counts,
                "most_common_verdict": most_common[0] if most_common[0] else None,
                "total_compared": len(similar_movies)
            }
    except Exception as e:
        log_error(f"Failed to get verdict context: {e}")
        return {"context": [], "source": None, "error": str(e)}
