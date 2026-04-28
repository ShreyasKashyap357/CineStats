from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
import sqlite3
from backend.database import get_db_connection, get_db_context
from src.logic.clash_detector import ClashDetector

router = APIRouter()

@router.get("/")
def get_movies(
    limit: int = 25, 
    offset: int = 0, 
    sort: str = "worldwide_gross_usd", 
    genre: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    origin_country: Optional[str] = None,
    language: Optional[str] = None,
    verdict: Optional[str] = None,
    min_gross_usd: Optional[float] = None,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """Fetch paginated movies with rich metadata. Returns total count for UI pagination."""
    allowed_sorts = ["worldwide_gross_usd", "india_net_cr", "release_date", "title_display"]
    if sort not in allowed_sorts:
        sort = "worldwide_gross_usd"
    
    # Build WHERE clause for filters
    where_clauses = []
    params = []
    
    if genre:
        where_clauses.append("genre LIKE ?")
        params.append(f"%{genre}%")
    
    if year_min:
        where_clauses.append("CAST(SUBSTR(release_date, 1, 4) AS INTEGER) >= ?")
        params.append(year_min)
    
    if year_max:
        where_clauses.append("CAST(SUBSTR(release_date, 1, 4) AS INTEGER) <= ?")
        params.append(year_max)
    
    if origin_country:
        where_clauses.append("origin_country LIKE ?")
        params.append(f"%{origin_country}%")
    
    if language:
        where_clauses.append("language LIKE ?")
        params.append(f"%{language}%")
    
    if verdict:
        where_clauses.append("verdict = ?")
        params.append(verdict)
    
    if min_gross_usd:
        where_clauses.append("worldwide_gross_usd >= ?")
        params.append(min_gross_usd)
    
    where_clause = ""
    if where_clauses:
        where_clause = "WHERE " + " AND ".join(where_clauses)
    
    # Get total count
    total_query = f"SELECT COUNT(*) FROM movies {where_clause}"
    total = db.execute(total_query, params).fetchone()[0]
        
    query = f"""
        SELECT 
            id, title_display, title_normalized, release_date, origin_country, 
            worldwide_gross_usd, domestic_gross_usd, foreign_gross_usd,
            india_net_cr, india_gross_cr, verdict, tmdb_id, bom_id, sacnilk_id,
            total_shows_sacnilk, overseas_gross_cr, poster_url, director, producer, studio, cast_json, overview, genre, language
        FROM movies
        {where_clause}
        ORDER BY {sort} DESC NULLS LAST
        LIMIT ? OFFSET ?
    """
    rows = db.execute(query, params + [limit, offset]).fetchall()
    return {"total": total, "items": [dict(r) for r in rows]}

@router.get("/{movie_id}")
def get_movie_detail(movie_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    """Fetch a single movie and its rollouts and daily performances."""
    movie = db.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
        
    movie_dict = dict(movie)
    
    # Fetch Rollouts
    rollouts = db.execute("SELECT * FROM movie_rollout WHERE movie_id = ?", (movie_id,)).fetchall()
    movie_dict["rollouts"] = [dict(r) for r in rollouts]
    
    # Fetch Daily
    daily = db.execute("SELECT * FROM daily_performance WHERE movie_id = ? ORDER BY date ASC", (movie_id,)).fetchall()
    movie_dict["daily_performance"] = [dict(r) for r in daily]
    
    return movie_dict

@router.delete("/{movie_id}")
def delete_movie(movie_id: int):
    """Delete a movie and all related data from the database."""
    with get_db_context() as conn:
        movie = conn.execute("SELECT id, title_display FROM movies WHERE id = ?", (movie_id,)).fetchone()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        title = movie[1]
        conn.execute("DELETE FROM daily_performance WHERE movie_id = ?", (movie_id,))
        conn.execute("DELETE FROM movie_rollout WHERE movie_id = ?", (movie_id,))
        conn.execute("DELETE FROM movie_franchises WHERE movie_id = ?", (movie_id,))
        conn.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        conn.commit()
    return {"status": "success", "message": f"Deleted '{title}' from database."}

@router.post("/{movie_id}/refresh")
def refresh_movie_data(movie_id: int):
    """Individually update a movie's deep metadata from TMDB."""
    from src.clients.tmdb_client import search_tmdb, get_movie_detail
    import json
    
    with get_db_context() as conn:
        movie = conn.execute("SELECT id, title_display, title_normalized FROM movies WHERE id = ?", (movie_id,)).fetchone()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
            
        m_id, title_display, title_normalized = movie
        title_to_search = title_normalized if title_normalized else title_display
        
        results = search_tmdb(title_to_search, "movie")
        if results and results[0].get("tmdb_id"):
            match = results[0]
            try:
                detail = get_movie_detail(match["tmdb_id"])
                conn.execute("""
                    UPDATE movies 
                    SET poster_url=?, tmdb_id=?, director=?, producer=?, studio=?, cast_json=?, overview=?
                    WHERE id=?
                """, (
                    detail.get("poster_url_card"), 
                    match["tmdb_id"], 
                    ", ".join(detail.get("directors", [])),
                    ", ".join(detail.get("producers", [])),
                    ", ".join(detail.get("studios", [])),
                    json.dumps(detail.get("cast", [])),
                    detail.get("overview"),
                    m_id
                ))
                conn.commit()
                return {"status": "success", "message": f"Successfully updated {title_display} from TMDB."}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to fetch details: {str(e)}")
                
        raise HTTPException(status_code=404, detail="Could not find movie on TMDB.")

@router.get("/{movie_id}/clashes")
def get_movie_clashes(movie_id: int, window_days: int = 14):
    """Get clashing movies for a given movie ID."""
    with get_db_context() as conn:
        clashes = ClashDetector.get_clashing_movies(conn, movie_id, window_days)
        return {"clashes": clashes}

@router.get("/{movie_id}/verdict-context")
def get_verdict_context(movie_id: int):
    """Get movies with similar verdict for comparison."""
    with get_db_context() as conn:
        # Get the current movie's verdict
        movie = conn.execute("SELECT verdict, genre, origin_country FROM movies WHERE id = ?", (movie_id,)).fetchone()
        if not movie or not movie['verdict']:
            return {"similar": []}
        
        verdict = movie['verdict']
        genre = movie['genre']
        country = movie['origin_country']
        
        # Find similar movies with same verdict
        similar = conn.execute("""
            SELECT id, title_display, release_date, worldwide_gross_usd, india_net_cr, verdict, poster_url
            FROM movies
            WHERE id != ? AND verdict = ?
            ORDER BY worldwide_gross_usd DESC
            LIMIT 10
        """, (movie_id, verdict)).fetchall()
        
        return {"similar": [dict(s) for s in similar]}

@router.get("/{movie_id}/on-this-day")
def get_on_this_day_context(movie_id: int):
    """Get movies released on the same day (month/day) in different years."""
    with get_db_context() as conn:
        # Get the current movie's release date
        movie = conn.execute("SELECT release_date FROM movies WHERE id = ?", (movie_id,)).fetchone()
        if not movie or not movie['release_date']:
            return {"same_day": []}
        
        release_date = movie['release_date']
        # Extract month and day (assuming YYYY-MM-DD format)
        month_day = release_date[5:]  # Gets MM-DD
        
        # Find movies released on the same month/day in different years
        same_day = conn.execute("""
            SELECT id, title_display, release_date, worldwide_gross_usd, india_net_cr, verdict, poster_url
            FROM movies
            WHERE id != ? AND release_date LIKE ?
            ORDER BY release_date DESC
            LIMIT 10
        """, (movie_id, f"%-{month_day}")).fetchall()
        
        return {"same_day": [dict(s) for s in same_day]}

@router.get("/{movie_id}/similar")
def get_similar_movies(movie_id: int):
    """Get similar movies using TMDB API."""
    from src.clients.tmdb_client import get_movie_similar
    
    # Get the current movie's tmdb_id
    with get_db_context() as conn:
        movie = conn.execute("SELECT tmdb_id FROM movies WHERE id = ?", (movie_id,)).fetchone()
        if not movie or not movie['tmdb_id']:
            return {"similar": []}
        
        tmdb_id = movie['tmdb_id']
    
    # Fetch similar movies from TMDB
    similar = get_movie_similar(tmdb_id)
    return {"similar": similar}

@router.get("/{movie_id}/franchise-hierarchy")
def get_franchise_hierarchy(movie_id: int):
    """Get franchise hierarchy for a movie (parent franchise and sub-franchises)."""
    with get_db_context() as conn:
        # Get franchises linked to this movie
        movie_franchises = conn.execute("""
            SELECT f.id, f.name, f.url, f.parent_franchise_id, f.franchise_type
            FROM movie_franchises mf
            JOIN franchises f ON mf.franchise_id = f.id
            WHERE mf.movie_id = ?
        """, (movie_id,)).fetchall()
        
        if not movie_franchises:
            return {"parent_franchise": None, "sub_franchises": [], "current_franchises": []}
        
        result = {
            "current_franchises": [dict(f) for f in movie_franchises],
            "parent_franchise": None,
            "sub_franchises": []
        }
        
        # Get parent franchise(s)
        parent_ids = set()
        for f in movie_franchises:
            if f['parent_franchise_id']:
                parent_ids.add(f['parent_franchise_id'])
        
        if parent_ids:
            parent_franchises = conn.execute("""
                SELECT id, name, url, parent_franchise_id, franchise_type
                FROM franchises
                WHERE id IN ({})
            """.format(','.join('?' * len(parent_ids))), list(parent_ids)).fetchall()
            result["parent_franchise"] = [dict(f) for f in parent_franchises]
        
        # Get sub-franchises (franchises that have this movie's franchises as parent)
        current_ids = [f['id'] for f in movie_franchises]
        if current_ids:
            sub_franchises = conn.execute("""
                SELECT id, name, url, parent_franchise_id, franchise_type
                FROM franchises
                WHERE parent_franchise_id IN ({})
            """.format(','.join('?' * len(current_ids))), current_ids).fetchall()
            result["sub_franchises"] = [dict(f) for f in sub_franchises]
        
        return result

@router.post("/backfill-posters")
def backfill_missing_posters():
    """Finds all movies without a poster_url and deep metadata, fetches from TMDB, and updates the DB."""
    from src.clients.tmdb_client import search_tmdb, get_movie_detail
    import json
    
    updated = 0
    with get_db_context() as conn:
        movies = conn.execute("SELECT id, title_display, release_date FROM movies WHERE poster_url IS NULL").fetchall()
        for m in movies:
            m_id, title, r_date = m
            # Try to search TMDB
            results = search_tmdb(title, "movie")
            if results:
                # Find best match
                match = results[0]
                # Deep fetch
                if match.get("tmdb_id"):
                    try:
                        detail = get_movie_detail(match["tmdb_id"])
                        conn.execute("""
                            UPDATE movies 
                            SET poster_url=?, tmdb_id=?, director=?, producer=?, studio=?, cast_json=?, overview=?
                            WHERE id=?
                        """, (
                            detail.get("poster_url_card"), 
                            match["tmdb_id"], 
                            ", ".join(detail.get("directors", [])),
                            ", ".join(detail.get("producers", [])),
                            ", ".join(detail.get("studios", [])),
                            json.dumps(detail.get("cast", [])),
                            detail.get("overview"),
                            m_id
                        ))
                        updated += 1
                    except Exception as e:
                        print(f"Failed to fetch details for {title}: {e}")
        conn.commit()
    return {"status": "success", "updated_count": updated}

@router.get("/{movie_id}/pdf")
def export_movie_pdf(movie_id: int):
    """Export a movie detail view as PDF."""
    from src.utils.pdf_generator import generate_movie_pdf
    
    with get_db_context() as conn:
        movie = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        movie_dict = dict(movie)
    
    pdf_bytes = generate_movie_pdf(movie_dict)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={movie_dict['title_display']}.pdf"}
    )
