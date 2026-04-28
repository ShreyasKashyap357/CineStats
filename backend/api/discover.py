from fastapi import APIRouter
from typing import List, Dict, Optional
from backend.database import get_db_context
from src.clients.tmdb_client import _api_get, get_poster_url
from datetime import datetime
from backend.logger import log_info, log_error, log_warning

router = APIRouter()

@router.get("/in-theatres")
def get_in_theatres():
    """Fetches movies currently playing from TMDB API."""
    try:
        data = _api_get("/movie/now_playing", {"region": "US"})
        results = []
        for r in data.get("results", [])[:12]:
            results.append({
                "tmdb_id": r["id"],
                "title": r["title"],
                "release_date": r["release_date"],
                "poster_url": get_poster_url(r.get("poster_path"), "w500"),
                "vote_average": r["vote_average"],
                "overview": r["overview"],
                "origin_country": r.get("origin_country"),
                "franchise_id": None
            })
        return {"results": results}
    except Exception as e:
        log_error(f"TMDB in-theatres unavailable: {e}")
        return {"results": []}

@router.get("/airing")
def get_airing():
    """Fetches TV series airing today from TMDB API."""
    try:
        data = _api_get("/tv/airing_today")
        results = []
        for r in data.get("results", [])[:12]:
            results.append({
                "tmdb_id": r["id"],
                "title": r["name"],
                "release_date": r.get("first_air_date"),
                "poster_url": get_poster_url(r.get("poster_path"), "w500"),
                "vote_average": r["vote_average"],
                "overview": r["overview"],
                "origin_country": r.get("origin_country"),
                "franchise_id": None
            })
        return {"results": results}
    except Exception as e:
        log_error(f"TMDB airing unavailable: {e}")
        return {"results": []}

@router.get("/trending")
def get_trending():
    """Fetches trending movies and TV globally from TMDB, plus Top Indian from Sacnilk."""
    results = []
    
    # 1. Fetch Sacnilk Top 10
    try:
        from src.scrapers.records_scraper import scrape_sacnilk_record
        sac_data = scrape_sacnilk_record("entertainmenttopbar/Top_10_Indian_Movies_(India_Net_Collection)")
        for idx, r in enumerate(sac_data[:4]): # Take top 4 Indian movies
            results.append({
                "tmdb_id": f"sacnilk_{idx}",
                "title": r.get("title"),
                "media_type": "movie",
                "worldwide_gross_usd": None, # Will show as green badge if mapped properly
                "vote_average": None,
                "poster_url": None, # Fallback icon
                "release_date": "Trending India",
                "overview": None
            })
    except Exception as e:
        print(f"Error fetching Sacnilk trending: {e}")
        
    # 2. Fetch TMDB
    try:
        data = _api_get("/trending/all/day")
        for r in data.get("results", [])[:8]: # Take top 8 TMDB
            results.append({
                "tmdb_id": r["id"],
                "title": r.get("title") or r.get("name"),
                "media_type": r.get("media_type"),
                "poster_url": get_poster_url(r["poster_path"], "w500"),
                "vote_average": r["vote_average"],
                "release_date": r.get("release_date") or r.get("first_air_date"),
                "overview": r.get("overview")
            })
    except Exception as e:
        log_error(f"Error fetching TMDB trending: {e}")
        
    return {"results": results}

@router.get("/movers")
def get_movers():
    """SQL query to find movies with huge daily_india_net_cr gains or overall DB stats."""
    with get_db_context() as conn:
        movies = conn.execute("""
            SELECT m.id, m.title_display, m.india_net_cr, m.worldwide_gross_usd, m.release_date, m.poster_url, m.overview, m.franchise_id, m.cast_json, m.origin_country, f.name as franchise_name
            FROM movies m
            LEFT JOIN franchises f ON m.franchise_id = f.id
            WHERE m.india_net_cr IS NOT NULL OR m.worldwide_gross_usd IS NOT NULL
            ORDER BY m.id DESC LIMIT 10
        """).fetchall()
        return {"results": [dict(m) for m in movies]}

@router.get("/on-this-day")
def get_on_this_day():
    """SQL query to find movies released on this specific month/day."""
    today_month_day = datetime.now().strftime("%m-%d")
    with get_db_context() as conn:
        movies = conn.execute(f"""
            SELECT m.id, m.title_display, m.release_date, m.worldwide_gross_usd, m.poster_url, m.overview, m.franchise_id, m.cast_json, m.origin_country, f.name as franchise_name
            FROM movies m
            LEFT JOIN franchises f ON m.franchise_id = f.id
            WHERE m.release_date LIKE '%-{today_month_day}'
            ORDER BY m.worldwide_gross_usd DESC LIMIT 10
        """).fetchall()
        return {"results": [dict(m) for m in movies]}

