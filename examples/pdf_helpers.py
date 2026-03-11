"""
Shared PDF helpers for MSCI Poland report generators.
Imported by generate_2026_pdf.py and generate_march_2026_pdf.py.
"""

from reportlab.lib.pagesizes import A4  # re-exported for importers
from reportlab.lib.units import cm      # re-exported for importers
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, KeepTogether,
)

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm

NAVY  = colors.HexColor("#0D1B2A")
BLUE  = colors.HexColor("#1565C0")
TEAL  = colors.HexColor("#00796B")
GREEN = colors.HexColor("#2E7D32")
RED   = colors.HexColor("#C62828")
AMBER = colors.HexColor("#E65100")
LGRAY = colors.HexColor("#F5F5F5")
MGRAY = colors.HexColor("#E0E0E0")
DGRAY = colors.HexColor("#757575")
WHITE = colors.white
BLACK = colors.black
CORAL = colors.HexColor("#BF360C")


def S(name, **kw):
    d = dict(fontSize=8.5, leading=12, fontName="Helvetica", textColor=BLACK, spaceAfter=3)
    d.update(kw)
    return ParagraphStyle(name, **d)


ST = {
    "h1":    S("h1", fontSize=15, leading=20, textColor=NAVY, fontName="Helvetica-Bold",
                spaceBefore=12, spaceAfter=6),
    "h2":    S("h2", fontSize=11, leading=14, textColor=BLUE, fontName="Helvetica-Bold",
                spaceBefore=8, spaceAfter=4),
    "h3":    S("h3", fontSize=9.5, leading=13, textColor=TEAL, fontName="Helvetica-Bold",
                spaceBefore=5, spaceAfter=3),
    "body":  S("body"),
    "small": S("small", fontSize=7.5, leading=11, textColor=DGRAY),
    "warn":  S("warn", fontSize=8, leading=12, textColor=CORAL, fontName="Helvetica-Bold"),
    "corr":  S("corr", fontSize=8, leading=12, textColor=GREEN, fontName="Helvetica-Bold"),
    "cell":  S("cell", fontSize=7.5, leading=10),
    "cellb": S("cellb", fontSize=7.5, leading=10, fontName="Helvetica-Bold"),
    "cellg": S("cellg", fontSize=7.5, leading=10, textColor=GREEN, fontName="Helvetica-Bold"),
    "cellr": S("cellr", fontSize=7.5, leading=10, textColor=RED, fontName="Helvetica-Bold"),
    "cella": S("cella", fontSize=7.5, leading=10, textColor=AMBER, fontName="Helvetica-Bold"),
    "celld": S("celld", fontSize=7.5, leading=10, textColor=DGRAY, fontName="Helvetica-Oblique"),
    "celln": S("celln", fontSize=7.5, leading=10, textColor=NAVY, fontName="Helvetica-Bold"),
}


def make_on_page(footer_left: str):
    """Return a page-callback that renders footer_left text on every page."""
    def _on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(DGRAY)
        canvas.drawString(MARGIN, 0.7*cm, footer_left)
        canvas.drawRightString(PAGE_W - MARGIN, 0.7*cm, f"Page {doc.page}")
        canvas.restoreState()
    return _on_page


def make_table(rows, col_ratios, header_bg=None, row_colors=None):
    """Build a styled reportlab Table from rows and fractional column widths."""
    if header_bg is None:
        header_bg = NAVY
    col_w = [(PAGE_W - 2*MARGIN) * r for r in col_ratios]
    row_colors = row_colors or [WHITE, LGRAY]
    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), row_colors),
        ("GRID",  (0, 0), (-1, -1), 0.3, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  7.5),
    ]))
    return t


