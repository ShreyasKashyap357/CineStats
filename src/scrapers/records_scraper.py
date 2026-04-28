from curl_cffi import requests
from bs4 import BeautifulSoup
from src.scrapers.sacnilk_scraper import get_sacnilk_session, _parse_crore, _normalize_title
from src.scrapers.bom_scraper import _get_soup as bom_soup, _parse_money
import rate_limits as rl

def scrape_bom_record(category: str) -> list:
    """Scrapes BOM records (overall, weekend, daily, misc)."""
    url = f"{rl.BOM['base_url']}/charts/{category}"
    try:
        soup = bom_soup(url)
        data = []
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if not headers:
                continue
            for tr in table.find_all("tr")[1:]:
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    rank = cells[0].get_text(strip=True)
                    title_tag = cells[1].find("a")
                    title = title_tag.get_text(strip=True) if title_tag else cells[1].get_text(strip=True)
                    
                    # Usually gross is the 3rd or 4th column depending on chart type
                    val_idx = 2 if "weekend" not in category.lower() else 3
                    val = cells[val_idx].get_text(strip=True) if len(cells) > val_idx else ""
                    
                    data.append({
                        "rank": int(rank.replace(',', '')) if rank.replace(',', '').isdigit() else None,
                        "title": title,
                        "value": val
                    })
            if data:
                break  # Only take the first table that had data
        return data
    except Exception as e:
        print(f"Error scraping BOM record {category}: {e}")
        return []

def scrape_sacnilk_record(path: str, max_results: int = 100) -> list:
    """
    Dynamically scrapes any Sacnilk Record page using their new Tailwind Card layout.
    Improved to capture both mobile and desktop cards for more entries.
    """
    url = f"https://www.sacnilk.com/{path}"
    
    session = get_sacnilk_session()
    
    try:
        resp = session.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        data = []
        seen_titles = set()  # Avoid duplicates
        
        # Try mobile cards first (they have unrounded decimal values)
        mobile_cards = soup.find_all("div", class_="md:hidden")
        
        for rank, card in enumerate(mobile_cards, start=1):
            title_tag = card.find("h3")
            if not title_tag:
                continue
                
            title = title_tag.get_text(strip=True)
            if title in seen_titles:
                continue
            seen_titles.add(title)
            
            link_tag = card.find("a")
            url_path = link_tag.get("href", "") if link_tag else ""
            
            # Dynamically grab whatever metrics are in the grid (WW, Gross, Day 1, Overseas, etc.)
            metrics = {}
            stat_grid = card.find("div", class_="grid")
            if stat_grid:
                # Loop through the inner divs (e.g., <div>Gross:<span>₹1,416.90Cr</span></div>)
                for stat in stat_grid.find_all("div", recursive=False):
                    text = stat.get_text(strip=True)
                    if ":" in text:
                        key, val = text.split(":", 1)
                        metrics[key.strip().lower()] = _parse_crore(val)
            
            data.append({
                "rank": rank,
                "title": title,
                "sacnilk_url": f"https://www.sacnilk.com{url_path}" if url_path else None,
                "metrics": metrics
            })
            
            if len(data) >= max_results:
                break
        
        # If we didn't get enough from mobile cards, try desktop cards
        if len(data) < max_results:
            desktop_cards = soup.find_all("div", class_=lambda x: x and ("hidden" in x or "md" in x))
            if not desktop_cards:
                # Try alternative selectors for desktop cards
                desktop_cards = soup.find_all("div", class_=lambda x: x and "md" in x and "block" in x)
            
            for rank, card in enumerate(desktop_cards, start=len(data) + 1):
                title_tag = card.find("h3") or card.find("h2")
                if not title_tag:
                    continue
                    
                title = title_tag.get_text(strip=True)
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                link_tag = card.find("a")
                url_path = link_tag.get("href", "") if link_tag else ""
                
                metrics = {}
                stat_grid = card.find("div", class_="grid")
                if stat_grid:
                    for stat in stat_grid.find_all("div", recursive=False):
                        text = stat.get_text(strip=True)
                        if ":" in text:
                            key, val = text.split(":", 1)
                            metrics[key.strip().lower()] = _parse_crore(val)
                
                data.append({
                    "rank": rank,
                    "title": title,
                    "sacnilk_url": f"https://www.sacnilk.com{url_path}" if url_path else None,
                    "metrics": metrics
                })
                
                if len(data) >= max_results:
                    break
                
        return data
        
    except Exception as e:
        print(f"Error scraping Sacnilk record {path}: {e}")
        return []
