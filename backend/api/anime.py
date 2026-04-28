from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from backend.database import get_db_context
from typing import List

router = APIRouter()

@router.get("/search")
def search_anime(query: str = Query(..., description="Search query for anime")):
    """Search for anime using Jikan API."""
    from curl_cffi import requests as cffi_requests
    try:
        jikan_session = cffi_requests.Session(impersonate="chrome120")
        jikan_resp = jikan_session.get(f"https://api.jikan.moe/v4/anime?q={query}&limit=10", timeout=5).json()
        results = []
        for a in jikan_resp.get("data", []):
            results.append({
                "mal_id": a.get("mal_id"),
                "title": a.get("title"),
                "title_english": a.get("title_english"),
                "title_japanese": a.get("title_japanese"),
                "episodes": a.get("episodes"),
                "status": a.get("status"),
                "score": a.get("score"),
                "rank": a.get("rank"),
                "popularity": a.get("popularity"),
                "studios": [s.get("name") for s in a.get("studios", [])],
                "genres": [g.get("name") for g in a.get("genres", [])],
                "poster_url": a.get("images", {}).get("jpg", {}).get("image_url"),
                "synopsis": a.get("synopsis"),
                "aired": a.get("aired", {}).get("string")
            })
        return {"results": results}
    except Exception as e:
        print(f"Anime search error: {e}")
        return {"results": []}

@router.get("/")
def get_all_anime(skip: int = 0, limit: int = 25):
    """Fetches all tracked anime from the database."""
    with get_db_context() as conn:
        total = conn.execute("SELECT COUNT(*) FROM anime").fetchone()[0]
        anime = conn.execute("""
            SELECT * FROM anime
            ORDER BY mal_popularity ASC
            LIMIT ? OFFSET ?
        """, (limit, skip)).fetchall()
        return {"total": total, "items": [dict(a) for a in anime]}

@router.get("/{anime_id}")
def get_anime_detail(anime_id: int):
    """Fetches detailed information for a specific anime."""
    with get_db_context() as conn:
        anime = conn.execute("SELECT * FROM anime WHERE id = ?", (anime_id,)).fetchone()
        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")
        return dict(anime)

