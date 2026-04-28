import time
from backend.database import get_db_context
from src.scrapers.sacnilk_scraper import scrape_box_office_collection_list
from src.scrapers.bom_scraper import scrape_daily_chart

def run_sacnilk_job(job_id: str):
    """Executes the Sacnilk scrape and updates DB."""
    from backend.queue import ScrapeQueueManager
    try:
        ScrapeQueueManager.update_job(job_id, "processing", 10, "Fetching Sacnilk list API (Cloudflare bypassing)...")
        
        # Scrape Sacnilk (bypasses CF and grabs Indian movies)
        movies = scrape_box_office_collection_list()
        
        if not movies:
            ScrapeQueueManager.update_job(job_id, "failed", 100, "No movies found or Cloudflare blocked.")
            return

        ScrapeQueueManager.update_job(job_id, "processing", 50, f"Found {len(movies)} movies. Upserting into DB...")
        
        with get_db_context() as conn:
            for m in movies:
                # Upsert into movies table
                conn.execute("""
                    INSERT INTO movies (title_display, title_normalized, release_date, language, source)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET 
                        title_display=excluded.title_display,
                        release_date=excluded.release_date
                """, (m['title_display'], m['title_normalized'], m['release_date'], m['language'], 'sacnilk'))
            conn.commit()
            
        ScrapeQueueManager.update_job(job_id, "completed", 100, f"Successfully processed {len(movies)} Indian movies.")
    except Exception as e:
        ScrapeQueueManager.update_job(job_id, "failed", 0, str(e))

def run_bom_job(job_id: str):
    """Executes BOM daily chart scrape and top 25 yearly (2022-2026), followed by deep-scrapes."""
    from src.scrapers.bom_scraper import scrape_movie_detail, scrape_yearly_chart
    from backend.queue import ScrapeQueueManager
    import pandas as pd
    try:
        ScrapeQueueManager.update_job(job_id, "processing", 5, "Fetching BOM Daily & Yearly Charts...")
        
        # 1. Fetch Daily
        df_daily = scrape_daily_chart()
        
        # 2. Fetch Yearly (Top 25 for 2022-2026)
        yearly_dfs = []
        for y in range(2022, 2027):
            try:
                y_df = scrape_yearly_chart(y)
                if not y_df.empty:
                    yearly_dfs.append(y_df.head(25))
            except Exception:
                pass
                
        if not df_daily.empty:
            yearly_dfs.append(df_daily)
            
        if not yearly_dfs:
            ScrapeQueueManager.update_job(job_id, "failed", 100, "No data found on BOM.")
            return
            
        combined_df = pd.concat(yearly_dfs, ignore_index=True)
        # Drop duplicates based on bom_url to avoid scraping the same movie twice
        combined_df = combined_df.drop_duplicates(subset=['bom_url'])
        
        movies = combined_df.to_dict('records')
        total = len(movies)
        ScrapeQueueManager.update_job(job_id, "processing", 10, f"Found {total} distinct movies. Initiating deep scrape...")
        
        with get_db_context() as conn:
            for idx, m in enumerate(movies):
                progress = int(10 + (idx / total * 80))
                ScrapeQueueManager.update_job(job_id, "processing", progress, f"Deep scraping: {m['title_display']}...")
                
                # Fetch deeper rollout data if URL exists
                detail = {}
                if m.get('bom_url'):
                    try:
                        detail = scrape_movie_detail(m['bom_url'])
                    except Exception:
                        pass
                
                # Insert Movie
                worldwide = detail.get('worldwide_gross_usd') or m.get('cumulative_gross_usd')
                domestic = detail.get('domestic_gross_usd') or m.get('daily_gross_usd')
                
                cursor = conn.execute("""
                    INSERT INTO movies (title_display, title_normalized, worldwide_gross_usd, domestic_gross_usd, foreign_gross_usd, opening_weekend_usd, theater_count, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET 
                        worldwide_gross_usd=excluded.worldwide_gross_usd,
                        domestic_gross_usd=excluded.domestic_gross_usd,
                        foreign_gross_usd=excluded.foreign_gross_usd,
                        opening_weekend_usd=excluded.opening_weekend_usd
                    RETURNING id
                """, (
                    m['title_display'], m['title_normalized'], worldwide, domestic, 
                    detail.get('foreign_gross_usd'), detail.get('opening_weekend_usd'), 
                    detail.get('theater_count'), 'bom'
                ))
                
                row = cursor.fetchone()
                db_movie_id = row[0] if row else None
                
                # Insert Rollouts
                if db_movie_id and detail.get('rollouts'):
                    for r in detail['rollouts']:
                        conn.execute("""
                            INSERT INTO movie_rollout (movie_id, country_name, region, gross_usd, opening_usd, release_date, source_url)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(movie_id, country_name) DO UPDATE SET
                                gross_usd=excluded.gross_usd,
                                opening_usd=excluded.opening_usd,
                                source_url=excluded.source_url
                        """, (
                            db_movie_id, r['country_name'], r['region'], 
                            r['gross_usd'], r['opening_usd'], r['release_date'], r.get('source_url')
                        ))
                
                conn.commit()
                time.sleep(1) # Polite delay
                
        ScrapeQueueManager.update_job(job_id, "completed", 100, f"Successfully processed {total} global movies with regional rollouts.")
    except Exception as e:
        ScrapeQueueManager.update_job(job_id, "failed", 0, str(e))
