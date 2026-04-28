"""
CineStats — Box Office Mojo Scraper
Section 14.1 of the v1.0 specification.

Scrapes:
  - Currently in theatres (daily chart)
  - Weekly box office chart
  - Individual movie pages (worldwide, domestic, foreign breakdown)
  - Opening weekend data

All monetary values are returned in USD.
"""
import re
import time
from curl_cffi import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import Optional

from src.rate_limiter import RateLimiter, FetchException
import rate_limits as rl

SOURCE_NAME = "bom_scraper"
_limiter = RateLimiter()


def _get_soup(url: str) -> BeautifulSoup:
    """Fetch a URL with rate limiting and return parsed soup."""
    if not _limiter.wait(rl.BOM["domain"]):
        raise FetchException(SOURCE_NAME, url, "Rate limit timeout")

    try:
        session = requests.Session(impersonate="chrome120")
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        raise FetchException(SOURCE_NAME, url, str(e))

    return BeautifulSoup(resp.text, "lxml")


def _parse_money(text: str) -> Optional[float]:
    """Parse monetary strings like '$599,234,567' or '$1.2B' to float."""
    if not text or text.strip() in ("-", "–", "N/A", ""):
        return None
    text = text.strip().replace(",", "").replace("$", "").replace("£", "").replace("€", "")

    # Handle B/M suffixes
    text_upper = text.upper().strip()
    if text_upper.endswith("B"):
        try:
            return float(text_upper[:-1]) * 1_000_000_000
        except ValueError:
            return None
    if text_upper.endswith("M"):
        try:
            return float(text_upper[:-1]) * 1_000_000
        except ValueError:
            return None
    if text_upper.endswith("K"):
        try:
            return float(text_upper[:-1]) * 1_000
        except ValueError:
            return None

    try:
        return float(text)
    except ValueError:
        return None


def _normalize_title(title: str) -> str:
    """Normalize a movie title for matching."""
    title = title.strip().lower()
    title = re.sub(r'[^\w\s]', '', title)  # remove punctuation
    title = re.sub(r'\s+', ' ', title)     # collapse whitespace
    return title.strip()


def scrape_daily_chart() -> pd.DataFrame:
    """Scrape the BOM daily chart for currently-in-theatres movies.

    Returns DataFrame with columns:
        title_display, title_normalized, rank, daily_gross_usd,
        cumulative_gross_usd, days_in_release, theater_count
    """
    url = f"{rl.BOM['base_url']}/daily/chart/"
    soup = _get_soup(url)

    rows = []
    table = soup.find("table")
    if not table:
        return pd.DataFrame()

    for tr in table.find_all("tr")[1:]:  # skip header
        cells = tr.find_all("td")
        if len(cells) < 9:
            continue
        try:
            # BOM daily chart layout varies, but typically:
            # rank, title, daily_gross, %change, theaters, avg, cumulative, day
            title_tag = cells[1].find("a")
            title_display = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
            href = title_tag.get("href", "") if title_tag else ""

            rows.append({
                "title_display":       title_display,
                "title_normalized":    _normalize_title(title_display),
                "rank":                _parse_money(cells[0].get_text()),
                "daily_gross_usd":     _parse_money(cells[2].get_text()),
                "theater_count":       _parse_money(cells[4].get_text()),
                "cumulative_gross_usd": _parse_money(cells[6].get_text()),
                "days_in_release":     _parse_money(cells[7].get_text()),
                "bom_url":             f"{rl.BOM['base_url']}{href}" if href else None,
                "source":              "bom",
            })
        except (IndexError, AttributeError):
            continue

    return pd.DataFrame(rows) if rows else pd.DataFrame()


def scrape_weekly_chart() -> pd.DataFrame:
    """Scrape the BOM weekly box office chart.

    Returns DataFrame with columns:
        title_display, title_normalized, weekly_gross_usd,
        total_gross_usd, weeks_in_release, theater_count
    """
    url = f"{rl.BOM['base_url']}/weekly/chart/"
    soup = _get_soup(url)

    rows = []
    table = soup.find("table")
    if not table:
        return pd.DataFrame()

    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all("td")
        if len(cells) < 8:
            continue
        try:
            title_tag = cells[1].find("a")
            title_display = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
            href = title_tag.get("href", "") if title_tag else ""

            rows.append({
                "title_display":       title_display,
                "title_normalized":    _normalize_title(title_display),
                "weekly_gross_usd":    _parse_money(cells[2].get_text()),
                "total_gross_usd":     _parse_money(cells[5].get_text()),
                "weeks_in_release":    _parse_money(cells[6].get_text()),
                "theater_count":       _parse_money(cells[3].get_text()),
                "bom_url":             f"{rl.BOM['base_url']}{href}" if href else None,
                "source":              "bom",
            })
        except (IndexError, AttributeError):
            continue

    return pd.DataFrame(rows) if rows else pd.DataFrame()


