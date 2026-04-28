import asyncio
import sqlite3
import uuid
from typing import Optional
from backend.database import get_db_context

from backend.orchestrator import run_sacnilk_job, run_bom_job

# Will be populated with actual scraper imports
SCRAPER_REGISTRY = {
    "sacnilk": run_sacnilk_job,
    "bom": run_bom_job
}

class ScrapeQueueManager:
    """SQLite-backed task queue for processing background scraping jobs."""
    
    @staticmethod
    def enqueue_job(module: str) -> str:
        job_id = str(uuid.uuid4())
        with get_db_context() as conn:
            conn.execute(
                "INSERT INTO scrape_jobs (id, status, module, progress_pct, message) VALUES (?, ?, ?, ?, ?)",
                (job_id, "pending", module, 0, "Job queued")
            )
            conn.commit()
        return job_id
        
    @staticmethod
    def claim_next_job() -> Optional[dict]:
        """Atomically claim the next pending job."""
        with get_db_context() as conn:
            job = conn.execute(
                "SELECT * FROM scrape_jobs WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1"
            ).fetchone()
            
            if job:
                job_dict = dict(job)
                conn.execute(
                    "UPDATE scrape_jobs SET status = 'processing', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (job_dict['id'],)
                )
                conn.commit()
                return job_dict
        return None
        
    @staticmethod
    def update_job(job_id: str, status: str, progress: int, message: str):
        with get_db_context() as conn:
            conn.execute(
                "UPDATE scrape_jobs SET status = ?, progress_pct = ?, message = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, progress, message, job_id)
            )
            conn.commit()

async def queue_worker():
    """Background worker that continuously polls for new jobs."""
    print("[CineStats Queue] Background worker started.")
    while True:
        try:
            job = ScrapeQueueManager.claim_next_job()
            if job:
                print(f"[CineStats Queue] Picked up job {job['id']} for module {job['module']}")
                ScrapeQueueManager.update_job(job['id'], "processing", 10, "Initializing scraper...")
                
                # Execute the scraper
                scraper_func = SCRAPER_REGISTRY.get(job['module'])
                if scraper_func:
                    # Run synchronous scrapers in executor to prevent event loop blocking
                    await asyncio.to_thread(scraper_func, job['id'])
                else:
                    ScrapeQueueManager.update_job(job['id'], "failed", 0, f"Unknown module: {job['module']}")
            else:
                await asyncio.sleep(2) # Poll delay
        except Exception as e:
            print(f"[CineStats Queue Error] {str(e)}")
            await asyncio.sleep(5)
