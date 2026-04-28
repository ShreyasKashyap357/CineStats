from fastapi import APIRouter
from typing import Optional, List
from src.clients.tmdb_client import search_tmdb
from src.scrapers.anime_scraper import fetch_jikan, fetch_anilist
from backend.database import get_db_context

router = APIRouter()

@router.get("/")
def global_search(query: str):
    """
    Unified search hitting TMDB (Movies, TV), Jikan/AniList (Anime), and local DB.
    """
    results = []
    
    # 1. Local Database Search
    with get_db_context() as conn:
        movies = conn.execute("SELECT id, title_display, release_date, worldwide_gross_usd FROM movies WHERE title_normalized LIKE ?", (f"%{query.lower().replace(' ', '')}%",)).fetchall()
        for m in movies:
            results.append({
                "source": "local_movie", "id": m[0], "title": m[1], 
                "year": m[2].split('-')[0] if m[2] else "?", 
                "gross": f"${(m[3] or 0)/1000000:.1f}M"
            })
            
        tvs = conn.execute("SELECT id, title_normalized, premiere_date FROM tv_series WHERE title_normalized LIKE ?", (f"%{query.lower().replace(' ', '')}%",)).fetchall()
        for t in tvs:
            results.append({
                "source": "local_tv", "id": t[0], "title": t[1], 
                "year": t[2].split('-')[0] if t[2] else "?"
            })
            
        animes = conn.execute("SELECT id, title_english, title_normalized, season_year FROM anime WHERE title_normalized LIKE ?", (f"%{query.lower().replace(' ', '')}%",)).fetchall()
        for a in animes:
            results.append({
                "source": "local_anime", "id": a[0], "title": a[1] or a[2], 
                "year": str(a[3] or "?")
            })

    # 2. TMDB Multi Search (graceful degradation)
    try:
        tmdb_results = search_tmdb(query)
        for t in tmdb_results:
            results.append({
                "source": f"tmdb_{t['media_type']}",
                "tmdb_id": t["tmdb_id"],
                "title": t["title"],
                "year": t["release_date"].split('-')[0] if t.get("release_date") else "?",
                "poster": t["poster_url_card"],
                "overview": t["overview"]
            })
    except Exception as e:
        print(f"[Search] TMDB unavailable, continuing with other sources: {e}")
        
    # 3. Jikan Anime Search (limit to top 3 to keep it snappy)
    from curl_cffi import requests as cffi_requests
    try:
        jikan_session = cffi_requests.Session(impersonate="chrome120")
        jikan_resp = jikan_session.get(f"https://api.jikan.moe/v4/anime?q={query}&limit=3", timeout=5).json()
        for a in jikan_resp.get("data", []):
            results.append({
                "source": "jikan_anime",
                "mal_id": a["mal_id"],
                "title": a.get("title_english") or a.get("title"),
                "year": a.get("year", "?"),
                "poster": a.get("images", {}).get("jpg", {}).get("large_image_url"),
                "overview": a.get("synopsis")
            })
    except Exception as e:
        print("Jikan search error:", e)

    return results

