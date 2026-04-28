from curl_cffi import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, Dict, Any, List

def search_tvmaze(query: str) -> Optional[Dict[str, Any]]:
    """Searches TVMaze for a show and returns metadata + episodes + cast/crew."""
    url = f"https://api.tvmaze.com/singlesearch/shows?q={query}&embed[]=episodes&embed[]=cast&embed[]=crew"
    try:
        session = requests.Session(impersonate="chrome120")
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Error fetching from TVMaze: {e}")
    return None

def scrape_wikipedia_viewers(show_name: str) -> Dict[str, float]:
    """
    Constructs a Wikipedia URL and scrapes the 'U.S. viewers (millions)' column.
    Returns a mapping of "{season}_{episode}": float_viewers.
    """
    formatted_name = show_name.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/List_of_{formatted_name}_episodes"
    
    viewership_map = {}
    headers = {
        "User-Agent": "CineStats/2.0 (student project; https://github.com/shrey/cinestats) python-requests/2.31.0"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            # Fallback for generic name
            url_fallback = f"https://en.wikipedia.org/wiki/List_of_{formatted_name}_(TV_series)_episodes"
            resp = requests.get(url_fallback, headers=headers, timeout=10)
            if resp.status_code != 200:
                return viewership_map
            
        tables = pd.read_html(resp.text)
        
        # Look for tables that might be episode lists (usually have 'No. overall', 'No. in season')
        for df in tables:
            # Flatten multi-index columns if they exist
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(-1)
                
            cols = [str(c).lower() for c in df.columns]
            
            # Identify columns
            season_col = None
            ep_col = None
            viewer_col = None
            
            for i, col in enumerate(cols):
                if 'in season' in col:
                    ep_col = df.columns[i]
                elif 'overall' in col:
                    pass
                elif 'viewers' in col and 'millions' in col:
                    viewer_col = df.columns[i]
                    
            # If we found viewers, but no explicit 'season' column, it's usually implied by the table itself 
            # (which we would need to track, but for now we assume a simple 'season' column or we skip)
            # A more robust parser would look at the Wikipedia section headers to determine season, 
            # but for MVP we will try to match based on the TVMaze episode title or simple episode index.
            
            # Simple heuristic: if we have 'No. in season' and 'Viewers', let's just extract them
            if ep_col and viewer_col:
                for _, row in df.iterrows():
                    try:
                        ep = int(str(row[ep_col]).split('[')[0])
                        val_str = str(row[viewer_col]).split('[')[0]
                        val = float(val_str)
                        # We don't know the season easily without parsing headers. 
                        # As a fallback, we return episode index.
                        # For a perfect match, we need TVMaze title matching or exact S/E tracking.
                        # Let's return just by episode title if available
                        title_col = next((c for c in df.columns if 'Title' in str(c)), None)
                        if title_col:
                            title = str(row[title_col]).strip('"').strip()
                            viewership_map[title.lower()] = val
                    except Exception:
                        continue
                        
    except Exception as e:
        print(f"Error scraping Wikipedia for {show_name}: {e}")
        
    return viewership_map

def pipeline_scrape_tv(query: str) -> Dict[str, Any]:
    """The master pipeline: TVMaze -> Wikipedia Handshake."""
    tvmaze_data = search_tvmaze(query)
    if not tvmaze_data:
        return {"status": "error", "message": "Not found on TVMaze"}
        
    show_name = tvmaze_data.get("name")
    episodes = tvmaze_data.get("_embedded", {}).get("episodes", [])
    
    # Wiki Pass
    wiki_viewers = scrape_wikipedia_viewers(show_name)
    
    # Merge
    merged_episodes = []
    for ep in episodes:
        title_lower = ep.get("name", "").lower()
        viewers = wiki_viewers.get(title_lower)
        merged_episodes.append({
            "season": ep.get("season"),
            "episode": ep.get("number"),
            "title": ep.get("name"),
            "air_date": ep.get("airdate"),
            "rating": ep.get("rating", {}).get("average"),
            "viewership_millions": viewers
        })
        
    # Extract Cast and Crew
    embedded = tvmaze_data.get("_embedded", {})
    import json
    
    cast_list = []
    for c in embedded.get("cast", [])[:15]:
        cast_list.append({
            "name": c.get("person", {}).get("name"),
            "character": c.get("character", {}).get("name"),
            "profile_path": c.get("person", {}).get("image", {}).get("medium") if c.get("person", {}).get("image") else None
        })
        
    directors = []
    producers = []
    for c in embedded.get("crew", []):
        t = c.get("type", "")
        if "Director" in t or "Creator" in t:
            directors.append(c.get("person", {}).get("name"))
        elif "Producer" in t:
            producers.append(c.get("person", {}).get("name"))
            
    # Deduplicate
    directors = list(set(directors))
    producers = list(set(producers))
        
    return {
        "status": "success",
        "series": {
            "name": show_name,
            "network": tvmaze_data.get("network", {}).get("name") if tvmaze_data.get("network") else tvmaze_data.get("webChannel", {}).get("name"),
            "genre": ", ".join(tvmaze_data.get("genres", [])),
            "status": tvmaze_data.get("status"),
            "premiere_date": tvmaze_data.get("premiered"),
            "tvmaze_id": tvmaze_data.get("id"),
            "avg_rating": tvmaze_data.get("rating", {}).get("average"),
            "cast_json": json.dumps(cast_list),
            "director": ", ".join(directors),
            "producer": ", ".join(producers),
            "studio": None, # TVMaze doesn't consistently provide studio outside of network
            "overview": BeautifulSoup(tvmaze_data.get("summary", ""), "lxml").get_text() if tvmaze_data.get("summary") else None
        },
        "episodes": merged_episodes
    }
