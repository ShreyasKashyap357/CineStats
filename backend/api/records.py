from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from backend.database import get_db_context
import json

router = APIRouter()

@router.get("/scrape")
def fetch_and_store_record(source: str, category: str, path: str = ""):
    """Scrapes a record list, stores it in DB, and returns it."""
    from src.scrapers.records_scraper import scrape_bom_record, scrape_sacnilk_record
    
    if source == "bom":
        data = scrape_bom_record(category)
        record_title = f"BOM {category.capitalize()}"
        path = path or category
    elif source == "sacnilk":
        path = category # The frontend passes the path inside the category param for sacnilk
        data = scrape_sacnilk_record(path)
        
        # Clean up the title from the slug, e.g. Bollywood_100_Cr_Club_All_Time -> Bollywood 100 Cr Club All Time
        clean_title = path.split('/')[-1].replace('_', ' ').replace('-', ' ').title()
        record_title = f"Sacnilk {clean_title}"
    else:
        raise HTTPException(status_code=400, detail="Invalid source")
        
    with get_db_context() as conn:
        # Create or Get Record ID
        cursor = conn.execute("""
            INSERT INTO records (title, category, source, url)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET title=excluded.title
            RETURNING id
        """, (record_title, category, source, path))
        
        record_id = cursor.fetchone()[0]
        
        # Clear old entries for this exact record to prevent rank collisions
        conn.execute("DELETE FROM record_entries WHERE record_id = ?", (record_id,))
        
        # Insert New Entries
        for r in data:
            # BOM returns 'value', Sacnilk returns 'metrics' dict
            val = json.dumps(r.get('metrics')) if 'metrics' in r else r.get('value')
            
            conn.execute("""
                INSERT INTO record_entries (record_id, rank, movie_title, primary_value)
                VALUES (?, ?, ?, ?)
            """, (record_id, r.get('rank'), r.get('title'), val))
            
        conn.commit()
        
    return {"status": "success", "record_id": record_id, "data": data}

@router.get("/list")
def list_saved_records():
    """Returns all stored records from the database."""
    with get_db_context() as conn:
        records = conn.execute("SELECT * FROM records ORDER BY title ASC").fetchall()
        return [dict(r) for r in records]
        
@router.get("/{record_id}")
def get_record_entries(record_id: int):
    """Returns entries for a specific record."""
    with get_db_context() as conn:
        entries = conn.execute("SELECT * FROM record_entries WHERE record_id = ? ORDER BY rank ASC", (record_id,)).fetchall()
        return [dict(r) for r in entries]

@router.delete("/clear")
def clear_all_records():
    """Deletes all records and their entries from the database."""
    with get_db_context() as conn:
        # Delete all entries first (foreign key constraint)
        conn.execute("DELETE FROM record_entries")
        # Delete all records
        conn.execute("DELETE FROM records")
        conn.commit()
    return {"status": "success", "message": "All records cleared"}

# BOM Extended Endpoints

@router.get("/bom/chart-links")
def get_bom_chart_links():
    """Extracts all chart sub-links from BOM main chart pages."""
    from src.scrapers.bom_scraper import scrape_bom_chart_links
    return scrape_bom_chart_links()

@router.get("/bom/calendar")
def get_bom_calendar(date_str: Optional[str] = None):
    """Scrapes BOM release calendar."""
    from src.scrapers.bom_scraper import scrape_bom_calendar
    return scrape_bom_calendar(date_str)

@router.get("/bom/calendar-changes")
def get_bom_calendar_changes():
    """Scrapes BOM release schedule changes."""
    from src.scrapers.bom_scraper import scrape_bom_calendar_changes
    return scrape_bom_calendar_changes()

@router.get("/bom/showdowns")
def get_bom_showdowns():
    """Scrapes BOM showdowns list."""
    from src.scrapers.bom_scraper import scrape_bom_showdowns
    return scrape_bom_showdowns()

@router.get("/bom/daily")
def get_bom_daily_view(year: int, view: str = "year", interval: Optional[str] = None):
    """Scrapes BOM daily view with various options."""
    from src.scrapers.bom_scraper import scrape_bom_daily_view
    return scrape_bom_daily_view(year, view, interval)

@router.get("/bom/weekend")
def get_bom_weekend_view(by_type: str = "year", value: Optional[str] = None):
    """Scrapes BOM weekend view."""
    from src.scrapers.bom_scraper import scrape_bom_weekend_view
    return scrape_bom_weekend_view(by_type, value)

@router.get("/bom/weekly")
def get_bom_weekly_view(by_type: str = "year", value: Optional[str] = None):
    """Scrapes BOM weekly view."""
    from src.scrapers.bom_scraper import scrape_bom_weekly_view
    return scrape_bom_weekly_view(by_type, value)

@router.get("/bom/monthly")
def get_bom_monthly_view(by_type: str = "month", value: Optional[str] = None, grosses_option: str = "totalGrosses", release_scale: str = "all"):
    """Scrapes BOM monthly view."""
    from src.scrapers.bom_scraper import scrape_bom_monthly_view
    return scrape_bom_monthly_view(by_type, value, grosses_option, release_scale)

@router.get("/bom/quarterly")
def get_bom_quarterly_view(by_type: str = "quarter", value: Optional[str] = None, grosses_option: str = "totalGrosses", release_scale: str = "limited"):
    """Scrapes BOM quarterly view."""
    from src.scrapers.bom_scraper import scrape_bom_quarterly_view
    return scrape_bom_quarterly_view(by_type, value, grosses_option, release_scale)

@router.get("/bom/yearly")
def get_bom_yearly_view(view: str = "overview", year: Optional[int] = None, interval: Optional[str] = None):
    """Scrapes BOM yearly view."""
    from src.scrapers.bom_scraper import scrape_bom_yearly_view
    return scrape_bom_yearly_view(view, year, interval)

@router.get("/bom/season")
def get_bom_season_view(by_type: str = "season", value: Optional[str] = None, year: Optional[int] = None, grosses_option: str = "calendarGrosses"):
    """Scrapes BOM season view."""
    from src.scrapers.bom_scraper import scrape_bom_season_view
    return scrape_bom_season_view(by_type, value, year, grosses_option)

@router.get("/bom/holiday-list")
def get_bom_holiday_list():
    """Scrapes list of available holidays from BOM holiday page."""
    from src.scrapers.bom_scraper import scrape_bom_holiday_list
    return scrape_bom_holiday_list()

@router.get("/bom/holiday")
def get_bom_holiday_view(by_type: str = "year", year: Optional[int] = None, holiday: Optional[str] = None):
    """Scrapes BOM holiday view."""
    from src.scrapers.bom_scraper import scrape_bom_holiday_view
    return scrape_bom_holiday_view(by_type, year, holiday)
