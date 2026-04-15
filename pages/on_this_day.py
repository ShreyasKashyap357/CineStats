"""
CineStats — On This Day Page
Browse historical releases and airings on any date.
"""
import streamlit as st
import pandas as pd
from datetime import date
from src.db.init_db import get_connection
from components import empty_state, section_header, table_has_data, fmt_currency
from components.error_boundary import error_boundary


@error_boundary
def render():
    st.markdown("# 📅 On This Day")
    st.caption("Discover what released or aired on any date in history.")

    selected_date = st.date_input("Pick a date", value=date.today(), key="otd_date")

    # Format for SQLite matching (MM-DD for anniversary, full date for exact)
    month_day = selected_date.strftime("%m-%d")
    full_date = selected_date.strftime("%Y-%m-%d")

    conn = get_connection()
    try:
        # ── Movies Released On This Date ─────────────────────────────────
        section_header("🎬 Movies Released on This Date", "otd-movies")

        if table_has_data(conn, "movies"):
            movies = pd.read_sql(
                "SELECT title_display, release_date, worldwide_gross_usd, india_net_cr, verdict "
                "FROM movies "
                "WHERE strftime('%m-%d', release_date) = ? "
                "ORDER BY release_date DESC",
                conn, params=(month_day,)
            )
            if not movies.empty:
                st.dataframe(movies, use_container_width=True, hide_index=True)
                st.caption(f"Found {len(movies)} movie(s) released on {selected_date.strftime('%B %d')} across all years.")
            else:
                st.info(f"No movies released on {selected_date.strftime('%B %d')} in our database.")
        else:
            st.info("No movie data available.")

        st.divider()

        # ── TV Episodes Aired On This Date ───────────────────────────────
        section_header("📺 TV Episodes Aired on This Date", "otd-tv")

        if table_has_data(conn, "tv_episodes"):
            episodes = pd.read_sql(
                "SELECT e.title as episode_title, e.season, e.episode, e.air_date, "
                "e.rating, e.us_viewers, s.title_display as series "
                "FROM tv_episodes e "
                "JOIN tv_series s ON e.series_id = s.id "
                "WHERE strftime('%m-%d', e.air_date) = ? "
                "ORDER BY e.air_date DESC",
                conn, params=(month_day,)
            )
            if not episodes.empty:
                st.dataframe(episodes, use_container_width=True, hide_index=True)
                st.caption(f"Found {len(episodes)} episode(s) aired on {selected_date.strftime('%B %d')}.")
            else:
                st.info(f"No TV episodes aired on {selected_date.strftime('%B %d')} in our database.")
        else:
            st.info("No TV episode data available.")

        st.divider()

        # ── Anime Episodes Aired On This Date ────────────────────────────
        section_header("🎌 Anime Episodes Aired on This Date", "otd-anime")

        if table_has_data(conn, "anime_episodes"):
            anime_eps = pd.read_sql(
                "SELECT ae.episode_number, ae.title, ae.air_date, ae.mal_score, "
                "a.title_english as anime "
                "FROM anime_episodes ae "
                "JOIN anime a ON ae.anime_id = a.id "
                "WHERE strftime('%m-%d', ae.air_date) = ? "
                "ORDER BY ae.air_date DESC",
                conn, params=(month_day,)
            )
            if not anime_eps.empty:
                st.dataframe(anime_eps, use_container_width=True, hide_index=True)
                st.caption(f"Found {len(anime_eps)} anime episode(s) aired on {selected_date.strftime('%B %d')}.")
            else:
                st.info(f"No anime episodes aired on {selected_date.strftime('%B %d')} in our database.")
        else:
            st.info("No anime episode data available.")

    finally:
        conn.close()
