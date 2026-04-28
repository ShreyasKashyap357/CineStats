from fastapi import APIRouter
from typing import Optional, List
from backend.database import get_db_context
from backend.logger import log_info, log_error

router = APIRouter()

@router.get("/similar/{content_type}/{id}")
def get_similar_titles(content_type: str, id: int, limit: int = 10):
    """Get similar titles based on rule-based scoring."""
    try:
        with get_db_context() as db:
            # Get the source item
            if content_type == "movie":
                source = db.execute("""
                    SELECT id, title_display, genre, origin_country, franchise_id, 
                           vote_average, worldwide_gross_usd
                    FROM movies WHERE id = ?
                """, (id,)).fetchone()
                
                if not source:
                    return {"results": []}
                
                source = dict(source)
                
                # Find similar movies using rule-based scoring
                similar = db.execute("""
                    SELECT id, title_display, genre, origin_country, franchise_id,
                           vote_average, worldwide_gross_usd, poster_url, 'movie' as content_type
                    FROM movies
                    WHERE id != ?
                    ORDER BY 
                        CASE 
                            WHEN franchise_id = ? THEN 3
                            WHEN genre = ? THEN 2
                            WHEN origin_country = ? THEN 1
                            ELSE 0
                        END DESC,
                        vote_average DESC
                    LIMIT ?
                """, (id, source.get("franchise_id"), source.get("genre"), source.get("origin_country"), limit * 2)).fetchall()
                
                results = [dict(s) for s in similar]
                
            elif content_type == "anime":
                source = db.execute("""
                    SELECT id, title_english, title_normalized, genre as genres, studio as studios, 
                           source_material as source, COALESCE(anilist_score, mal_score, 0) as score, demographic
                    FROM anime WHERE id = ?
                """, (id,)).fetchone()
                
                if not source:
                    return {"results": []}
                
                source = dict(source)
                
                similar = db.execute("""
                    SELECT id, COALESCE(title_english, title_normalized) as title_display,
                           genre as genres, studio as studios, source_material as source, COALESCE(anilist_score, mal_score, 0) as score, poster_url, 'anime' as content_type
                    FROM anime
                    WHERE id != ?
                    ORDER BY 
                        CASE 
                            WHEN studio = ? THEN 3
                            WHEN source_material = ? THEN 2
                            WHEN demographic = ? THEN 1
                            ELSE 0
                        END DESC,
                        COALESCE(anilist_score, mal_score, 0) DESC
                    LIMIT ?
                """, (id, source.get("studios"), source.get("source"), source.get("demographic"), limit * 2)).fetchall()
                
                results = [dict(s) for s in similar]
                
            elif content_type == "tv":
                source = db.execute("""
                    SELECT id, title_display, genre, network, premiere_date
                    FROM tv_series WHERE id = ?
                """, (id,)).fetchone()
                
                if not source:
                    return {"results": []}
                
                source = dict(source)
                
                similar = db.execute("""
                    SELECT id, title_display, genre, network, premiere_date, poster_url, 'tv' as content_type
                    FROM tv_series
                    WHERE id != ?
                    ORDER BY 
                        CASE 
                            WHEN network = ? THEN 2
                            WHEN genre = ? THEN 1
                            ELSE 0
                        END DESC
                    LIMIT ?
                """, (id, source.get("network"), source.get("genre"), limit * 2)).fetchall()
                
                results = [dict(s) for s in similar]
                
            else:
                return {"results": []}
            
            return {"results": results[:limit]}
    except Exception as e:
        log_error(f"Failed to get similar titles: {e}")
        return {"results": []}
