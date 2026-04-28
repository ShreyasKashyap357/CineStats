from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional
from backend.database import get_db_context

router = APIRouter()

@router.get("/search")
def search_tv_series(query: str = Query(..., description="Search query for TV series")):
    """Search for TV series using TMDB API."""
    from src.clients.tmdb_client import search_tmdb
    try:
        results = search_tmdb(query, "tv")
        formatted = []
        for t in results:
            formatted.append({
                "tmdb_id": t.get("tmdb_id"),
                "title": t.get("title"),
                "poster_url": t.get("poster_url"),
                "overview": t.get("overview"),
                "first_air_date": t.get("first_air_date"),
                "vote_average": t.get("vote_average"),
                "origin_country": t.get("origin_country")
            })
        return {"results": formatted}
    except Exception as e:
        print(f"TV search error: {e}")
        return {"results": []}

@router.get("/")
def get_all_tv_series(
    skip: int = 0, 
    limit: int = 25,
    status: Optional[str] = None,
    origin_country: Optional[str] = None,
    network: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    genre: Optional[str] = None
):
    """Powers the paginated grid on the React TV Tab with advanced filters."""
    with get_db_context() as conn:
        # Build WHERE clause for filters
        where_clauses = []
        params = []
        
        if status:
            where_clauses.append("status = ?")
            params.append(status)
        
        if origin_country:
            where_clauses.append("origin_country LIKE ?")
            params.append(f"%{origin_country}%")
        
        if network:
            where_clauses.append("network LIKE ?")
            params.append(f"%{network}%")
        
        if year_min:
            where_clauses.append("CAST(SUBSTR(premiere_date, 1, 4) AS INTEGER) >= ?")
            params.append(year_min)
        
        if year_max:
            where_clauses.append("CAST(SUBSTR(premiere_date, 1, 4) AS INTEGER) <= ?")
            params.append(year_max)
        
        if genre:
            where_clauses.append("genre LIKE ?")
            params.append(f"%{genre}%")
        
        where_clause = ""
        if where_clauses:
            where_clause = "WHERE " + " AND ".join(where_clauses)
        
        total = conn.execute(f"SELECT COUNT(*) FROM tv_series {where_clause}", params).fetchone()[0]
        series = conn.execute(f"""
            SELECT id, title_display as name, network, genre, status, premiere_date, total_seasons, total_episodes, avg_rating, tvmaze_id, tmdb_id, poster_url, overview, origin_country
            FROM tv_series
            {where_clause}
            ORDER BY premiere_date DESC
            LIMIT ? OFFSET ?
        """, params + [limit, skip]).fetchall()
        return {"total": total, "items": [dict(s) for s in series]}

@router.get("/{series_id}")
def get_tv_series_detail(series_id: int):
    """Joins tv_series and tv_episodes for the detail view charts."""
    with get_db_context() as conn:
        # Get series metadata
        series_row = conn.execute("""
            SELECT id, title_display as name, network, genre, status, premiere_date, total_seasons, total_episodes, avg_rating, tvmaze_id, tmdb_id, poster_url, overview, director, producer, studio, cast_json
            FROM tv_series WHERE id = ?
        """, (series_id,)).fetchone()
        
        if not series_row:
            raise HTTPException(status_code=404, detail="Series not found")
            
        series = dict(series_row)
        
        # Get episodes
        episodes = conn.execute("""
            SELECT season, episode, title, air_date, us_viewers as viewership_millions, rating
            FROM tv_episodes
            WHERE series_id = ?
            ORDER BY season ASC, episode ASC
        """, (series_id,)).fetchall()
        
        series["episodes"] = [dict(ep) for ep in episodes]
        return series

@router.get("/{series_id}/charts")
def get_tv_charts(series_id: int):
    """Get episode-by-episode viewership and rating line charts data."""
    with get_db_context() as conn:
        episodes = conn.execute("""
            SELECT season, episode, title, air_date, us_viewers as viewership_millions, rating
            FROM tv_episodes
            WHERE series_id = ?
            ORDER BY season ASC, episode ASC
        """, (series_id,)).fetchall()
        
        if not episodes:
            return {"viewership": [], "ratings": []}
        
        viewership_data = []
        ratings_data = []
        
        for ep in episodes:
            ep_dict = dict(ep)
            viewership_data.append({
                "episode": ep_dict["episode"],
                "season": ep_dict["season"],
                "viewership": ep_dict.get("viewership_millions", 0),
                "title": ep_dict["title"]
            })
            ratings_data.append({
                "episode": ep_dict["episode"],
                "season": ep_dict["season"],
                "rating": ep_dict.get("rating", 0),
                "title": ep_dict["title"]
            })
        
        return {"viewership": viewership_data, "ratings": ratings_data}

