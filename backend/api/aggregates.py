from fastapi import APIRouter
from typing import Optional
from backend.database import get_db_context
from backend.logger import log_info, log_error

router = APIRouter()

@router.get("/genres")
def get_genre_aggregates(content_type: Optional[str] = None):
    """Get aggregate statistics by genre."""
    try:
        with get_db_context() as db:
            results = []
            
            if content_type == "movie" or not content_type:
                movies = db.execute("""
                    SELECT genre, COUNT(*) as count, 
                           AVG(worldwide_gross_usd) as avg_gross,
                           SUM(worldwide_gross_usd) as total_gross
                    FROM movies
                    WHERE genre IS NOT NULL
                    GROUP BY genre
                    ORDER BY total_gross DESC
                """).fetchall()
                for row in movies:
                    row_dict = dict(row)
                    row_dict["content_type"] = "movie"
                    results.append(row_dict)
            
            if content_type == "anime" or not content_type:
                anime = db.execute("""
                    SELECT genre as genres, COUNT(*) as count,
                           AVG(COALESCE(anilist_score, mal_score, 0)) as avg_score
                    FROM anime
                    WHERE genre IS NOT NULL
                    GROUP BY genre
                    ORDER BY count DESC
                """).fetchall()
                for row in anime:
                    row_dict = dict(row)
                    row_dict["content_type"] = "anime"
                    results.append(row_dict)
            
            if content_type == "tv" or not content_type:
                tv = db.execute("""
                    SELECT genre, COUNT(*) as count
                    FROM tv_series
                    WHERE genre IS NOT NULL
                    GROUP BY genre
                    ORDER BY count DESC
                """).fetchall()
                for row in tv:
                    row_dict = dict(row)
                    row_dict["content_type"] = "tv"
                    results.append(row_dict)
            
            return {"results": results}
    except Exception as e:
        log_error(f"Failed to get genre aggregates: {e}")
        return {"results": []}

@router.get("/studios")
def get_studio_aggregates(content_type: Optional[str] = None):
    """Get aggregate statistics by studio."""
    try:
        with get_db_context() as db:
            results = []
            
            if content_type == "anime" or not content_type:
                anime = db.execute("""
                    SELECT studio as studios, COUNT(*) as count,
                           AVG(COALESCE(anilist_score, mal_score, 0)) as avg_score
                    FROM anime
                    WHERE studio IS NOT NULL
                    GROUP BY studio
                    ORDER BY count DESC
                    LIMIT 20
                """).fetchall()
                for row in anime:
                    row_dict = dict(row)
                    row_dict["content_type"] = "anime"
                    results.append(row_dict)
            
            if content_type == "tv" or not content_type:
                tv = db.execute("""
                    SELECT network as studio, COUNT(*) as count
                    FROM tv_series
                    WHERE network IS NOT NULL
                    GROUP BY network
                    ORDER BY count DESC
                    LIMIT 20
                """).fetchall()
                for row in tv:
                    row_dict = dict(row)
                    row_dict["content_type"] = "tv"
                    results.append(row_dict)
            
            return {"results": results}
    except Exception as e:
        log_error(f"Failed to get studio aggregates: {e}")
        return {"results": []}
