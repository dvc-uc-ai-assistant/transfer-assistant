# backend/pdf_export.py — NEXA PDF export
# Provides one function called from app.py:
# generate_chat_pdf(messages, title) → io.BytesIO
# uses reportlab to build the PDF entirely in memory (no temp files).
# safe for GCP Cloud Run / App Engine read-only filesystems.


import io
import re
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)


# STYLES
def _build_styles():
    base = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ChatTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.HexColor("#111827"),
        spaceAfter=4,
    )

    meta_style = ParagraphStyle(
        "ChatMeta",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        textColor=colors.HexColor("#6b7280"),
        spaceAfter=16,
    )

    user_label_style = ParagraphStyle(
        "UserLabel",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=colors.HexColor("#1a56db"),
        spaceAfter=3,
    )

    user_text_style = ParagraphStyle(
        "UserText",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#1e3a5f"),
        spaceAfter=4,
        leftIndent=12,
    )

    assistant_label_style = ParagraphStyle(
        "AssistantLabel",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=colors.HexColor("#166534"),
        spaceAfter=3,
    )

    assistant_text_style = ParagraphStyle(
        "AssistantText",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#111827"),
        spaceAfter=4,
        leftIndent=12,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=4,
        spaceBefore=8,
        leftIndent=12,
    )

    subheading_style = ParagraphStyle(
        "SubHeading",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=colors.HexColor("#374151"),
        spaceAfter=3,
        spaceBefore=6,
        leftIndent=12,
    )

    bullet_style = ParagraphStyle(
        "BulletItem",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#111827"),
        spaceAfter=2,
        leftIndent=24,
        bulletIndent=12,
    )

    footer_style = ParagraphStyle(
        "Footer",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        textColor=colors.HexColor("#9ca3af"),
    )

    return {
        "title":            title_style,
        "meta":             meta_style,
        "user_label":       user_label_style,
        "user_text":        user_text_style,
        "assistant_label":  assistant_label_style,
        "assistant_text":   assistant_text_style,
        "heading":          heading_style,
        "subheading":       subheading_style,
        "bullet":           bullet_style,
        "footer":           footer_style,
    }


# MARKDOWN HELPERS

def _escape_xml(text: str) -> str:
    """Escape characters that break ReportLab's XML parser."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _apply_inline_markdown(text: str) -> str:
    """Convert **bold** and *italic* to ReportLab XML tags."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    return text


def _is_table_row(line: str) -> bool:
    return line.strip().startswith("|") and line.strip().endswith("|")


def _is_separator_row(line: str) -> bool:
    return _is_table_row(line) and re.match(r'^[\s|:\-]+$', line)


def _parse_table(lines: list[str]) -> list[list[str]]:
    """Parse markdown table lines into a 2D list of cell strings."""
    rows = []
    for line in lines:
        if _is_separator_row(line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        cells = [re.sub(r'\*\*(.+?)\*\*', r'\1', cell) for cell in cells]
        rows.append(cells)
    return rows


def _build_table_flowable(rows: list[list[str]], available_width: float) -> Table:
    """Turn a 2D list into a styled ReportLab Table."""
    if not rows:
        return None

    num_cols = max(len(r) for r in rows)
    padded = [r + [""] * (num_cols - len(r)) for r in rows]

    cell_style = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=8.5,
        textColor=colors.HexColor("#111827"),
        leading=11,
    )
    header_style = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        textColor=colors.HexColor("#111827"),
        leading=11,
    )

    para_rows = []
    for i, row in enumerate(padded):
        style = header_style if i == 0 else cell_style
        para_rows.append([Paragraph(_escape_xml(cell), style) for cell in row])

    col_width = available_width / num_cols

    tbl = Table(para_rows, colWidths=[col_width] * num_cols, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  colors.HexColor("#e8f0fe")),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.HexColor("#1f2937")),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",           (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
        ("VALIGN",         (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 5),
    ]))
    return tbl


