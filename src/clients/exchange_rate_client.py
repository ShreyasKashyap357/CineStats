"""
CineStats — Exchange Rate Client
Section 14.8 of the v1.0 specification.

Fetches exchange rates once per session from open.er-api.com.
Falls back to hardcoded rates if the API is unavailable.
"""
import requests
from typing import Optional

from constants import FALLBACK_RATES, SUPPORTED_CURRENCIES
import rate_limits as rl

SOURCE_NAME = "exchange_rate_client"


def fetch_rates() -> dict[str, float]:
    """Fetch current USD-based exchange rates.

    Returns dict mapping currency code to rate (e.g. {'INR': 83.5, 'EUR': 0.92}).
    Falls back to FALLBACK_RATES on error.
    """
    try:
        resp = requests.get(rl.EXCHANGE_RATE["base_url"], timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("result") == "success":
            rates = data.get("rates", {})
            # Filter to only supported currencies
            return {
                code: rates.get(code, FALLBACK_RATES.get(code, 1.0))
                for code in SUPPORTED_CURRENCIES
            }
    except Exception:
        pass

    # Fallback
    return FALLBACK_RATES.copy()
