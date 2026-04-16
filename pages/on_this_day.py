"""
CineStats — On This Day Page
Browse historical releases and airings on any date.
Default: shows top movies across ALL years for today's month-day.
Optional: filter by a specific year.
"""
import streamlit as st
import pandas as pd
from datetime import date
from src.db.init_db import get_connection
from components import empty_state, section_header, table_has_data, movie_card
from constants import OTD_DEFAULT_LIMIT
from components.error_boundary import error_boundary


@error_boundary
def render():
    st.markdown("# 📅 On This Day")
    st.caption("Discover what released or aired on any date in history.")

    otd_limit = st.session_state.get("otd_limit", OTD_DEFAULT_LIMIT)

    # ── Controls ─────────────────────────────────────────────────────────
    ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])
    with ctrl1:
        selected_date = st.date_input("Pick a date", value=date.today(), key="otd_date")
    with ctrl2:
        mode = st.radio("Mode", ["All Years", "Specific Year"], key="otd_mode", horizontal=True)
    with ctrl3:
        year_filter = None
        if mode == "Specific Year":
            year_filter = st.number_input("Year", min_value=1900, max_value=2100,
                                          value=selected_date.year, key="otd_year")

    month_day = selected_date.strftime("%m-%d")
    date_display = selected_date.strftime("%B %d")

    conn = get_connection()
    try:
        # ── Movies ───────────────────────────────────────────────────────
        section_header(f"🎬 Movies Released on {date_display}", "otd-movies")

        if table_has_data(conn, "movies"):
            if year_filter:
                movies = pd.read_sql(
                    "SELECT title_display, release_date, worldwide_gross_usd, india_net_cr, verdict "
                    "FROM movies "
                    "WHERE strftime('%m-%d', release_date) = ? AND strftime('%Y', release_date) = ? "
                    "ORDER BY worldwide_gross_usd DESC NULLS LAST "
                    "LIMIT ?",
                    conn, params=(month_day, str(year_filter), otd_limit)
                )
            else:
                movies = pd.read_sql(
                    "SELECT title_display, release_date, worldwide_gross_usd, india_net_cr, verdict "
                    "FROM movies "
                    "WHERE strftime('%m-%d', release_date) = ? "
                    "ORDER BY worldwide_gross_usd DESC NULLS LAST "
                    "LIMIT ?",
                    conn, params=(month_day, otd_limit)
                )

            if not movies.empty:
                # Render as cards with year shown
                cols = st.columns(4)
                for idx, (_, row) in enumerate(movies.iterrows()):
                    with cols[idx % 4]:
                        title = row.get("title_display", "Unknown")
                        release_yr = str(row.get("release_date", ""))[:4]
                        display_title = f"{title} ({release_yr})" if release_yr else title
                        movie_card(
                            title=display_title,
                            gross_usd=row.get("worldwide_gross_usd"),
                            india_net_cr=row.get("india_net_cr"),
                            verdict=row.get("verdict", ""),
                        )
                st.caption(
                    f"Showing top {len(movies)} movie(s) released on {date_display}"
                    f"{f' in {year_filter}' if year_filter else ' across all years'}."
                )
            else:
                st.info(f"No movies released on {date_display}"
                        f"{f' in {year_filter}' if year_filter else ''} in our database.")
        else:
            empty_state("No movie data available.", "🎬")

        st.divider()

        # ── TV Episodes ──────────────────────────────────────────────────
        section_header(f"📺 TV Episodes Aired on {date_display}", "otd-tv")

        if table_has_data(conn, "tv_episodes"):
            year_clause = "AND strftime('%Y', e.air_date) = ?" if year_filter else ""
            params = [month_day, str(year_filter), otd_limit] if year_filter else [month_day, otd_limit]

            episodes = pd.read_sql(
                f"SELECT e.title as episode_title, e.season, e.episode, e.air_date, "
                f"e.rating, e.us_viewers, s.title_display as series "
                f"FROM tv_episodes e "
                f"JOIN tv_series s ON e.series_id = s.id "
                f"WHERE strftime('%m-%d', e.air_date) = ? {year_clause} "
                f"ORDER BY e.air_date DESC LIMIT ?",
                conn, params=params
            )
            if not episodes.empty:
                st.dataframe(episodes, use_container_width=True, hide_index=True)
                st.caption(f"Found {len(episodes)} episode(s).")
            else:
                st.info(f"No TV episodes aired on {date_display} in our database.")
        else:
            st.info("No TV episode data available.")

        st.divider()

        # ── Anime Episodes ───────────────────────────────────────────────
        section_header(f"🎌 Anime Episodes Aired on {date_display}", "otd-anime")

        if table_has_data(conn, "anime_episodes"):
            year_clause = "AND strftime('%Y', ae.air_date) = ?" if year_filter else ""
            params = [month_day, str(year_filter), otd_limit] if year_filter else [month_day, otd_limit]

            anime_eps = pd.read_sql(
                f"SELECT ae.episode_number, ae.title, ae.air_date, ae.mal_score, "
                f"a.title_english as anime "
                f"FROM anime_episodes ae "
                f"JOIN anime a ON ae.anime_id = a.id "
                f"WHERE strftime('%m-%d', ae.air_date) = ? {year_clause} "
                f"ORDER BY ae.air_date DESC LIMIT ?",
                conn, params=params
            )
            if not anime_eps.empty:
                st.dataframe(anime_eps, use_container_width=True, hide_index=True)
                st.caption(f"Found {len(anime_eps)} anime episode(s).")
            else:
                st.info(f"No anime episodes aired on {date_display} in our database.")
        else:
            st.info("No anime episode data available.")

    finally:
        conn.close()
