"""
CineStats — Centralised Theme & Style Constants
Section 22 of the v1.0 specification.
"""

# ── Dark Mode (Primary) ─────────────────────────────────────────────────────
DARK = {
    "canvas":           "#0F172A",   # deep navy-black
    "card":             "#1E293B",   # card / panel background
    "card_border":      "#334155",   # 1px card border
    "primary":          "#3B82F6",   # blue — CTAs, active nav, links
    "secondary":        "#8B5CF6",   # purple — franchise/series elements
    "success":          "#10B981",   # green — positive trends, hit verdict
    "danger":           "#EF4444",   # red — negative trends, flop verdict
    "warning":          "#F59E0B",   # amber — average verdict, caution
    "text_primary":     "#F1F5F9",   # primary text
    "text_secondary":   "#94A3B8",   # secondary/muted text
    "text_tertiary":    "#64748B",   # tertiary text (labels, dates)
    "divider":          "#334155",   # horizontal rules
    "chart_bg":         "#0F172A",   # plotly chart background
    "chart_grid":       "#1E293B",   # plotly gridlines
}

# ── Light Mode ───────────────────────────────────────────────────────────────
LIGHT = {
    "canvas":           "#FFFFFF",
    "card":             "#F8FAFC",
    "card_border":      "#E2E8F0",
    "primary":          "#2563EB",
    "secondary":        "#7C3AED",
    "success":          "#059669",
    "danger":           "#DC2626",
    "warning":          "#D97706",
    "text_primary":     "#0F172A",
    "text_secondary":   "#475569",
    "text_tertiary":    "#94A3B8",
    "divider":          "#E2E8F0",
    "chart_bg":         "#FFFFFF",
    "chart_grid":       "#F1F5F9",
}

# ── Verdict Colours ──────────────────────────────────────────────────────────
VERDICT_COLORS = {
    "All-Time Blockbuster": "#10B981",
    "Blockbuster":          "#34D399",
    "Super Hit":            "#3B82F6",
    "Hit":                  "#60A5FA",
    "Above Average":        "#8B5CF6",
    "Average":              "#F59E0B",
    "Below Average":        "#F97316",
    "Flop":                 "#EF4444",
    "Disaster":             "#991B1B",
}

# ── Content Type Badge Colours ───────────────────────────────────────────────
CONTENT_TYPE_COLORS = {
    "movie":              "#3B82F6",
    "tv_series":          "#8B5CF6",
    "anime":              "#EC4899",
    "western_animation":  "#F59E0B",
    "cartoon":            "#10B981",
}

# ── Component Specs ──────────────────────────────────────────────────────────
CARD_BORDER_RADIUS = "8px"
CARD_BORDER_WIDTH  = "1px"
STAT_CARD_MIN_WIDTH = "140px"
POSTER_ASPECT_RATIO = "2/3"

# ── Plotly Templates ─────────────────────────────────────────────────────────
def get_plotly_layout(mode: str = "dark") -> dict:
    """Return a Plotly layout dict matching the CineStats theme."""
    t = DARK if mode == "dark" else LIGHT
    return {
        "paper_bgcolor": t["chart_bg"],
        "plot_bgcolor":  t["chart_bg"],
        "font":          {"color": t["text_primary"], "family": "Inter, sans-serif"},
        "xaxis":         {"gridcolor": t["chart_grid"], "zerolinecolor": t["divider"]},
        "yaxis":         {"gridcolor": t["chart_grid"], "zerolinecolor": t["divider"]},
        "colorway":      [t["primary"], t["secondary"], t["success"],
                          t["warning"], t["danger"], "#EC4899", "#14B8A6"],
        "margin":        {"l": 40, "r": 20, "t": 40, "b": 40},
    }


# ── CSS Injection ────────────────────────────────────────────────────────────
def inject_css(mode: str = "dark"):
    """Return CSS string for Streamlit st.markdown injection."""
    t = DARK if mode == "dark" else LIGHT
    return f"""
    <style>
        .cinestats-card {{
            background: {t['card']};
            border: {CARD_BORDER_WIDTH} solid {t['card_border']};
            border-radius: {CARD_BORDER_RADIUS};
            padding: 1rem;
            margin-bottom: 0.75rem;
            color: {t['text_primary']};
        }}
        .cinestats-card:hover {{
            border-color: {t['primary']};
            box-shadow: 0 0 12px {t['primary']}33;
            transition: all 0.2s ease;
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: {t['text_primary']};
        }}
        .stat-label {{
            font-size: 0.75rem;
            color: {t['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .verdict-badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.7rem;
            font-weight: 600;
            color: white;
        }}
        .content-badge {{
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.65rem;
            font-weight: 600;
            color: white;
        }}
        .trend-up {{ color: {t['success']}; }}
        .trend-down {{ color: {t['danger']}; }}
        .poster-fallback {{
            background: {t['card']};
            border: 1px dashed {t['card_border']};
            border-radius: {CARD_BORDER_RADIUS};
            display: flex;
            align-items: center;
            justify-content: center;
            color: {t['text_tertiary']};
            font-size: 0.8rem;
            aspect-ratio: {POSTER_ASPECT_RATIO};
        }}
    </style>
    """
