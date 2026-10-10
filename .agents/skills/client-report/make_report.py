"""Build a client-facing PDF report (audit findings or applied fixes) for ALLEN with reportlab."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

INK = colors.HexColor("#2a2b2f")
MUTED = colors.HexColor("#515151")
HELP = colors.HexColor("#808988")
ACCENT = colors.HexColor("#c8662a")
BORDER = colors.HexColor("#d1c9bf")
CARD = colors.HexColor("#fffdf8")
SURFACE = colors.HexColor("#f5eee1")

SEVERITIES = {
    "Crítica": ("C", colors.HexColor("#9b2c2c"), colors.HexColor("#f8e6e4")),
    "Alta": ("A", colors.HexColor("#c8662a"), colors.HexColor("#fbebdf")),
    "Media": ("M", colors.HexColor("#9a7416"), colors.HexColor("#fbf3dc")),
    "Baja": ("B", colors.HexColor("#55796f"), colors.HexColor("#e6f0ec")),
}
FIELDS = {
    "audit": (("problem", "Problema"), ("impact", "Impacto"), ("recommendation", "Recomendación")),
    "fixes": (("finding", "Hallazgo"), ("solution", "Solución")),
}
INTERNAL_PATTERNS = (
    (r"\b[\w.-]+/[\w./-]*\.(py|js|mjs|css|html|xml|json|yml|yaml|ps1|spec)\b", "ruta de archivo"),
    (r"\b\w+\.(py|js|mjs|ps1)\b", "nombre de archivo de código"),
    (r"\b[0-9a-f]{7,40}\b", "hash de commit"),
    (r"/api/[\w/{}-]+", "endpoint interno"),
    (r"\b(fix|feat|design|security|android|chore)/[\w.-]+", "nombre de rama"),
    (r"\btest_\w+", "nombre de prueba"),
    (r"\b\w+\(\)", "nombre de función"),
)

MONTHS = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre")


def style(name, **kw) -> ParagraphStyle:
    base = dict(fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, **base)


S = {
    "brand": style("brand", fontName="Helvetica-Bold", fontSize=13, textColor=ACCENT, leading=16, spaceAfter=40),
    "cover_title": style("cover_title", fontName="Times-Bold", fontSize=32, leading=38, spaceAfter=10),
    "cover_sub": style("cover_sub", fontSize=13, leading=18, textColor=MUTED, spaceAfter=36),
    "meta_k": style("meta_k", fontSize=9, textColor=HELP, leading=12),
    "meta_v": style("meta_v", fontName="Helvetica-Bold", fontSize=11.5, leading=15),
    "h1": style("h1", fontName="Times-Bold", fontSize=22, leading=27, spaceBefore=4, spaceAfter=12),
    "h2": style("h2", fontName="Helvetica-Bold", fontSize=13, leading=17, spaceBefore=16, spaceAfter=8),
    "body": style("body", spaceAfter=8),
    "label": style("label", fontName="Helvetica-Bold", fontSize=8.5, textColor=MUTED, leading=11),
    "card_title": style("card_title", fontName="Helvetica-Bold", fontSize=12, leading=16),
    "badge": style("badge", fontName="Helvetica-Bold", fontSize=8.5, leading=11, alignment=TA_CENTER),
    "cell": style("cell", fontSize=10, leading=13),
    "cell_b": style("cell_b", fontName="Helvetica-Bold", fontSize=10, leading=13),
}


def para(text: str, st: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), st)


def long_date(value: str) -> str:
    try:
        d = date.fromisoformat(value)
    except ValueError:
        return value
    return f"{d.day} de {MONTHS[d.month - 1]} de {d.year}"


def find_internal_refs(data: dict) -> list[str]:
    texts = [data.get("title", ""), data.get("summary", "")]
    for item in data["items"]:
        texts += [str(v) for k, v in item.items() if k != "severity"]
    hits = []
    for text in texts:
        for pattern, kind in INTERNAL_PATTERNS:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                hits.append(f"{kind}: «{match.group(0)}»")
    return sorted(set(hits))


def validate(data: dict) -> None:
    kind = data.get("kind", "audit")
    if kind not in FIELDS:
        sys.exit(f"kind debe ser 'audit' o 'fixes', no {kind!r}")
    if not data.get("items"):
        sys.exit("El JSON no tiene items.")
    for n, item in enumerate(data["items"], 1):
        if item.get("severity") not in SEVERITIES:
            sys.exit(f"Item {n}: severity debe ser una de {', '.join(SEVERITIES)}")
        missing = [k for k, _ in FIELDS[kind] if not item.get(k)] + ([] if item.get("title") else ["title"])
        if missing:
            sys.exit(f"Item {n}: faltan campos {', '.join(missing)}")


def cover(data: dict) -> list:
    rows = [("Versión", data.get("version", "-")), ("Fecha", long_date(data.get("date", date.today().isoformat())))]
    if data.get("client"):
        rows.append(("Cliente", data["client"]))
    if data.get("author"):
        rows.append(("Preparado por", data["author"]))
    meta = Table([[para(k.upper(), S["meta_k"]), para(v, S["meta_v"])] for k, v in rows], colWidths=[38 * mm, 120 * mm])
    meta.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    subtitle = "Informe de correcciones" if data.get("kind") == "fixes" else "Informe de auditoría técnica"
    return [
        Spacer(1, 30 * mm),
        para(data.get("product", "ALLEN").upper(), S["brand"]),
        para(data.get("title", subtitle), S["cover_title"]),
        para(subtitle if data.get("title", subtitle).lower() not in subtitle.lower() else "Tutor educativo local, privado y offline", S["cover_sub"]),
        meta,
        PageBreak(),
    ]


def summary(data: dict) -> list:
    out = [para("Resumen ejecutivo", S["h1"])]
    for block in str(data.get("summary", "")).split("\n\n"):
        if block.strip():
            out.append(para(block.strip(), S["body"]))
    counts = {sev: sum(1 for i in data["items"] if i["severity"] == sev) for sev in SEVERITIES}
    header = [para("Severidad", S["cell_b"])] + [para(sev, S["cell_b"]) for sev in SEVERITIES] + [para("Total", S["cell_b"])]
    values = [para("Elementos", S["cell"])] + [para(str(counts[sev]), S["cell_b"]) for sev in SEVERITIES] + [para(str(len(data["items"])), S["cell_b"])]
    table = Table([header, values], colWidths=[34 * mm] + [26 * mm] * 4 + [22 * mm])
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    for col, (_, (_, fg, bg)) in enumerate(SEVERITIES.items(), 1):
        commands += [("BACKGROUND", (col, 1), (col, 1), bg), ("TEXTCOLOR", (col, 1), (col, 1), fg)]
    table.setStyle(TableStyle(commands))
    out += [Spacer(1, 6), table]
    return out


def card(item: dict, code: str, kind: str, width: float) -> list:
    letter, fg, bg = SEVERITIES[item["severity"]]
    badge = Table([[para(item["severity"].upper(), style("b", parent=S["badge"], textColor=fg))]], colWidths=[24 * mm])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg), ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    inner_w = width - 4 * mm - 24  # minus the 12pt side paddings of the card cell
    head = Table([[para(f"{code}  ·  {item['title']}", S["card_title"]), badge]], colWidths=[inner_w - 30 * mm, 30 * mm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    rows = [[head]]
    fields = list(FIELDS[kind]) + ([("status", "Estado")] if kind == "fixes" and item.get("status") else [])
    for key, label in fields:
        rows.append([para(label.upper(), S["label"])])
        rows.append([para(item[key], S["body"])])
    body = Table(rows, colWidths=[inner_w])
    body.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (0, 0), 8),
    ]))
    frame = Table([["", body]], colWidths=[4 * mm, width - 4 * mm])
    frame.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), fg), ("BACKGROUND", (1, 0), (1, 0), CARD),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER), ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ("LEFTPADDING", (1, 0), (1, 0), 12), ("RIGHTPADDING", (1, 0), (1, 0), 12),
        ("TOPPADDING", (1, 0), (1, 0), 12), ("BOTTOMPADDING", (1, 0), (1, 0), 8),
    ]))
    return [frame, Spacer(1, 10)]


def cards(data: dict, width: float) -> list:
    kind = data.get("kind", "audit")
    out = [Spacer(1, 10), para("Correcciones aplicadas" if kind == "fixes" else "Hallazgos", S["h1"])]
    for sev, (letter, _, _) in SEVERITIES.items():
        items = [i for i in data["items"] if i["severity"] == sev]
        if not items:
            continue
        heading = [para(f"Severidad {sev.lower()} ({len(items)})", S["h2"])]
        for n, item in enumerate(items, 1):
            # The first card carries its heading so a heading never ends a page alone.
            out.append(KeepTogether((heading if n == 1 else []) + card(item, f"{letter}-{n:02d}", kind, width)))
    return out


def build(data: dict, output: Path) -> None:
    footer_text = f"{data.get('product', 'ALLEN')} · {data.get('title') or 'Informe'} · versión {data.get('version', '-')}"

    def on_page(canvas, doc):
        if doc.page == 1:
            canvas.saveState()
            canvas.setFillColor(ACCENT)
            canvas.rect(0, A4[1] - 8 * mm, A4[0], 8 * mm, stroke=0, fill=1)
            canvas.restoreState()
            return
        canvas.saveState()
        canvas.setStrokeColor(BORDER)
        canvas.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor(HELP)
        canvas.drawString(20 * mm, 10 * mm, footer_text)
        canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Página {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(output), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm, bottomMargin=22 * mm,
        title=data.get("title", "Informe"), author=data.get("author", data.get("product", "ALLEN")),
    )
    story = cover(data) + summary(data) + cards(data, doc.width)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON con hallazgos o correcciones")
    parser.add_argument("-o", "--output", type=Path, help="PDF de salida (por defecto, junto al JSON)")
    parser.add_argument("--allow-internal", action="store_true", help="no bloquear referencias internas")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    data = json.loads(args.input.read_text(encoding="utf-8"))
    data.setdefault("kind", "audit")
    validate(data)
    hits = find_internal_refs(data)
    if hits and not args.allow_internal:
        print("El informe contiene posibles referencias internas; reescríbelas para el cliente:")
        for hit in hits:
            print("  -", hit)
        return 2
    output = args.output or args.input.with_suffix(".pdf")
    build(data, output)
    print(f"PDF generado: {output.resolve()} ({len(data['items'])} elementos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
