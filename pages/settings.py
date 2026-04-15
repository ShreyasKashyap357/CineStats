"""
CineStats — Settings Page
Preferences, data management, scrape triggers, and log viewer.
"""
import streamlit as st
import pandas as pd
from src.db.init_db import get_connection
from src.db.log_helpers import get_recent_events, prune_log
from src.db.cache_helpers import prune_cache
from components import stat_card, section_header, table_has_data
from constants import (
    SUPPORTED_CURRENCIES, DEFAULT_CURRENCY, PAGE_SIZES,
    CONTENT_TYPES, CONTENT_TYPE_LABELS, APP_NAME, APP_VERSION,
)
from components.error_boundary import error_boundary


@error_boundary
def render():
    st.markdown("# ⚙️ Settings")
    st.caption("Manage preferences, data sources, and application state.")

    tab_prefs, tab_data, tab_logs, tab_about = st.tabs([
        "🎛️ Preferences", "📦 Data Management", "📋 Activity Log", "ℹ️ About"
    ])

    # ── Preferences Tab ──────────────────────────────────────────────────
    with tab_prefs:
        section_header("🎛️ Display Preferences")

        c1, c2 = st.columns(2)
        with c1:
            new_page_size = st.selectbox(
                "Default Page Size",
                PAGE_SIZES,
                index=PAGE_SIZES.index(st.session_state.get("page_size", 24)),
                key="settings_page_size",
            )
            if new_page_size != st.session_state.get("page_size"):
                st.session_state.page_size = new_page_size

        with c2:
            new_content = st.selectbox(
                "Default Content Type",
                CONTENT_TYPES,
                format_func=lambda x: CONTENT_TYPE_LABELS.get(x, x),
                index=CONTENT_TYPES.index(st.session_state.get("content_type", "movie")),
                key="settings_content_type",
            )
            if new_content != st.session_state.get("content_type"):
                st.session_state.content_type = new_content

        expand = st.checkbox(
            "Auto-expand all sections",
            value=st.session_state.get("expand_sections", True),
            key="settings_expand",
        )
        st.session_state.expand_sections = expand

        st.divider()
        section_header("📊 Current Session")
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            stat_card("Currency", st.session_state.get("currency", DEFAULT_CURRENCY))
        with sc2:
            stat_card("Theme", st.session_state.get("theme_mode", "dark").title())
        with sc3:
            stat_card("Page Size", st.session_state.get("page_size", 24))
        with sc4:
            sid = st.session_state.get("session_id", "N/A")
            stat_card("Session", sid[:8] + "…" if len(sid) > 8 else sid)

    # ── Data Management Tab ──────────────────────────────────────────────
    with tab_data:
        section_header("📦 Database Statistics")

        conn = get_connection()
        try:
            tables = ["movies", "tv_series", "anime", "daily_performance",
                       "tv_episodes", "anime_episodes", "franchises"]
            cols = st.columns(4)
            for i, table in enumerate(tables):
                with cols[i % 4]:
                    try:
                        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    except Exception:
                        count = 0
                    stat_card(table.replace("_", " ").title(), count)

            st.divider()
            section_header("🧹 Maintenance")

            mc1, mc2 = st.columns(2)
            with mc1:
                if st.button("🗑️ Prune Old Cache (>7 days)", use_container_width=True):
                    prune_cache(conn, days=7)
                    st.success("Scrape cache pruned.")
            with mc2:
                if st.button("🗑️ Prune Old Logs (>90 days)", use_container_width=True):
                    prune_log(conn, days=90)
                    st.success("Activity logs pruned.")

            st.divider()
            section_header("⚠️ Danger Zone")
            st.warning("These actions are irreversible.")

            if st.button("🔄 Reset Database", type="secondary", use_container_width=True):
                st.session_state["confirm_reset"] = True

            if st.session_state.get("confirm_reset"):
                st.error("Are you sure? This will delete ALL data.")
                rc1, rc2 = st.columns(2)
                with rc1:
                    if st.button("Yes, reset everything", type="primary"):
                        import os
                        from constants import DB_PATH
                        conn.close()
                        if os.path.exists(DB_PATH):
                            os.remove(DB_PATH)
                        from src.db.init_db import init_db
                        init_db()
                        st.session_state["confirm_reset"] = False
                        st.session_state["db_initialized"] = True
                        st.success("Database reset complete.")
                        st.rerun()
                with rc2:
                    if st.button("Cancel"):
                        st.session_state["confirm_reset"] = False
                        st.rerun()
        finally:
            conn.close()

    # ── Activity Log Tab ─────────────────────────────────────────────────
    with tab_logs:
        section_header("📋 Recent Activity")

        conn = get_connection()
        try:
            log_filter = st.selectbox(
                "Filter by event type",
                ["All", "scrape", "api_call", "error", "user_action"],
                key="log_filter",
            )

            event_type = None if log_filter == "All" else log_filter
            events = get_recent_events(conn, limit=100, event_type=event_type)

            if events:
                log_df = pd.DataFrame(events)
                display_cols = [c for c in ["timestamp", "level", "event_type", "source", "entity_key", "message", "success"] if c in log_df.columns]
                st.dataframe(log_df[display_cols], use_container_width=True, hide_index=True)
            else:
                st.info("No activity logged yet.")
        finally:
            conn.close()

    # ── About Tab ────────────────────────────────────────────────────────
    with tab_about:
        section_header(f"ℹ️ About {APP_NAME}")

        st.markdown(f"""
        **{APP_NAME}** v{APP_VERSION}

        Global Movies, TV & Animation Analytics Tracker.

        ### Data Sources
        | Source | Type | Rate Limit |
        |---|---|---|
        | Box Office Mojo | Web Scraper | 2s delay |
        | Sacnilk | Web Scraper | 2s delay |
        | TMDB | REST API | 40 req/10s |
        | Jikan (MAL) | REST API | 3 req/s, 60 req/min |
        | AniList | GraphQL API | 90 req/min |
        | TVMaze | REST API | 20 req/10s |
        | Wikipedia | Web Scraper | 2s delay |

        ### Tech Stack
        - **Frontend**: Streamlit
        - **Database**: SQLite (WAL mode)
        - **Charts**: Plotly
        - **Matching**: rapidfuzz
        - **Scraping**: BeautifulSoup4 + requests
        """)
