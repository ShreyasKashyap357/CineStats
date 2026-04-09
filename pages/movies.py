"""CineStats — Movies Page (stub for Phase 8)."""
import streamlit as st
import pandas as pd
from src.db.init_db import get_connection


def render():
    st.markdown("# 🎬 Movies")
    st.caption("Browse box office data from BOM and Sacnilk.")

    conn = get_connection()
    try:
        movies = pd.read_sql(
            "SELECT title_display, release_date, worldwide_gross_usd, india_net_cr, verdict "
            "FROM movies ORDER BY worldwide_gross_usd DESC NULLS LAST LIMIT 50",
            conn)
        if not movies.empty:
            st.dataframe(movies, use_container_width=True, hide_index=True)
        else:
            st.info("No movie data yet. Run a scrape to populate.")
    finally:
        conn.close()
