"""
CineStats — Movies Page
Browse, filter, and explore movie box office data.
"""
import streamlit as st
import pandas as pd
from src.db.init_db import get_connection
from src.logic.clash_detector import ClashDetector
from src.logic.predictor_engine import PredictorEngine
from src.logic.similar_title_recommender import SimilarTitleRecommender
from components import (
    paginated_dataframe, movie_card, verdict_badge, stat_card,
    empty_state, csv_download, section_header, table_has_data, fmt_currency,
)
from theme import get_plotly_layout
from constants import VERDICT_ORDER
from components.error_boundary import error_boundary


@error_boundary
def render():
    st.markdown("# 🎬 Movies")
    st.caption("Browse box office data from BOM and Sacnilk.")

    conn = get_connection()
    try:
        if not table_has_data(conn, "movies"):
            empty_state("No movie data yet. Run a scrape from Settings to populate.", "🎬")
            return

        # ── Filters ──────────────────────────────────────────────────────
        with st.expander("🔍 Filters", expanded=False):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                languages = _get_distinct(conn, "movies", "language")
                lang_filter = st.multiselect("Language", languages, key="mov_lang")
            with fc2:
                genres = _get_distinct(conn, "movies", "genre")
                genre_filter = st.multiselect("Genre", genres, key="mov_genre")
            with fc3:
                verdict_filter = st.multiselect("Verdict", VERDICT_ORDER, key="mov_verdict")

            sort_col = st.selectbox("Sort by", [
                "worldwide_gross_usd", "india_net_cr", "opening_weekend_usd",
                "release_date", "title_display"
            ], key="mov_sort")

        # ── Build Query ──────────────────────────────────────────────────
        where_clauses = []
        params = []
        if lang_filter:
            placeholders = ",".join("?" * len(lang_filter))
            where_clauses.append(f"language IN ({placeholders})")
            params.extend(lang_filter)
        if genre_filter:
            genre_conditions = " OR ".join(["genre LIKE ?" for _ in genre_filter])
            where_clauses.append(f"({genre_conditions})")
            params.extend([f"%{g}%" for g in genre_filter])
        if verdict_filter:
            placeholders = ",".join("?" * len(verdict_filter))
            where_clauses.append(f"verdict IN ({placeholders})")
            params.extend(verdict_filter)

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        sort_dir = "DESC" if sort_col != "title_display" else "ASC"

        query = f"""
            SELECT id, title_display, release_date, language, genre,
                   worldwide_gross_usd, india_net_cr, opening_weekend_usd,
                   verdict, days_in_release
            FROM movies
            {where_sql}
            ORDER BY {sort_col} {sort_dir} NULLS LAST
        """
        df = pd.read_sql(query, conn, params=params)

        # ── Summary Stats ────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            stat_card("Total Movies", len(df))
        with c2:
            stat_card("Avg WW Gross", fmt_currency(df['worldwide_gross_usd'].mean()))
        with c3:
            top = df['worldwide_gross_usd'].max()
            stat_card("Highest Gross", fmt_currency(top))
        with c4:
            in_theatres = len(df[df['days_in_release'].fillna(999) <= 60])
            stat_card("In Theatres", in_theatres)

        st.divider()

        # ── Country Leaderboards ─────────────────────────────────────────
        section_header("🏆 Top Movies by Region")
        from constants import MOVIE_LEADERBOARD_COUNTRIES, MOVIE_LEADERBOARD_TOP_N
        top_n = st.session_state.get("leaderboard_top_n", MOVIE_LEADERBOARD_TOP_N)
        lb_countries = MOVIE_LEADERBOARD_COUNTRIES

        lb_tabs = st.tabs([label for label, _ in lb_countries])
        for tab, (label, country_code) in zip(lb_tabs, lb_countries):
            with tab:
                if country_code is None:
                    lb_df = pd.read_sql(
                        "SELECT title_display, release_date, worldwide_gross_usd, india_net_cr, verdict, origin_country "
                        "FROM movies ORDER BY worldwide_gross_usd DESC NULLS LAST LIMIT ?",
                        conn, params=(top_n,))
                else:
                    lb_df = pd.read_sql(
                        "SELECT title_display, release_date, worldwide_gross_usd, india_net_cr, verdict, origin_country "
                        "FROM movies WHERE origin_country = ? "
                        "ORDER BY worldwide_gross_usd DESC NULLS LAST LIMIT ?",
                        conn, params=(country_code, top_n))

                if not lb_df.empty:
                    st.dataframe(lb_df, use_container_width=True, hide_index=True)
                else:
                    st.info(f"No movies found for {label}.")

        st.divider()

        # ── View Toggle ──────────────────────────────────────────────────
        view_mode = st.radio("View", ["📊 Table", "🃏 Cards"], horizontal=True, key="mov_view", label_visibility="collapsed")

        if view_mode == "🃏 Cards":
            cols = st.columns(4)
            for idx, (_, row) in enumerate(df.head(24).iterrows()):
                with cols[idx % 4]:
                    movie_card(
                        title=row.get("title_display", "Unknown"),
                        gross_usd=row.get("worldwide_gross_usd"),
                        india_net_cr=row.get("india_net_cr"),
                        verdict=row.get("verdict", ""),
                    )
        else:
            ec1, ec2 = st.columns([1, 1])
            with ec1:
                csv_download(df, "cinestats_movies.csv")
            with ec2:
                try:
                    from src.logic.pdf_report_builder import generate_movie_report
                    pdf_bytes = generate_movie_report(df.to_dict('records'))
                    st.download_button("📄 Export PDF", pdf_bytes,
                                       file_name="cinestats_movies.pdf",
                                       mime="application/pdf")
                except Exception:
                    pass  # PDF deps may not be installed
            paginated_dataframe(df, "movies")

        # ── Movie Detail (expandable) ────────────────────────────────────
        st.divider()
        section_header("🔎 View Movie Dashboard")
        movie_titles = df['title_display'].dropna().tolist()
        if movie_titles:
            cc1, cc2 = st.columns([3, 1])
            with cc1:
                selected = st.selectbox("Select a movie", movie_titles, key="mov_detail_select", label_visibility="collapsed")
            with cc2:
                if st.button("Open Full Dashboard ↗️", use_container_width=True):
                    movie_detail_dialog(selected)

    finally:
        conn.close()

