from fastapi import APIRouter, HTTPException
from typing import Optional, List
from backend.database import get_db_context
from backend.logger import log_info, log_error

router = APIRouter()

@router.get("/anime-intra/{anime_id}")
def anime_intra_compare(anime_id: int):
    """Compare seasons/cours/arcs within the same anime series."""
    try:
        with get_db_context() as db:
            anime = db.execute("SELECT * FROM anime WHERE id = ?", (anime_id,)).fetchone()
            if not anime:
                return {"results": []}
            
            anime_dict = dict(anime)
            
            # Create comparison data for different structural views
            results = []
            
            # Cour comparison
            total_eps = anime_dict.get("episodes", 0) or 0
            if total_eps > 0:
                cour_eps = total_eps // 4
                for i in range(4):
                    results.append({
                        "type": "cour",
                        "name": f"Cour {i+1}",
                        "episodes": cour_eps,
                        "anime_id": anime_id,
                        "title": anime_dict.get("title_english") or anime_dict.get("title_normalized")
                    })
            
            # Season comparison
            results.append({
                "type": "season",
                "name": "Season 1",
                "episodes": total_eps,
                "score": anime_dict.get("anilist_score") or anime_dict.get("mal_score") or 0,
                "anime_id": anime_id,
                "title": anime_dict.get("title_english") or anime_dict.get("title_normalized")
            })
            
            return {"results": results}
    except Exception as e:
        log_error(f"Failed to perform anime intra-series comparison: {e}")
        return {"results": []}

@router.get("/cross-category")
def cross_category_compare(
    ids: List[int],
    content_types: List[str]
):
    """Compare items across different content types (movies, tv, anime, western, cartoons)."""
    try:
        results = []
        
        with get_db_context() as db:
            for item_id, content_type in zip(ids, content_types):
                if content_type == "movie":
                    item = db.execute("""
                        SELECT id, title_display, release_date, worldwide_gross_usd, 
                               india_net_cr, vote_average, verdict, 'movie' as content_type
                        FROM movies WHERE id = ?
                    """, (item_id,)).fetchone()
                    if item:
                        results.append(dict(item))
                
                elif content_type == "tv":
                    item = db.execute("""
                        SELECT id, title_display, premiere_date as release_date, 
                               'tv' as content_type
                        FROM tv_series WHERE id = ?
                    """, (item_id,)).fetchone()
                    if item:
                        results.append(dict(item))
                
                elif content_type == "anime":
                    item = db.execute("""
                        SELECT id, COALESCE(title_english, title_normalized) as title_display, 
                               (season_year || '-' || season) as release_date, COALESCE(anilist_score, mal_score, 0) as vote_average, 'anime' as content_type
                        FROM anime WHERE id = ?
                    """, (item_id,)).fetchone()
                    if item:
                        results.append(dict(item))
                
                elif content_type == "western":
                    item = db.execute("""
                        SELECT id, title_display, release_date, worldwide_gross_usd, 
                               vote_average, 'western' as content_type
                        FROM movies WHERE id = ? AND origin_country != 'India'
                    """, (item_id,)).fetchone()
                    if item:
                        results.append(dict(item))
                
                elif content_type == "cartoons":
                    item = db.execute("""
                        SELECT id, title_display, premiere_date as release_date, 
                               'cartoons' as content_type
                        FROM tv_series WHERE id = ?
                    """, (item_id,)).fetchone()
                    if item:
                        results.append(dict(item))
        
        return {"results": results}
    except Exception as e:
        log_error(f"Failed to perform cross-category comparison: {e}")
        return {"results": []}


@router.post("/save")
def save_comparison(
    name: str,
    content_type: str,
    ids: List[int],
    user_id: Optional[str] = None
):
    """Save a comparison for later access."""
    try:
        with get_db_context() as db:
            # Create saved_comparisons table if it doesn't exist
            db.execute("""
                CREATE TABLE IF NOT EXISTS saved_comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    item_ids TEXT NOT NULL,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Save the comparison
            item_ids_str = ",".join(map(str, ids))
            db.execute("""
                INSERT INTO saved_comparisons (name, content_type, item_ids, user_id)
                VALUES (?, ?, ?, ?)
            """, (name, content_type, item_ids_str, user_id))
            
            return {"success": True, "message": "Comparison saved"}
    except Exception as e:
        log_error(f"Failed to save comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def get_saved_comparisons(user_id: Optional[str] = None):
    """Get all saved comparisons for a user."""
    try:
        with get_db_context() as db:
            # Check if table exists
            table_check = db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='saved_comparisons'
            """).fetchone()
            
            if not table_check:
                return {"comparisons": []}
            
            # Get comparisons
            if user_id:
                comparisons = db.execute("""
                    SELECT id, name, content_type, item_ids, created_at
                    FROM saved_comparisons
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                """, (user_id,)).fetchall()
            else:
                comparisons = db.execute("""
                    SELECT id, name, content_type, item_ids, created_at
                    FROM saved_comparisons
                    ORDER BY created_at DESC
                """).fetchall()
            
            results = []
            for comp in comparisons:
                comp_dict = dict(comp)
                comp_dict["item_ids"] = [int(x) for x in comp_dict["item_ids"].split(",")]
                results.append(comp_dict)
            
            return {"comparisons": results}
    except Exception as e:
        log_error(f"Failed to get saved comparisons: {e}")
        return {"comparisons": []}

@router.delete("/{comparison_id}")
def delete_comparison(comparison_id: int, user_id: Optional[str] = None):
    """Delete a saved comparison."""
    try:
        with get_db_context() as db:
            if user_id:
                db.execute("""
                    DELETE FROM saved_comparisons
                    WHERE id = ? AND user_id = ?
                """, (comparison_id, user_id))
            else:
                db.execute("""
                    DELETE FROM saved_comparisons
                    WHERE id = ?
                """, (comparison_id,))
            
            return {"success": True, "message": "Comparison deleted"}
    except Exception as e:
        log_error(f"Failed to delete comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))

