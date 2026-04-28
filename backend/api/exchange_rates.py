from fastapi import APIRouter
from src.clients.exchange_rate_client import fetch_rates
from backend.logger import log_info, log_error

router = APIRouter()

@router.get("/")
def get_exchange_rates():
    """Get current exchange rates for USD to supported currencies."""
    try:
        rates = fetch_rates()
        log_info("Fetched exchange rates successfully")
        return {"rates": rates, "base": "USD"}
    except Exception as e:
        log_error(f"Failed to fetch exchange rates: {e}")
        return {"rates": {}, "base": "USD", "error": str(e)}
