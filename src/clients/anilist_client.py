"""
CineStats — AniList GraphQL Client
Section 14.5 of the v1.0 specification.

Provides:
  - Anime search and metadata from AniList via GraphQL
  - AniList ID, scores, popularity
  - Rate Limits: 90 req/min
"""
import requests
from typing import Optional, Dict, Any, List

from src.rate_limiter import RateLimiter, FetchException
import rate_limits as rl

SOURCE_NAME = "anilist_client"
_limiter = RateLimiter()
_BASE = rl.ANILIST["base_url"]

_ANIME_QUERY = """
query ($search: String, $idMal: Int) {
  Media (search: $search, idMal: $idMal, type: ANIME) {
    id
    idMal
    title {
      romaji
      english
      native
    }
    averageScore
    popularity
    episodes
    status
    season
    seasonYear
  }
}
"""


def _graphql_request(variables: Dict[str, Any]) -> Dict[str, Any]:
    """Make a GraphQL request to AniList."""
    if not _limiter.wait(rl.ANILIST["domain"]):
        raise FetchException(SOURCE_NAME, "graphql", "Rate limit timeout")

    try:
        resp = requests.post(
            _BASE,
            json={"query": _ANIME_QUERY, "variables": variables},
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json().get("data", {}).get("Media")
        return data if data else {}
    except requests.RequestException as e:
        raise FetchException(SOURCE_NAME, "graphql", str(e))


def get_anime_by_mal_id(mal_id: int) -> Dict[str, Any]:
    """Fetch AniList data using a known MAL ID."""
    data = _graphql_request({"idMal": mal_id})
    return _parse_media_node(data)


def search_anime(title: str) -> Dict[str, Any]:
    """Search for an anime by title on AniList. Returns the top match."""
    data = _graphql_request({"search": title})
    return _parse_media_node(data)


def _parse_media_node(item: Dict[str, Any]) -> Dict[str, Any]:
    """Parse AniList GraphQL response into our standard dictionary structure."""
    if not item:
        return {}
        
    title_obj = item.get("title", {})
    title_display = title_obj.get("romaji") or title_obj.get("english")
        
    return {
        "anilist_id": item.get("id"),
        "mal_id": item.get("idMal"),
        "title_display": title_display,
        "title_english": title_obj.get("english"),
        "title_japanese": title_obj.get("native"),
        "anilist_score": item.get("averageScore"),
        "anilist_popularity": item.get("popularity"),
        "episodes": item.get("episodes"),
        "status": item.get("status"),
        "season": item.get("season"),
        "season_year": item.get("seasonYear")
    }
