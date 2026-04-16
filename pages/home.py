"""
CineStats — Home Page
Dashboard overview with live sections wired to backend logic.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from src.db.init_db import get_connection
from src.db.log_helpers import get_recently_added
from src.logic.mover_calculator import MoverCalculator
from components import (
    stat_card, movie_card, verdict_badge, empty_state,
    section_header, table_has_data, fmt_currency,
)
from constants import get_data_cutoff, CONTENT_TYPE_LABELS
from components.error_boundary import error_boundary


@error_boundary
def render():
    st.markdown("# 🏠 Home")
    st.caption(f"Data current as of {get_data_cutoff()}")

    # Jump-to-section nav
    cols = st.columns(7)
    sections = [
        ("🎬", "In Theatres"), ("📺", "Airing"), ("🔥", "Trending"),
        ("📈", "Movers"), ("📅", "On This Day"), ("🏆", "Top of Year"),
        ("🆕", "What's New"),
    ]
    for col, (icon, label) in zip(cols, sections):
        anchor_id = label.lower().replace(' ', '-').replace("'", "")
        col.markdown(
            f"<a href='#{anchor_id}' "
            f"style='text-decoration:none;color:#3B82F6;'>"
            f"{icon} {label}</a>",
            unsafe_allow_html=True,
        )

    st.divider()

    conn = get_connection()
    try:
        # ── Currently in Theatres ────────────────────────────────────────
        section_header("🎬 Currently in Theatres", "in-theatres")
        if table_has_data(conn, "movies"):
            movies = pd.read_sql(
                """SELECT title_display, worldwide_gross_usd, india_net_cr,
                          verdict, release_date, days_in_release, tmdb_id
                   FROM movies
                   WHERE days_in_release IS NOT NULL AND days_in_release <= 60
                   ORDER BY worldwide_gross_usd DESC NULLS LAST
                   LIMIT 12""",
                conn)
            if not movies.empty:
                _render_movie_cards(movies)
            else:
                st.info("No movies currently in theatres.")
        else:
            empty_state("No movie data yet. Scrape from Settings to populate.", "🎬")

        st.divider()

        # ── Currently Airing ─────────────────────────────────────────────
        section_header("📺 Currently Airing", "airing")
        has_airing = False

        for ctype, label in CONTENT_TYPE_LABELS.items():
            if ctype == "movie":
                continue
            tbl = "anime" if ctype == "anime" else "tv_series"
            if table_has_data(conn, tbl):
                status_col = "status"
                title_col = "title_english" if ctype == "anime" else "title_display"
                rating_col = "mal_score" if ctype == "anime" else "avg_rating"

                airing = pd.read_sql(
                    f"SELECT {title_col} as title, genre, {rating_col} as rating "
                    f"FROM {tbl} WHERE LOWER(status) IN ('running', 'ongoing', 'currently airing') "
                    f"LIMIT 8",
                    conn)
                if not airing.empty:
                    has_airing = True
                    st.markdown(f"### {label}")
                    st.dataframe(airing, use_container_width=True, hide_index=True)

        if not has_airing:
            st.info("Currently airing shows will appear after TV/Anime data is fetched.")

        st.divider()

        # ── Trending This Week ───────────────────────────────────────────
        section_header("🔥 Trending This Week", "trending")
        if table_has_data(conn, "movies"):
            trending = pd.read_sql(
                "SELECT title_display, worldwide_gross_usd, verdict "
                "FROM movies ORDER BY last_updated DESC LIMIT 10",
                conn)
            if not trending.empty:
                st.dataframe(trending, use_container_width=True, hide_index=True)
            else:
                st.info("No trending data available.")
        else:
            st.info("Trending data will populate from TMDB and MAL trending endpoints.")

        st.divider()

        # ── Daily / Weekend Movers ───────────────────────────────────────
        section_header("📈 Daily / Weekend Movers", "movers")
        if table_has_data(conn, "daily_performance"):
            today_str = date.today().strftime("%Y-%m-%d")
            yesterday_str = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

            result = MoverCalculator.get_top_gainers_and_losers(conn, today_str)
            if result['gainers'].empty and result['losers'].empty:
                # Try yesterday
                result = MoverCalculator.get_top_gainers_and_losers(conn, yesterday_str)

            mc1, mc2 = st.columns(2)
            with mc1:
                st.markdown("#### 📈 Top Gainers")
                if not result['gainers'].empty:
                    for _, row in result['gainers'].iterrows():
                        pct = row['pct_change']
                        st.markdown(
                            f"- **{row['title_display']}** "
                            f"<span class='trend-up'>+{pct:.1f}%</span>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("No gainers today.")

            with mc2:
                st.markdown("#### 📉 Top Losers")
                if not result['losers'].empty:
                    for _, row in result['losers'].iterrows():
                        pct = row['pct_change']
                        st.markdown(
                            f"- **{row['title_display']}** "
                            f"<span class='trend-down'>{pct:.1f}%</span>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("No losers today.")
        else:
            st.info("Movers will display after daily performance data is scraped.")

        st.divider()

        # ── On This Day ──────────────────────────────────────────────────
        section_header("📅 On This Day", "on-this-day")
        month_day = date.today().strftime("%m-%d")

        otd_items = []
        if table_has_data(conn, "movies"):
            otd_movies = pd.read_sql(
                "SELECT title_display, release_date, 'Movie' as type "
                "FROM movies WHERE strftime('%m-%d', release_date) = ? "
                "ORDER BY release_date DESC LIMIT 5",
                conn, params=(month_day,))
            if not otd_movies.empty:
                otd_items.append(otd_movies)

        if otd_items:
            combined = pd.concat(otd_items, ignore_index=True)
            st.dataframe(combined, use_container_width=True, hide_index=True)
            st.page_link("pages/on_this_day.py", label="See all →", icon="📅")
        else:
            st.info("No historical releases on this date.")

        st.divider()

        # ── Top of Year ──────────────────────────────────────────────────
        section_header("🏆 Top of Year", "top-of-year")
        current_year = date.today().year
        if table_has_data(conn, "movies"):
            top_year = pd.read_sql(
                "SELECT title_display, worldwide_gross_usd, india_net_cr, verdict "
                "FROM movies WHERE strftime('%Y', release_date) = ? "
                "ORDER BY worldwide_gross_usd DESC NULLS LAST LIMIT 10",
                conn, params=(str(current_year),))
            if not top_year.empty:
                st.dataframe(top_year, use_container_width=True, hide_index=True)
            else:
                st.info(f"No movies from {current_year} in the database yet.")
        else:
            st.info("Year-to-date top performers will appear after data is scraped.")


    finally:
        conn.close()


def _render_movie_cards(df: pd.DataFrame):
    """Render movie poster cards in a grid."""
    cols = st.columns(4)
    for idx, (_, movie) in enumerate(df.head(12).iterrows()):
        with cols[idx % 4]:
            movie_card(
                title=movie.get("title_display", "Unknown"),
                gross_usd=movie.get("worldwide_gross_usd"),
                india_net_cr=movie.get("india_net_cr"),
                verdict=movie.get("verdict", ""),
            )
