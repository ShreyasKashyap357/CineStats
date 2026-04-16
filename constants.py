"""
CineStats — Application Constants
Fallback exchange rates, config values, data cutoff logic.
"""
from datetime import date, timedelta, datetime, timezone

# ── App Metadata ─────────────────────────────────────────────────────────────
APP_NAME    = "CineStats"
APP_VERSION = "1.0"

# ── Supported Currencies ─────────────────────────────────────────────────────
SUPPORTED_CURRENCIES = ["USD", "INR", "EUR", "GBP", "JPY", "AED", "AUD", "CAD", "SGD"]
DEFAULT_CURRENCY = "INR"

CURRENCY_SYMBOLS = {
    "USD": "$", "INR": "₹", "EUR": "€", "GBP": "£", "JPY": "¥",
    "AED": "AED", "AUD": "A$", "CAD": "C$", "SGD": "S$",
}

# ── Fallback Exchange Rates (approximate, used when API unavailable) ─────────
FALLBACK_RATES = {
    "USD": 1.0,
    "INR": 93,
    "EUR": 0.86,
    "GBP": 0.75,
    "JPY": 158,
    "AED": 3.67,
    "AUD": 1.42,
    "CAD": 1.38,
    "SGD": 1.27,
}

# ── Country Lens ─────────────────────────────────────────────────────────────
MAX_COUNTRY_LENS = 3  # Global + up to 3 additional countries

# ── Pagination ───────────────────────────────────────────────────────────────
PAGE_SIZES = [12, 24, 48]
DEFAULT_PAGE_SIZE = 24

# ── Content Types ────────────────────────────────────────────────────────────
CONTENT_TYPES = ["movie", "tv_series", "anime", "western_animation", "cartoon"]

CONTENT_TYPE_LABELS = {
    "movie":              "Movie",
    "tv_series":          "TV Series",
    "anime":              "Anime",
    "western_animation":  "Western Animation",
    "cartoon":            "Cartoon",
}

# ── Anime Demographics ──────────────────────────────────────────────────────
ANIME_DEMOGRAPHICS = ["Shounen", "Shoujo", "Seinen", "Josei", "Kodomomuke"]

# ── Verdict Order (best to worst) ────────────────────────────────────────────
VERDICT_ORDER = [
    "All-Time Blockbuster", "Blockbuster", "Super Hit", "Hit",
    "Above Average", "Average", "Below Average", "Flop", "Disaster",
]

# ── Franchise Relationship Tags ──────────────────────────────────────────────
RELATIONSHIP_TAGS = [
    "original", "reboot", "continuation", "spin_off", "parallel_entry", "remake",
]

# ── Data Cutoff ──────────────────────────────────────────────────────────────
def get_data_cutoff() -> date:
    """Return the data cutoff date (1-2 days prior to current date).
    If all timezones have passed midnight (UTC), use yesterday;
    otherwise use day before yesterday."""
    now_utc = datetime.now(timezone.utc)
    # If it's past noon UTC, most timezones have passed midnight
    if now_utc.hour >= 12:
        return (now_utc - timedelta(days=1)).date()
    return (now_utc - timedelta(days=2)).date()

# ── Database ─────────────────────────────────────────────────────────────────
DB_PATH     = "cinestats.db"
SEED_DB_PATH = "seed.db"
SCHEMA_VERSION = 1

# ── Matching ─────────────────────────────────────────────────────────────────
FUZZY_MATCH_THRESHOLD = 85      # rapidfuzz score threshold
DATE_PROXIMITY_DAYS   = 7       # release date matching window

# ── Similar Titles ───────────────────────────────────────────────────────────
SIMILAR_TITLES_COUNT  = 10       # max suggestions
SIMILAR_GENRE_SCORE   = 3
SIMILAR_COUNTRY_SCORE = 2
SIMILAR_DECADE_SCORE  = 1
SIMILAR_GROSS_SCORE   = 2       # within 2x factor

# ── Predictor Engine ─────────────────────────────────────────────────────────
PREDICTOR_LOOKBACK_YEARS = 10    # historical data window

# ── Clash Detector ───────────────────────────────────────────────────────────
CLASH_DATE_TOLERANCE_DAYS = 1   # ±1 day for release date matching

# ── Movers ───────────────────────────────────────────────────────────────────
MOVERS_TOP_N = 10                # top 5 gainers + top 5 losers

# ── On This Day ─────────────────────────────────────────────────────────────
OTD_DEFAULT_LIMIT = 10           # default number of entries shown on "On This Day"

# ── Movie Leaderboard ───────────────────────────────────────────────────────
# Each entry: (label, country_filter_value_for_origin_country_column)
# "Global" means no country filter — just top by worldwide_gross_usd
MOVIE_LEADERBOARD_COUNTRIES = [
    ("🌍 Global", None),
    ("🇮🇳 India", "IN"),
    ("🇺🇸 United States", "US"),
]
MOVIE_LEADERBOARD_TOP_N = 10
