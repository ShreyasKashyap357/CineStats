"""
CineStats — TMDB API Client
Section 14.3 of the v1.0 specification.

Provides:
  - Movie search and metadata
  - Poster URLs (w185 for cards, w500 for detail)
  - Genre tags, cast, crew, origin country, runtime
  - Trending movies
"""
from curl_cffi import requests
from typing import Optional
import os

from src.rate_limiter import RateLimiter, FetchException
import rate_limits as rl

SOURCE_NAME = "tmdb_client"
_limiter = RateLimiter()
_BASE = rl.TMDB["base_url"]


def _get_api_key() -> str:
    """Get TMDB API key from secrets or env."""
    api_key = os.environ.get("TMDB_API_KEY", "")
    if api_key:
        return api_key
        
    try:
        import tomli
        with open(".streamlit/secrets.toml", "rb") as f:
            secrets = tomli.load(f)
            return secrets.get("TMDB_API_KEY", "")
    except Exception:
        pass
        
    try:
        import toml
        with open(".streamlit/secrets.toml", "r") as f:
            secrets = toml.load(f)
            return secrets.get("TMDB_API_KEY", "")
    except Exception:
        pass
        
    return ""


def _api_get(endpoint: str, params: dict = None) -> dict:
    """Make an authenticated GET to the TMDB API with retry logic."""
    if not _limiter.wait(rl.TMDB["domain"]):
        raise FetchException(SOURCE_NAME, endpoint, "Rate limit timeout")

    api_key = _get_api_key()
    if not api_key:
        raise FetchException(SOURCE_NAME, endpoint, "TMDB API key not configured")

    url = f"{_BASE}{endpoint}"
    all_params = {"api_key": api_key, **(params or {})}

    import time
    # Cycle through different browser profiles in case one gets blocked
    profiles = ["safari15_3", "chrome110", "chrome107"]
    last_error = None
    
    for attempt in range(3):
        try:
            profile = profiles[attempt % len(profiles)]
            session = requests.Session(impersonate=profile)
            resp = session.get(url, params=all_params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last_error = e
            if attempt < 2:
                time.sleep(2 * (attempt + 1))  # 2s, 4s backoff
            
    raise FetchException(SOURCE_NAME, endpoint, str(last_error))


def get_poster_url(poster_path: str, size: str = "w185") -> Optional[str]:
    """Build a full poster URL from a TMDB poster path.

    Args:
        poster_path: e.g. '/kqjL17yufvn9OVLyXYpvtyrFfak.jpg'
        size: 'w185' for thumbnails, 'w500' for detail/PDF
    """
    if not poster_path:
        return None
    return f"{rl.TMDB['img_base']}/{size}{poster_path}"


def search_movie(title: str, year: int = None) -> list[dict]:
    """Search TMDB for movies by title.

    Returns list of dicts with:
        tmdb_id, title, original_title, release_date, poster_path,
        poster_url_card, poster_url_detail, overview, popularity
    """
    params = {"query": title, "include_adult": "false"}
    if year:
        params["year"] = str(year)

    data = _api_get("/search/movie", params)
    results = []
    for item in data.get("results", []):
        poster_path = item.get("poster_path")
        results.append({
            "tmdb_id":           item.get("id"),
            "title":             item.get("title"),
            "original_title":    item.get("original_title"),
            "release_date":      item.get("release_date"),
            "poster_path":       poster_path,
            "poster_url_card":   get_poster_url(poster_path, rl.TMDB["poster_card"]),
            "poster_url_detail": get_poster_url(poster_path, rl.TMDB["poster_detail"]),
            "overview":          item.get("overview"),
            "popularity":        item.get("popularity"),
            "vote_average":      item.get("vote_average"),
            "genre_ids":         item.get("genre_ids", []),
        })
    return results


def get_movie_detail(tmdb_id: int) -> dict:
    """Get full movie details from TMDB including credits.

    Returns dict with:
        tmdb_id, title, original_title, release_date, runtime, overview,
        budget, revenue, genres, origin_country, poster_path, poster_url_card,
        poster_url_detail, cast, crew, directors
    """
    data = _api_get(f"/movie/{tmdb_id}", {"append_to_response": "credits"})

    poster_path = data.get("poster_path")
    genres = [g["name"] for g in data.get("genres", [])]
    countries = [c.get("iso_3166_1") for c in data.get("production_countries", [])]

    # Extract cast and crew
    credits = data.get("credits", {})
    cast = [
        {"name": c["name"], "character": c.get("character", ""),
         "profile_path": c.get("profile_path")}
        for c in credits.get("cast", [])[:15]  # top 15
    ]
    directors = [
        c["name"] for c in credits.get("crew", [])
        if c.get("job") == "Director"
    ]

    producers = [
        c["name"] for c in credits.get("crew", [])
        if c.get("job") == "Producer"
    ]
    studios = [c["name"] for c in data.get("production_companies", [])]

    result = {
        "tmdb_id":           data.get("id"),
        "title":             data.get("title"),
        "original_title":    data.get("original_title"),
        "release_date":      data.get("release_date"),
        "runtime":           data.get("runtime"),
        "overview":          data.get("overview"),
        "budget":            data.get("budget"),
        "revenue":           data.get("revenue"),
        "genre":             ", ".join(genres),
        "origin_country":    countries[0] if countries else None,
        "poster_path":       poster_path,
        "poster_url_card":   get_poster_url(poster_path, rl.TMDB["poster_card"]),
        "poster_url_detail": get_poster_url(poster_path, rl.TMDB["poster_detail"]),
        "cast":              cast,
        "directors":         directors,
        "producers":         producers,
        "studios":           studios,
    }
    
    # Wiki Fallback Pattern
    if not result['revenue'] or not result['origin_country']:
        try:
            from src.scrapers.wikipedia_movie_scraper import get_movie_infobox_data
            wiki_data = get_movie_infobox_data(result['title'], result['release_date'][:4] if result['release_date'] else "")
            if not result['revenue'] and wiki_data.get('worldwide_gross_usd'):
                result['revenue'] = int(wiki_data['worldwide_gross_usd'])
            if not result['origin_country'] and wiki_data.get('country'):
                result['origin_country'] = wiki_data['country']
        except Exception:
            pass
            
    return result


def get_trending_movies(time_window: str = "week") -> list[dict]:
    """Get trending movies from TMDB.

    Args:
        time_window: 'day' or 'week'
    """
    data = _api_get(f"/trending/movie/{time_window}")
    results = []
    for item in data.get("results", []):
        poster_path = item.get("poster_path")
        results.append({
            "tmdb_id":           item.get("id"),
            "title":             item.get("title"),
            "release_date":      item.get("release_date"),
            "poster_url_card":   get_poster_url(poster_path, rl.TMDB["poster_card"]),
            "vote_average":      item.get("vote_average"),
            "popularity":        item.get("popularity"),
        })
    return results

def search_tmdb(query: str, search_type: str = "multi") -> list[dict]:
    """Search TMDB for movies or tv shows."""
    data = _api_get(f"/search/{search_type}", {"query": query, "include_adult": "false"})
    results = []
    for item in data.get("results", []):
        if item.get("media_type") not in ("movie", "tv") and search_type == "multi":
            continue
            
        poster_path = item.get("poster_path")
        results.append({
            "tmdb_id":           item.get("id"),
            "title":             item.get("title") or item.get("name"),
            "original_title":    item.get("original_title") or item.get("original_name"),
            "release_date":      item.get("release_date") or item.get("first_air_date"),
            "overview":          item.get("overview"),
            "poster_url_card":   get_poster_url(poster_path, rl.TMDB["poster_card"]) if poster_path else None,
            "media_type":        item.get("media_type", search_type)
        })
    return results


def get_genre_list() -> dict[int, str]:
    """Get the TMDB genre ID → name mapping."""
    data = _api_get("/genre/movie/list")
    return {g["id"]: g["name"] for g in data.get("genres", [])}


def get_movie_similar(tmdb_id: int) -> list[dict]:
    """Get similar movies from TMDB.
    
    Returns list of dicts with:
        tmdb_id, title, release_date, poster_url_card, vote_average, overview
    """
    data = _api_get(f"/movie/{tmdb_id}/similar")
    results = []
    for item in data.get("results", []):
        poster_path = item.get("poster_path")
        results.append({
            "tmdb_id":           item.get("id"),
            "title":             item.get("title"),
            "release_date":      item.get("release_date"),
            "poster_url_card":   get_poster_url(poster_path, rl.TMDB["poster_card"]),
            "vote_average":      item.get("vote_average"),
            "overview":          item.get("overview"),
        })
    return results


def get_tv_similar(tmdb_id: int) -> list[dict]:
    """Get similar TV shows from TMDB.
    
    Returns list of dicts with:
        tmdb_id, title, first_air_date, poster_url_card, vote_average, overview
    """
    data = _api_get(f"/tv/{tmdb_id}/similar")
    results = []
    for item in data.get("results", []):
        poster_path = item.get("poster_path")
        results.append({
            "tmdb_id":           item.get("id"),
            "title":             item.get("name"),
            "first_air_date":    item.get("first_air_date"),
            "poster_url_card":   get_poster_url(poster_path, rl.TMDB["poster_card"]),
            "vote_average":      item.get("vote_average"),
            "overview":          item.get("overview"),
        })
    return results