def scrape_yearly_chart(year: int = None) -> pd.DataFrame:
    """Scrape the BOM yearly domestic chart.

    Returns DataFrame with columns:
        title_display, title_normalized, worldwide_gross_usd,
        domestic_gross_usd, release_date
    """
    if year is None:
        year = date.today().year

    url = f"{rl.BOM['base_url']}/year/world/{year}/"
    soup = _get_soup(url)

    rows = []
    table = soup.find("table")
    if not table:
        return pd.DataFrame()

    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all("td")
        if len(cells) < 5:
            continue
        try:
            title_tag = cells[1].find("a")
            title_display = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
            href = title_tag.get("href", "") if title_tag else ""

            rows.append({
                "title_display":       title_display,
                "title_normalized":    _normalize_title(title_display),
                "worldwide_gross_usd": _parse_money(cells[2].get_text()),
                "domestic_gross_usd":  _parse_money(cells[3].get_text()),
                "foreign_gross_usd":   _parse_money(cells[4].get_text()),
                "release_date":        _extract_date(cells),
                "bom_url":             f"{rl.BOM['base_url']}{href}" if href else None,
                "source":              "bom",
            })
        except (IndexError, AttributeError):
            continue

    return pd.DataFrame(rows) if rows else pd.DataFrame()


def scrape_movie_detail(bom_url: str) -> dict:
    """Scrape a specific movie page on BOM for full breakdown.

    Returns dict with:
        title_display, title_normalized, release_date, worldwide_gross_usd,
        domestic_gross_usd, foreign_gross_usd, opening_weekend_usd,
        theater_count, days_in_release
    """
    soup = _get_soup(bom_url)

    result = {"source": "bom", "bom_url": bom_url}

    # Title
    title_el = soup.find("h1")
    if title_el:
        result["title_display"] = title_el.get_text(strip=True)
        result["title_normalized"] = _normalize_title(result["title_display"])

    # Summary section — look for money spans
    money_divs = soup.find_all("div", class_=re.compile(r"mojo-performance"))
    for div in money_divs:
        label_el = div.find("span", class_="a-size-small")
        value_el = div.find("span", class_="money")
        if not label_el or not value_el:
            continue
        label = label_el.get_text(strip=True).lower()
        value = _parse_money(value_el.get_text())

        if "domestic" in label:
            result["domestic_gross_usd"] = value
        elif "international" in label or "foreign" in label:
            result["foreign_gross_usd"] = value
        elif "worldwide" in label:
            result["worldwide_gross_usd"] = value

    # Opening weekend / theater count from summary table
    summary_table = soup.find("div", id="a-page")
    if summary_table:
        for row in summary_table.find_all("div", class_="a-section"):
            text = row.get_text(strip=True).lower()
            if "opening" in text:
                money_el = row.find("span", class_="money")
                if money_el:
                    result["opening_weekend_usd"] = _parse_money(money_el.get_text())
            elif "theate" in text or "widest" in text:
                nums = re.findall(r'[\d,]+', row.get_text())
                if nums:
                    result["theater_count"] = int(nums[0].replace(",", ""))

    # Release date
    for span in soup.find_all("span"):
        text = span.get_text(strip=True)
        date_match = re.search(r'(\w+ \d{1,2}, \d{4})', text)
        if date_match:
            try:
                result["release_date"] = datetime.strptime(
                    date_match.group(1), "%B %d, %Y"
                ).date().isoformat()
                break
            except ValueError:
                continue

    # Extract Regional Rollout Data
    rollouts = []
    
    # Try fetching the All-Territories nested page for explicit regional rollouts
    all_territories_url = None
    if "/release/rl" in bom_url:
        base_release = bom_url.split("?")[0].rstrip("/")
        all_territories_url = f"{base_release}/All-Territories/"
    
    rollout_soup = soup
    if all_territories_url:
        try:
            rollout_soup = _get_soup(all_territories_url)
        except Exception:
            pass # fallback to original soup
            
    for table in rollout_soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if "market" in headers and "gross" in headers:
            # Find the region name (usually previous heading or div)
            region_name = "Unknown"
            prev_el = table.find_previous_sibling()
            while prev_el:
                text = prev_el.get_text(strip=True)
                if text and len(text) < 50:
                    region_name = text
                    break
                prev_el = prev_el.find_previous_sibling()
                
            for tr in table.find_all("tr")[1:]: # skip header
                cells = tr.find_all("td")
                if len(cells) >= 4:
                    market = cells[0].get_text(strip=True)
                    release = cells[1].get_text(strip=True)
                    opening = _parse_money(cells[2].get_text())
                    gross = _parse_money(cells[3].get_text())
                    
                    if market and market != "–" and market.lower() != "domestic":
                        href_tag = cells[0].find('a')
                        source_url = "https://www.boxofficemojo.com" + href_tag['href'] if href_tag and href_tag.has_attr('href') else None
                        
                        rollouts.append({
                            "country_name": market,
                            "region": region_name,
                            "opening_usd": opening,
                            "gross_usd": gross,
                            "release_date": release,
                            "source_url": source_url
                        })
                        
    result["rollouts"] = rollouts
    return result

