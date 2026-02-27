"""
PDF export service — generates a professional clinical report.
"""
from __future__ import annotations
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from backend.core.config import get_settings

cfg = get_settings()

# ── colour palette ────────────────────────────────────────────────────────────
TEAL     = colors.HexColor("#0D9488")
DARK     = colors.HexColor("#0F172A")
MUTED    = colors.HexColor("#64748B")
BG_LIGHT = colors.HexColor("#F0FDFA")
RED_FLAG = colors.HexColor("#DC2626")


def build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["title"] = ParagraphStyle(
        "title", fontName="Helvetica-Bold", fontSize=20,
        textColor=DARK, spaceAfter=4, alignment=TA_CENTER,
    )
    styles["subtitle"] = ParagraphStyle(
        "subtitle", fontName="Helvetica", fontSize=11,
        textColor=MUTED, spaceAfter=2, alignment=TA_CENTER,
    )
    styles["section_header"] = ParagraphStyle(
        "section_header", fontName="Helvetica-Bold", fontSize=12,
        textColor=TEAL, spaceBefore=14, spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "body", fontName="Helvetica", fontSize=10,
        textColor=DARK, leading=15, spaceAfter=4,
    )
    styles["red_flag"] = ParagraphStyle(
        "red_flag", fontName="Helvetica-Bold", fontSize=10,
        textColor=RED_FLAG, leading=15, spaceAfter=4,
    )
    styles["disclaimer"] = ParagraphStyle(
        "disclaimer", fontName="Helvetica-Oblique", fontSize=8,
        textColor=MUTED, leading=12, alignment=TA_CENTER,
    )
    return styles


def export_session_pdf(
    session_history: list[dict],
    patient_info: dict | None = None,
) -> bytes:
    """
    Build a PDF from the session history and return raw bytes.
    session_history: list of {role, content, timestamp}
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
    )
    styles = build_styles()
    story = []

    # ── Header ───────────────────────────────────────────────────────────────
    story.append(Paragraph("LlamaTron RS1 Nemesis", styles["title"]))
    story.append(Paragraph("Clinical Decision Support — Session Report", styles["subtitle"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=TEAL))
    story.append(Spacer(1, 0.4*cm))

    # ── Meta table ───────────────────────────────────────────────────────────
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    meta_data = [["Generated", now]]
    if patient_info:
        if patient_info.get("age"):
            meta_data.append(["Patient Age", str(patient_info["age"])])
        if patient_info.get("sex"):
            meta_data.append(["Patient Sex", patient_info["sex"].title()])

    meta_table = Table(meta_data, colWidths=[4*cm, 12*cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR", (1, 0), (1, -1), DARK),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BG_LIGHT, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Conversation turns ────────────────────────────────────────────────────
    for i, turn in enumerate(session_history):
        role = turn.get("role", "")
        content = turn.get("content", "")
        ts = turn.get("timestamp", "")

        if role == "user":
            story.append(Paragraph(f"🧑 Patient / Clinician Query", styles["section_header"]))
            if ts:
                story.append(Paragraph(ts, styles["disclaimer"]))
            story.append(Paragraph(content.replace("\n", "<br/>"), styles["body"]))

        elif role == "assistant":
            story.append(Paragraph(f"🤖 LlamaTron Analysis", styles["section_header"]))
            # Render markdown-style bold headers inside content
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 0.15*cm))
                    continue
                if line.startswith("## "):
                    story.append(Paragraph(line[3:], styles["section_header"]))
                elif "Red Flag" in line or "⚠️" in line:
                    story.append(Paragraph(line, styles["red_flag"]))
                else:
                    story.append(Paragraph(line, styles["body"]))

        story.append(Spacer(1, 0.2*cm))
        if i < len(session_history) - 1:
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#E2E8F0")))
            story.append(Spacer(1, 0.2*cm))

    # ── Disclaimer ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=MUTED))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "⚠️  DISCLAIMER: This document is AI-generated and intended for research "
        "and educational purposes only. It is NOT a substitute for professional "
        "medical advice, diagnosis, or treatment. Always consult a qualified "
        "healthcare provider for clinical decisions.",
        styles["disclaimer"],
    ))

    doc.build(story)
    return buffer.getvalue()
