"""
CineStats — Error Boundary
Wraps page render functions to catch unexpected errors gracefully.
"""
import streamlit as st
import traceback
from functools import wraps


def error_boundary(func):
    """Decorator that wraps a page render() in a try-except,
    showing a friendly error message instead of crashing the app."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error("⚠️ Something went wrong loading this page.")
            with st.expander("🔍 Error Details", expanded=False):
                st.code(traceback.format_exc(), language="python")
            st.info("Try refreshing the page. If the issue persists, check Settings → Activity Log.")
    return wrapper
