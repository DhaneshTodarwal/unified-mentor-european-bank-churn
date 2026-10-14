"""Build a polished PDF version of the research paper from Markdown."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports" / "research_paper.md"
OUTPUT = ROOT / "output" / "pdf" / "European_Banking_Churn_Research_Paper.pdf"


def ascii_text(value: str) -> str:
    """Normalize punctuation that is unreliable in PDF fonts and extraction."""

    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2011": "-",
        "\u00d7": "x",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def inline_markup(value: str) -> str:
    """Convert the small Markdown subset used in the report to Paragraph markup."""

    value = ascii_text(value)
    links: list[str] = []

    def hold_link(match: re.Match[str]) -> str:
        label = html.escape(match.group(1))
        url = html.escape(match.group(2), quote=True)
        links.append(f'<link href="{url}" color="#1f5f8b">{label}</link>')
        return f"@@LINK{len(links) - 1}@@"

    value = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)", hold_link, value)
    value = html.escape(value, quote=False)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    for index, link in enumerate(links):
        value = value.replace(f"@@LINK{index}@@", link)
    return value


def table_flowable(rows: list[list[str]], available_width: float) -> Table:
    columns = max(len(row) for row in rows)
    normalized = [row + [""] * (columns - len(row)) for row in rows]
    cell_style = ParagraphStyle(
        "TableCell",
        parent=getSampleStyleSheet()["BodyText"],
        fontName="Helvetica",
        fontSize=7.2 if columns >= 6 else 7.8,
        leading=9.2 if columns >= 6 else 10,
        spaceAfter=0,
    )
    header_style = ParagraphStyle(
        "TableHeader",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )
    data = []
    for row_index, row in enumerate(normalized):
        style = header_style if row_index == 0 else cell_style
        data.append([Paragraph(inline_markup(cell.strip()), style) for cell in row])

    table = Table(data, colWidths=[available_width / columns] * columns, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#153b5b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#a8b8c5")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f7fafc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f7fa")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def parse_markdown(markdown: str, styles: dict[str, ParagraphStyle], width: float) -> list:
    lines = [ascii_text(line.rstrip()) for line in markdown.splitlines()]
    story: list = []
    index = 0
    paragraph_lines: list[str] = []
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            story.append(Paragraph(inline_markup(" ".join(part.strip() for part in paragraph_lines)), styles["Body"]))
            story.append(Spacer(1, 4))
            paragraph_lines = []

    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            flush_paragraph()
            if not in_code:
                in_code = True
                code_lines = []
            else:
                code_markup = "<br/>".join(inline_markup(code_line) for code_line in code_lines)
                story.append(Paragraph(code_markup, styles["Code"]))
                story.append(Spacer(1, 6))
                in_code = False
            index += 1
            continue
        if in_code:
            code_lines.append(line)
            index += 1
            continue
        if not line.strip():
            flush_paragraph()
            index += 1
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            style_name = {1: "Title", 2: "Heading2", 3: "Heading3"}[level]
            story.append(Paragraph(inline_markup(heading.group(2)), styles[style_name]))
            if level == 1:
                story.append(Spacer(1, 5))
            index += 1
            continue

        if line.startswith("|") and index + 1 < len(lines) and re.match(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$", lines[index + 1]):
            flush_paragraph()
            table_rows: list[list[str]] = []
            while index < len(lines) and lines[index].startswith("|"):
                raw = lines[index].strip().strip("|")
                if not re.match(r"^\s*:?-+:?\s*(\|\s*:?-+:?\s*)*$", raw):
                    table_rows.append([cell.strip() for cell in raw.split("|")])
                index += 1
            if table_rows:
                story.append(table_flowable(table_rows, width))
                story.append(Spacer(1, 8))
            continue

        bullet = re.match(r"^[-*]\s+(.+)$", line)
        if bullet:
            flush_paragraph()
            story.append(Paragraph(f"- {inline_markup(bullet.group(1))}", styles["Bullet"]))
            index += 1
            continue

        numbered = re.match(r"^(\d+)\.\s+(.+)$", line)
        if numbered:
            flush_paragraph()
            story.append(Paragraph(f"{numbered.group(1)}. {inline_markup(numbered.group(2))}", styles["Body"]))
            index += 1
            continue

        paragraph_lines.append(line)
        index += 1

    flush_paragraph()
    return story


def draw_footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d0dbe3"))
    canvas.line(document.leftMargin, 16 * mm, A4[0] - document.rightMargin, 16 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#5d6b75"))
    canvas.drawString(document.leftMargin, 10.5 * mm, "Unified Mentor | Data Analyst Internship")
    canvas.drawRightString(A4[0] - document.rightMargin, 10.5 * mm, f"Page {document.page}")
    canvas.restoreState()


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=25,
            textColor=colors.HexColor("#153b5b"),
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "Heading2": ParagraphStyle(
            "ReportHeading2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13.5,
            leading=17,
            textColor=colors.HexColor("#153b5b"),
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "Heading3": ParagraphStyle(
            "ReportHeading3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#1f5f8b"),
            spaceBefore=7,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "ReportBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=13,
            textColor=colors.HexColor("#1d252c"),
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "Bullet": ParagraphStyle(
            "ReportBullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.5,
            leftIndent=13,
            firstLineIndent=-9,
            textColor=colors.HexColor("#1d252c"),
            spaceAfter=2,
        ),
        "Code": ParagraphStyle(
            "ReportCode",
            fontName="Courier",
            fontSize=7.8,
            leading=10,
            leftIndent=10,
            rightIndent=10,
            backColor=colors.HexColor("#f1f4f6"),
            borderColor=colors.HexColor("#d0dbe3"),
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=5,
        ),
    }

    document = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=17 * mm,
        rightMargin=17 * mm,
        topMargin=16 * mm,
        bottomMargin=22 * mm,
        title="Customer Segmentation & Churn Pattern Analytics in European Banking",
        author="Dhanesh Todarwal",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="normal")
    document.addPageTemplates([PageTemplate(id="report", frames=[frame], onPage=draw_footer)])
    story = parse_markdown(SOURCE.read_text(encoding="utf-8"), styles, document.width)
    document.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()
