from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.queue import ScrapeQueueManager
from backend.database import get_db_connection

router = APIRouter()

class ScrapeRequest(BaseModel):
    module: str
    
@router.post("/trigger")
def trigger_scrape(req: ScrapeRequest):
    """Enqueue a new scrape job."""
    valid_modules = ["bom", "sacnilk", "tmdb", "fx", "trending"]
    if req.module not in valid_modules:
        raise HTTPException(status_code=400, detail=f"Invalid module. Must be one of {valid_modules}")
        
    job_id = ScrapeQueueManager.enqueue_job(req.module)
    return {"job_id": job_id, "status": "queued", "message": f"Successfully queued job for {req.module}"}

@router.get("/status/{job_id}")
def check_job_status(job_id: str):
    """Poll the status of a specific scrape job."""
    from backend.database import get_db_context
    with get_db_context() as conn:
        job = conn.execute(
            "SELECT id, status, module, progress_pct, message, updated_at FROM scrape_jobs WHERE id = ?", 
            (job_id,)
        ).fetchone()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
            
        return dict(job)
@router.post("/search-and-scrape")
def search_and_scrape_movie(req: ScrapeRequest):
    """Deep search DDG to find BOM/Sacnilk URLs and scrape a missing movie."""
    from src.scrapers.sacnilk_scraper import search_sacnilk, scrape_movie_detail as scrape_sacnilk_detail
    from src.scrapers.bom_scraper import search_bom, scrape_movie_detail as scrape_bom_detail
    from backend.database import get_db_context
    from src.scrapers.sacnilk_scraper import _normalize_title
    
    sac_url = search_sacnilk(req.module) # module is the query here
    bom_url = search_bom(req.module)
    
    if not sac_url and not bom_url:
        raise HTTPException(status_code=404, detail="Movie not found on Sacnilk or BOM.")
        
    sac_data = scrape_sacnilk_detail(sac_url) if sac_url else {}
    bom_data = scrape_bom_detail(bom_url) if bom_url else {}
    
    title_display = sac_data.get('title_display') or bom_data.get('title_display') or req.module
    title_normalized = _normalize_title(title_display)
    
    with get_db_context() as conn:
        cursor = conn.execute("""
            INSERT INTO movies (
                title_display, title_normalized, release_date, language, 
                india_net_cr, india_gross_cr, verdict, total_shows_sacnilk, overseas_gross_cr,
                worldwide_gross_usd, domestic_gross_usd, foreign_gross_usd, 
                sacnilk_id, bom_id, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                india_net_cr=excluded.india_net_cr,
                worldwide_gross_usd=excluded.worldwide_gross_usd
            RETURNING id
        """, (
            title_display, title_normalized, 
            sac_data.get('release_date') or bom_data.get('release_date'),
            sac_data.get('language'),
            sac_data.get('india_net_cr'), sac_data.get('india_gross_cr'),
            sac_data.get('verdict'), sac_data.get('total_shows_sacnilk'),
            sac_data.get('overseas_gross_cr'),
            bom_data.get('worldwide_gross_usd'), bom_data.get('domestic_gross_usd'),
            bom_data.get('foreign_gross_usd'),
            sac_url, bom_url, 'search'
        ))
        
        movie_id = cursor.fetchone()[0]
        
        # Insert BOM rollouts if any
        if bom_data.get('rollouts'):
            for r in bom_data['rollouts']:
                conn.execute("""
                    INSERT INTO movie_rollout (movie_id, country_name, region, gross_usd, opening_usd, release_date, source_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(movie_id, country_name) DO UPDATE SET gross_usd=excluded.gross_usd
                """, (
                    movie_id, r['country_name'], r['region'], r['gross_usd'], 
                    r['opening_usd'], r['release_date'], r.get('source_url')
                ))
                
        # Insert Daily Performance if any
        if sac_data.get('daily_performance'):
            for d in sac_data['daily_performance']:
                conn.execute("""
                    INSERT INTO daily_performance (movie_id, date, daily_india_net_cr, cumulative_india_net_cr)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(movie_id, date) DO UPDATE SET daily_india_net_cr=excluded.daily_india_net_cr
                """, (movie_id, d['day'], d.get('daily_india_net_cr'), d.get('cumulative_india_net_cr')))
                
        conn.commit()
        
    return {"status": "success", "movie_id": movie_id, "title": title_display}