@router.get("/top-of-year")
def get_top_of_year(year: Optional[int] = None, content_type: Optional[str] = None):
    """Get top content of a specific year by content type."""
    if not year:
        from datetime import datetime
        year = datetime.now().year
    
    results = []
    with get_db_context() as conn:
        if content_type == "movie" or not content_type:
            movies = conn.execute("""
                SELECT m.id, m.title_display, m.release_date, m.worldwide_gross_usd, m.india_net_cr, m.poster_url, m.overview, m.franchise_id, m.cast_json, m.origin_country, f.name as franchise_name, 'movie' as content_type
                FROM movies m
                LEFT JOIN franchises f ON m.franchise_id = f.id
                WHERE m.release_date LIKE '{year}-%'
                ORDER BY m.worldwide_gross_usd DESC LIMIT 20
            """).fetchall()
            results.extend([dict(m) for m in movies])
        
        if content_type == "tv" or not content_type:
            tv = conn.execute("""
                SELECT id, title_display, premiere_date as release_date, poster_url, overview, 
                       'tv' as content_type
                FROM tv_series
                WHERE premiere_date LIKE '{year}-%'
                ORDER BY id DESC LIMIT 20
            """).fetchall()
            results.extend([dict(t) for t in tv])
        
        if content_type == "anime" or not content_type:
            anime = conn.execute(f"""
                SELECT id, COALESCE(title_english, title_normalized) as title_display, 
                       (season_year || '-' || season) as release_date, poster_url, 
                       NULL as overview, 'anime' as content_type
                FROM anime
                WHERE season_year = {year}
                ORDER BY id DESC LIMIT 20
            """).fetchall()
            results.extend([dict(a) for a in anime])
        
        return {"results": results, "year": year, "content_type": content_type}

@router.get("/recent")
def get_recent():
    """SQL query to find recently added movies, TV series, and anime from app_log if available."""
    results = []
    with get_db_context() as conn:
        # Check if app_log table exists for more accurate recent data
        table_check = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='app_log'
        """).fetchone()
        
        if table_check:
            # Get recent entries from app_log using entity_key
            recent_logs = conn.execute("""
                SELECT DISTINCT entity_key as title_key
                FROM app_log
                WHERE event_type LIKE '%scrape%' OR event_type LIKE '%add%'
                ORDER BY timestamp DESC
                LIMIT 15
            """).fetchall()
            
            if recent_logs:
                title_keys = [log["title_key"] for log in recent_logs if log["title_key"]]
                if title_keys:
                    placeholders = ",".join(["?"] * len(title_keys))
                    
                    # Get movie details for recent logs
                    movies = conn.execute(f"""
                        SELECT 'movie' as media_type, id, title_display as title, release_date, poster_url
                        FROM movies
                        WHERE title_normalized IN ({placeholders})
                        ORDER BY last_updated DESC
                    """, (*title_keys,)).fetchall()
                    results.extend([dict(m) for m in movies])
        
        # Fallback or supplement with recent by ID
        if len(results) < 5:
            movies = conn.execute("""
                SELECT 'movie' as media_type, id, title_display as title, release_date, poster_url
                FROM movies 
                ORDER BY id DESC LIMIT 5
            """).fetchall()
            results.extend([dict(m) for m in movies])
        
        # Recent TV series
        tv = conn.execute("""
            SELECT 'tv' as media_type, id, title_display as title, premiere_date as release_date, poster_url
            FROM tv_series 
            ORDER BY id DESC LIMIT 5
        """).fetchall()
        results.extend([dict(t) for t in tv])
        
        # Recent anime
        anime = conn.execute("""
            SELECT 'anime' as media_type, id, 
                COALESCE(title_english, title_normalized) as title, 
                (season_year || '-' || season) as release_date,
                poster_url
            FROM anime 
            ORDER BY id DESC LIMIT 5
        """).fetchall()
        results.extend([dict(a) for a in anime])
        
        # Sort by combined recency (use id as proxy for insertion time)
        results.sort(key=lambda x: x['id'], reverse=True)
        return {"results": results[:12]}

@router.get("/trending-week")
def get_trending_week():
    """Get trending content for the week - combines BOM movers and trending anime."""
    results = []
    with get_db_context() as conn:
        # Get recent BOM movers (last 7 days worth of data)
        movies = conn.execute("""
            SELECT id, title_display, release_date, worldwide_gross_usd, poster_url, 
                   'movie' as content_type, 'box_office' as trend_source
            FROM movies
            WHERE worldwide_gross_usd IS NOT NULL
            ORDER BY last_updated DESC
            LIMIT 10
        """).fetchall()
        results.extend([dict(m) for m in movies])
        
        # Get trending anime (by recent addition/popularity)
        anime = conn.execute("""
            SELECT id, COALESCE(title_english, title_normalized) as title_display, 
                   (season_year || '-' || season) as release_date, poster_url, 
                   COALESCE(anilist_score, mal_score, 0) as score, 'anime' as content_type, 
                   'anilist' as trend_source
            FROM anime
            WHERE anilist_score IS NOT NULL OR mal_score IS NOT NULL
            ORDER BY COALESCE(anilist_score, mal_score, 0) DESC, last_updated DESC
            LIMIT 10
        """).fetchall()
        results.extend([dict(a) for a in anime])
        
        # Get trending TV series
        tv = conn.execute("""
            SELECT id, title_display, premiere_date as release_date, poster_url,
                   'tv' as content_type, 'recent' as trend_source
            FROM tv_series
            ORDER BY last_updated DESC
            LIMIT 10
        """).fetchall()
        results.extend([dict(t) for t in tv])
        
        return {"results": results[:30]}

@router.get("/on-this-day-preview")
def get_on_this_day_preview():
    """Get 4-6 notable titles released on today's date for Home page preview."""
    from datetime import datetime
    today = datetime.now()
    today_month_day = today.strftime("%m-%d")
    
    with get_db_context() as conn:
        movies = conn.execute(f"""
            SELECT m.id, m.title_display, m.release_date, m.worldwide_gross_usd, m.poster_url, 
                   m.overview, m.vote_average, 'movie' as content_type
            FROM movies m
            WHERE m.release_date LIKE '%-{today_month_day}'
            ORDER BY m.worldwide_gross_usd DESC LIMIT 6
        """).fetchall()
        
        # If not enough movies, add TV and anime
        results = [dict(m) for m in movies]
        
        if len(results) < 6:
            tv = conn.execute(f"""
                SELECT id, title_display, premiere_date as release_date, poster_url, overview,
                       'tv' as content_type
                FROM tv_series
                WHERE premiere_date LIKE '%-{today_month_day}'
                ORDER BY id DESC LIMIT 3
            """).fetchall()
            results.extend([dict(t) for t in tv])
        
        if len(results) < 6:
            anime = conn.execute(f"""
                SELECT id, COALESCE(title_english, title_normalized) as title_display, 
                       (season_year || '-' || season) as release_date, poster_url, NULL as overview, 'anime' as content_type
                FROM anime
                WHERE season_year = {today[:4]}
                ORDER BY id DESC LIMIT 3
            """).fetchall()
            results.extend([dict(a) for a in anime])
        
        return {"results": results[:6], "date": today.strftime("%B %d")}

