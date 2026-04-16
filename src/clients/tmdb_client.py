"""
CineStats — TMDB API Client
Section 14.3 of the v1.0 specification.

Provides:
  - Movie search and metadata
  - Poster URLs (w185 for cards, w500 for detail)
  - Genre tags, cast, crew, origin country, runtime
  - Trending movies
"""
import requests
import streamlit as st
from typing import Optional

from src.rate_limiter import RateLimiter, FetchException
import rate_limits as rl

SOURCE_NAME = "tmdb_client"
_limiter = RateLimiter()
_BASE = rl.TMDB["base_url"]


def _get_api_key() -> str:
    """Get TMDB API key from Streamlit secrets."""
    try:
        return st.secrets["TMDB_API_KEY"]
    except Exception:
        # Fallback for non-Streamlit contexts (testing)
        import os
        return os.environ.get("TMDB_API_KEY", "")


def _api_get(endpoint: str, params: dict = None) -> dict:
    """Make an authenticated GET to the TMDB API."""
    if not _limiter.wait(rl.TMDB["domain"]):
        raise FetchException(SOURCE_NAME, endpoint, "Rate limit timeout")

    api_key = _get_api_key()
    if not api_key:
        raise FetchException(SOURCE_NAME, endpoint, "TMDB API key not configured")

    url = f"{_BASE}{endpoint}"
    all_params = {"api_key": api_key, **(params or {})}

    import time
    for attempt in range(3):
        try:
            resp = requests.get(url, params=all_params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.SSLError as e:
            if attempt == 2:
                raise FetchException(SOURCE_NAME, endpoint, str(e))
            time.sleep(1)
        except requests.RequestException as e:
            raise FetchException(SOURCE_NAME, endpoint, str(e))


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

    return {
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
    }


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


def get_genre_list() -> dict[int, str]:
    """Get the TMDB genre ID → name mapping."""
    data = _api_get("/genre/movie/list")
    return {g["id"]: g["name"] for g in data.get("genres", [])}
