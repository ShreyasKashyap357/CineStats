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
from curl_cffi import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import Optional

from src.rate_limiter import RateLimiter, FetchException
import rate_limits as rl

SOURCE_NAME = "sacnilk_scraper"
_limiter = RateLimiter()
_session = None

def get_sacnilk_session() -> requests.Session:
    """Returns a centralized curl_cffi session mimicking Chrome to bypass Cloudflare natively."""
    global _session
    if _session is None:
        _session = requests.Session(impersonate="chrome120")
        # Pre-fetch the home page to solve the JS challenge and snag cf_clearance
        try:
            _session.get("https://sacnilk.com/", timeout=15)
        except Exception as e:
            print(f"[Sacnilk Auth] Initial Cloudflare handshake failed: {e}")
    return _session

def _get_soup(url: str, session: Optional[requests.Session] = None) -> BeautifulSoup:
    """Fetch a URL with rate limiting and return parsed soup, bypassing Cloudflare."""
    if not _limiter.wait(rl.SACNILK["domain"]):
        raise FetchException(SOURCE_NAME, url, "Rate limit timeout")

    req_obj = session if session else get_sacnilk_session()
    
    try:
        resp = req_obj.get(url, timeout=15)
        if hasattr(resp, 'raise_for_status'):
            resp.raise_for_status()
    except Exception as e:
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


