from fastapi import APIRouter
from typing import Optional
from backend.database import get_db_context
from backend.logger import log_info, log_error

router = APIRouter()

@router.get("/")
def get_movers():
    """Get daily and weekend movers for movies (global and India)."""
    try:
        with get_db_context() as db:
            # For now, return mock data since we don't have daily performance data
            # This would be populated from daily_performance table when available
            global_movers = [
                {
                    "id": 1,
                    "title_display": "Example Movie 1",
                    "poster_url": None,
                    "daily_gross_usd": 15000000,
                    "daily_change_pct": 25.5,
                    "worldwide_gross_usd": 500000000
                },
                {
                    "id": 2,
                    "title_display": "Example Movie 2",
                    "poster_url": None,
                    "daily_gross_usd": 12000000,
                    "daily_change_pct": -5.2,
                    "worldwide_gross_usd": 300000000
                }
            ]
            
            india_movers = [
                {
                    "id": 3,
                    "title_display": "Example Indian Movie 1",
                    "poster_url": None,
                    "daily_india_net_cr": 15.5,
                    "daily_change_pct": 30.0,
                    "india_net_cr": 250.0
                },
                {
                    "id": 4,
                    "title_display": "Example Indian Movie 2",
                    "poster_url": None,
                    "daily_india_net_cr": 12.0,
                    "daily_change_pct": -8.5,
                    "india_net_cr": 180.0
                }
            ]
            
            return {
                "global_gainers": global_movers[:5],
                "global_losers": [],
                "india_gainers": india_movers[:5],
                "india_losers": []
            }
    except Exception as e:
        log_error(f"Failed to get movers: {e}")
        return {"global_gainers": [], "global_losers": [], "india_gainers": [], "india_losers": []}
