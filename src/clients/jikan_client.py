"""
CineStats — Jikan API (MAL) Client
Section 14.4 of the v1.0 specification.

Provides:
  - Anime search and metadata from MyAnimeList (MAL) via Jikan v4
  - MAL ID, scores, rank, popularity, members, demographic, genre, studio
  - Jikan Rate Limits: 3 req/sec, 60 req/min (Strictly enforced)
"""
import requests
import time
from typing import Optional, Dict, Any, List

from src.rate_limiter import RateLimiter, FetchException
import rate_limits as rl

SOURCE_NAME = "jikan_client"
_limiter = RateLimiter()
_BASE = rl.JIKAN["base_url"]


def _api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a GET request to the Jikan API with strict rate limiting."""
    if not _limiter.wait(rl.JIKAN["domain"]):
        raise FetchException(SOURCE_NAME, endpoint, "Rate limit timeout")

    url = f"{_BASE}{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=15)
        # Jikan might return 429 even with our limiter if global limits hit
        if resp.status_code == 429:
            time.sleep(2) # Backoff and retry once
            resp = requests.get(url, params=params, timeout=15)
            
        resp.raise_for_status()
        return resp.json().get("data", {})
    except requests.RequestException as e:
        raise FetchException(SOURCE_NAME, endpoint, str(e))


def search_anime(title: str) -> List[Dict[str, Any]]:
    """Search for anime by title.
    
    Returns a list of dictionaries with standard anime fields.
    """
    params = {"q": title, "limit": 10}
    # For search, data is a list
    data_list = []
    
    if not _limiter.wait(rl.JIKAN["domain"]):
        raise FetchException(SOURCE_NAME, "/anime", "Rate limit timeout")

    url = f"{_BASE}/anime"
    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 429:
            time.sleep(2)
            resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data_list = resp.json().get("data", [])
    except requests.RequestException as e:
        raise FetchException(SOURCE_NAME, "/anime", str(e))

    results = []
    for item in data_list:
        results.append(_parse_anime_node(item))
    return results


def get_anime_by_id(mal_id: int) -> Dict[str, Any]:
    """Get full details for a specific MAL ID."""
    data = _api_get(f"/anime/{mal_id}")
    return _parse_anime_node(data)


def get_anime_episodes(mal_id: int) -> List[Dict[str, Any]]:
    """Get episodes for an anime."""
    # Note: Jikan paginates episodes, for V1 we might just grab page 1 or iterate
    # Let's grab first page for now
    if not _limiter.wait(rl.JIKAN["domain"]):
        raise FetchException(SOURCE_NAME, f"/anime/{mal_id}/episodes", "Rate limit timeout")

    url = f"{_BASE}/anime/{mal_id}/episodes"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data_list = resp.json().get("data", [])
    except requests.RequestException as e:
        raise FetchException(SOURCE_NAME, f"/anime/{mal_id}/episodes", str(e))

    episodes = []
    for ep in data_list:
        episodes.append({
            "mal_id": mal_id,
            "episode_number": ep.get("mal_id"), # In episodes, mal_id is the episode number in the scope
            "title": ep.get("title"),
            "title_japanese": ep.get("title_japanese"),
            "air_date": ep.get("aired"), # Needs formatting later
            "mal_score": ep.get("score")
        })
    return episodes


def _parse_anime_node(item: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a Jikan anime data node into our standard dictionary."""
    if not item:
        return {}
        
    titles = item.get("titles", [])
    title_english = next((t["title"] for t in titles if t["type"] == "English"), None)
    title_japanese = next((t["title"] for t in titles if t["type"] == "Japanese"), None)
    
    genres = [g["name"] for g in item.get("genres", [])]
    explicit_genres = [g["name"] for g in item.get("explicit_genres", [])]
    themes = [t["name"] for t in item.get("themes", [])]
    all_genres = genres + explicit_genres + themes
    
    demographics = [d["name"] for d in item.get("demographics", [])]
    studios = [s["name"] for s in item.get("studios", [])]
    
    poster_url = item.get("images", {}).get("jpg", {}).get("large_image_url")
    if not poster_url:
        poster_url = item.get("images", {}).get("jpg", {}).get("image_url")

    return {
        "mal_id": item.get("mal_id"),
        "title_display": item.get("title"),
        "title_english": title_english,
        "title_japanese": title_japanese,
        "title_normalized": item.get("title", "").strip().lower(), # Basic normalization
        "mal_score": item.get("score"),
        "mal_rank": item.get("rank"),
        "mal_popularity": item.get("popularity"),
        "mal_members": item.get("members"),
        "mal_favourites": item.get("favorites"),
        "episodes": item.get("episodes"),
        "status": item.get("status"),
        "demographic": demographics[0] if demographics else None,
        "genre": ", ".join(all_genres) if all_genres else None,
        "studio": ", ".join(studios) if studios else None,
        "source_material": item.get("source"),
        "season": item.get("season"),
        "season_year": item.get("year"),
        "poster_url": poster_url,
    }
