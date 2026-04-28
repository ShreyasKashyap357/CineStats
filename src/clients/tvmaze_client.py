"""
CineStats — TVMaze API Client
Section 14.6 of the v1.0 specification.

Provides:
  - TV series search and metadata
  - Episode lists and air dates
  - Runtime, status, premier date, network
  - Rate Limits: 20 req/10sec
"""
from curl_cffi import requests
from typing import Optional, Dict, Any, List

from src.rate_limiter import RateLimiter, FetchException
import rate_limits as rl

SOURCE_NAME = "tvmaze_client"
_limiter = RateLimiter()
_BASE = rl.TVMAZE["base_url"]


def _api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Make a GET request to the TVMaze API."""
    if not _limiter.wait(rl.TVMAZE["domain"]):
        raise FetchException(SOURCE_NAME, endpoint, "Rate limit timeout")

    url = f"{_BASE}{endpoint}"
    try:
        session = requests.Session(impersonate="chrome120")
        resp = session.get(url, params=params, timeout=15)
        # TVMaze returns 404 for missing shows/episodes
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise FetchException(SOURCE_NAME, endpoint, str(e))


def search_tv_series(title: str) -> List[Dict[str, Any]]:
    """Search for TV series by title.
    
    Returns a list of matching shows.
    """
    data = _api_get("/search/shows", {"q": title})
    if not data:
        return []
        
    results = []
    for item in data:
        show = item.get("show", {})
        results.append(_parse_show_node(show))
    return results


def get_tv_series_detail(tvmaze_id: int) -> Optional[Dict[str, Any]]:
    """Get TV series details by TVMaze ID."""
    show = _api_get(f"/shows/{tvmaze_id}")
    if not show:
        return None
    return _parse_show_node(show)


def get_tv_episodes(tvmaze_id: int) -> List[Dict[str, Any]]:
    """Get all episodes for a specific TVMaze ID."""
    data = _api_get(f"/shows/{tvmaze_id}/episodes")
    if not data:
        return []
        
    episodes = []
    for ep in data:
        episodes.append({
            "tvmaze_id": tvmaze_id,
            "season": ep.get("season"),
            "episode": ep.get("number"),
            "title": ep.get("name"),
            "air_date": ep.get("airdate"),
            "rating": ep.get("rating", {}).get("average")
        })
    return episodes


def _parse_show_node(show: Dict[str, Any]) -> Dict[str, Any]:
    """Parse TVMaze show node into our standard dictionary."""
    network = show.get("network") or show.get("webChannel")
    network_name = network.get("name") if network else None
    origin_country = network.get("country", {}).get("code") if network and network.get("country") else None

    # TVMaze often tags animated shows; we'll map content_type later, but we can capture genres
    genres = show.get("genres", [])
    content_type = "tv_series"
    if "Anime" in genres:
        content_type = "anime"
    elif "Animation" in genres:
        # Default to western_animation, will be refined if kodomomuke/cartoon later
        content_type = "western_animation"

    return {
        "tvmaze_id": show.get("id"),
        "title_display": show.get("name"),
        "title_normalized": show.get("name", "").strip().lower(),
        "origin_country": origin_country,
        "network": network_name,
        "genre": ", ".join(genres) if genres else None,
        "status": show.get("status"),
        "premiere_date": show.get("premiered"),
        "avg_rating": show.get("rating", {}).get("average"),
        "content_type": content_type,
        "tmdb_id": show.get("externals", {}).get("thetvdb") or show.get("externals", {}).get("imdb"), # TVMaze doesn't consistently have TMDB ID, often has TVDB/IMDB
    }
