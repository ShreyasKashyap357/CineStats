from fastapi import APIRouter, HTTPException
from typing import List, Dict
from backend.database import get_db_context

router = APIRouter()

@router.get("/list/{category}")
def list_franchises(category: str):
    """Fetches the master list of franchises, brands, or genres from BOM."""
    if category not in ["brand", "franchise", "genre"]:
        raise HTTPException(status_code=400, detail="Invalid category")
        
    from src.scrapers.bom_scraper import scrape_franchise_list
    data = scrape_franchise_list(category)
    
    # Store them in DB so they have an ID
    with get_db_context() as conn:
        for f in data:
            # Check if franchise with this url already exists
            existing = conn.execute("SELECT id FROM franchises WHERE url = ?", (f['url'],)).fetchone()
            if existing:
                conn.execute("UPDATE franchises SET name=?, franchise_type=? WHERE id=?",
                             (f['name'], f['type'], existing[0]))
            else:
                conn.execute("""
                    INSERT INTO franchises (name, franchise_type, url) 
                    VALUES (?, ?, ?)
                """, (f['name'], f['type'], f['url']))
        conn.commit()
        
    return data

@router.get("/detail")
def get_franchise_detail(url: str):
    """Scrapes the specific franchise, fetches its movies, and links them."""
    from src.scrapers.bom_scraper import scrape_franchise_detail
    from src.scrapers.bom_scraper import _normalize_title
    
    movies = scrape_franchise_detail(url)
    
    with get_db_context() as conn:
        # Get franchise ID
        cursor = conn.execute("SELECT id FROM franchises WHERE url = ?", (url,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Franchise not found in DB")
        franchise_id = row[0]
        
        # Insert movies (shallow) and link them
        for m in movies:
            title_norm = _normalize_title(m['title'])
            # Check if movie with this bom_url already exists
            existing = conn.execute(
                "SELECT id FROM movies WHERE title_normalized = ? OR bom_id = ?",
                (title_norm, m.get('url'))
            ).fetchone()
            
            if existing:
                movie_id = existing[0]
            else:
                c = conn.execute("""
                    INSERT INTO movies (title_display, title_normalized, bom_id, source)
                    VALUES (?, ?, ?, ?)
                """, (m['title'], title_norm, m.get('url'), 'bom_franchise'))
                movie_id = c.lastrowid
            
            # Link (ignore if already linked)
            conn.execute("""
                INSERT OR IGNORE INTO movie_franchises (movie_id, franchise_id)
                VALUES (?, ?)
            """, (movie_id, franchise_id))
            
        conn.commit()
        
    return {"status": "success", "movies": movies}