def scrape_currently_running(progress_callback=None) -> list:
    """Scrape Sacnilk for currently running Indian films.

    Returns a list of dicts with preliminary data, including sacnilk_url.
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
                    # Use a pipe separator to catch inner spans (e.g. Pallichattambi|Mollywood | 2026)
                    raw_text = cells[0].get_text(separator='|', strip=True) 
                    parts = [p.strip() for p in raw_text.split('|') if p.strip()]
                    
                    # Usually: [Title, Industry, Year] or [Title]
                    title_display = parts[0] if parts else raw_text
                    industry = parts[1].replace("•", "").strip() if len(parts) > 1 else None
                    year = parts[2] if len(parts) > 2 else None
                    
                    href = title_tag.get("href", "") if title_tag else ""

                    # Extract basic collection
                    collection = None
                    for cell in cells[1:]:
                        val = _parse_crore(cell.get_text())
                        if val is not None and val > 0:
                            collection = val
                            break

                    rows.append({
                        "title_display":    title_display,
                        "title_normalized": _normalize_title(title_display),
                        "language":         industry,
                        "release_date":     f"{year}-01-01" if year and year.isdigit() else None, 
                        "india_net_cr":     collection,
                        "sacnilk_url":      f"{rl.SACNILK['base_url']}{href}" if href else None,
                        "source":           "sacnilk",
                    })
                except (IndexError, AttributeError):
                    continue

    return rows

def scrape_box_office_collection_list(progress_callback=None) -> list:
    """Uses curl_cffi to navigate the filter API and grab all Indian movies."""
    base_url = 'https://sacnilk.com/entertainmenttopbar/Box_Office_Collection'
    session = requests.Session(impersonate="chrome120")
    
    try:
        response = session.get(base_url, params={'hl': 'en'}, timeout=15)
    except Exception:
        return []
        
    soup = BeautifulSoup(response.text, 'lxml')
    token_input = soup.find('input', {'name': 'list_cache_token'})
    if not token_input:
        return []
        
    cache_token = token_input.get('value')
    offset = 0
    batch_size = 10
    has_more_data = True
    all_movies = []
    
    headers = {
        'accept': '*/*',
        'origin': 'https://sacnilk.com',
        'referer': 'https://sacnilk.com/entertainmenttopbar/Box_Office_Collection?hl=en',
    }

    # Fetch max 100 movies to prevent hanging forever
    while has_more_data and offset < 100:
        payload = {
            'action': (None, 'filter_movies'),
            'offset': (None, str(offset)),
            'load_more': (None, 'true'),
            'current_movie_count': (None, str(batch_size)),
            'list_cache_token': (None, cache_token),
            'date_range': (None, 'All Time'),
            'movie_name': (None, ''),
        }
        
        try:
            api_response = session.post(
                base_url,
                params={'hl': 'en'},
                headers=headers,
                files=payload,
                timeout=15
            )
        except Exception:
            break
            
        data = api_response.text 
        if not data or "no more records" in data.lower() or len(data.strip()) == 0:
            break
            
        # Parse the HTML snippets returned by API
        api_soup = BeautifulSoup(data, 'lxml')
        for tr in api_soup.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) < 4:
                continue
            try:
                title_tag = cells[0].find("a") or cells[1].find("a")
                raw_text = cells[0].get_text(separator='|', strip=True) 
                parts = [p.strip() for p in raw_text.split('|') if p.strip()]
                
                title_display = parts[0] if parts else raw_text
                
                # Better filtering for non-movie content
                non_movie_keywords = [
                    '50 ', 'total', 'overall', 'summary', 'all time', 'lifetime', 
                    'collection', 'gross', 'net', 'worldwide', 'india', 'overseas',
                    'year', 'weekend', 'opening', 'day', 'week', 'month',
                    'rank', 'position', 'top', 'bottom', 'list', 'chart',
                    'records', 'record', 'club', 'cr ', 'cr.', 'lakh', 'million',
                    'billion', 'box office', 'bo', 'collection', 'earnings'
                ]
                
                # Skip if title is empty or contains non-movie keywords
                if not title_display:
                    continue
                    
                title_lower = title_display.lower()
                if any(keyword in title_lower for keyword in non_movie_keywords):
                    continue
                
                # Skip if title is mostly numbers or symbols (likely a summary row)
                if sum(c.isdigit() for c in title_display) > len(title_display) / 2:
                    continue
                    
                industry = parts[1].replace("•", "").strip() if len(parts) > 1 else None
                year = parts[2] if len(parts) > 2 else None
                href = title_tag.get("href", "") if title_tag else ""
                
                # Only keep Indian films with valid industry
                if industry and ("wood" in industry.lower() or "india" in industry.lower()):
                    all_movies.append({
                        "title_display":    title_display,
                        "title_normalized": _normalize_title(title_display),
                        "language":         industry,
                        "release_date":     f"{year}-01-01" if year and year.isdigit() else None,
                        "sacnilk_url":      f"{rl.SACNILK['base_url']}{href}" if href else None,
                        "source":           "sacnilk"
                    })
            except Exception:
                pass
                
        offset += batch_size
        import time
        time.sleep(2)
        
    return all_movies

def search_sacnilk(query: str) -> Optional[str]:
    """Uses DuckDuckGo Lite to find the sacnilk URL for a specific movie query."""
    import urllib.parse
    try:
        session = requests.Session(impersonate="chrome120")
        resp = session.post(
            "https://lite.duckduckgo.com/lite/",
            data={"q": f"site:sacnilk.com {query}"},
            timeout=10
        )
        soup = BeautifulSoup(resp.text, "lxml")
        
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "sacnilk.com" in href and "Box_Office_Collection" not in href and "news" not in href:
                # DDG Lite wraps URLs in a redirect
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                real_url = parsed.get("uddg", [href])[0]
                if "sacnilk.com" in real_url:
                    return real_url
        return None
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")
        return None

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
            
    # Overseas (Nullable Trapping)
    result["overseas_gross_cr"] = None
    overseas_match = re.search(r'overseas\s*(?:gross)?\s*[:\-]?\s*₹?\s*([\d,.]+)\s*(?:Cr|cr)', page_text, re.I)
    if overseas_match:
         result["overseas_gross_cr"] = _parse_crore(overseas_match.group(1))
         
    # Total Shows (Nullable Trapping)
    result["total_shows"] = None
    shows_match = re.search(r'(?:across|in|with)\s*([\d,]+)\s*(?:shows|screenings)', page_text, re.I)
    if shows_match:
         try:
             result["total_shows"] = int(shows_match.group(1).replace(",", "").strip())
         except ValueError:
             pass

    return result


def scrape_daywise_collection(sacnilk_url: str) -> pd.DataFrame:
    """Scrape day-wise collection from Sacnilk chart data.

    Returns DataFrame with columns:
        day, daily_india_net_cr, cumulative_india_net_cr
    """
    import re
    html = str(_get_soup(sacnilk_url))
    rows = []

    labels_match = re.search(r'const labels\s*=\s*\[(.*?)\];', html)
    net_match = re.search(r'const netData\s*=\s*\[(.*?)\];', html)
    
    if labels_match and net_match:
        # Extract contents and strip quotes 
        labels_raw = labels_match.group(1).split(',')
        net_raw = net_match.group(1).split(',')
        
        cumulative = 0.0
        for lbl, net_val in zip(labels_raw, net_raw):
            day_str = lbl.replace('"', '').replace("'", "").strip()
            try:
                val = float(net_val.strip())
                cumulative += val
                rows.append({
                    "day": day_str,
                    "daily_india_net_cr": val,
                    "cumulative_india_net_cr": round(cumulative, 2)
                })
            except ValueError:
                continue

    return pd.DataFrame(rows)