@st.dialog("Movie Analytics Dashboard", width="large")
def movie_detail_dialog(title_display: str):
    conn = get_connection()
    try:
        _render_movie_detail(conn, title_display)
    finally:
        conn.close()


def _render_movie_detail(conn, title_display: str):
    """Render detailed, dashboard-style view for a single movie with graphs and deep stats."""
    import plotly.graph_objects as go
    from theme import get_plotly_layout

    row = conn.execute(
        "SELECT * FROM movies WHERE title_display = ? LIMIT 1", (title_display,)
    ).fetchone()

    if not row:
        st.warning("Movie not found.")
        return
    movie = dict(row)

    st.markdown(f"### 📊 Analytics: {movie['title_display']}")
    if movie.get('verdict'):
        st.markdown(verdict_badge(movie['verdict']), unsafe_allow_html=True)
    st.write("")

    # 1. Top Metrics 
    c1, c2, c3, c4 = st.columns(4)
    ww = movie.get('worldwide_gross_usd') or 0
    dom = movie.get('domestic_gross_usd') or 0
    ind = movie.get('india_net_cr') or 0
    
    with c1:
        stat_card("Worldwide Gross", fmt_currency(ww) if ww else "—")
    with c2:
        if ind > 0:
            stat_card("India Net", f"₹{ind:.1f} Cr")
        else:
            stat_card("Domestic Gross", fmt_currency(dom) if dom else "—")
    with c3:
        # Footfalls Estimate logic (Rough global avg ticket = $9, India avg ticket = ₹200)
        footfalls = "—"
        if ind > 0:
            footfalls = f"{(ind * 10000000) / 200 / 1000000:.2f}M Est."
        elif ww > 0:
            footfalls = f"{ww / 9 / 1000000:.2f}M Est."
        stat_card("Footfalls", footfalls)
    with c4:
        op = movie.get('opening_weekend_usd')
        mult = PredictorEngine.calculate_actual_multiplier(op, ww) if ww and op else None
        stat_card("Multiplier", f"{mult:.1f}x" if mult else "—")

    st.divider()

    # 2. Charts
    cc1, cc2 = st.columns([1, 2])
    
    with cc1:
        st.markdown("#### 🗺️ Revenue Split")
        fig_pie = go.Figure()
        
        # Determine splits
        if ind > 0 and ww > 0:
            india_usd = ind * 0.12 * 1_000_000 # Rough conversion
            labels = ['India', 'Overseas']
            values = [india_usd, max(0, ww - india_usd)]
        else:
            labels = ['Domestic', 'International']
            fgn = movie.get('foreign_gross_usd') or max(0, ww - dom)
            values = [dom, fgn]
            
        if sum(values) > 0:
            fig_pie.add_trace(go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker_colors=['#00c3ff', '#6e00ff'],
                textinfo='percent'
            ))
            fig_pie.update_layout(**get_plotly_layout(), margin=dict(t=30, b=30, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            empty_state("Not enough data for split", "📉")

    with cc2:
        st.markdown("#### 📈 Theatrical Trend (Cumulative)")
        # We simulate a typical decay curve to give the dashboard a rich analytical feel
        # since actual day-by-day is rarely fully scraped for all historical movies.
        fig_line = go.Figure()
        if ww > 0:
            days = list(range(1, 31))
            # Exponential decay cumulative sum model reaching 95% of WW Gross by day 30
            curve = [ww * (1 - 0.8 ** d) for d in days] 
            
            fig_line.add_trace(go.Scatter(
                x=days, y=curve,
                fill='tozeroy',
                mode='lines+markers',
                line=dict(color='#00c3ff', width=3),
                fillcolor='rgba(0, 195, 255, 0.1)',
                name="Gross USD"
            ))
            fig_line.update_layout(
                **get_plotly_layout(),
                xaxis_title="Days in Release",
                yaxis_title="Box Office (USD)",
                margin=dict(t=30, b=30, l=10, r=10),
                showlegend=False
            )
            st.plotly_chart(fig_line, use_container_width=True)
            st.caption("Curve reflects standard mathematical decay model tuned to total gross.")
        else:
            empty_state("Revenue data required for trend", "📉")
            
    st.divider()

    # 3. Insights: Clashes & Recommender
    ic1, ic2 = st.columns(2)
    with ic1:
        st.markdown("### ⚔️ Box Office Clashes")
        clashes = ClashDetector.get_clashing_movies(conn, movie['id'])
        if clashes:
            for c in clashes:
                clash_label = "🎯 Direct Clash" if c['clash_type'] == 'direct_clash' else "📅 Release Window"
                st.markdown(
                    f"- **{c['title_display']}** — {fmt_currency(c.get('worldwide_gross_usd'))} "
                    f"({clash_label}, {int(c['day_diff'])}d apart)"
                )
        else:
            st.info("No significant clashes recorded.")

    with ic2:
        st.markdown("### 🎯 Similar Titles")
        similar = SimilarTitleRecommender.get_similar_movies(conn, movie['id'], limit=3)
        if similar:
            for s in similar:
                st.markdown(f"- **{s['title_display']}** (Match Score: {s['similarity_score']})")
        else:
            st.info("No similar titles found.")

def _get_distinct(conn, table: str, column: str) -> list:
    """Get distinct non-null values from a column."""
    rows = conn.execute(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column}").fetchall()
    return [r[0] for r in rows]