def _render_markdown_to_flowables(
    content: str,
    styles: dict,
    is_user: bool,
    available_width: float,
) -> list:
    """
    Convert a markdown string into a list of ReportLab flowables.
    Handles: ## headings, ### subheadings, bullet lists, numbered lists,
             markdown tables, bold/italic inline, and plain paragraphs.
    """
    text_style = styles["user_text"] if is_user else styles["assistant_text"]
    flowables  = []
    lines      = content.split("\n")
    i          = 0

    while i < len(lines):
        line     = lines[i]
        stripped = line.strip()

        # blank line
        if not stripped:
            i += 1
            continue

        # Heading
        if stripped.startswith("## "):
            text = _escape_xml(stripped[3:].strip())
            text = _apply_inline_markdown(text)
            flowables.append(Paragraph(text, styles["heading"]))
            i += 1
            continue

        # Subheading
        if stripped.startswith("### "):
            text = _escape_xml(stripped[4:].strip())
            text = _apply_inline_markdown(text)
            flowables.append(Paragraph(text, styles["subheading"]))
            i += 1
            continue

        # markdown table
        if _is_table_row(stripped):
            table_lines = []
            while i < len(lines) and _is_table_row(lines[i].strip()):
                table_lines.append(lines[i])
                i += 1
            rows = _parse_table(table_lines)
            if rows:
                tbl = _build_table_flowable(rows, available_width - 24)
                if tbl:
                    flowables.append(Spacer(1, 4))
                    flowables.append(tbl)
                    flowables.append(Spacer(1, 6))
            continue

        # bullet point
        if re.match(r'^[-*•]\s+', stripped):
            text = re.sub(r'^[-*•]\s+', '', stripped)
            text = _escape_xml(text)
            text = _apply_inline_markdown(text)
            flowables.append(Paragraph(f"• {text}", styles["bullet"]))
            i += 1
            continue

        # numbered list
        if re.match(r'^\d+\.\s+', stripped):
            text = re.sub(r'^\d+\.\s+', '', stripped)
            num  = re.match(r'^(\d+)\.', stripped).group(1)
            text = _escape_xml(text)
            text = _apply_inline_markdown(text)
            flowables.append(Paragraph(f"{num}. {text}", styles["bullet"]))
            i += 1
            continue

        # plain paragraph
        text = _escape_xml(stripped)
        text = _apply_inline_markdown(text)
        flowables.append(Paragraph(text, text_style))
        i += 1

    return flowables


# MAIN EXPORT FUNCTION

def generate_chat_pdf(
    messages: list[dict],
    title: str = "Chat Conversation",
) -> io.BytesIO:
    """
    Builds a PDF from a list of chat messages entirely in memory.

    Parameters:
        messages — list of {"role": "user"|"assistant", "content": "..."}
        title    — heading shown at the top of the PDF

    Returns:
        io.BytesIO buffer — ready to pass directly to Flask's send_file()
    """

    buffer = io.BytesIO()

    left_margin     = 0.85 * inch
    right_margin    = 0.85 * inch
    page_width      = letter[0]
    available_width = page_width - left_margin - right_margin

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=right_margin,
        leftMargin=left_margin,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
    )

    styles = _build_styles()
    story  = []

    # header
    story.append(Paragraph(_escape_xml(title), styles["title"]))
    story.append(Paragraph(
        f"Downloaded: {datetime.datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}",
        styles["meta"]
    ))
    story.append(HRFlowable(
        width="100%", thickness=1,
        color=colors.HexColor("#e5e7eb"),
        spaceAfter=14,
    ))

    # messages
    for msg in messages:
        role    = msg.get("role", "unknown")
        content = msg.get("content", "").strip()

        if role == "user":
            story.append(Paragraph("You:", styles["user_label"]))
            story.extend(_render_markdown_to_flowables(
                content, styles, is_user=True, available_width=available_width
            ))
        else:
            story.append(Paragraph("NEXA:", styles["assistant_label"]))
            story.extend(_render_markdown_to_flowables(
                content, styles, is_user=False, available_width=available_width
            ))

        story.append(Spacer(1, 6))
        story.append(HRFlowable(
            width="100%", thickness=0.5,
            color=colors.HexColor("#e5e7eb"),
            spaceAfter=8,
        ))

    # footer
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Generated by NEXA — for reference purposes only.",
        styles["footer"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer