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
import requests
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

    headers = {"User-Agent": rl.BOM["user_agent"]}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
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

    return result


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
