"""
CineStats — TV Series Page
Browse TV series data from TVMaze and Wikipedia viewership scraping.
"""
import streamlit as st
import pandas as pd
from src.db.init_db import get_connection
from components import (
    paginated_dataframe, stat_card, empty_state, csv_download,
    section_header, table_has_data, content_type_badge,
)


def render():
    st.markdown("# 📺 TV Series")
    st.caption("Browse TV series data from TVMaze and Wikipedia.")

    conn = get_connection()
    try:
        if not table_has_data(conn, "tv_series"):
            empty_state("No TV series data yet. Fetch data from Settings.", "📺")
            return

        # ── Filters ──────────────────────────────────────────────────────
        with st.expander("🔍 Filters", expanded=False):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                networks = _get_distinct(conn, "tv_series", "network")
                net_filter = st.multiselect("Network", networks, key="tv_net")
            with fc2:
                statuses = _get_distinct(conn, "tv_series", "status")
                status_filter = st.multiselect("Status", statuses, key="tv_status")
            with fc3:
                sort_col = st.selectbox("Sort by", [
                    "avg_rating", "total_episodes", "premiere_date", "title_display"
                ], key="tv_sort")

        # ── Build Query ──────────────────────────────────────────────────
        where_clauses = ["content_type = 'tv_series'"]
        params = []
        if net_filter:
            placeholders = ",".join("?" * len(net_filter))
            where_clauses.append(f"network IN ({placeholders})")
            params.extend(net_filter)
        if status_filter:
            placeholders = ",".join("?" * len(status_filter))
            where_clauses.append(f"status IN ({placeholders})")
            params.extend(status_filter)

        where_sql = "WHERE " + " AND ".join(where_clauses)
        sort_dir = "DESC" if sort_col not in ("title_display", "premiere_date") else "ASC"

        query = f"""
            SELECT id, title_display, network, status, genre,
                   total_seasons, total_episodes, avg_rating, premiere_date
            FROM tv_series
            {where_sql}
            ORDER BY {sort_col} {sort_dir} NULLS LAST
        """
        df = pd.read_sql(query, conn, params=params)

        # ── Summary Stats ────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            stat_card("Total Series", len(df))
        with c2:
            stat_card("Avg Rating", f"{df['avg_rating'].mean():.1f}" if not df['avg_rating'].isna().all() else "—")
        with c3:
            stat_card("Ongoing", len(df[df['status'].str.lower() == 'running']) if 'status' in df.columns else 0)
        with c4:
            stat_card("Total Episodes", int(df['total_episodes'].sum()) if not df['total_episodes'].isna().all() else 0)

        st.divider()

        csv_download(df, "cinestats_tv_series.csv")
        paginated_dataframe(df, "tv_series")

        # ── Series Detail ────────────────────────────────────────────────
        st.divider()
        section_header("🔎 Series Detail")
        titles = df['title_display'].dropna().tolist()
        if titles:
            selected = st.selectbox("Select a series", titles, key="tv_detail_select")
            if selected:
                _render_series_detail(conn, selected)

    finally:
        conn.close()


def _render_series_detail(conn, title_display: str):
    """Render detail view for a TV series with episode data."""
    row = conn.execute(
        "SELECT * FROM tv_series WHERE title_display = ? LIMIT 1", (title_display,)
    ).fetchone()

    if not row:
        st.warning("Series not found.")
        return
    series = dict(row)

    c1, c2, c3 = st.columns(3)
    with c1:
        stat_card("Seasons", series.get('total_seasons', '—'))
    with c2:
        stat_card("Episodes", series.get('total_episodes', '—'))
    with c3:
        stat_card("Rating", f"{series.get('avg_rating', 0):.1f}" if series.get('avg_rating') else "—")

    # Episode list
    episodes = pd.read_sql(
        "SELECT season, episode, title, air_date, rating, us_viewers "
        "FROM tv_episodes WHERE series_id = ? ORDER BY season, episode",
        conn, params=(series['id'],)
    )
    if not episodes.empty:
        st.markdown("### 📋 Episodes")
        paginated_dataframe(episodes, f"tv_ep_{series['id']}")
    else:
        st.info("No episode data available for this series.")


def _get_distinct(conn, table: str, column: str) -> list:
    rows = conn.execute(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column}").fetchall()
    return [r[0] for r in rows]