def search_bom(query: str) -> Optional[str]:
    """Uses DuckDuckGo Lite to find the BOM URL for a specific movie query."""
    import urllib.parse
    from bs4 import BeautifulSoup
    
    try:
        session = requests.Session(impersonate="chrome120")
        resp = session.post(
            "https://lite.duckduckgo.com/lite/",
            data={"q": f"site:boxofficemojo.com/title {query}"},
            timeout=10
        )
        soup = BeautifulSoup(resp.text, "lxml")
        
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "boxofficemojo.com/title" in href:
                # DDG Lite wraps URLs in a redirect
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                real_url = parsed.get("uddg", [href])[0]
                if "boxofficemojo.com/title" in real_url:
                    return real_url
        return None
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")
        return None

def scrape_country_daily_performance(country_url: str) -> list:
    """On-demand scraper for a specific country's rollout breakdown."""
    try:
        soup = _get_soup(country_url)
        data = []
        
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if "date" in headers and "gross" in headers:
                for tr in table.find_all("tr")[1:]:
                    cells = tr.find_all("td")
                    if len(cells) >= 3:
                        date_str = cells[0].get_text(strip=True)
                        gross_idx = headers.index("gross")
                        gross_str = cells[gross_idx].get_text(strip=True)
                        
                        data.append({
                            "date": date_str,
                            "gross": gross_str
                        })
                break
        return data
    except Exception as e:
        print(f"Error scraping country rollout: {e}")
        return []

def scrape_franchise_list(category: str) -> list:
    """Scrapes the master list of BOM Brands, Franchises, or Genres."""
    url = f"{rl.BOM['base_url']}/{category}/"
    try:
        soup = _get_soup(url)
        data = []
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:
                cells = tr.find_all("td")
                if len(cells) >= 4:
                    name_tag = cells[0].find("a")
                    if name_tag:
                        data.append({
                            "name": name_tag.get_text(strip=True),
                            "url": f"{rl.BOM['base_url']}{name_tag.get('href', '')}",
                            "total_gross": cells[1].get_text(strip=True),
                            "releases": cells[2].get_text(strip=True),
                            "top_release": cells[3].get_text(strip=True),
                            "type": category
                        })
            break
        return data
    except Exception as e:
        print(f"Error scraping franchise list {category}: {e}")
        return []

def scrape_franchise_detail(url: str) -> list:
    """Scrapes all movies within a specific franchise/brand."""
    try:
        soup = _get_soup(url)
        movies = []
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:
                cells = tr.find_all("td")
                if len(cells) >= 2:
                    title_tag = cells[1].find("a")
                    if title_tag:
                        movies.append({
                            "title": title_tag.get_text(strip=True),
                            "url": f"{rl.BOM['base_url']}{title_tag.get('href', '')}",
                            "gross": cells[2].get_text(strip=True) if len(cells) > 2 else None,
                            "release_date": cells[5].get_text(strip=True) if len(cells) > 5 else None
                        })
            break
        return movies
    except Exception as e:
        print(f"Error scraping franchise detail: {e}")
        return []


