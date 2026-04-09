"""
CineStats — API Rate Limit Constants
Section 19 of the v1.0 specification.
All rate limits defined here. No hardcoded delay values elsewhere.
"""

# Per-domain rate limit configurations
# Format: (max_requests, time_window_seconds)

JIKAN = {
    "domain":    "api.jikan.moe",
    "per_sec":   (3, 1),       # 3 requests per second
    "per_min":   (60, 60),     # 60 requests per minute
    "base_url":  "https://api.jikan.moe/v4",
}

ANILIST = {
    "domain":    "graphql.anilist.co",
    "per_min":   (90, 60),     # 90 requests per minute
    "base_url":  "https://graphql.anilist.co",
}

TVMAZE = {
    "domain":    "api.tvmaze.com",
    "per_window": (20, 10),    # 20 requests per 10 seconds
    "base_url":  "https://api.tvmaze.com",
}

TMDB = {
    "domain":    "api.themoviedb.org",
    "per_window": (40, 10),    # ~40 requests per 10 seconds
    "base_url":  "https://api.themoviedb.org/3",
    "img_base":  "https://image.tmdb.org/t/p",
    "poster_card":   "w185",   # card thumbnails
    "poster_detail": "w500",   # detail view and PDF
}

BOM = {
    "domain":       "www.boxofficemojo.com",
    "min_delay_s":  2.0,       # minimum 2 seconds between requests
    "base_url":     "https://www.boxofficemojo.com",
    "user_agent":   "CineStats-Bot/1.0 (personal project; non-commercial)",
}

SACNILK = {
    "domain":       "www.sacnilk.com",
    "min_delay_s":  2.0,
    "base_url":     "https://www.sacnilk.com",
    "user_agent":   "CineStats-Bot/1.0 (personal project; non-commercial)",
}

WIKIPEDIA = {
    "domain":       "en.wikipedia.org",
    "min_delay_s":  2.0,
    "user_agent":   "CineStats-Bot/1.0 (personal project; non-commercial)",
}

EXCHANGE_RATE = {
    "domain":    "open.er-api.com",
    "per_session": 1,          # single call per session
    "base_url":  "https://open.er-api.com/v6/latest/USD",
}