@router.get("/{series_id}/season-compare")
def get_tv_season_compare(series_id: int):
    """Get season comparison bar chart data."""
    with get_db_context() as conn:
        seasons = conn.execute("""
            SELECT season, 
                   AVG(us_viewers) as avg_viewership,
                   AVG(rating) as avg_rating,
                   COUNT(*) as episode_count
            FROM tv_episodes
            WHERE series_id = ?
            GROUP BY season
            ORDER BY season ASC
        """, (series_id,)).fetchall()
        
        return {"seasons": [dict(s) for s in seasons]}

@router.get("/{series_id}/episodes")
def get_tv_episode_table(series_id: int, season: Optional[int] = None):
    """Get expandable per-season episode list."""
    with get_db_context() as conn:
        if season:
            episodes = conn.execute("""
                SELECT season, episode, title, air_date, us_viewers as viewership_millions, rating
                FROM tv_episodes
                WHERE series_id = ? AND season = ?
                ORDER BY episode ASC
            """, (series_id, season)).fetchall()
        else:
            episodes = conn.execute("""
                SELECT season, episode, title, air_date, us_viewers as viewership_millions, rating
                FROM tv_episodes
                WHERE series_id = ?
                ORDER BY season ASC, episode ASC
            """, (series_id,)).fetchall()
        
        # Group by season
        seasons = {}
        for ep in episodes:
            ep_dict = dict(ep)
            season_num = ep_dict["season"]
            if season_num not in seasons:
                seasons[season_num] = []
            seasons[season_num].append(ep_dict)
        
        return {"seasons": seasons}


@router.post("/scrape")
def trigger_tv_scrape(query: str, background_tasks: BackgroundTasks):
    """Pushes a TVMaze + Wikipedia scrape job."""
    
    def background_scrape_task(q: str):
        from src.scrapers.tv_scraper import pipeline_scrape_tv
        result = pipeline_scrape_tv(q)
        if result.get("status") == "success":
            s = result["series"]
            eps = result["episodes"]
            
            with get_db_context() as conn:
                # Check if Series exists
                cursor = conn.execute("SELECT id FROM tv_series WHERE tvmaze_id = ?", (s["tvmaze_id"],))
                row = cursor.fetchone()
                
                if row:
                    series_id = row[0]
                    conn.execute("""
                        UPDATE tv_series 
                        SET status=?, avg_rating=?, director=?, producer=?, studio=?, cast_json=?, overview=?
                        WHERE id=?
                    """, (s["status"], s["avg_rating"], s.get("director"), s.get("producer"), s.get("studio"), s.get("cast_json"), s.get("overview"), series_id))
                else:
                    cursor = conn.execute("""
                        INSERT INTO tv_series (title_normalized, title_display, network, genre, status, premiere_date, tvmaze_id, avg_rating, director, producer, studio, cast_json, overview)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        RETURNING id
                    """, (s["name"].lower(), s["name"], s["network"], s["genre"], s["status"], s["premiere_date"], s["tvmaze_id"], s["avg_rating"], s.get("director"), s.get("producer"), s.get("studio"), s.get("cast_json"), s.get("overview")))
                    series_id = cursor.fetchone()[0]
                
                # Insert Episodes
                for ep in eps:
                    # tv_episodes DOES have UNIQUE(series_id, season, episode)
                    conn.execute("""
                        INSERT INTO tv_episodes (series_id, season, episode, title, air_date, us_viewers, rating)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(series_id, season, episode) DO UPDATE SET
                            us_viewers=excluded.us_viewers,
                            rating=excluded.rating
                    """, (series_id, ep["season"], ep["episode"], ep["title"], ep["air_date"], ep["viewership_millions"], ep["rating"]))
                    
                # Update total seasons/eps
                conn.execute("""
                    UPDATE tv_series 
                    SET total_episodes = (SELECT COUNT(*) FROM tv_episodes WHERE series_id = ?),
                        total_seasons = (SELECT MAX(season) FROM tv_episodes WHERE series_id = ?)
                    WHERE id = ?
                """, (series_id, series_id, series_id))
                
                conn.commit()

    background_tasks.add_task(background_scrape_task, query)
    return {"message": "Scrape job queued", "query": query}

