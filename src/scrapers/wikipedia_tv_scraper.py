"""
CineStats — Wikipedia TV Scraper
Section 14.7 of the v1.0 specification.

Scrapes:
  - Episode tables from Wikipedia TV series articles.
  - Specifically looks for 'U.S. viewers (millions)' or similar columns.
  - Matches data back to episodes based on season/episode number.
"""
import re
from curl_cffi import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any

from src.rate_limiter import RateLimiter, FetchException
import rate_limits as rl

SOURCE_NAME = "wikipedia_tv_scraper"
_limiter = RateLimiter()


def _get_soup(url: str) -> BeautifulSoup:
    """Fetch a URL with rate limiting and return parsed soup."""
    if not _limiter.wait(rl.WIKIPEDIA["domain"]):
        raise FetchException(SOURCE_NAME, url, "Rate limit timeout")

    try:
        session = requests.Session(impersonate="chrome120")
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        raise FetchException(SOURCE_NAME, url, str(e))

    return BeautifulSoup(resp.text, "lxml")


def scrape_viewership_data(wiki_url: str) -> List[Dict[str, Any]]:
    """Scrape viewership data from a Wikipedia TV show episode list.
    
    Returns a list of dictionaries with episode numbers and viewership data.
    """
    soup = _get_soup(wiki_url)
    episodes_data = []

    # Wikipedia episode tables usually have the class 'wikitable' and 'plainrowheaders'
    tables = soup.find_all("table", class_="wikitable")
    
    current_season = 1
    
    for table in tables:
        # Check if this table has viewership data
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        
        viewers_col_idx = -1
        ep_col_idx = -1
        
        for i, header in enumerate(headers):
            if "viewer" in header and "million" in header:
                viewers_col_idx = i
            if "no." in header and "season" in header:
                ep_col_idx = i
                
        # If no explicit season specific number, look for general episode number
        if ep_col_idx == -1:
            for i, header in enumerate(headers):
                if header == "no.":
                    ep_col_idx = i
                    break

        if viewers_col_idx != -1 and ep_col_idx != -1:
            # We found an episode table with viewership
            rows = table.find_all("tr", class_="vevent")
            for row in rows:
                cells = row.find_all(["th", "td"])
                if len(cells) > max(ep_col_idx, viewers_col_idx):
                    try:
                        ep_text = cells[ep_col_idx].get_text(strip=True)
                        viewers_text = cells[viewers_col_idx].get_text(strip=True)
                        
                        # Clean viewers text (remove references like [12])
                        viewers_text = re.sub(r'\[\d+\]', '', viewers_text)
                        viewers = float(viewers_text) if viewers_text and viewers_text != "TBD" else None
                        
                        if viewers is not None:
                            episodes_data.append({
                                "season": current_season,
                                "episode": int(ep_text),
                                "us_viewers_millions": viewers
                            })
                    except (ValueError, IndexError):
                        continue
            current_season += 1
            
    return episodes_data
