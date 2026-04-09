"""
CineStats — Upsert Helpers
INSERT OR REPLACE operations for all content tables.
"""
import sqlite3
from typing import Optional
from datetime import datetime


def upsert_movie(conn: sqlite3.Connection, data: dict) -> int:
    """Upsert a movie record. Returns the movie id."""
    conn.execute("""
        INSERT INTO movies (
            title_normalized, title_display, release_date, origin_country,
            language, genre, franchise_id, worldwide_gross_usd, domestic_gross_usd,
            foreign_gross_usd, india_net_cr, india_gross_cr, opening_weekend_usd,
            theater_count, verdict, days_in_release, runtime_mins, tmdb_id,
            source, match_confidence, last_updated
        ) VALUES (
            :title_normalized, :title_display, :release_date, :origin_country,
            :language, :genre, :franchise_id, :worldwide_gross_usd, :domestic_gross_usd,
            :foreign_gross_usd, :india_net_cr, :india_gross_cr, :opening_weekend_usd,
            :theater_count, :verdict, :days_in_release, :runtime_mins, :tmdb_id,
            :source, :match_confidence, :last_updated
        )
        ON CONFLICT(id) DO UPDATE SET
            title_display=excluded.title_display,
            worldwide_gross_usd=excluded.worldwide_gross_usd,
            domestic_gross_usd=excluded.domestic_gross_usd,
            foreign_gross_usd=excluded.foreign_gross_usd,
            india_net_cr=excluded.india_net_cr,
            india_gross_cr=excluded.india_gross_cr,
            opening_weekend_usd=excluded.opening_weekend_usd,
            theater_count=excluded.theater_count,
            verdict=excluded.verdict,
            days_in_release=excluded.days_in_release,
            source=excluded.source,
            match_confidence=excluded.match_confidence,
            last_updated=excluded.last_updated
    """, {
        "title_normalized":    data.get("title_normalized"),
        "title_display":       data.get("title_display"),
        "release_date":        data.get("release_date"),
        "origin_country":      data.get("origin_country"),
        "language":            data.get("language"),
        "genre":               data.get("genre"),
        "franchise_id":        data.get("franchise_id"),
        "worldwide_gross_usd": data.get("worldwide_gross_usd"),
        "domestic_gross_usd":  data.get("domestic_gross_usd"),
        "foreign_gross_usd":   data.get("foreign_gross_usd"),
        "india_net_cr":        data.get("india_net_cr"),
        "india_gross_cr":      data.get("india_gross_cr"),
        "opening_weekend_usd": data.get("opening_weekend_usd"),
        "theater_count":       data.get("theater_count"),
        "verdict":             data.get("verdict"),
        "days_in_release":     data.get("days_in_release"),
        "runtime_mins":        data.get("runtime_mins"),
        "tmdb_id":             data.get("tmdb_id"),
        "source":              data.get("source", "unknown"),
        "match_confidence":    data.get("match_confidence"),
        "last_updated":        datetime.utcnow().isoformat(),
    })
    conn.commit()
    
    # Return the ID of the upserted row
    row = conn.execute(
        "SELECT id FROM movies WHERE title_normalized = ? ORDER BY id DESC LIMIT 1",
        (data.get("title_normalized"),)
    ).fetchone()
    return row[0] if row else -1


def upsert_daily_performance(conn: sqlite3.Connection, movie_id: int, data: dict):
    """Upsert a daily performance record."""
    conn.execute("""
        INSERT OR REPLACE INTO daily_performance (
            movie_id, date, daily_gross_usd, daily_india_net_cr,
            cumulative_gross_usd, cumulative_india_net, theater_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        movie_id,
        data.get("date"),
        data.get("daily_gross_usd"),
        data.get("daily_india_net_cr"),
        data.get("cumulative_gross_usd"),
        data.get("cumulative_india_net"),
        data.get("theater_count"),
    ))
    conn.commit()


def upsert_tv_series(conn: sqlite3.Connection, data: dict) -> int:
    """Upsert a TV series record."""
    conn.execute("""
        INSERT INTO tv_series (
            title_normalized, title_display, origin_country, network,
            genre, status, premiere_date, total_seasons, total_episodes,
            avg_rating, content_type, age_rating, is_kodomomuke,
            tvmaze_id, tmdb_id, last_updated
        ) VALUES (
            :title_normalized, :title_display, :origin_country, :network,
            :genre, :status, :premiere_date, :total_seasons, :total_episodes,
            :avg_rating, :content_type, :age_rating, :is_kodomomuke,
            :tvmaze_id, :tmdb_id, :last_updated
        )
        ON CONFLICT(id) DO UPDATE SET
            title_display=excluded.title_display,
            status=excluded.status,
            total_seasons=excluded.total_seasons,
            total_episodes=excluded.total_episodes,
            avg_rating=excluded.avg_rating,
            last_updated=excluded.last_updated
    """, {
        **{k: data.get(k) for k in [
            "title_normalized", "title_display", "origin_country", "network",
            "genre", "status", "premiere_date", "total_seasons", "total_episodes",
            "avg_rating", "content_type", "age_rating", "tvmaze_id", "tmdb_id",
        ]},
        "is_kodomomuke": data.get("is_kodomomuke", 0),
        "last_updated": datetime.utcnow().isoformat(),
    })
    conn.commit()
    row = conn.execute(
        "SELECT id FROM tv_series WHERE title_normalized = ? ORDER BY id DESC LIMIT 1",
        (data.get("title_normalized"),)
    ).fetchone()
    return row[0] if row else -1


def upsert_anime(conn: sqlite3.Connection, data: dict) -> int:
    """Upsert an anime record."""
    conn.execute("""
        INSERT INTO anime (
            title_normalized, title_japanese, title_english,
            mal_id, anilist_id, mal_score, mal_rank, mal_popularity,
            mal_members, mal_favourites, anilist_score, anilist_popularity,
            episodes, status, demographic, genre, studio, source_material,
            season, season_year, origin_country, poster_url, last_updated
        ) VALUES (
            :title_normalized, :title_japanese, :title_english,
            :mal_id, :anilist_id, :mal_score, :mal_rank, :mal_popularity,
            :mal_members, :mal_favourites, :anilist_score, :anilist_popularity,
            :episodes, :status, :demographic, :genre, :studio, :source_material,
            :season, :season_year, :origin_country, :poster_url, :last_updated
        )
        ON CONFLICT(id) DO UPDATE SET
            mal_score=excluded.mal_score,
            mal_rank=excluded.mal_rank,
            anilist_score=excluded.anilist_score,
            episodes=excluded.episodes,
            status=excluded.status,
            last_updated=excluded.last_updated
    """, {
        **{k: data.get(k) for k in [
            "title_normalized", "title_japanese", "title_english",
            "mal_id", "anilist_id", "mal_score", "mal_rank", "mal_popularity",
            "mal_members", "mal_favourites", "anilist_score", "anilist_popularity",
            "episodes", "status", "demographic", "genre", "studio", "source_material",
            "season", "season_year", "poster_url",
        ]},
        "origin_country": data.get("origin_country", "JP"),
        "last_updated": datetime.utcnow().isoformat(),
    })
    conn.commit()
    row = conn.execute(
        "SELECT id FROM anime WHERE title_normalized = ? ORDER BY id DESC LIMIT 1",
        (data.get("title_normalized"),)
    ).fetchone()
    return row[0] if row else -1
