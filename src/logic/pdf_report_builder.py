"""
CineStats — PDF Report Builder
Generates downloadable PDF reports for movies, TV series, and anime.
Uses ReportLab for PDF generation.
"""
import io
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from constants import APP_NAME, APP_VERSION


# ── Styles ───────────────────────────────────────────────────────────────────
def _get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CineTitle',
        parent=styles['Title'],
        fontSize=20,
        spaceAfter=12,
        textColor=colors.HexColor("#0F172A"),
    ))
    styles.add(ParagraphStyle(
        name='CineH2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        textColor=colors.HexColor("#1E293B"),
    ))
    styles.add(ParagraphStyle(
        name='CineBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.HexColor("#334155"),
    ))
    styles.add(ParagraphStyle(
        name='CineCaption',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor("#64748B"),
    ))
    return styles


# ── Table Helper ─────────────────────────────────────────────────────────────
def _build_table(headers: list, rows: list) -> Table:
    """Build a styled ReportLab Table."""
    data = [headers] + rows
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3B82F6")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return table


# ── Footer ───────────────────────────────────────────────────────────────────
def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(colors.HexColor("#94A3B8"))
    canvas.drawString(1.5 * cm, 1 * cm,
                      f"{APP_NAME} v{APP_VERSION} — Generated {date.today().isoformat()}")
    canvas.drawRightString(A4[0] - 1.5 * cm, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ── Public API ───────────────────────────────────────────────────────────────

def generate_movie_report(movies: list) -> bytes:
    """
    Generate a PDF report for a list of movie dicts.
    Returns PDF as bytes suitable for st.download_button.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=1.5 * cm, bottomMargin=2 * cm,
                            leftMargin=1.5 * cm, rightMargin=1.5 * cm)
    styles = _get_styles()
    story = []

    # Title
    story.append(Paragraph(f"{APP_NAME} — Movie Report", styles['CineTitle']))
    story.append(Paragraph(
        f"Generated: {date.today().isoformat()} | {len(movies)} movie(s)",
        styles['CineCaption']))
    story.append(Spacer(1, 12))

    # Summary
    if movies:
        total_gross = sum(m.get('worldwide_gross_usd', 0) or 0 for m in movies)
        story.append(Paragraph(
            f"Total Worldwide Gross: ${total_gross:,.0f}", styles['CineBody']))
        story.append(Spacer(1, 8))

    # Table
    headers = ['Title', 'Release Date', 'WW Gross ($)', 'India Net (₹Cr)', 'Verdict']
    rows = []
    for m in movies:
        rows.append([
            str(m.get('title_display', '—')),
            str(m.get('release_date', '—')),
            '${:,.0f}'.format(m.get('worldwide_gross_usd', 0) or 0),
            '₹{:.1f} Cr'.format(m.get('india_net_cr', 0) or 0),
            str(m.get('verdict', '—')),
        ])

    if rows:
        story.append(_build_table(headers, rows))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


def generate_tv_report(series_list: list) -> bytes:
    """Generate a PDF report for TV series."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=1.5 * cm, bottomMargin=2 * cm,
                            leftMargin=1.5 * cm, rightMargin=1.5 * cm)
    styles = _get_styles()
    story = []

    story.append(Paragraph(f"{APP_NAME} — TV Series Report", styles['CineTitle']))
    story.append(Paragraph(
        f"Generated: {date.today().isoformat()} | {len(series_list)} series",
        styles['CineCaption']))
    story.append(Spacer(1, 12))

    headers = ['Title', 'Network', 'Seasons', 'Episodes', 'Rating', 'Status']
    rows = []
    for s in series_list:
        rows.append([
            str(s.get('title_display', '—')),
            str(s.get('network', '—')),
            str(s.get('total_seasons', '—')),
            str(s.get('total_episodes', '—')),
            str(s.get('avg_rating', '—')),
            str(s.get('status', '—')),
        ])

    if rows:
        story.append(_build_table(headers, rows))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


def generate_anime_report(anime_list: list) -> bytes:
    """Generate a PDF report for anime."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=1.5 * cm, bottomMargin=2 * cm,
                            leftMargin=1.5 * cm, rightMargin=1.5 * cm)
    styles = _get_styles()
    story = []

    story.append(Paragraph(f"{APP_NAME} — Anime Report", styles['CineTitle']))
    story.append(Paragraph(
        f"Generated: {date.today().isoformat()} | {len(anime_list)} anime",
        styles['CineCaption']))
    story.append(Spacer(1, 12))

    headers = ['Title', 'MAL Score', 'AniList', 'Episodes', 'Studio', 'Demographic']
    rows = []
    for a in anime_list:
        rows.append([
            str(a.get('title_english', '—')),
            str(a.get('mal_score', '—')),
            str(a.get('anilist_score', '—')),
            str(a.get('episodes', '—')),
            str(a.get('studio', '—')),
            str(a.get('demographic', '—')),
        ])

    if rows:
        story.append(_build_table(headers, rows))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
