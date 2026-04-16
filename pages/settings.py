"""
CineStats — Settings Page
Preferences, data management, scrape triggers, and log viewer.
"""
import streamlit as st
import pandas as pd
from src.db.init_db import get_connection
from src.db.log_helpers import get_recent_events, prune_log, log_event
from src.db.cache_helpers import prune_cache
from components import stat_card, section_header, table_has_data
from constants import (
    SUPPORTED_CURRENCIES, DEFAULT_CURRENCY, PAGE_SIZES,
    CONTENT_TYPES, CONTENT_TYPE_LABELS, APP_NAME, APP_VERSION,
    OTD_DEFAULT_LIMIT, MOVIE_LEADERBOARD_TOP_N,
)
from components.error_boundary import error_boundary


@error_boundary
def render():
    st.markdown("# ⚙️ Settings")
    st.caption("Manage preferences, data sources, and application state.")

    tab_prefs, tab_scrape, tab_data, tab_logs, tab_about = st.tabs([
        "🎛️ Preferences", "🔄 Fetch Data", "📦 Data Management", "📋 Activity Log", "ℹ️ About"
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
        section_header("📅 On This Day")
        otd_limit = st.number_input(
            "Max entries shown on 'On This Day'",
            min_value=5, max_value=50,
            value=st.session_state.get("otd_limit", OTD_DEFAULT_LIMIT),
            key="settings_otd_limit",
        )
        st.session_state.otd_limit = otd_limit

        st.divider()
        section_header("🏆 Movie Leaderboard")
        lb_top_n = st.number_input(
            "Top N movies per category",
            min_value=3, max_value=25,
            value=st.session_state.get("leaderboard_top_n", MOVIE_LEADERBOARD_TOP_N),
            key="settings_lb_top_n",
        )
        st.session_state.leaderboard_top_n = lb_top_n

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

    # ── Fetch Data Tab ───────────────────────────────────────────────────
    with tab_scrape:
        section_header("🔄 Fetch / Scrape Data")
        st.caption("Trigger data fetching from external sources. Each button runs the corresponding scraper or API client.")

        conn = get_connection()
        try:
            st.markdown("### 🎬 Movies")
            sm1, sm2, sm3 = st.columns(3)
            with sm1:
                if st.button("📊 Fetch from Box Office Mojo", use_container_width=True, key="scrape_bom"):
                    _run_scraper(conn, "bom_scraper", "Box Office Mojo")
            with sm2:
                if st.button("🇮🇳 Fetch from Sacnilk", use_container_width=True, key="scrape_sacnilk"):
                    _run_scraper(conn, "sacnilk_scraper", "Sacnilk")
            with sm3:
                if st.button("🎥 Enrich via TMDB", use_container_width=True, key="scrape_tmdb"):
                    _run_scraper(conn, "tmdb_client", "TMDB")

            st.divider()

            st.markdown("### 💱 Utilities")
            if st.button("🔄 Refresh Exchange Rates", use_container_width=True, key="scrape_fx"):
                _run_scraper(conn, "exchange_rate_client", "Exchange Rates")

        finally:
            conn.close()

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


def _run_scraper(conn, source_module: str, display_name: str):
    """Attempt to run a scraper/client. Logs the result."""
    try:
        if source_module == "bom_scraper":
            from src.scrapers.bom_scraper import scrape_daily_chart, scrape_yearly_chart
            with st.spinner(f"Fetching from {display_name}..."):
                daily = scrape_daily_chart()
                yearly = scrape_yearly_chart()
                count = len(daily) + len(yearly)
                # Store into movies table
                _upsert_movies_from_df(conn, daily)
                _upsert_movies_from_df(conn, yearly)
                st.info(f"Fetched {len(daily)} daily + {len(yearly)} yearly entries.")

        elif source_module == "sacnilk_scraper":
            from src.scrapers.sacnilk_scraper import scrape_currently_running
            with st.spinner(f"Fetching from {display_name}..."):
                df = scrape_currently_running()
                _upsert_movies_from_df(conn, df)
                st.info(f"Fetched {len(df)} Indian movies.")

        elif source_module == "tmdb_client":
            from src.clients.tmdb_client import get_trending_movies, get_movie_detail
            with st.spinner(f"Enriching via {display_name}..."):
                trending = get_trending_movies("week")
                st.info(f"Fetched {len(trending)} trending movies from TMDB.")

        elif source_module == "tvmaze_client":
            from src.clients.tvmaze_client import search_tv_series
            with st.spinner(f"Fetching from {display_name}..."):
                st.info("TVMaze requires a search query. Use the search page to find specific shows.")

        elif source_module == "wikipedia_tv_scraper":
            from src.scrapers.wikipedia_tv_scraper import scrape_viewership_data
            with st.spinner(f"Scraping {display_name}..."):
                st.info("Wikipedia scraper requires a specific URL. Use the TV Series detail page.")

        elif source_module == "jikan_client":
            from src.clients.jikan_client import search_anime
            with st.spinner(f"Fetching from {display_name}..."):
                st.info("Jikan requires a search query. Use the search page to find specific anime.")

        elif source_module == "anilist_client":
            from src.clients.anilist_client import search_anime
            with st.spinner(f"Fetching from {display_name}..."):
                st.info("AniList requires a search query. Use the search page to find specific anime.")

        elif source_module == "exchange_rate_client":
            from src.clients.exchange_rate_client import fetch_rates
            with st.spinner("Refreshing exchange rates..."):
                rates = fetch_rates()
                st.session_state.exchange_rates = rates
                st.info(f"Loaded {len(rates)} exchange rates.")

        log_event(conn, "INFO", "scrape", source_module, display_name,
                  f"Successfully ran {display_name}")
        st.success(f"✅ {display_name} completed successfully!")

    except ImportError as e:
        st.warning(f"⚠️ Module not found: {e}. The {display_name} client may not be fully implemented yet.")
        log_event(conn, "WARNING", "scrape", source_module, display_name,
                  f"Import error: {e}", success=0)
    except Exception as e:
        st.error(f"❌ Error fetching from {display_name}: {e}")
        log_event(conn, "ERROR", "error", source_module, display_name,
                  str(e), success=0)


def _upsert_movies_from_df(conn, df):
    """Insert or update movies table from a scraped DataFrame."""
    if df is None or df.empty:
        return
    for _, row in df.iterrows():
        data = row.to_dict()
        title_norm = data.get("title_normalized")
        if not title_norm:
            continue
        # Check if exists
        existing = conn.execute(
            "SELECT id FROM movies WHERE title_normalized = ?", (title_norm,)
        ).fetchone()
        if existing:
            # Update non-null fields
            updates = []
            params = []
            for col in ["worldwide_gross_usd", "domestic_gross_usd", "india_net_cr",
                         "opening_weekend_usd", "verdict", "release_date", "days_in_release"]:
                val = data.get(col)
                if val is not None:
                    updates.append(f"{col} = ?")
                    params.append(val)
            if updates:
                params.append(existing[0])
                conn.execute(f"UPDATE movies SET {', '.join(updates)} WHERE id = ?", params)
        else:
            conn.execute(
                """INSERT INTO movies (title_display, title_normalized, source,
                   worldwide_gross_usd, india_net_cr, release_date, verdict)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data.get("title_display"), title_norm, data.get("source", "unknown"),
                 data.get("worldwide_gross_usd"), data.get("india_net_cr"),
                 data.get("release_date"), data.get("verdict"))
            )
    conn.commit()
