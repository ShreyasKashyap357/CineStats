"""
CineStats — Streamlit Application Entry Point
Sidebar navigation, session state initialisation, page routing.
"""
import streamlit as st
import uuid
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theme import inject_css, DARK, LIGHT, get_plotly_layout
from constants import (
    APP_NAME, APP_VERSION, DEFAULT_CURRENCY, SUPPORTED_CURRENCIES,
    DEFAULT_PAGE_SIZE, CONTENT_TYPES,
)
from src.db.init_db import init_db, get_connection

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_NAME} — Movie, TV & Animation Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Session State Initialisation ─────────────────────────────────────────────
def _init_session():
    """Initialise all session state keys on first load."""
    defaults = {
        "session_id":       str(uuid.uuid4()),
        "user_uuid":        None,       # set from localStorage later
        "theme_mode":       "dark",
        "currency":         DEFAULT_CURRENCY,
        "country_lens":     ["Global"],
        "page_size":        DEFAULT_PAGE_SIZE,
        "expand_sections":  True,
        "content_type":     "movie",
        "current_page":     "🏠 Home",
        "exchange_rates":   None,       # fetched once on session start
        "db_initialized":   False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_session()

# ── Database Init ────────────────────────────────────────────────────────────
if not st.session_state.db_initialized:
    init_db()
    st.session_state.db_initialized = True


# ── CSS Injection ────────────────────────────────────────────────────────────
st.markdown(inject_css(st.session_state.theme_mode), unsafe_allow_html=True)


# ── Navigation & Sidebar ─────────────────────────────────────────────────────
# Navigation setup
from pages import home, movies, tv_series, animated_shows, compare, on_this_day, search, settings

pages = {
    "": [
        st.Page(home.render, title="Home", icon="🏠", url_path="home", default=True),
        st.Page(movies.render, title="Movies", icon="🎬", url_path="movies"),
        st.Page(tv_series.render, title="TV Series", icon="📺", url_path="tv_series"),
        st.Page(animated_shows.render, title="Animated Shows", icon="✨", url_path="animated_shows"),
        st.Page(compare.render, title="Compare", icon="⚖️", url_path="compare"),
        st.Page(on_this_day.render, title="On This Day", icon="📅", url_path="on_this_day"),
        st.Page(search.render, title="Search", icon="🔍", url_path="search"),
        st.Page(settings.render, title="Settings", icon="⚙️", url_path="settings"),
    ]
}

pg = st.navigation(pages, position="hidden")

with st.sidebar:
    # App branding
    st.markdown(f"""
    <div style="text-align:center; padding: 0.5rem 0 0.5rem 0;">
        <span style="font-size:2rem;">🎬</span>
        <h2 style="margin:0; color:#F1F5F9;">CineStats</h2>
        <p style="margin:0; font-size:0.75rem; color:#64748B;">
            Global Movie, TV & Animation Analytics
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Manual page links sequentially under branding
    for p in pages[""]:
        st.page_link(p)

    st.divider()

    # Currency selector
    st.session_state.currency = st.selectbox(
        "💱 Currency",
        SUPPORTED_CURRENCIES,
        index=SUPPORTED_CURRENCIES.index(st.session_state.currency),
    )

    # Theme toggle
    is_dark = st.toggle(
        "☀️ / 🌙 Dark Mode",
        value=(st.session_state.theme_mode == "dark")
    )
    new_theme = "dark" if is_dark else "light"
    if new_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = new_theme
        st.rerun()

    # Version footer
    st.markdown(f"""
    <div style="position:fixed; bottom:1rem; font-size:0.65rem; color:#64748B;">
        {APP_NAME} v{APP_VERSION}
    </div>
    """, unsafe_allow_html=True)

# Run the selected page
pg.run()