@router.post("/{series_id}/refresh")
def refresh_tv_series_data(series_id: int):
    """Individually update a TV series's deep metadata from TVMaze."""
    from src.scrapers.tv_scraper import pipeline_scrape_tv
    import json
    
    with get_db_context() as conn:
        series = conn.execute("SELECT id, title_display, tvmaze_id FROM tv_series WHERE id = ?", (series_id,)).fetchone()
        if not series:
            raise HTTPException(status_code=404, detail="Series not found")
            
        s_id, title_display, tvmaze_id = series
        if not tvmaze_id:
            raise HTTPException(status_code=400, detail="Series has no tvmaze_id to refresh from")
        
        # Re-scrape using the existing tvmaze_id
        result = pipeline_scrape_tv(title_display)
        if result.get("status") == "success":
            s = result["series"]
            eps = result["episodes"]
            
            conn.execute("""
                UPDATE tv_series 
                SET status=?, avg_rating=?, director=?, producer=?, studio=?, cast_json=?, overview=?
                WHERE id=?
            """, (s["status"], s["avg_rating"], s.get("director"), s.get("producer"), s.get("studio"), s.get("cast_json"), s.get("overview"), s_id))
            
            # Update Episodes
            for ep in eps:
                conn.execute("""
                    INSERT INTO tv_episodes (series_id, season, episode, title, air_date, us_viewers, rating)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(series_id, season, episode) DO UPDATE SET
                        us_viewers=excluded.us_viewers,
                        rating=excluded.rating
                """, (s_id, ep["season"], ep["episode"], ep["title"], ep["air_date"], ep["viewership_millions"], ep["rating"]))
            
            # Update total seasons/eps
            conn.execute("""
                UPDATE tv_series 
                SET total_episodes = (SELECT COUNT(*) FROM tv_episodes WHERE series_id = ?),
                    total_seasons = (SELECT MAX(season) FROM tv_episodes WHERE series_id = ?)
                WHERE id = ?
            """, (s_id, s_id, s_id))
            
            conn.commit()
            return {"status": "success", "message": f"Successfully updated {title_display} from TVMaze."}
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh data from TVMaze")

@router.delete("/{series_id}")
def delete_tv_series(series_id: int):
    """Delete a TV series and all its episodes from the database."""
    with get_db_context() as conn:
        series = conn.execute("SELECT id, title_display FROM tv_series WHERE id = ?", (series_id,)).fetchone()
        if not series:
            raise HTTPException(status_code=404, detail="Series not found")
        title = series[1]
        conn.execute("DELETE FROM tv_episodes WHERE series_id = ?", (series_id,))
        conn.execute("DELETE FROM tv_series WHERE id = ?", (series_id,))
        conn.commit()
    return {"status": "success", "message": f"Deleted '{title}' from database."}

@router.get("/{series_id}/similar")
def get_similar_tv_series(series_id: int):
    """Get similar TV series using TMDB API."""
    from src.clients.tmdb_client import get_tv_similar
    
    # Get the current series' tmdb_id
    with get_db_context() as conn:
        series = conn.execute("SELECT tmdb_id FROM tv_series WHERE id = ?", (series_id,)).fetchone()
        if not series or not series['tmdb_id']:
            return {"similar": []}
        
        tmdb_id = series['tmdb_id']
    
    # Fetch similar series from TMDB
    similar = get_tv_similar(tmdb_id)
    return {"similar": similar}

@router.get("/{series_id}/pdf")
def export_tv_series_pdf(series_id: int):
    """Export a TV series detail view as PDF."""
    from src.utils.pdf_generator import generate_tv_series_pdf
    import io
    
    with get_db_context() as conn:
        series = conn.execute("SELECT * FROM tv_series WHERE id = ?", (series_id,)).fetchone()
        if not series:
            raise HTTPException(status_code=404, detail="TV Series not found")
        
        series_dict = dict(series)
    
    pdf_bytes = generate_tv_series_pdf(series_dict)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={series_dict['title_display']}.pdf"}
    )
