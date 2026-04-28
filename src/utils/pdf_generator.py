"""
PDF Generator for CineStats Detail Views
Generates PDF reports for Movies and TV Series using ReportLab.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import tempfile
import os
from typing import Dict, Any

def generate_movie_pdf(movie: Dict[str, Any]) -> bytes:
    """Generate a PDF report for a movie detail view."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#3B82F6'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1E40AF'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Title
    story.append(Paragraph(movie.get('title_display', 'Unknown Movie'), title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Basic Info
    basic_data = [
        ['Release Date', movie.get('release_date', 'N/A')],
        ['Origin Country', movie.get('origin_country', 'N/A')],
        ['Language', movie.get('language', 'N/A')],
        ['Genre', movie.get('genre', 'N/A')],
        ['Director', movie.get('director', 'N/A')],
        ['Studio', movie.get('studio', 'N/A')],
    ]
    
    story.append(Paragraph('Basic Information', heading_style))
    basic_table = Table(basic_data, colWidths=[2*inch, 4*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(basic_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Financial Data
    financial_data = [
        ['Worldwide Gross', f"${(movie.get('worldwide_gross_usd', 0) or 0) / 1000000:.1f}M"],
        ['Domestic Gross', f"${(movie.get('domestic_gross_usd', 0) or 0) / 1000000:.1f}M"],
        ['Foreign Gross', f"${(movie.get('foreign_gross_usd', 0) or 0) / 1000000:.1f}M"],
        ['India Net', f"₹{movie.get('india_net_cr', 0) or 0} Cr"],
        ['India Gross', f"₹{movie.get('india_gross_cr', 0) or 0} Cr"],
        ['Verdict', movie.get('verdict', 'N/A')],
    ]
    
    story.append(Paragraph('Financial Performance', heading_style))
    financial_table = Table(financial_data, colWidths=[2*inch, 4*inch])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(financial_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Overview
    if movie.get('overview'):
        story.append(Paragraph('Overview', heading_style))
        story.append(Paragraph(movie['overview'], styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.read()

def generate_tv_series_pdf(series: Dict[str, Any]) -> bytes:
    """Generate a PDF report for a TV series detail view."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#8B5CF6'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#6D28D9'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Title
    story.append(Paragraph(series.get('title_display', 'Unknown Series'), title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Basic Info
    basic_data = [
        ['Network', series.get('network', 'N/A')],
        ['Status', series.get('status', 'N/A')],
        ['Premiere Date', series.get('premiere_date', 'N/A')],
        ['Genre', series.get('genre', 'N/A')],
        ['Director', series.get('director', 'N/A')],
        ['Studio', series.get('studio', 'N/A')],
        ['Total Seasons', str(series.get('total_seasons', 0))],
        ['Total Episodes', str(series.get('total_episodes', 0))],
    ]
    
    story.append(Paragraph('Basic Information', heading_style))
    basic_table = Table(basic_data, colWidths=[2*inch, 4*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(basic_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Rating Info
    if series.get('avg_rating'):
        story.append(Paragraph('Rating', heading_style))
        story.append(Paragraph(f"Average Rating: {series['avg_rating']}/10", styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
    
    # Overview
    if series.get('overview'):
        story.append(Paragraph('Overview', heading_style))
        story.append(Paragraph(series['overview'], styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.read()
