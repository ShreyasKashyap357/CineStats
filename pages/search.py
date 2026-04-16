"""
CineStats — Search Page
Unified search across movies, TV series, and anime.
"""
import streamlit as st
import pandas as pd
from src.db.init_db import get_connection
from components import paginated_dataframe, empty_state, content_type_badge, table_has_data
from components.error_boundary import error_boundary


@error_boundary
def render():
    st.markdown("# 🔍 Search")
    st.caption("Search across all content types.")

    query_text = st.text_input("Search titles...", placeholder="e.g. Avengers, Breaking Bad, Naruto", key="search_query")

    if not query_text or len(query_text) < 2:
        st.info("Type at least 2 characters to search.")
        return

    search_term = f"%{query_text}%"
    conn = get_connection()

    try:
        results = []

        # ── Movies ───────────────────────────────────────────────────────
        if table_has_data(conn, "movies"):
            movies = pd.read_sql(
                "SELECT title_display as title, 'Movie' as type, release_date, "
                "worldwide_gross_usd as metric, verdict as detail "
                "FROM movies WHERE title_display LIKE ? OR title_normalized LIKE ? "
                "ORDER BY worldwide_gross_usd DESC NULLS LAST LIMIT 20",
                conn, params=(search_term, search_term)
            )
            if not movies.empty:
                results.append(movies)

        # ── TV Series ────────────────────────────────────────────────────
        if table_has_data(conn, "tv_series"):
            tv = pd.read_sql(
                "SELECT title_display as title, 'TV Series' as type, premiere_date as release_date, "
                "avg_rating as metric, status as detail "
                "FROM tv_series WHERE title_display LIKE ? OR title_normalized LIKE ? "
                "ORDER BY avg_rating DESC NULLS LAST LIMIT 20",
                conn, params=(search_term, search_term)
            )
            if not tv.empty:
                results.append(tv)

        # ── Anime ────────────────────────────────────────────────────────
        if table_has_data(conn, "anime"):
            anime = pd.read_sql(
                "SELECT title_english as title, 'Anime' as type, NULL as release_date, "
                "mal_score as metric, demographic as detail "
                "FROM anime WHERE title_english LIKE ? OR title_normalized LIKE ? "
                "OR title_japanese LIKE ? "
                "ORDER BY mal_score DESC NULLS LAST LIMIT 20",
                conn, params=(search_term, search_term, search_term)
            )
            if not anime.empty:
                results.append(anime)

        if results:
            combined = pd.concat(results, ignore_index=True)
            st.success(f"Found {len(combined)} result(s) for \"{query_text}\"")
            paginated_dataframe(combined, "search_results")
            
            st.divider()
            st.markdown("### 🔎 View Details")
            
            # Create a selection list like "Movie: Inception", "Anime: Naruto"
            combined["selection_label"] = combined["type"] + ": " + combined["title"]
            options = combined["selection_label"].tolist()
            
            selected_label = st.selectbox("Select title to view details", ["-- Select --"] + options, key="search_detail_select")
            
            if selected_label and selected_label != "-- Select --":
                # Parse type and title
                # Because labels are "Type: Title", we split by first ': '
                ctype, title = selected_label.split(": ", 1)
                
                st.markdown(f"#### {ctype} Details: {title}")
                
                if ctype == "Movie":
                    from pages.movies import _render_movie_detail
                    _render_movie_detail(conn, title)
                elif ctype == "TV Series":
                    from pages.tv_series import _render_series_detail
                    _render_series_detail(conn, title)
                elif ctype == "Anime":
                    from pages.animated_shows import _render_anime_detail
                    _render_anime_detail(conn, title)
                    
        else:
            empty_state(f"No results found for \"{query_text}\"", "🔍")

    finally:
        conn.close()