@router.get("/on-this-day")
def get_on_this_day(
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    mode: str = "released",
    content_type: Optional[List[str]] = None
):
    """Fetches content released on a specific date or within a date range."""
    try:
        with get_db_context() as db:
            results = {}
            
            # Parse dates
            if date:
                month_day = date[5:]  # MM-DD
            elif start_date and end_date:
                month_day = None
            else:
                month_day = datetime.now().strftime("%m-%d")
            
            content_types = content_type or ["movies", "tv", "anime"]
            
            # Movies
            if "movies" in content_types:
                if date:
                    movies = db.execute("""
                        SELECT id, title_display, release_date, poster_url
                        FROM movies 
                        WHERE strftime('%m-%d', release_date) = ?
                        ORDER BY release_date DESC
                    """, (month_day,)).fetchall()
                elif start_date and end_date:
                    movies = db.execute("""
                        SELECT id, title_display, release_date, poster_url
                        FROM movies 
                        WHERE release_date BETWEEN ? AND ?
                        ORDER BY release_date DESC
                    """, (start_date, end_date)).fetchall()
                else:
                    movies = []
                results["movies"] = [dict(m) for m in movies]
            
            # TV Series
            if "tv" in content_types:
                if date:
                    tv = db.execute("""
                        SELECT id, title_display, premiere_date as release_date, poster_url
                        FROM tv_series 
                        WHERE strftime('%m-%d', premiere_date) = ?
                        ORDER BY premiere_date DESC
                    """, (month_day,)).fetchall()
                elif start_date and end_date:
                    tv = db.execute("""
                        SELECT id, title_display, premiere_date as release_date, poster_url
                        FROM tv_series 
                        WHERE premiere_date BETWEEN ? AND ?
                        ORDER BY premiere_date DESC
                    """, (start_date, end_date)).fetchall()
                else:
                    tv = []
                results["tv"] = [dict(t) for t in tv]
            
            # Anime
            if "anime" in content_types:
                if date:
                    anime = db.execute("""
                        SELECT id, COALESCE(title_english, title_normalized) as title_display, 
                               (season_year || '-' || season) as release_date, poster_url
                        FROM anime 
                        WHERE season_year = ?
                        ORDER BY id DESC
                    """, (date[:4],)).fetchall()
                elif start_date and end_date:
                    anime = db.execute("""
                        SELECT id, COALESCE(title_english, title_normalized) as title_display, 
                               (season_year || '-' || season) as release_date, poster_url
                        FROM anime 
                        WHERE season_year BETWEEN ? AND ?
                        ORDER BY id DESC
                    """, (start_date[:4], end_date[:4])).fetchall()
                else:
                    anime = []
                results["anime"] = [dict(a) for a in anime]
            
            return results
    except Exception as e:
        log_error(f"On This Day query failed: {e}")
        return {}