def candidate_card(c, thesis_label="Why this stock gets included",
                   checklist_label="Verify Before Entry") -> list:
    """
    Render one candidate as a card: header bar, metrics strip, two-column body, footer.
    thesis_label / checklist_label let callers customise column headings.
    """
    items = []
    icon = {
        "HIGH":   "★★ TOP PICK",
        "MEDIUM": "★ MEDIUM CONVICTION",
        "WATCH":  "◇ WATCH",
        "SHORT":  "⚠ SHORT / AVOID",
    }.get(c.conviction, c.conviction)

    hdr = Table([[
        Paragraph(f"{c.company}  ({c.ticker})  [{c.current_msci_status}]",
                  S("h", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE)),
        Paragraph(f"{icon}  ·  {c.target_review}  ·  {c.event_type}",
                  S("h2", fontSize=8, textColor=colors.HexColor("#B0BEC5"), alignment=TA_RIGHT)),
    ]], colWidths=[(PAGE_W-2*MARGIN)*0.55, (PAGE_W-2*MARGIN)*0.45])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    items.append(KeepTogether([hdr]))

    # Metrics strip
    pct_vs = f"{c.pct_vs_threshold:+.0f}%"
    metrics = [
        ("Price PLN",       f"PLN {c.price_pln:,.2f}"),
        ("Cap PLN",         f"PLN {c.full_cap_pln_b:.2f}B"),
        ("Cap USD",         f"${c.full_cap_usd_b:.2f}B"),
        ("vs threshold",    pct_vs),
        ("Float-adj [EST]", f"${c.float_adj_cap_usd_b:.2f}B"),
        ("ATVR [EST]",      f"{c.atvr_3m_pct:.0f}%"),
        ("RS% [EST]",       f"{c.rs_percentile:.0f}th"),
        ("200d MA [EST]",   "▲ Above" if c.above_200d_ma else "▼ Below"),
        ("12M return",      f"{c.return_12m_pct:+.0f}%"),
        ("Momentum",        "✓ PASS" if c.momentum_passes_filter else "✗ SKIP"),
    ]
    n = len(metrics)
    met_cells = []
    for m_label, m_val in metrics:
        is_neg = m_val.startswith("-") or "SKIP" in m_val or "▼" in m_val or "SELL" in m_val
        is_pos = "✓" in m_val or "▲" in m_val or (m_label == "vs threshold" and "+" in pct_vs)
        val_color = RED if is_neg else (GREEN if is_pos else
                    (AMBER if m_label == "vs threshold" and "-" in m_val else BLACK))
        met_cells.append(Table([
            [Paragraph(m_label, S("ml", fontSize=6, textColor=DGRAY,
                                  fontName="Helvetica-Bold", alignment=TA_CENTER))],
            [Paragraph(m_val,   S("mv", fontSize=8, textColor=val_color,
                                  fontName="Helvetica-Bold", alignment=TA_CENTER))],
        ], colWidths=[(PAGE_W-2*MARGIN)/n],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LGRAY),
            ("BOX",        (0, 0), (-1, -1), 0.3, MGRAY),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])))
    met_t = Table([met_cells], colWidths=[(PAGE_W-2*MARGIN)/n]*n)
    met_t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    items.append(met_t)

    # Two-column body
    thesis_text = c.inclusion_thesis.replace("\n", "<br/>")
    why_text    = c.why_now_in_2026.replace("\n", "<br/>")
    risks_text  = "".join(f"• {r}<br/>" for r in c.key_risks)
    check_text  = "".join(f"{v}<br/>" for v in c.verify_checklist)

    left = Paragraph(
        f"<b>{thesis_label}:</b><br/>{thesis_text}<br/><br/>"
        f"<b>Why 2026 specifically:</b><br/>{why_text}",
        S("lb", fontSize=7.8, leading=11))

    right_content = [
        Paragraph("Key Risks", S("rh", fontSize=9, fontName="Helvetica-Bold",
                                  textColor=RED, spaceAfter=2)),
        Paragraph(risks_text, S("rb", fontSize=7.5, leading=11)),
        Spacer(1, 0.1*cm),
        Paragraph(checklist_label, S("vh", fontSize=9, fontName="Helvetica-Bold",
                                      textColor=BLUE, spaceAfter=2)),
        Paragraph(check_text, S("vb", fontSize=7.5, leading=11,
                                 textColor=colors.HexColor("#1A237E"))),
    ]
    right = Table([[item] for item in right_content],
                  style=TableStyle([
                      ("TOPPADDING",    (0, 0), (-1, -1), 0),
                      ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                  ]))

    body = Table([[left, right]],
                 colWidths=[(PAGE_W-2*MARGIN)*0.52, (PAGE_W-2*MARGIN)*0.48])
    body.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5), ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBEFORE",    (1, 0), (1, -1),  0.5, MGRAY),
    ]))
    items.append(body)

    # Entry/exit footer
    is_deletion = c.conviction == "SHORT" or c.event_type == "Deletion Risk"
    if not is_deletion:
        entry_text = (
            f"<b>Entry signal:</b> T−45 before {c.target_review} SAR  |  "
            f"<b>Verified price:</b> PLN {c.price_pln:,.0f}  |  "
            f"<b>TP exit:</b> effective date  |  "
            f"<b>FP exit:</b> if NOT in SAR announcement, sell within 30 min  |  "
            f"<b>Historical base rate (Standard Add, 2018-2025):</b> avg +14.3% "
            f"announcement-to-effective"
        )
        bg, border = colors.HexColor("#E3F2FD"), BLUE
    else:
        entry_text = (
            f"<b>Status:</b> {c.event_type}  |  "
            f"<b>Action:</b> Avoid in Standard-tracking strategies  |  "
            f"<b>Post-deletion reversal:</b> stocks typically recover +5-10% in 30 days "
            f"after forced selling completes"
        )
        bg, border = colors.HexColor("#FFEBEE"), RED

    footer = Table([[Paragraph(entry_text, S("ft", fontSize=7.5, leading=11))]],
                   colWidths=[PAGE_W-2*MARGIN])
    footer.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("BOX",           (0, 0), (-1, -1), 0.5, border),
        ("TOPPADDING",    (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8), ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    items.append(footer)
    items.append(Spacer(1, 0.5*cm))
    return items
