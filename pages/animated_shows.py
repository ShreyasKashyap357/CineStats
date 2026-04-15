"""
CineStats — Animated Shows Page
Sub-sectioned into Anime, Western Animation, and Cartoons.
"""
import streamlit as st
import pandas as pd
from src.db.init_db import get_connection
from components import (
    paginated_dataframe, stat_card, empty_state, csv_download,
    section_header, table_has_data,
)


def render():
    st.markdown("# ✨ Animated Shows")
    st.caption("Anime, Western Animation, and Cartoons — all in one place.")

    tab_anime, tab_western, tab_cartoon = st.tabs(["🎌 Anime", "🧸 Western Animation", "👶 Cartoons"])

    conn = get_connection()
    try:
        # ── Anime Tab ────────────────────────────────────────────────────
        with tab_anime:
            _render_anime_tab(conn)

        # ── Western Animation Tab ────────────────────────────────────────
        with tab_western:
            _render_tv_subtype(conn, "western_animation", "Western Animation", "🧸")

        # ── Cartoons Tab ─────────────────────────────────────────────────
        with tab_cartoon:
            _render_tv_subtype(conn, "cartoon", "Cartoons", "👶")

    finally:
        conn.close()


def _render_anime_tab(conn):
    """Render anime browsing with MAL/AniList data."""
    if not table_has_data(conn, "anime"):
        empty_state("No anime data yet. Fetch from Jikan/AniList in Settings.", "🎌")
        return

    # Filters
    with st.expander("🔍 Filters", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            demographics = _get_distinct(conn, "anime", "demographic")
            demo_filter = st.multiselect("Demographic", demographics, key="anime_demo")
        with fc2:
            studios = _get_distinct(conn, "anime", "studio")
            studio_filter = st.multiselect("Studio", studios, key="anime_studio")
        with fc3:
            sort_col = st.selectbox("Sort by", [
                "mal_score", "mal_popularity", "mal_members", "anilist_score", "title_normalized"
            ], key="anime_sort")

    # Build query
    where_clauses = []
    params = []
    if demo_filter:
        ph = ",".join("?" * len(demo_filter))
        where_clauses.append(f"demographic IN ({ph})")
        params.extend(demo_filter)
    if studio_filter:
        ph = ",".join("?" * len(studio_filter))
        where_clauses.append(f"studio IN ({ph})")
        params.extend(studio_filter)

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    sort_dir = "DESC" if sort_col not in ("title_normalized",) else "ASC"

    query = f"""
        SELECT id, title_english, title_japanese, mal_score, anilist_score,
               mal_popularity, mal_members, episodes, status,
               demographic, genre, studio, season, season_year
        FROM anime
        {where_sql}
        ORDER BY {sort_col} {sort_dir} NULLS LAST
    """
    df = pd.read_sql(query, conn, params=params)

    # Summary stats
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Total Anime", len(df))
    with c2:
        stat_card("Avg MAL Score", f"{df['mal_score'].mean():.2f}" if not df['mal_score'].isna().all() else "—")
    with c3:
        stat_card("Avg AniList", f"{df['anilist_score'].mean():.1f}" if not df['anilist_score'].isna().all() else "—")
    with c4:
        stat_card("Airing", len(df[df['status'].str.lower() == 'currently airing']) if 'status' in df.columns else 0)

    st.divider()
    csv_download(df, "cinestats_anime.csv")
    paginated_dataframe(df, "anime")

    # Detail view
    st.divider()
    section_header("🔎 Anime Detail")
    titles = df['title_english'].dropna().tolist()
    if titles:
        selected = st.selectbox("Select an anime", titles, key="anime_detail_select")
        if selected:
            _render_anime_detail(conn, selected)


def _render_anime_detail(conn, title_english: str):
    """Render detailed anime view with seasons and episodes."""
    row = conn.execute(
        "SELECT * FROM anime WHERE title_english = ? LIMIT 1", (title_english,)
    ).fetchone()

    if not row:
        st.warning("Anime not found.")
        return
    anime = dict(row)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("MAL Score", f"{anime.get('mal_score', 0):.2f}" if anime.get('mal_score') else "—")
    with c2:
        stat_card("AniList Score", f"{anime.get('anilist_score', 0):.1f}" if anime.get('anilist_score') else "—")
    with c3:
        stat_card("Members", f"{anime.get('mal_members', 0):,}" if anime.get('mal_members') else "—")
    with c4:
        stat_card("Episodes", anime.get('episodes', '—'))

    # Seasons
    seasons = pd.read_sql(
        "SELECT season_number, cour_number, title, episodes_start, episodes_end, arc_name, is_split "
        "FROM anime_seasons WHERE anime_id = ? ORDER BY season_number, cour_number",
        conn, params=(anime['id'],)
    )
    if not seasons.empty:
        st.markdown("### 📅 Seasons / Cours")
        st.dataframe(seasons, use_container_width=True, hide_index=True)

    # Episodes
    episodes = pd.read_sql(
        "SELECT episode_number, title, air_date, mal_score "
        "FROM anime_episodes WHERE anime_id = ? ORDER BY episode_number",
        conn, params=(anime['id'],)
    )
    if not episodes.empty:
        st.markdown("### 📋 Episodes")
        paginated_dataframe(episodes, f"anime_ep_{anime['id']}")


def _render_tv_subtype(conn, content_type: str, label: str, icon: str):
    """Render Western Animation or Cartoon sub-tab from tv_series table."""
    has_data = False
    try:
        row = conn.execute(
            "SELECT 1 FROM tv_series WHERE content_type = ? LIMIT 1", (content_type,)
        ).fetchone()
        has_data = row is not None
    except Exception:
        pass

    if not has_data:
        empty_state(f"No {label} data yet. Fetch data from Settings.", icon)
        return

    df = pd.read_sql(
        "SELECT title_display, network, status, genre, total_seasons, total_episodes, avg_rating, premiere_date "
        "FROM tv_series WHERE content_type = ? ORDER BY avg_rating DESC NULLS LAST",
        conn, params=(content_type,)
    )

    c1, c2 = st.columns(2)
    with c1:
        stat_card(f"Total {label}", len(df))
    with c2:
        stat_card("Avg Rating", f"{df['avg_rating'].mean():.1f}" if not df['avg_rating'].isna().all() else "—")

    csv_download(df, f"cinestats_{content_type}.csv")
    paginated_dataframe(df, content_type)


def _get_distinct(conn, table: str, column: str) -> list:
    rows = conn.execute(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column}").fetchall()
    return [r[0] for r in rows]
