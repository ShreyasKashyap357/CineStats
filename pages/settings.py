"""CineStats — Settings Page (stub for Phase 15)."""
import streamlit as st
from constants import SUPPORTED_CURRENCIES, DEFAULT_CURRENCY


def render():
    st.markdown("# ⚙️ Settings")

    st.markdown("## Preferences")
    st.info("Full settings (currency, country lens, default content type, theme, expandable sections, PDF defaults, log viewer) will be implemented in Phase 15.")

    st.markdown("### Current Session State")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Currency", st.session_state.get("currency", DEFAULT_CURRENCY))
        st.metric("Theme", st.session_state.get("theme_mode", "dark"))
    with col2:
        st.metric("Page Size", st.session_state.get("page_size", 24))
        st.metric("Session ID", st.session_state.get("session_id", "N/A")[:8] + "...")
