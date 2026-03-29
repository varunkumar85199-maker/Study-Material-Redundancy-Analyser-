"""
note_generator.py
=================
Merged topics se PDF ya TXT notes generate karta hai.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle
)
from datetime import datetime


class NoteGenerator:

    def generate(self, topics: list[dict], outpath: str, fmt: str = "pdf"):
        """PDF ya TXT file generate karne ka main function."""
        if fmt == "pdf":
            self._to_pdf(topics, outpath)
        else:
            self._to_txt(topics, outpath)

    # ───────────────────────────────────────────────────────────────
    # 1. PDF Notes Generator
    # ───────────────────────────────────────────────────────────────
    def _to_pdf(self, topics: list[dict], outpath: str):

        doc = SimpleDocTemplate(
            outpath,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()

        # Title Styles
        title_style = ParagraphStyle(
            "TitleMain",
            parent=styles["Title"],
            fontSize=22,
            textColor=colors.HexColor("#5349C8"),
            spaceAfter=6,
        )

        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=20,
        )

        heading_style = ParagraphStyle(
            "HeadingTopic",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.HexColor("#3C3489"),
            spaceBefore=14,
            spaceAfter=4,
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=16,
            spaceAfter=8,
        )

        source_style = ParagraphStyle(
            "Source",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
            spaceAfter=4,
        )

        story = []

        # ── Cover Page ──
        story.append(Paragraph("StudySync — Merged Study Notes", title_style))

        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%d %b %Y, %I:%M %p')} "
            f"&nbsp;|&nbsp; Total topics: {len(topics)}",
            subtitle_style
        ))

        story.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#AFA9EC")))

        story.append(Spacer(1, 0.4 * cm))

        # ── Summary Table ──
        table_data = [["#", "Topic", "Sources", "Overlap %"]]

        for i, t in enumerate(topics, 1):
            table_data.append([
                str(i),
                t["topic"],
                ", ".join(s.replace(".pdf", "").replace(".docx", "")
                          for s in t["sources"]),
                f"{t.get('overlap', 0)}%",
            ])

        table = Table(table_data, colWidths=[1 * cm, 6 * cm, 7 * cm, 2 * cm])

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEDFE")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#3C3489")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#F8F8FC")]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D3D1C7")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.6 * cm))

        # ── Individual Topics ──
        for i, t in enumerate(topics, 1):
            story.append(HRFlowable(
                width="100%", thickness=0.5,
                color=colors.HexColor("#D3D1C7")
            ))

            story.append(Paragraph(f"{i}. {t['topic']}", heading_style))

            story.append(Paragraph(
                "Sources: " + " | ".join(t["sources"]),
                source_style
            ))

            story.append(Paragraph(t["merged_text"], body_style))

        doc.build(story)
        print(f"[PDF SAVED] → {outpath}")

    # ───────────────────────────────────────────────────────────────
    # 2. TXT Notes Generator
    # ───────────────────────────────────────────────────────────────
    def _to_txt(self, topics: list[dict], outpath: str):

        lines = [
            "=" * 60,
            "  STUDYSYNC — MERGED STUDY NOTES",
            f"  Generated: {datetime.now().strftime('%d %b %Y')}",
            f"  Total Topics: {len(topics)}",
            "=" * 60,
            "",
        ]

        for i, t in enumerate(topics, 1):
            lines.append(f"{i}. {t['topic'].upper()}")
            lines.append(f"   Sources: {', '.join(t['sources'])}")
            lines.append(f"   Overlap: {t.get('overlap', 0)}%")
            lines.append("")
            lines.append(t["merged_text"])
            lines.append("")
            lines.append("-" * 60)
            lines.append("")

        with open(outpath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"[TXT SAVED] → {outpath}")
