"""
CineStats — Wikipedia Movie Scraper
Fallback mechanism for missing budget, box office, and country data.
"""
from curl_cffi import requests
import re
from typing import Dict, Any

def get_movie_infobox_data(title: str, year: str = "") -> Dict[str, Any]:
    """Search Wikipedia for a movie and extract box office/country data from its Infobox."""
    query = f"{title} film" if not year else f"{title} {year} film"
    
    # 1. Search for page
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&utf8=&format=json"
    try:
        _session = requests.Session(impersonate="chrome120")
        search_res = _session.get(search_url, timeout=10).json()
        results = search_res.get('query', {}).get('search', [])
        if not results:
            return {}
        page_title = results[0]['title']
    except Exception:
        return {}
        
    # 2. Extract Infobox
    extract_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&titles={page_title}&format=json"
    try:
        _session2 = requests.Session(impersonate="chrome120")
        content_res = _session2.get(extract_url, timeout=10).json()
        pages = content_res.get('query', {}).get('pages', {})
        page_content = list(pages.values())[0].get('revisions', [{}])[0].get('*', '')
    except Exception:
        return {}
        
    result = {}
    
    # Simple regex for Country and Box Office in standard Wiki infoboxes
    country_match = re.search(r'\|\s*country\s*=\s*(.+?)\n', page_content, re.IGNORECASE)
    if country_match:
        # Clean wiki links [[United States]] -> United States
        clean_country = re.sub(r'\[\[(.*?)\]\]', r'\1', country_match.group(1))
        clean_country = clean_country.split('|')[-1].strip()
        result['country'] = clean_country
        
    bo_match = re.search(r'\|\s*box office\s*=\s*(.+?)\n', page_content, re.IGNORECASE)
    if bo_match:
        bo_str = bo_match.group(1).lower()
        # Very basic heuristic parsing for 'million' and 'crore'
        num_matches = re.findall(r'[\d.,]+', bo_str)
        if num_matches:
            val = float(num_matches[0].replace(',', ''))
            if 'billion' in bo_str:
                val *= 1000
            if 'million' in bo_str:
                result['worldwide_gross_usd'] = val * 1_000_000
            elif 'crore' in bo_str or 'cr' in bo_str:
                result['india_gross_cr'] = val
                
    return result
