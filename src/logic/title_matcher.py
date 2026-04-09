"""
CineStats — Title Matcher
Section 14.10 of the v1.0 specification.

Matches movie titles across BOM ↔ Sacnilk using:
  1. Exact normalized title match
  2. Fuzzy matching via rapidfuzz (threshold: 85)
  3. Release date proximity within ±7 days
  4. Manual override mapping from match_overrides table
  5. Match confidence score stored with each match
"""
import re
from datetime import date, timedelta
from typing import Optional
from rapidfuzz import fuzz, process

from constants import FUZZY_MATCH_THRESHOLD, DATE_PROXIMITY_DAYS


def normalize_title(title: str) -> str:
    """Normalize a movie title for matching.

    Lowercases, removes punctuation, collapses whitespace.
    """
    title = title.strip().lower()
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()


def _date_within_window(date1: str, date2: str,
                        window_days: int = DATE_PROXIMITY_DAYS) -> bool:
    """Check if two date strings are within window_days of each other."""
    if not date1 or not date2:
        return True  # if either is missing, don't penalise

    try:
        d1 = date.fromisoformat(str(date1)[:10])
        d2 = date.fromisoformat(str(date2)[:10])
        return abs((d1 - d2).days) <= window_days
    except (ValueError, TypeError):
        return True


def match_titles(source_title: str, candidates: list[dict],
                 source_date: str = None,
                 overrides: dict = None) -> Optional[dict]:
    """Find the best matching title from a list of candidates.

    Args:
        source_title: the title to match
        candidates: list of dicts, each with 'title_normalized' and optionally 'release_date'
        source_date: release date of the source title (for proximity filtering)
        overrides: dict mapping source_title_normalized → target_title_normalized

    Returns:
        Dict with 'matched_title', 'match_confidence', 'match_method', and matched candidate data.
        None if no match found.
    """
    source_norm = normalize_title(source_title)

    # 1. Check manual overrides first
    if overrides and source_norm in overrides:
        target_norm = overrides[source_norm]
        for c in candidates:
            if c.get("title_normalized") == target_norm:
                return {
                    **c,
                    "matched_title":    c.get("title_normalized"),
                    "match_confidence": 1.0,
                    "match_method":     "manual_override",
                }

    # 2. Exact match
    for c in candidates:
        if c.get("title_normalized") == source_norm:
            if source_date and c.get("release_date"):
                if _date_within_window(source_date, c["release_date"]):
                    return {
                        **c,
                        "matched_title":    c["title_normalized"],
                        "match_confidence": 1.0,
                        "match_method":     "exact",
                    }
            else:
                return {
                    **c,
                    "matched_title":    c["title_normalized"],
                    "match_confidence": 1.0,
                    "match_method":     "exact",
                }

    # 3. Fuzzy match
    candidate_titles = [c.get("title_normalized", "") for c in candidates]
    if not candidate_titles:
        return None

    result = process.extractOne(
        source_norm, candidate_titles,
        scorer=fuzz.WRatio,
        score_cutoff=FUZZY_MATCH_THRESHOLD,
    )

    if result:
        matched_title, score, idx = result
        candidate = candidates[idx]

        # Check date proximity
        if source_date and candidate.get("release_date"):
            if not _date_within_window(source_date, candidate["release_date"]):
                # Date mismatch, lower confidence
                score *= 0.7

        confidence = round(score / 100.0, 3)

        return {
            **candidate,
            "matched_title":    matched_title,
            "match_confidence": confidence,
            "match_method":     "fuzzy",
        }

    return None


def get_overrides(conn) -> dict:
    """Load manual match overrides from the database.

    Returns dict mapping normalized source title → normalized target title.
    """
    try:
        rows = conn.execute(
            "SELECT source_title, target_title_normalized FROM match_overrides"
        ).fetchall()
        return {
            normalize_title(row[0]): row[1]
            for row in rows
        }
    except Exception:
        return {}


def merge_movie_data(bom_data: dict, sacnilk_data: dict,
                     tmdb_data: dict = None,
                     match_confidence: float = 1.0) -> dict:
    """Merge data from BOM, Sacnilk, and TMDB into a single movie record.

    BOM provides: worldwide/domestic/foreign grosses, opening weekend, theaters
    Sacnilk provides: India net/gross, verdict, language
    TMDB provides: poster, genre, cast, runtime, origin_country

    Returns a merged dict ready for upsert_movie().
    """
    merged = {
        "source": "merged",
        "match_confidence": match_confidence,
    }

    # BOM fields (primary for worldwide data)
    for key in ["title_normalized", "title_display", "release_date",
                "worldwide_gross_usd", "domestic_gross_usd", "foreign_gross_usd",
                "opening_weekend_usd", "theater_count", "days_in_release"]:
        if bom_data.get(key) is not None:
            merged[key] = bom_data[key]

    # Sacnilk fields (primary for India data)
    for key in ["india_net_cr", "india_gross_cr", "verdict", "language"]:
        if sacnilk_data.get(key) is not None:
            merged[key] = sacnilk_data[key]

    # Sacnilk fallbacks for fields BOM might not have
    for key in ["title_normalized", "title_display", "release_date"]:
        if merged.get(key) is None and sacnilk_data.get(key) is not None:
            merged[key] = sacnilk_data[key]

    # TMDB fields (enrichment)
    if tmdb_data:
        for key in ["genre", "runtime_mins", "origin_country", "tmdb_id"]:
            tmdb_key = "runtime" if key == "runtime_mins" else key
            if tmdb_data.get(tmdb_key) is not None:
                merged[key] = tmdb_data[tmdb_key]

        # Don't overwrite existing title
        if merged.get("origin_country") is None:
            merged["origin_country"] = tmdb_data.get("origin_country")

    return merged
