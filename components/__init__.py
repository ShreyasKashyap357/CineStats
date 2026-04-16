"""
CineStats — Reusable UI Components
Shared rendering functions used across multiple pages.
"""
import streamlit as st
import pandas as pd
from theme import VERDICT_COLORS, CONTENT_TYPE_COLORS, DARK, LIGHT


# ── Stat Card ────────────────────────────────────────────────────────────────
def stat_card(label: str, value, prefix: str = "", suffix: str = ""):
    """Render a compact stat metric inside a styled card."""
    display_val = f"{prefix}{value}{suffix}" if value is not None else "—"
    st.markdown(f"""
    <div class="cinestats-card" style="text-align:center; padding:0.75rem;">
        <div class="stat-label">{label}</div>
        <div class="stat-value">{display_val}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Verdict Badge ────────────────────────────────────────────────────────────
def verdict_badge(verdict: str) -> str:
    """Return an HTML span for a verdict badge."""
    if not verdict:
        return ""
    color = VERDICT_COLORS.get(verdict, "#64748B")
    return f'<span class="verdict-badge" style="background:{color};">{verdict}</span>'


# ── Content Type Badge ───────────────────────────────────────────────────────
def content_type_badge(ctype: str, label: str = None) -> str:
    """Return HTML for a content-type pill badge."""
    color = CONTENT_TYPE_COLORS.get(ctype, "#64748B")
    display = label or ctype.replace("_", " ").title()
    return f'<span class="content-badge" style="background:{color};">{display}</span>'


# ── Movie Card ───────────────────────────────────────────────────────────────
def movie_card(title: str, gross_usd=None, india_net_cr=None,
               verdict: str = "", poster_url: str = None, tmdb_id=None):
    """Render a single movie card with poster fallback."""
    import math
    poster_html = ""
    if poster_url and isinstance(poster_url, str) and poster_url.startswith("http"):
        poster_html = f'<img src="{poster_url}" style="width:100%; border-radius:6px 6px 0 0; aspect-ratio:2/3; object-fit:cover;" />'
    else:
        poster_html = '<div class="poster-fallback" style="height:300px; display:flex; align-items:center; justify-content:center; background:#1e293b; color:#64748b; border-radius:6px 6px 0 0;">No Poster</div>'

    gross_str = ""
    if gross_usd and not (isinstance(gross_usd, float) and math.isnan(gross_usd)):
        gross_str = '${:,.0f} WW'.format(gross_usd)
        # Convert to INR too based on ~83 conversion rate roughly just to satisfy user, or just show USD
        inr_val = gross_usd * 83.0 / 10000000 
        gross_str += f" (₹{inr_val:.1f} Cr)"
    else:
        gross_str = "N/A"

    india_str = ""
    if india_net_cr and not (isinstance(india_net_cr, float) and math.isnan(india_net_cr)):
        india_str = f" · ₹{india_net_cr:.1f} Cr"

    verdict_html = verdict_badge(verdict) if verdict and isinstance(verdict, str) and verdict.lower() != 'nan' else ""

    html = f"""
    <div class="cinestats-card" style="padding:0; overflow:hidden;">
        {poster_html}
        <div style="padding:0.6rem;">
            <h4 style="margin:0 0 0.25rem 0; font-size:1rem;">{title}</h4>
            <p style="margin:0 0 0.5rem 0; font-size:0.8rem; color:#94A3B8;">{gross_str}{india_str}</p>
            {verdict_html}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ── Paginated Table ──────────────────────────────────────────────────────────
def paginated_dataframe(df: pd.DataFrame, key: str, page_size: int = None):
    """Render a formatted DataFrame with Previous / Next pagination controls."""
    if df.empty:
        st.info("No data to display.")
        return

    # Create a nice display copy
    display_df = df.copy()
    
    # Format common numeric/currency columns
    numeric_cols = [c for c in display_df.columns if "usd" in c.lower() or "cr" in c.lower() or "gross" in c.lower()]
    for col in numeric_cols:
        if pd.api.types.is_numeric_dtype(display_df[col]):
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
            
    # Clean up column names for display
    display_df.columns = [c.replace("_usd", "").replace("_cr", "").replace("_", " ").title() for c in display_df.columns]
    
    # Fill Nones/NaNs
    display_df = display_df.fillna("—")

    if page_size is None:
        page_size = st.session_state.get("page_size", 24)

    total = len(display_df)
    total_pages = max(1, (total + page_size - 1) // page_size)

    page_key = f"page_{key}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    current_page = st.session_state[page_key]
    start = current_page * page_size
    end = min(start + page_size, total)

    st.dataframe(display_df.iloc[start:end], use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅ Previous", key=f"prev_{key}", disabled=(current_page == 0)):
            st.session_state[page_key] -= 1
            st.rerun()
    with col2:
        st.caption(f"Page {current_page + 1} of {total_pages} ({total} rows)")
    with col3:
        if st.button("Next ➡", key=f"next_{key}", disabled=(current_page >= total_pages - 1)):
            st.session_state[page_key] += 1
            st.rerun()


# ── Empty State ──────────────────────────────────────────────────────────────
def empty_state(message: str, icon: str = "📭"):
    """Render a styled empty-state placeholder."""
    st.markdown(f"""
    <div style="text-align:center; padding:3rem 1rem; color:#64748B;">
        <div style="font-size:3rem;">{icon}</div>
        <p style="margin-top:0.5rem;">{message}</p>
    </div>
    """, unsafe_allow_html=True)


# ── CSV Download Button ─────────────────────────────────────────────────────
def csv_download(df: pd.DataFrame, filename: str = "cinestats_export.csv", label: str = "📥 Export CSV"):
    """Render a CSV download button for a DataFrame."""
    if df.empty:
        return
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(label, csv_data, file_name=filename, mime="text/csv")


# ── Section Header ───────────────────────────────────────────────────────────
def section_header(text: str, anchor: str = None):
    """Render an h2 with an optional anchor id."""
    aid = anchor or text.lower().replace(" ", "-").replace("'", "")
    st.markdown(f'<h2 id="{aid}">{text}</h2>', unsafe_allow_html=True)


# ── Table Has Data ───────────────────────────────────────────────────────────
def table_has_data(conn, table: str) -> bool:
    """Check if a table has any rows."""
    try:
        row = conn.execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone()
        return row is not None
    except Exception:
        return False


# ── Format Currency ──────────────────────────────────────────────────────────
def fmt_currency(value, currency: str = "USD") -> str:
    """Format a number as currency string."""
    from constants import CURRENCY_SYMBOLS
    if value is None:
        return "—"
    sym = CURRENCY_SYMBOLS.get(currency, "$")
    if abs(value) >= 1_000_000_000:
        return f"{sym}{value / 1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"{sym}{value / 1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"{sym}{value / 1_000:.1f}K"
    return f"{sym}{value:,.0f}"
