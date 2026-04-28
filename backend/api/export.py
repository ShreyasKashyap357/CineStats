from fastapi import APIRouter, HTTPException
from typing import Optional, List
from backend.database import get_db_context
from backend.logger import log_info, log_error
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

router = APIRouter()

@router.post("/pdf")
def export_to_pdf(
    content_type: str,
    ids: List[int],
    title: Optional[str] = None
):
    """Export content to PDF."""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=1
        )
        
        elements = []
        
        # Cover page
        if title:
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 0.5 * inch))
        
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        elements.append(Spacer(1, 1 * inch))
        
        # Fetch data based on content type
        with get_db_context() as db:
            if content_type == "movie":
                placeholders = ",".join(["?"] * len(ids))
                data = db.execute(f"""
                    SELECT title_display, release_date, worldwide_gross_usd, india_net_cr, 
                           verdict, origin_country, genre
                    FROM movies WHERE id IN ({placeholders})
                """, (*ids,)).fetchall()
                
                # Table data
                table_data = [["Title", "Release Date", "Worldwide Gross", "India Net (Cr)", "Verdict", "Country", "Genre"]]
                for row in data:
                    row_dict = dict(row)
                    table_data.append([
                        row_dict.get("title_display", ""),
                        row_dict.get("release_date", ""),
                        f"${row_dict.get('worldwide_gross_usd', 0):,.0f}" if row_dict.get("worldwide_gross_usd") else "N/A",
                        f"{row_dict.get('india_net_cr', 0):.1f}" if row_dict.get("india_net_cr") else "N/A",
                        row_dict.get("verdict", ""),
                        row_dict.get("origin_country", ""),
                        row_dict.get("genre", "")
                    ])
                
            elif content_type == "anime":
                placeholders = ",".join(["?"] * len(ids))
                data = db.execute(f"""
                    SELECT COALESCE(title_english, title_normalized) as title_display, 
                           (season_year || '-' || season) as aired, 
                           COALESCE(anilist_score, mal_score, 0) as score, episodes, genre as genres, studio as studios
                    FROM anime WHERE id IN ({placeholders})
                """, (*ids,)).fetchall()
                
                table_data = [["Title", "Aired", "Score", "Episodes", "Genres", "Studios"]]
                for row in data:
                    row_dict = dict(row)
                    table_data.append([
                        row_dict.get("title_display", ""),
                        row_dict.get("aired", ""),
                        f"{row_dict.get('score', 0):.1f}" if row_dict.get("score") else "N/A",
                        str(row_dict.get("episodes", "")) if row_dict.get("episodes") else "N/A",
                        row_dict.get("genres", ""),
                        row_dict.get("studios", "")
                    ])
                
            elif content_type == "tv":
                placeholders = ",".join(["?"] * len(ids))
                data = db.execute(f"""
                    SELECT title_display, premiere_date, genre, network, status
                    FROM tv_series WHERE id IN ({placeholders})
                """, (*ids,)).fetchall()
                
                table_data = [["Title", "Premiere Date", "Genre", "Network", "Status"]]
                for row in data:
                    row_dict = dict(row)
                    table_data.append([
                        row_dict.get("title_display", ""),
                        row_dict.get("premiere_date", ""),
                        row_dict.get("genre", ""),
                        row_dict.get("network", ""),
                        row_dict.get("status", "")
                    ])
            else:
                raise HTTPException(status_code=400, detail="Invalid content type")
        
        # Create table
        table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        from fastapi.responses import Response
        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={content_type}_export.pdf"}
        )
        
    except Exception as e:
        log_error(f"Failed to export PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))
