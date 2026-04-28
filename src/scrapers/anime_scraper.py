from curl_cffi import requests
from typing import Dict, Any, Optional

def fetch_jikan(query: str) -> Optional[Dict[str, Any]]:
    """Searches MyAnimeList via Jikan REST API."""
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=1"
    try:
        session = requests.Session(impersonate="chrome120")
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("data"):
                return data["data"][0]
    except Exception as e:
        print(f"Jikan fetch error: {e}")
    return None

def fetch_anilist(search_term: str = None, mal_id: int = None) -> Optional[Dict[str, Any]]:
    """Fetches anime data via AniList GraphQL."""
    query = '''
    query ($idMal: Int, $search: String) {
        Media (idMal: $idMal, search: $search, type: ANIME) {
            id
            idMal
            title {
                romaji
                english
                native
            }
            episodes
            status
            season
            seasonYear
            averageScore
            popularity
            coverImage {
                extraLarge
            }
            studios(isMain: true) {
                nodes {
                    name
                }
            }
            source
            genres
        }
    }
    '''
    variables = {}
    if mal_id:
        variables["idMal"] = mal_id
    elif search_term:
        variables["search"] = search_term
    else:
        return None
        
    url = "https://graphql.anilist.co"
    try:
        session = requests.Session(impersonate="chrome120")
        resp = session.post(url, json={"query": query, "variables": variables}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("Media")
    except Exception as e:
        print(f"AniList fetch error: {e}")
    return None

def pipeline_scrape_anime(query: str) -> Dict[str, Any]:
    """Master pipeline: Jikan -> AniList Handshake."""
    jikan_data = fetch_jikan(query)
    
    mal_id = None
    if jikan_data:
        mal_id = jikan_data.get("mal_id")
        
    anilist_data = fetch_anilist(search_term=query if not mal_id else None, mal_id=mal_id)
    
    if not jikan_data and not anilist_data:
        return {"status": "error", "message": "Anime not found on MAL or AniList."}
        
    # We will prioritize AniList metadata because it's cleaner, but fallback to Jikan for MAL specific stats
    
    # Safe extractors
    al = anilist_data or {}
    jk = jikan_data or {}
    
    title_romaji = al.get("title", {}).get("romaji") or jk.get("title")
    title_english = al.get("title", {}).get("english") or jk.get("title_english")
    title_japanese = al.get("title", {}).get("native") or jk.get("title_japanese")
    
    # Extract Studio
    studio = None
    if al.get("studios", {}).get("nodes"):
        studio = al["studios"]["nodes"][0].get("name")
    elif jk.get("studios"):
        studio = jk["studios"][0].get("name")
        
    # Extract Demographic (only in MAL)
    demographic = None
    if jk.get("demographics"):
        demographic = jk["demographics"][0].get("name")
        
    return {
        "status": "success",
        "data": {
            "title_normalized": (title_english or title_romaji or "Unknown").lower(),
            "title_japanese": title_japanese,
            "title_english": title_english or title_romaji,
            "mal_id": jk.get("mal_id") or al.get("idMal"),
            "anilist_id": al.get("id"),
            "mal_score": jk.get("score"),
            "mal_rank": jk.get("rank"),
            "mal_popularity": jk.get("popularity"),
            "mal_members": jk.get("members"),
            "mal_favourites": jk.get("favorites"),
            "anilist_score": al.get("averageScore"),
            "anilist_popularity": al.get("popularity"),
            "episodes": al.get("episodes") or jk.get("episodes"),
            "status": al.get("status") or jk.get("status"),
            "demographic": demographic,
            "genre": ", ".join(al.get("genres", [])) if al.get("genres") else ", ".join([g["name"] for g in jk.get("genres", [])]),
            "studio": studio,
            "source_material": al.get("source") or jk.get("source"),
            "season": al.get("season") or jk.get("season"),
            "season_year": al.get("seasonYear") or jk.get("year"),
            "poster_url": al.get("coverImage", {}).get("extraLarge") or jk.get("images", {}).get("jpg", {}).get("large_image_url")
        }
    }