@router.get("/advanced")
def advanced_search(
    query: Optional[str] = None,
    content_type: Optional[str] = None,
    year: Optional[int] = None,
    country: Optional[str] = None,
    language: Optional[str] = None,
    min_score: Optional[float] = None,
    min_gross: Optional[float] = None,
    status: Optional[str] = None,
    network: Optional[str] = None,
    limit: int = 50
):
    """Advanced search with multiple filters."""
    results = []
    
    with get_db_context() as conn:
        # Build dynamic query for movies
        if content_type == "movie" or not content_type:
            sql = "SELECT id, title_display, release_date, worldwide_gross_usd, vote_average, origin_country, genre, verdict FROM movies WHERE 1=1"
            params = []
            
            if query:
                sql += " AND title_normalized LIKE ?"
                params.append(f"%{query.lower().replace(' ', '')}%")
            if year:
                sql += " AND release_date LIKE ?"
                params.append(f"{year}-%")
            if country:
                sql += " AND origin_country = ?"
                params.append(country)
            if language:
                sql += " AND language = ?"
                params.append(language)
            if min_score:
                sql += " AND vote_average >= ?"
                params.append(min_score)
            if min_gross:
                sql += " AND worldwide_gross_usd >= ?"
                params.append(min_gross)
            if status:
                sql += " AND verdict = ?"
                params.append(status)
            
            sql += " ORDER BY worldwide_gross_usd DESC LIMIT ?"
            params.append(limit)
            
            movies = conn.execute(sql, params).fetchall()
            for m in movies:
                results.append({
                    "source": "movie",
                    "id": m[0],
                    "title": m[1],
                    "release_date": m[2],
                    "worldwide_gross_usd": m[3],
                    "vote_average": m[4],
                    "origin_country": m[5],
                    "genre": m[6],
                    "verdict": m[7]
                })
        
        # Build dynamic query for TV series
        if content_type == "tv" or not content_type:
            sql = "SELECT id, title_display, premiere_date, genre, network, status FROM tv_series WHERE 1=1"
            params = []
            
            if query:
                sql += " AND title_normalized LIKE ?"
                params.append(f"%{query.lower().replace(' ', '')}%")
            if year:
                sql += " AND premiere_date LIKE ?"
                params.append(f"{year}-%")
            if network:
                sql += " AND network = ?"
                params.append(network)
            if status:
                sql += " AND status = ?"
                params.append(status)
            
            sql += " ORDER BY id DESC LIMIT ?"
            params.append(limit)
            
            tvs = conn.execute(sql, params).fetchall()
            for t in tvs:
                results.append({
                    "source": "tv",
                    "id": t[0],
                    "title": t[1],
                    "premiere_date": t[2],
                    "genre": t[3],
                    "network": t[4],
                    "status": t[5]
                })
        
        # Build dynamic query for anime
        if content_type == "anime" or not content_type:
            sql = "SELECT id, COALESCE(title_english, title_normalized) as title_display, (season_year || '-' || season) as aired, COALESCE(anilist_score, mal_score, 0) as score, genre as genres, studio as studios, status FROM anime WHERE 1=1"
            params = []
            
            if query:
                sql += " AND title_normalized LIKE ?"
                params.append(f"%{query.lower().replace(' ', '')}%")
            if year:
                sql += " AND season_year = ?"
                params.append(year)
            if min_score:
                sql += " AND COALESCE(anilist_score, mal_score, 0) >= ?"
                params.append(min_score)
            if status:
                sql += " AND status = ?"
                params.append(status)
            
            sql += " ORDER BY COALESCE(anilist_score, mal_score, 0) DESC LIMIT ?"
            params.append(limit)
            
            animes = conn.execute(sql, params).fetchall()
            for a in animes:
                results.append({
                    "source": "anime",
                    "id": a[0],
                    "title": a[1],
                    "aired": a[2],
                    "score": a[3],
                    "genres": a[4],
                    "studios": a[5],
                    "status": a[6]
                })
    
    return {"results": results[:limit]}

@router.post("/recent")
def save_recent_search(query: str, user_id: Optional[str] = None):
    """Save a recent search query."""
    try:
        with get_db_context() as db:
            # Create recent_searches table if it doesn't exist
            db.execute("""
                CREATE TABLE IF NOT EXISTS recent_searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Save the search
            db.execute("""
                INSERT INTO recent_searches (query, user_id)
                VALUES (?, ?)
            """, (query, user_id))
            
            # Keep only last 10 searches per user
            if user_id:
                db.execute("""
                    DELETE FROM recent_searches
                    WHERE id NOT IN (
                        SELECT id FROM recent_searches
                        WHERE user_id = ?
                        ORDER BY created_at DESC
                        LIMIT 10
                    ) AND user_id = ?
                """, (user_id, user_id))
            else:
                db.execute("""
                    DELETE FROM recent_searches
                    WHERE id NOT IN (
                        SELECT id FROM recent_searches
                        ORDER BY created_at DESC
                        LIMIT 10
                    )
                """)
            
            return {"success": True}
    except Exception as e:
        print(f"Failed to save recent search: {e}")
        return {"success": False}

@router.get("/recent")
def get_recent_searches(user_id: Optional[str] = None):
    """Get recent search queries."""
    try:
        with get_db_context() as db:
            # Check if table exists
            table_check = db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='recent_searches'
            """).fetchone()
            
            if not table_check:
                return {"searches": []}
            
            # Get recent searches
            if user_id:
                searches = db.execute("""
                    SELECT query, created_at
                    FROM recent_searches
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 10
                """, (user_id,)).fetchall()
            else:
                searches = db.execute("""
                    SELECT query, created_at
                    FROM recent_searches
                    ORDER BY created_at DESC
                    LIMIT 10
                """).fetchall()
            
            return {"searches": [dict(s) for s in searches]}
    except Exception as e:
        print(f"Failed to get recent searches: {e}")
        return {"searches": []}

@router.delete("/recent")
def clear_recent_searches(user_id: Optional[str] = None):
    """Clear recent search queries."""
    try:
        with get_db_context() as db:
            if user_id:
                db.execute("""
                    DELETE FROM recent_searches
                    WHERE user_id = ?
                """, (user_id,))
            else:
                db.execute("""
                    DELETE FROM recent_searches
                """)
            
            return {"success": True}
    except Exception as e:
        print(f"Failed to clear recent searches: {e}")
        return {"success": False}