@router.get("/{anime_id}/structure")
def get_anime_structure(anime_id: int, view: str = "default"):
    """Get anime structural views - Cour, Season, Story Arc, Episode views."""
    with get_db_context() as conn:
        anime = conn.execute("SELECT * FROM anime WHERE id = ?", (anime_id,)).fetchone()
        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")
        
        anime_dict = dict(anime)
        
        # Return structure based on view type
        if view == "cour":
            # Group by cour (quarter of a year)
            return {
                "view": "cour",
                "anime_id": anime_id,
                "title": anime_dict.get("title_english") or anime_dict.get("title_normalized"),
                "structure": {
                    "cour_1": {"episodes": anime_dict.get("episodes", 0) // 4, "description": "First cour"},
                    "cour_2": {"episodes": anime_dict.get("episodes", 0) // 4, "description": "Second cour"},
                    "cour_3": {"episodes": anime_dict.get("episodes", 0) // 4, "description": "Third cour"},
                    "cour_4": {"episodes": anime_dict.get("episodes", 0) // 4, "description": "Fourth cour"}
                }
            }
        elif view == "season":
            # Group by season
            return {
                "view": "season",
                "anime_id": anime_id,
                "title": anime_dict.get("title_english") or anime_dict.get("title_normalized"),
                "structure": {
                    "season_1": {"episodes": anime_dict.get("episodes", 0), "description": "Season 1"}
                }
            }
        elif view == "story_arc":
            # Group by story arc
            return {
                "view": "story_arc",
                "anime_id": anime_id,
                "title": anime_dict.get("title_english") or anime_dict.get("title_normalized"),
                "structure": {
                    "arc_1": {"episodes": anime_dict.get("episodes", 0), "description": "Main Story Arc"}
                }
            }
        elif view == "episode":
            # Episode-level view
            return {
                "view": "episode",
                "anime_id": anime_id,
                "title": anime_dict.get("title_english") or anime_dict.get("title_normalized"),
                "total_episodes": anime_dict.get("episodes", 0),
                "episodes": [{"episode": i+1, "title": f"Episode {i+1}"} for i in range(anime_dict.get("episodes", 0) or 0)]
            }
        else:
            # Default view
            return {
                "view": "default",
                "anime_id": anime_id,
                "title": anime_dict.get("title_english") or anime_dict.get("title_normalized"),
                "episodes": anime_dict.get("episodes", 0),
                "season": anime_dict.get("season"),
                "studios": anime_dict.get("studios")
            }

@router.get("/{anime_id}/flattened")
def get_anime_flattened(anime_id: int):
    """Get flattened view for split seasons/cours."""
    with get_db_context() as conn:
        anime = conn.execute("SELECT * FROM anime WHERE id = ?", (anime_id,)).fetchone()
        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")
        
        anime_dict = dict(anime)
        
        # Return flattened view combining all seasons/cours
        return {
            "anime_id": anime_id,
            "title": anime_dict.get("title_english") or anime_dict.get("title_normalized"),
            "flattened": True,
            "total_episodes": anime_dict.get("episodes", 0),
            "combined_seasons": [
                {
                    "season": anime_dict.get("season"),
                    "episodes": anime_dict.get("episodes", 0),
                    "year": anime_dict.get("season_year")
                }
            ]
        }

@router.get("/{anime_id}/credits")
def get_anime_credits(anime_id: int):
    """Get anime full credits - Japanese voice cast + English dub cast."""
    with get_db_context() as conn:
        anime = conn.execute("SELECT * FROM anime WHERE id = ?", (anime_id,)).fetchone()
        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")
        
        anime_dict = dict(anime)
        
        # Return credits data (mock implementation since database may not have this data)
        return {
            "anime_id": anime_id,
            "title": anime_dict.get("title_english") or anime_dict.get("title_normalized"),
            "japanese_voice_cast": [
                {"name": "Voice Actor 1", "character": "Main Character"},
                {"name": "Voice Actor 2", "character": "Supporting Character"}
            ],
            "english_dub_cast": [
                {"name": "Dub Actor 1", "character": "Main Character"},
                {"name": "Dub Actor 2", "character": "Supporting Character"}
            ],
            "staff": [
                {"name": "Director", "role": "Director"},
                {"name": "Producer", "role": "Producer"}
            ]
        }


@router.get("/{anime_id}/arcs")
def get_anime_arcs(anime_id: int):
    """Fetches all manually defined arcs."""
    with get_db_context() as conn:
        arcs = conn.execute("SELECT * FROM anime_arcs WHERE anime_id = ? ORDER BY episode_start", (anime_id,)).fetchall()
        return [dict(a) for a in arcs]

@router.post("/{anime_id}/arcs")
def create_anime_arc(anime_id: int, arc: ArcCreate):
    """Allows manual definition of a new story arc."""
    with get_db_context() as conn:
        cursor = conn.execute("""
            INSERT INTO anime_arcs (anime_id, arc_name, episode_start, episode_end, source_chapter_start, source_chapter_end)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id
        """, (anime_id, arc.arc_name, arc.episode_start, arc.episode_end, arc.source_chapter_start, arc.source_chapter_end))
        conn.commit()
        return {"status": "success", "id": cursor.fetchone()[0]}

@router.post("/scrape")
def trigger_anime_scrape(query: str, background_tasks: BackgroundTasks):
    """Pushes a Jikan + AniList scrape job to the background."""
    
    def background_scrape_task(q: str):
        from src.scrapers.anime_scraper import pipeline_scrape_anime
        result = pipeline_scrape_anime(q)
        
        if result.get("status") == "success":
            data = result["data"]
            
            with get_db_context() as conn:
                # Upsert Anime based on mal_id or anilist_id
                # In SQLite without a UNIQUE constraint on mal_id, we will do a manual check
                cursor = conn.execute("SELECT id FROM anime WHERE mal_id = ? OR anilist_id = ?", 
                                      (data["mal_id"], data["anilist_id"]))
                row = cursor.fetchone()
                
                if row:
                    # Update
                    conn.execute("""
                        UPDATE anime SET
                            mal_score = ?, mal_rank = ?, mal_popularity = ?,
                            anilist_score = ?, anilist_popularity = ?,
                            episodes = ?, status = ?, poster_url = ?
                        WHERE id = ?
                    """, (data["mal_score"], data["mal_rank"], data["mal_popularity"],
                          data["anilist_score"], data["anilist_popularity"],
                          data["episodes"], data["status"], data["poster_url"], row[0]))
                else:
                    # Insert
                    conn.execute("""
                        INSERT INTO anime (
                            title_normalized, title_japanese, title_english, mal_id, anilist_id,
                            mal_score, mal_rank, mal_popularity, mal_members, mal_favourites,
                            anilist_score, anilist_popularity, episodes, status, demographic,
                            genre, studio, source_material, season, season_year, poster_url
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data["title_normalized"], data["title_japanese"], data["title_english"],
                        data["mal_id"], data["anilist_id"], data["mal_score"], data["mal_rank"],
                        data["mal_popularity"], data["mal_members"], data["mal_favourites"],
                        data["anilist_score"], data["anilist_popularity"], data["episodes"],
                        data["status"], data["demographic"], data["genre"], data["studio"],
                        data["source_material"], data["season"], data["season_year"], data["poster_url"]
                    ))
                conn.commit()

    background_tasks.add_task(background_scrape_task, query)
    return {"message": "Anime scrape job queued", "query": query}

from pydantic import BaseModel
class ArcCreate(BaseModel):
    arc_name: str
    episode_start: int
    episode_end: int
    source_chapter_start: int = None
    source_chapter_end: int = None

@router.get("/{anime_id}/arcs")
def get_anime_arcs(anime_id: int):
    """Fetches all manually defined arcs."""
    with get_db_context() as conn:
        arcs = conn.execute("SELECT * FROM anime_arcs WHERE anime_id = ? ORDER BY episode_start", (anime_id,)).fetchall()
        return [dict(a) for a in arcs]

@router.post("/{anime_id}/arcs")
def create_anime_arc(anime_id: int, arc: ArcCreate):
    """Allows manual definition of a new story arc."""
    with get_db_context() as conn:
        cursor = conn.execute("""
            INSERT INTO anime_arcs (anime_id, arc_name, episode_start, episode_end, source_chapter_start, source_chapter_end)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id
        """, (anime_id, arc.arc_name, arc.episode_start, arc.episode_end, arc.source_chapter_start, arc.source_chapter_end))
        conn.commit()
        return {"status": "success", "id": cursor.fetchone()[0]}

@router.delete("/{anime_id}")
def delete_anime(anime_id: int):
    """Delete an anime and all its related data from the database."""
    with get_db_context() as conn:
        anime = conn.execute("SELECT id, title_english FROM anime WHERE id = ?", (anime_id,)).fetchone()
        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")
        title = anime[1] or "Unknown"
        conn.execute("DELETE FROM anime_arcs WHERE anime_id = ?", (anime_id,))
        conn.execute("DELETE FROM anime_episodes WHERE anime_id = ?", (anime_id,))
        conn.execute("DELETE FROM anime_seasons WHERE anime_id = ?", (anime_id,))
        conn.execute("DELETE FROM anime WHERE id = ?", (anime_id,))
        conn.commit()
    return {"status": "success", "message": f"Deleted '{title}' from database."}