def _extract_date(cells: list) -> Optional[str]:
    """Try to extract a date from table cells."""
    for cell in cells:
        text = cell.get_text(strip=True)
        date_match = re.search(r'(\w+ \d{1,2}, \d{4})', text)
        if date_match:
            try:
                return datetime.strptime(
                    date_match.group(1), "%B %d, %Y"
                ).date().isoformat()
            except ValueError:
                continue
    return None


def scrape_bom_chart_links() -> dict:
    """Extracts all chart sub-links from BOM main chart pages.
    
    Returns dict with categories as keys and list of (name, url) tuples as values.
    Categories: domestic, worldwide, weekend, daily, misc, record
    """
    base_urls = {
        "domestic": f"{rl.BOM['base_url']}/chart/top_lifetime_gross/",
        "worldwide": f"{rl.BOM['base_url']}/chart/ww_top_lifetime_gross/?area=XWW",
        "weekend": f"{rl.BOM['base_url']}/charts/weekend/",
        "daily": f"{rl.BOM['base_url']}/charts/daily/",
        "misc": f"{rl.BOM['base_url']}/charts/misc/",
        "record": f"{rl.BOM['base_url']}/chart/record/"
    }
    
    all_links = {}
    
    for category, url in base_urls.items():
        try:
            soup = _get_soup(url)
            links = []
            
            # Find all tables with chart links
            for table in soup.find_all("table"):
                for tr in table.find_all("tr"):
                    cells = tr.find_all("td")
                    if len(cells) >= 1:
                        # Check all cells for links
                        for cell in cells:
                            link_tag = cell.find("a")
                            if link_tag:
                                name = link_tag.get_text(strip=True)
                                href = link_tag.get("href", "")
                                # Skip empty or invalid links
                                if href and name and not href.startswith("#") and "javascript" not in href.lower():
                                    full_url = f"{rl.BOM['base_url']}{href}" if not href.startswith("http") else href
                                    # Avoid duplicates
                                    if not any(l[1] == full_url for l in links):
                                        links.append((name, full_url))
            
            all_links[category] = links
        except Exception as e:
            print(f"Error extracting links for {category}: {e}")
            all_links[category] = []
    
    return all_links


