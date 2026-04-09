"""
CineStats — Home Page
Section 4 of the v1.0 specification.

Sections:
  - Jump-to-section anchor nav
  - Currently in Theatres
  - Currently Airing (split by content type)
  - Trending This Week
  - Daily / Weekend Movers
  - On This Day preview
  - Top of Year
  - What's New
"""
import streamlit as st
import pandas as pd
from src.db.init_db import get_connection
from src.db.log_helpers import get_recently_added
from constants import get_data_cutoff, CONTENT_TYPE_LABELS


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
        col.markdown(
            f"<a href='#{label.lower().replace(' ', '-')}' "
            f"style='text-decoration:none;color:#3B82F6;'>"
            f"{icon} {label}</a>",
            unsafe_allow_html=True,
        )

    st.divider()

    conn = get_connection()
    try:
        # ── Currently in Theatres ────────────────────────────────────────
        st.markdown("## 🎬 Currently in Theatres", anchor="in-theatres")
        movies = pd.read_sql(
            """SELECT title_display, worldwide_gross_usd, india_net_cr,
                      verdict, release_date, days_in_release, tmdb_id
               FROM movies
               WHERE days_in_release IS NOT NULL AND days_in_release <= 60
               ORDER BY worldwide_gross_usd DESC NULLS LAST
               LIMIT 12""",
            conn) if _table_has_data(conn, "movies") else pd.DataFrame()

        if not movies.empty:
            _render_movie_cards(movies)
        else:
            st.info("No movies currently in theatres. Data will appear after the first scrape.")

        st.divider()

        # ── Currently Airing ─────────────────────────────────────────────
        st.markdown("## 📺 Currently Airing", anchor="airing")
        for ctype, label in CONTENT_TYPE_LABELS.items():
            if ctype == "movie":
                continue
            table = "anime" if ctype == "anime" else "tv_series"
            if _table_has_data(conn, table):
                airing = pd.read_sql(
                    f"SELECT * FROM {table} WHERE status='Ongoing' LIMIT 8", conn)
                if not airing.empty:
                    st.markdown(f"### {label}")
                    st.dataframe(airing[["title_display", "genre", "avg_rating" if "avg_rating" in airing.columns else "mal_score"]].head(8),
                                 use_container_width=True, hide_index=True)
        st.info("Currently airing shows will appear after TV/Anime data is fetched.")

        st.divider()

        # ── Trending This Week ───────────────────────────────────────────
        st.markdown("## 🔥 Trending This Week", anchor="trending")
        st.info("Trending data will populate from TMDB and MAL trending endpoints.")

        st.divider()

        # ── Daily / Weekend Movers ───────────────────────────────────────
        st.markdown("## 📈 Daily / Weekend Movers", anchor="movers")
        st.info("Movers will display top 5 gainers and losers among currently running films.")

        st.divider()

        # ── On This Day ──────────────────────────────────────────────────
        st.markdown("## 📅 On This Day", anchor="on-this-day")
        st.info("Shows releases and airings on this date in history.")

        st.divider()

        # ── Top of Year ──────────────────────────────────────────────────
        st.markdown("## 🏆 Top of Year", anchor="top-of-year")
        st.info("Year-to-date top performers by content type.")

        st.divider()

        # ── What's New ───────────────────────────────────────────────────
        st.markdown("## 🆕 What's New", anchor="what's-new")
        recent = get_recently_added(conn, limit=10)
        if recent:
            for item in recent:
                st.markdown(f"- **{item['entity_key']}** from `{item['source']}` ({item['timestamp'][:10]})")
        else:
            st.info("Recent activity will appear after data is fetched.")

    finally:
        conn.close()


def _table_has_data(conn, table: str) -> bool:
    """Check if a table has any rows."""
    try:
        row = conn.execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone()
        return row is not None
    except Exception:
        return False


def _render_movie_cards(df: pd.DataFrame):
    """Render movie poster cards in a grid."""
    cols = st.columns(4)
    for idx, (_, movie) in enumerate(df.head(12).iterrows()):
        with cols[idx % 4]:
            title = movie.get("title_display", "Unknown")
            gross = movie.get("worldwide_gross_usd")
            verdict = movie.get("verdict", "")
            india_net = movie.get("india_net_cr")

            st.markdown(f"""
            <div class="cinestats-card">
                <h4 style="margin:0 0 0.3rem 0; font-size:0.9rem;">{title}</h4>
                <p style="margin:0; font-size:0.75rem; color:#94A3B8;">
                    {'${:,.0f}'.format(gross) + ' WW' if gross else 'N/A'}
                    {' · ₹' + '{:.1f}'.format(india_net) + ' Cr' if india_net else ''}
                </p>
                {f'<span class="verdict-badge" style="background:{_verdict_color(verdict)};">{verdict}</span>' if verdict else ''}
            </div>
            """, unsafe_allow_html=True)


def _verdict_color(verdict: str) -> str:
    from theme import VERDICT_COLORS
    return VERDICT_COLORS.get(verdict, "#64748B")
