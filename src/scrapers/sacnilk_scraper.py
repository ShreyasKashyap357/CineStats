"""
CineStats — Sacnilk Scraper
Section 14.2 of the v1.0 specification.

Scrapes:
  - Currently running Indian films
  - Day-wise collection data
  - India net, India gross, verdict
  - Opening day / opening weekend data

All monetary values are returned in INR Crores.
"""
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import Optional

from src.rate_limiter import RateLimiter, FetchException
import rate_limits as rl

SOURCE_NAME = "sacnilk_scraper"
_limiter = RateLimiter()


def _get_soup(url: str) -> BeautifulSoup:
    """Fetch a URL with rate limiting and return parsed soup."""
    if not _limiter.wait(rl.SACNILK["domain"]):
        raise FetchException(SOURCE_NAME, url, "Rate limit timeout")

    headers = {"User-Agent": rl.SACNILK["user_agent"]}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise FetchException(SOURCE_NAME, url, str(e))

    return BeautifulSoup(resp.text, "lxml")


def _parse_crore(text: str) -> Optional[float]:
    """Parse Indian monetary strings like '₹21.50 Cr' or '21.5' to float (crores)."""
    if not text or text.strip() in ("-", "–", "N/A", ""):
        return None
    text = text.strip().replace("₹", "").replace(",", "").replace("Cr", "").replace("cr", "")
    text = text.strip()

    # Handle Lakh (0.01 Cr)
    if "L" in text.upper() or "Lakh" in text:
        text = text.upper().replace("L", "").replace("LAKH", "").strip()
        try:
            return float(text) / 100.0  # convert lakhs to crores
        except ValueError:
            return None

    try:
        return float(text)
    except ValueError:
        return None


def _normalize_title(title: str) -> str:
    """Normalize a movie title for matching."""
    title = title.strip().lower()
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()


def scrape_currently_running() -> pd.DataFrame:
    """Scrape Sacnilk for currently running Indian films.

    Returns DataFrame with columns:
        title_display, title_normalized, language, india_net_cr,
        india_gross_cr, verdict, release_date, days_in_release
    """
    urls = [
        f"{rl.SACNILK['base_url']}/news/Top_Grossing_Indian_Movies_Of_All_Time",
        f"{rl.SACNILK['base_url']}/news/Box_Office_Collection_2024",
        f"{rl.SACNILK['base_url']}/news/Box_Office_Collection_2025",
        f"{rl.SACNILK['base_url']}/news/South_Indian_Movies_Box_Office_Collection_2024"
    ]
    
    rows = []
    
    for url in urls:
        try:
            soup = _get_soup(url)
        except FetchException:
            continue
            
        tables = soup.find_all("table")
        for table in tables:
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) < 4:
                    continue
                try:
                    title_tag = cells[0].find("a") or cells[1].find("a")
                    title_display = title_tag.get_text(strip=True) if title_tag else cells[0].get_text(strip=True)
                    href = title_tag.get("href", "") if title_tag else ""

                    # Try to extract collection data from cells
                    collection = None
                    for cell in cells[1:]:
                        val = _parse_crore(cell.get_text())
                        if val is not None and val > 0:
                            collection = val
                            break

                    rows.append({
                        "title_display":    title_display,
                        "title_normalized": _normalize_title(title_display),
                        "india_net_cr":     collection,
                        "sacnilk_url":      f"{rl.SACNILK['base_url']}{href}" if href else None,
                        "source":           "sacnilk",
                    })
                except (IndexError, AttributeError):
                    continue

    return pd.DataFrame(rows) if rows else pd.DataFrame()


def scrape_movie_detail(sacnilk_url: str) -> dict:
    """Scrape a specific movie page on Sacnilk for full India data.

    Returns dict with:
        title_display, title_normalized, language, release_date,
        india_net_cr, india_gross_cr, verdict, days_in_release
    """
    soup = _get_soup(sacnilk_url)
    result = {"source": "sacnilk", "sacnilk_url": sacnilk_url}

    # Title
    title_el = soup.find("h1") or soup.find("h2")
    if title_el:
        result["title_display"] = title_el.get_text(strip=True)
        result["title_normalized"] = _normalize_title(result["title_display"])

    # Scan page text for key data
    page_text = soup.get_text()

    # Verdict
    for verdict in ["All-Time Blockbuster", "Blockbuster", "Super Hit", "Hit",
                     "Above Average", "Average", "Below Average", "Flop", "Disaster"]:
        if verdict.lower() in page_text.lower():
            result["verdict"] = verdict
            break

    # Net collection
    net_match = re.search(r'(?:net|nett)\s*[:\-]?\s*₹?\s*([\d,.]+)\s*(?:Cr|cr)', page_text, re.I)
    if net_match:
        result["india_net_cr"] = _parse_crore(net_match.group(1))

    # Gross collection
    gross_match = re.search(r'gross\s*[:\-]?\s*₹?\s*([\d,.]+)\s*(?:Cr|cr)', page_text, re.I)
    if gross_match:
        result["india_gross_cr"] = _parse_crore(gross_match.group(1))

    # Language
    lang_match = re.search(r'language\s*[:\-]?\s*(\w+)', page_text, re.I)
    if lang_match:
        result["language"] = lang_match.group(1).strip()

    # Release date
    date_match = re.search(r'release\s*date\s*[:\-]?\s*(\d{1,2}\s+\w+\s+\d{4})', page_text, re.I)
    if date_match:
        try:
            result["release_date"] = datetime.strptime(
                date_match.group(1).strip(), "%d %B %Y"
            ).date().isoformat()
        except ValueError:
            pass

    return result


def scrape_daywise_collection(sacnilk_url: str) -> pd.DataFrame:
    """Scrape day-wise collection table for a movie.

    Returns DataFrame with columns:
        day, date, daily_india_net_cr, cumulative_india_net_cr
    """
    soup = _get_soup(sacnilk_url)
    rows = []

    # Look for day-wise table
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if any("day" in h for h in headers) and any("collection" in h or "net" in h for h in headers):
            for tr in table.find_all("tr")[1:]:
                cells = tr.find_all("td")
                if len(cells) < 3:
                    continue
                try:
                    rows.append({
                        "day":                      cells[0].get_text(strip=True),
                        "daily_india_net_cr":        _parse_crore(cells[1].get_text()),
                        "cumulative_india_net_cr":   _parse_crore(cells[2].get_text()),
                    })
                except (IndexError, AttributeError):
                    continue
            if rows:
                break

    return pd.DataFrame(rows) if rows else pd.DataFrame()
