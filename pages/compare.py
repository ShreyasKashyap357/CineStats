"""
CineStats — Compare Page
Within-category and cross-category side-by-side comparisons.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.db.init_db import get_connection
from components import stat_card, empty_state, section_header, table_has_data, fmt_currency
from theme import get_plotly_layout
from components.error_boundary import error_boundary


@error_boundary
def render():
    st.markdown("# ⚖️ Compare")
    st.caption("Side-by-side performance comparisons.")

    conn = get_connection()
    try:
        compare_mode = st.radio(
            "Comparison Type",
            ["🎬 Movies vs Movies", "📺 TV vs TV", "🎌 Anime vs Anime", "🔀 Cross-Category"],
            horizontal=True,
            key="compare_mode",
        )

        if compare_mode == "🎬 Movies vs Movies":
            _compare_movies(conn)
        elif compare_mode == "📺 TV vs TV":
            _compare_tv(conn)
        elif compare_mode == "🎌 Anime vs Anime":
            _compare_anime(conn)
        else:
            _compare_cross(conn)
    finally:
        conn.close()


def _compare_movies(conn):
    """Compare two or more movies side by side."""
    if not table_has_data(conn, "movies"):
        empty_state("No movie data to compare.", "🎬")
        return

    titles = [r[0] for r in conn.execute(
        "SELECT title_display FROM movies WHERE title_display IS NOT NULL ORDER BY title_display"
    ).fetchall()]

    selected = st.multiselect("Select movies to compare (2-5)", titles, max_selections=5, key="cmp_movies")

    if len(selected) < 2:
        st.info("Select at least 2 movies to compare.")
        return

    placeholders = ",".join("?" * len(selected))
    df = pd.read_sql(
        f"SELECT title_display, worldwide_gross_usd, india_net_cr, opening_weekend_usd, "
        f"verdict, release_date, days_in_release, language, genre "
        f"FROM movies WHERE title_display IN ({placeholders})",
        conn, params=selected
    )

    st.dataframe(df, use_container_width=True, hide_index=True)

    # Chart: WW Gross comparison
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['title_display'],
        y=df['worldwide_gross_usd'],
        name="WW Gross (USD)",
        marker_color="#3B82F6",
    ))
    if not df['india_net_cr'].isna().all():
        fig.add_trace(go.Bar(
            x=df['title_display'],
            y=df['india_net_cr'],
            name="India Net (Cr)",
            marker_color="#8B5CF6",
            yaxis="y2",
        ))
    fig.update_layout(
        **get_plotly_layout(st.session_state.get("theme_mode", "dark")),
        title="Box Office Comparison",
        barmode="group",
        yaxis2=dict(overlaying="y", side="right", title="₹ Cr"),
    )
    st.plotly_chart(fig, use_container_width=True)


def _compare_tv(conn):
    """Compare TV series."""
    if not table_has_data(conn, "tv_series"):
        empty_state("No TV series data to compare.", "📺")
        return

    titles = [r[0] for r in conn.execute(
        "SELECT title_display FROM tv_series WHERE title_display IS NOT NULL ORDER BY title_display"
    ).fetchall()]

    selected = st.multiselect("Select series to compare (2-5)", titles, max_selections=5, key="cmp_tv")

    if len(selected) < 2:
        st.info("Select at least 2 series to compare.")
        return

    placeholders = ",".join("?" * len(selected))
    df = pd.read_sql(
        f"SELECT title_display, network, total_seasons, total_episodes, avg_rating, status "
        f"FROM tv_series WHERE title_display IN ({placeholders})",
        conn, params=selected
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Radar chart
    if not df['avg_rating'].isna().all():
        fig = go.Figure()
        for _, row in df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row['avg_rating'] or 0, row['total_seasons'] or 0, row['total_episodes'] or 0],
                theta=["Rating", "Seasons", "Episodes"],
                fill="toself",
                name=row['title_display'],
            ))
        fig.update_layout(
            **get_plotly_layout(st.session_state.get("theme_mode", "dark")),
            title="Series Comparison",
            polar=dict(radialaxis=dict(visible=True)),
        )
        st.plotly_chart(fig, use_container_width=True)


def _compare_anime(conn):
    """Compare anime entries."""
    if not table_has_data(conn, "anime"):
        empty_state("No anime data to compare.", "🎌")
        return

    titles = [r[0] for r in conn.execute(
        "SELECT title_english FROM anime WHERE title_english IS NOT NULL ORDER BY title_english"
    ).fetchall()]

    selected = st.multiselect("Select anime to compare (2-5)", titles, max_selections=5, key="cmp_anime")

    if len(selected) < 2:
        st.info("Select at least 2 anime to compare.")
        return

    placeholders = ",".join("?" * len(selected))
    df = pd.read_sql(
        f"SELECT title_english, mal_score, anilist_score, mal_members, mal_popularity, "
        f"episodes, demographic, studio "
        f"FROM anime WHERE title_english IN ({placeholders})",
        conn, params=selected
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['title_english'], y=df['mal_score'], name="MAL Score", marker_color="#3B82F6"))
    fig.add_trace(go.Bar(x=df['title_english'], y=df['anilist_score'], name="AniList Score", marker_color="#EC4899"))
    fig.update_layout(
        **get_plotly_layout(st.session_state.get("theme_mode", "dark")),
        title="Score Comparison",
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)


def _compare_cross(conn):
    """Cross-category comparison (movie vs TV vs anime)."""
    st.info("Select one item from each category to compare metrics across content types.")

    c1, c2, c3 = st.columns(3)

    movie_title = None
    tv_title = None
    anime_title = None

    with c1:
        if table_has_data(conn, "movies"):
            titles = [r[0] for r in conn.execute(
                "SELECT title_display FROM movies WHERE title_display IS NOT NULL ORDER BY title_display"
            ).fetchall()]
            movie_title = st.selectbox("🎬 Movie", ["(none)"] + titles, key="cross_movie")
            if movie_title == "(none)":
                movie_title = None

    with c2:
        if table_has_data(conn, "tv_series"):
            titles = [r[0] for r in conn.execute(
                "SELECT title_display FROM tv_series WHERE title_display IS NOT NULL ORDER BY title_display"
            ).fetchall()]
            tv_title = st.selectbox("📺 TV Series", ["(none)"] + titles, key="cross_tv")
            if tv_title == "(none)":
                tv_title = None

    with c3:
        if table_has_data(conn, "anime"):
            titles = [r[0] for r in conn.execute(
                "SELECT title_english FROM anime WHERE title_english IS NOT NULL ORDER BY title_english"
            ).fetchall()]
            anime_title = st.selectbox("🎌 Anime", ["(none)"] + titles, key="cross_anime")
            if anime_title == "(none)":
                anime_title = None

    entries = []
    if movie_title:
        row = conn.execute("SELECT title_display as title, verdict, worldwide_gross_usd as metric FROM movies WHERE title_display = ?", (movie_title,)).fetchone()
        if row:
            entries.append({"Title": row['title'], "Type": "Movie", "Metric": fmt_currency(row['metric']), "Detail": row['verdict'] or "—"})
    if tv_title:
        row = conn.execute("SELECT title_display as title, avg_rating, total_episodes FROM tv_series WHERE title_display = ?", (tv_title,)).fetchone()
        if row:
            entries.append({"Title": row['title'], "Type": "TV Series", "Metric": f"Rating: {row['avg_rating']}", "Detail": f"{row['total_episodes']} eps"})
    if anime_title:
        row = conn.execute("SELECT title_english as title, mal_score, episodes FROM anime WHERE title_english = ?", (anime_title,)).fetchone()
        if row:
            entries.append({"Title": row['title'], "Type": "Anime", "Metric": f"MAL: {row['mal_score']}", "Detail": f"{row['episodes']} eps"})

    if len(entries) >= 2:
        st.dataframe(pd.DataFrame(entries), use_container_width=True, hide_index=True)
    elif entries:
        st.warning("Select at least 2 items across categories.")
