from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import platform
import os
from contextlib import asynccontextmanager
from backend.queue import queue_worker
from backend.logger import log_info, log_error, get_logger

logger = get_logger("backend-main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: spawn queue worker
    logger.info("=" * 60)
    logger.info("CINESTATS API STARTUP")
    logger.info("=" * 60)
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python Version: {platform.python_version()}")
    logger.info(f"Working Directory: {os.getcwd()}")
    logger.info(f"Environment: {'Development' if os.getenv('DEBUG') else 'Production'}")
    
    logger.info("Starting CineStats API...")
    worker_task = asyncio.create_task(queue_worker())
    logger.info("Queue worker started")
    
    # Log registered routes
    logger.info("Registered API Routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            logger.info(f"  {', '.join(route.methods)} {route.path}")
    
    logger.info("=" * 60)
    logger.info("CINESTATS API READY")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown: cancel task
    logger.info("=" * 60)
    logger.info("CINESTATS API SHUTDOWN")
    logger.info("=" * 60)
    logger.info("Shutting down CineStats API...")
    worker_task.cancel()
    logger.info("Queue worker cancelled")
    logger.info("CineStats API stopped successfully")
    logger.info("=" * 60)

app = FastAPI(
    title="CineStats API",
    description="Backend API for the CineStats decoupled architecture.",
    version="2.0.0",
    lifespan=lifespan
)

# Allow React Frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "online", "message": "CineStats API is running."}

from backend.api import scraper, movies, franchises, records, discover, tv, anime, search, settings, watchlist, movers, clash, exchange_rates, logs, recommendations, export, verdict, aggregates, comparisons

# Mount Routers
app.include_router(movies.router, prefix="/api/movies", tags=["Movies"])
app.include_router(scraper.router, prefix="/api/scrape", tags=["Scraping Queue"])
app.include_router(search.router, prefix="/api/search", tags=["Global Search"])
app.include_router(franchises.router, prefix="/api/franchises", tags=["Franchises"])
app.include_router(records.router, prefix="/api/records", tags=["Records"])
app.include_router(discover.router, prefix="/api/discover", tags=["Discover Hub"])
app.include_router(tv.router, prefix="/api/tv", tags=["TV Series"])
app.include_router(anime.router, prefix="/api/anime", tags=["Anime"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["Watchlist"])
app.include_router(movers.router, prefix="/api/movers", tags=["Movers"])
app.include_router(clash.router, prefix="/api/clash", tags=["Clash Analyzer"])
app.include_router(exchange_rates.router, prefix="/api/exchange-rates", tags=["Exchange Rates"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(verdict.router, prefix="/api/verdict", tags=["Verdict"])
app.include_router(aggregates.router, prefix="/api/aggregates", tags=["Aggregates"])
app.include_router(comparisons.router, prefix="/api/comparisons", tags=["Comparisons"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