def scrape_bom_calendar(date_str: str = None) -> list:
    """Scrapes BOM release calendar.
    
    Args:
        date_str: Optional date string in YYYY-MM-DD format. If None, uses current date.
    
    Returns list of movies with release schedule info.
    """
    if date_str:
        url = f"{rl.BOM['base_url']}/calendar/{date_str}/"
    else:
        url = f"{rl.BOM['base_url']}/calendar/"
    
    try:
        soup = _get_soup(url)
        movies = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    try:
                        release_date = cells[0].get_text(strip=True)
                        title_tag = cells[1].find("a")
                        title = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
                        distributor = cells[2].get_text(strip=True) if len(cells) > 2 else None
                        scale = cells[3].get_text(strip=True) if len(cells) > 3 else None
                        
                        href = title_tag.get("href", "") if title_tag else ""
                        
                        movies.append({
                            "title_display": title,
                            "title_normalized": _normalize_title(title),
                            "release_date": release_date,
                            "distributor": distributor,
                            "scale": scale,
                            "bom_url": f"{rl.BOM['base_url']}{href}" if href else None,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return movies
    except Exception as e:
        print(f"Error scraping BOM calendar: {e}")
        return []


def scrape_bom_calendar_changes() -> list:
    """Scrapes BOM release schedule changes."""
    url = f"{rl.BOM['base_url']}/calendar/changes/"
    
    try:
        soup = _get_soup(url)
        changes = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 5:
                    try:
                        release_date = cells[0].get_text(strip=True)
                        title = cells[1].get_text(strip=True)
                        distributor = cells[2].get_text(strip=True)
                        scale = cells[3].get_text(strip=True)
                        date_change = cells[4].get_text(strip=True)
                        
                        changes.append({
                            "title": title,
                            "release_date": release_date,
                            "distributor": distributor,
                            "scale": scale,
                            "date_change": date_change,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return changes
    except Exception as e:
        print(f"Error scraping BOM calendar changes: {e}")
        return []


def scrape_bom_showdowns() -> list:
    """Scrapes BOM showdowns list."""
    url = f"{rl.BOM['base_url']}/showdown/"
    
    try:
        soup = _get_soup(url)
        showdowns = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 2:
                    try:
                        title_tag = cells[0].find("a")
                        title = title_tag.get_text(strip=True) if title_tag else cells[0].get_text(strip=True)
                        href = title_tag.get("href", "") if title_tag else ""
                        description = cells[1].get_text(strip=True) if len(cells) > 1 else None
                        
                        showdowns.append({
                            "title": title,
                            "description": description,
                            "bom_url": f"{rl.BOM['base_url']}{href}" if href else None,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return showdowns
    except Exception as e:
        print(f"Error scraping BOM showdowns: {e}")
        return []


def scrape_bom_daily_view(year: int, view: str = "year", interval: str = None) -> list:
    """Scrapes BOM daily view with various options.
    
    Args:
        year: Year to scrape
        view: 'year', 'season', 'quarter', 'month', 'holiday', 'cumulative'
        interval: For season views: 'winter', 'spring', 'summer', 'fall', 'holiday'
                  For cumulative: 'year_to_date' or 'cumulative_[month]'
    """
    if view == "year":
        url = f"{rl.BOM['base_url']}/daily/{year}/?view=year"
    elif view == "season" and interval:
        url = f"{rl.BOM['base_url']}/daily/{year}/?interval={interval}&view=season"
    elif view == "cumulative" and interval:
        url = f"{rl.BOM['base_url']}/daily/{year}/?interval={interval}&view=cumulative"
    else:
        url = f"{rl.BOM['base_url']}/daily/{year}/?view={view}"
    
    try:
        soup = _get_soup(url)
        data = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 2:
                    try:
                        date_tag = cells[0].find("a")
                        date_str = date_tag.get_text(strip=True) if date_tag else cells[0].get_text(strip=True)
                        gross = _parse_money(cells[1].get_text(strip=True)) if len(cells) > 1 else None
                        
                        href = date_tag.get("href", "") if date_tag else ""
                        
                        data.append({
                            "date": date_str,
                            "gross_usd": gross,
                            "bom_url": f"{rl.BOM['base_url']}{href}" if href else None,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return data
    except Exception as e:
        print(f"Error scraping BOM daily view: {e}")
        return []


def scrape_bom_weekend_view(by_type: str = "year", value: str = None) -> list:
    """Scrapes BOM weekend view.
    
    Args:
        by_type: 'year' or 'week'
        value: Year number for 'year', week number (1-53) for 'week'
    """
    if by_type == "week" and value:
        url = f"{rl.BOM['base_url']}/weekend/by-week/{value}/"
    elif by_type == "year" and value:
        url = f"{rl.BOM['base_url']}/weekend/by-year/{value}/"
    else:
        url = f"{rl.BOM['base_url']}/weekend/"
    
    try:
        soup = _get_soup(url)
        data = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    try:
                        rank = _parse_money(cells[0].get_text(strip=True))
                        title_tag = cells[1].find("a")
                        title = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
                        gross = _parse_money(cells[2].get_text(strip=True)) if len(cells) > 2 else None
                        
                        href = title_tag.get("href", "") if title_tag else ""
                        
                        data.append({
                            "rank": rank,
                            "title": title,
                            "title_normalized": _normalize_title(title),
                            "gross_usd": gross,
                            "bom_url": f"{rl.BOM['base_url']}{href}" if href else None,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return data
    except Exception as e:
        print(f"Error scraping BOM weekend view: {e}")
        return []


def scrape_bom_weekly_view(by_type: str = "year", value: str = None) -> list:
    """Scrapes BOM weekly view.
    
    Args:
        by_type: 'year' or 'week'
        value: Year number for 'year', week number for 'week'
    """
    if by_type == "week" and value:
        url = f"{rl.BOM['base_url']}/weekly/by-week/{value}/"
    elif by_type == "year" and value:
        url = f"{rl.BOM['base_url']}/weekly/by-year/{value}/"
    else:
        url = f"{rl.BOM['base_url']}/weekly/"
    
    try:
        soup = _get_soup(url)
        data = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    try:
                        rank = _parse_money(cells[0].get_text(strip=True))
                        title_tag = cells[1].find("a")
                        title = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
                        gross = _parse_money(cells[2].get_text(strip=True)) if len(cells) > 2 else None
                        
                        href = title_tag.get("href", "") if title_tag else ""
                        
                        data.append({
                            "rank": rank,
                            "title": title,
                            "title_normalized": _normalize_title(title),
                            "gross_usd": gross,
                            "bom_url": f"{rl.BOM['base_url']}{href}" if href else None,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return data
    except Exception as e:
        print(f"Error scraping BOM weekly view: {e}")
        return []


def scrape_bom_monthly_view(by_type: str = "month", value: str = None, grosses_option: str = "totalGrosses", release_scale: str = "all") -> list:
    """Scrapes BOM monthly view.
    
    Args:
        by_type: 'month', 'year', 'to-date'
        value: Month name for 'month', year for 'year'/'to-date'
        grosses_option: 'calendarGrosses' or 'totalGrosses'
        release_scale: 'all', 'wide', or 'limited'
    """
    if by_type == "month" and value:
        url = f"{rl.BOM['base_url']}/month/{value}/?grossesOption={grosses_option}&releaseScale={release_scale}"
    elif by_type == "year" and value:
        url = f"{rl.BOM['base_url']}/month/by-year/{value}/?grossesOption={grosses_option}&releaseScale={release_scale}"
    elif by_type == "to-date" and value:
        url = f"{rl.BOM['base_url']}/month/to-date/{value}/"
    else:
        url = f"{rl.BOM['base_url']}/month/february/?grossesOption={grosses_option}"
    
    try:
        soup = _get_soup(url)
        data = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    try:
                        rank = _parse_money(cells[0].get_text(strip=True))
                        title_tag = cells[1].find("a")
                        title = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
                        gross = _parse_money(cells[2].get_text(strip=True)) if len(cells) > 2 else None
                        
                        href = title_tag.get("href", "") if title_tag else ""
                        
                        data.append({
                            "rank": rank,
                            "title": title,
                            "title_normalized": _normalize_title(title),
                            "gross_usd": gross,
                            "bom_url": f"{rl.BOM['base_url']}{href}" if href else None,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return data
    except Exception as e:
        print(f"Error scraping BOM monthly view: {e}")
        return []


def scrape_bom_quarterly_view(by_type: str = "quarter", value: str = None, grosses_option: str = "totalGrosses", release_scale: str = "limited") -> list:
    """Scrapes BOM quarterly view.
    
    Args:
        by_type: 'quarter', 'year', 'to-date'
        value: Quarter (q1-q4) for 'quarter', year for others
        grosses_option: 'calendarGrosses' or 'totalGrosses'
        release_scale: 'all', 'wide', or 'limited'
    """
    if by_type == "quarter" and value:
        url = f"{rl.BOM['base_url']}/quarter/{value}/?grossesOption={grosses_option}&releaseScale={release_scale}"
    elif by_type == "year" and value:
        url = f"{rl.BOM['base_url']}/quarter/by-year/{value}/?grossesOption={grosses_option}&releaseScale={release_scale}"
    elif by_type == "to-date" and value:
        url = f"{rl.BOM['base_url']}/quarter/to-date/{value}/"
    else:
        url = f"{rl.BOM['base_url']}/quarter/q1/?grossesOption={grosses_option}"
    
    try:
        soup = _get_soup(url)
        data = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    try:
                        rank = _parse_money(cells[0].get_text(strip=True))
                        title_tag = cells[1].find("a")
                        title = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
                        gross = _parse_money(cells[2].get_text(strip=True)) if len(cells) > 2 else None
                        
                        href = title_tag.get("href", "") if title_tag else ""
                        
                        data.append({
                            "rank": rank,
                            "title": title,
                            "title_normalized": _normalize_title(title),
                            "gross_usd": gross,
                            "bom_url": f"{rl.BOM['base_url']}{href}" if href else None,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return data
    except Exception as e:
        print(f"Error scraping BOM quarterly view: {e}")
        return []


def scrape_bom_yearly_view(view: str = "overview", year: int = None, interval: str = None) -> list:
    """Scrapes BOM yearly view.
    
    Args:
        view: 'overview' or 'ytd'
        year: Year for YTD comparison
        interval: For YTD: 'year_to_date' or 'cumulative_[month]'
    """
    if view == "ytd" and year:
        if interval:
            url = f"{rl.BOM['base_url']}/year/ytd/{year}/?interval={interval}"
        else:
            url = f"{rl.BOM['base_url']}/year/ytd/{year}/"
    else:
        url = f"{rl.BOM['base_url']}/year/?grossesOption=totalGrosses"
    
    try:
        soup = _get_soup(url)
        data = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    try:
                        rank = _parse_money(cells[0].get_text(strip=True))
                        title_tag = cells[1].find("a")
                        title = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
                        gross = _parse_money(cells[2].get_text(strip=True)) if len(cells) > 2 else None
                        
                        href = title_tag.get("href", "") if title_tag else ""
                        
                        data.append({
                            "rank": rank,
                            "title": title,
                            "title_normalized": _normalize_title(title),
                            "gross_usd": gross,
                            "bom_url": f"{rl.BOM['base_url']}{href}" if href else None,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return data
    except Exception as e:
        print(f"Error scraping BOM yearly view: {e}")
        return []


def scrape_bom_season_view(by_type: str = "season", value: str = None, year: int = None, grosses_option: str = "calendarGrosses") -> list:
    """Scrapes BOM season view.
    
    Args:
        by_type: 'season', 'year', 'to-date'
        value: Season name for 'season' (winter, spring, summer, fall)
        year: Year for 'year'/'to-date'
        grosses_option: 'calendarGrosses' or 'totalGrosses'
    """
    if by_type == "season" and value:
        url = f"{rl.BOM['base_url']}/season/{value}/?grossesOption={grosses_option}"
    elif by_type == "year" and year:
        url = f"{rl.BOM['base_url']}/season/by-year/{year}/?grossesOption={grosses_option}"
    elif by_type == "to-date" and year:
        url = f"{rl.BOM['base_url']}/season/to-date/{year}/"
    else:
        url = f"{rl.BOM['base_url']}/season/winter/?grossesOption={grosses_option}"
    
    try:
        soup = _get_soup(url)
        data = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    try:
                        rank = _parse_money(cells[0].get_text(strip=True))
                        title_tag = cells[1].find("a")
                        title = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
                        gross = _parse_money(cells[2].get_text(strip=True)) if len(cells) > 2 else None
                        
                        href = title_tag.get("href", "") if title_tag else ""
                        
                        data.append({
                            "rank": rank,
                            "title": title,
                            "title_normalized": _normalize_title(title),
                            "gross_usd": gross,
                            "bom_url": f"{rl.BOM['base_url']}{href}" if href else None,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return data
    except Exception as e:
        print(f"Error scraping BOM season view: {e}")
        return []


def scrape_bom_holiday_list() -> list:
    """Scrapes list of available holidays from BOM holiday page."""
    url = f"{rl.BOM['base_url']}/holiday/"
    
    try:
        soup = _get_soup(url)
        holidays = []
        
        # Find holiday links in the page
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "/holiday/" in href and href != "/holiday/":
                name = a.get_text(strip=True)
                if name:
                    full_url = f"{rl.BOM['base_url']}{href}" if not href.startswith("http") else href
                    holidays.append({
                        "name": name,
                        "url": full_url
                    })
        
        return holidays
    except Exception as e:
        print(f"Error scraping BOM holiday list: {e}")
        return []


def scrape_bom_holiday_view(by_type: str = "year", year: int = None, holiday: str = None) -> list:
    """Scrapes BOM holiday view.
    
    Args:
        by_type: 'year' or 'holiday'
        year: Year for 'year' view
        holiday: Holiday name for 'holiday' view (e.g., 'easter_sunday')
    """
    if by_type == "year" and year:
        url = f"{rl.BOM['base_url']}/holiday/by-year/{year}/?grossesOption=calendarGrosses"
    elif by_type == "holiday" and holiday and year:
        url = f"{rl.BOM['base_url']}/holiday/{holiday}/{year}/"
    else:
        url = f"{rl.BOM['base_url']}/holiday/"
    
    try:
        soup = _get_soup(url)
        data = []
        
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[1:]:  # skip header
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    try:
                        rank = _parse_money(cells[0].get_text(strip=True))
                        title_tag = cells[1].find("a")
                        title = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
                        gross = _parse_money(cells[2].get_text(strip=True)) if len(cells) > 2 else None
                        
                        href = title_tag.get("href", "") if title_tag else ""
                        
                        data.append({
                            "rank": rank,
                            "title": title,
                            "title_normalized": _normalize_title(title),
                            "gross_usd": gross,
                            "bom_url": f"{rl.BOM['base_url']}{href}" if href else None,
                            "source": "bom"
                        })
                    except (IndexError, AttributeError):
                        continue
        
        return data
    except Exception as e:
        print(f"Error scraping BOM holiday view: {e}")
        return []
