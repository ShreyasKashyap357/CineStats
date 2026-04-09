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

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # App branding (reduced padding)
    st.markdown(f"""
    <div style="text-align:center; padding: 0;">
        <span style="font-size:2rem; line-height: 1;">🎬</span>
        <h2 style="margin: 0; color:#F1F5F9; font-size: 1.5rem;">CineStats</h2>
        <p style="margin: 0; font-size:0.7rem; color:#64748B;">
            Global Movie, TV & Animation Analytics
        </p>
    </div>
    <hr style="margin: 0.75rem 0; border: none; border-top: 1px solid rgba(148, 163, 184, 0.2);" />
    """, unsafe_allow_html=True)

    # Manual page links sequentially under branding
    for p in pages[""]:
        st.page_link(p)

    st.markdown("""<hr style="margin: 0.75rem 0; border: none; border-top: 1px solid rgba(148, 163, 184, 0.2);" />""", unsafe_allow_html=True)

    # Currency selector
    st.session_state.currency = st.selectbox(
        "💱 Currency",
        SUPPORTED_CURRENCIES,
        index=SUPPORTED_CURRENCIES.index(st.session_state.currency),
    )

    # Theme toggle returned to sidebar
    is_dark = st.session_state.theme_mode == "dark"
    theme_text = "☀️ Switch to Light Mode" if is_dark else "🌙 Switch to Dark Mode"
    if st.button(theme_text, use_container_width=True):
        new_mode = "light" if is_dark else "dark"
        st.session_state.theme_mode = new_mode
        
        # Override Streamlit's native theme globally
        import os
        from theme import DARK, LIGHT
        t = DARK if new_mode == "dark" else LIGHT
        
        config_str = f"""[theme]
base = "{new_mode}"
primaryColor = "{t['primary']}"
backgroundColor = "{t['canvas']}"
secondaryBackgroundColor = "{t['card']}"
textColor = "{t['text_primary']}"

[server]
headless = true
"""
        with open(os.path.join(".streamlit", "config.toml"), "w", encoding="utf-8") as f:
            f.write(config_str)
            
        st.rerun()

    # Version footer
    st.markdown(f"""
    <div style="position:fixed; bottom:1rem; font-size:0.65rem; color:#64748B;">
        {APP_NAME} v{APP_VERSION}
    </div>
    """, unsafe_allow_html=True)

# Run the selected page
pg.run()


