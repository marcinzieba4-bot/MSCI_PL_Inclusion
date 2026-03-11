"""
PDF Report — Combined MSCI + FTSE Poland Inclusion 2026
========================================================
Four views in one document:
  1. Combined dashboard (all trades, ranked by conviction + forced buying)
  2. MSCI-only trades (MSCI Poland Standard events)
  3. FTSE-only trades (FTSE Developed Europe events)
  4. Dual-index trades (same stock in both — highest priority)
  5. Individual stock cards (full detail)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)

from examples.combined_report_2026 import build_combined_report, CombinedReport, UnifiedTrade
from examples.pdf_helpers import (
    A4, cm,
    PAGE_W, PAGE_H, MARGIN,
    NAVY, BLUE, TEAL, GREEN, RED, AMBER, LGRAY, MGRAY, DGRAY, WHITE, BLACK, CORAL,
    S, ST, make_on_page, make_table as _table, candidate_card,
)

PURPLE = colors.HexColor("#6A1B9A")
CYAN   = colors.HexColor("#00838F")

_on_page = make_on_page(
    "MSCI + FTSE Poland Inclusion 2026  |  Combined Report  |  March 2026  |  [EST] fields require live verification"
)

_TIER_ORDER = {"HIGH": 0, "MEDIUM": 1, "WATCH": 2, "SHORT": 3}
_TIER_ICONS = {"HIGH": "★★ HIGH", "MEDIUM": "★ MEDIUM", "WATCH": "◇ WATCH", "SHORT": "⚠ AVOID"}
_SOURCE_COLOR = {"MSCI": BLUE, "FTSE": PURPLE, "Both": GREEN}


def _source_badge(source: str) -> str:
    """Return coloured XML badge for the source column."""
    if source == "Both":
        return '<font color="#2E7D32"><b>DUAL ★</b></font>'
    if source == "MSCI":
        return '<font color="#1565C0"><b>MSCI</b></font>'
    return '<font color="#6A1B9A"><b>FTSE</b></font>'


# ─────────────────────────────────────────────────────────────────────────────
# 1. Cover — combined summary tiles + full trade table
# ─────────────────────────────────────────────────────────────────────────────
def cover(report: CombinedReport) -> list:
    items = []
    items.append(Spacer(1, 0.4 * cm))
    items.append(HRFlowable(width="100%", thickness=4, color=NAVY, spaceAfter=10))
    items.append(Paragraph(
        "POLAND INDEX INCLUSION 2026 — COMBINED MSCI + FTSE",
        S("t", fontSize=20, leading=26, textColor=NAVY, fontName="Helvetica-Bold", alignment=TA_CENTER)))
    items.append(Paragraph(
        "MSCI Poland Standard (EM) · FTSE Developed Europe · Dual-Index Plays · March 2026",
        S("s", fontSize=10, leading=14, textColor=BLUE, alignment=TA_CENTER)))
    items.append(Paragraph(
        "MSCI: semi-annual reviews (May / Nov)  ·  FTSE: quarterly reviews (Mar / Jun / Sep / Dec)",
        S("m", fontSize=8, textColor=DGRAY, alignment=TA_CENTER)))
    items.append(HRFlowable(width="100%", thickness=1, color=MGRAY, spaceBefore=6, spaceAfter=8))

    d = report.to_json_dict()["summary"]

    # ── Index comparison box ──
    cmp_text = (
        "<b>MSCI Poland Standard (Emerging Market)</b><br/>"
        "Reviews: semi-annual (May + Nov SAR)  ·  AUM tracking: ~$8-10B directly + "
        "~$3B via MSCI EM weight  ·  Forced buying per Standard Add: $200-340M [EST]<br/><br/>"
        "<b>FTSE Developed Europe (Poland is FTSE Developed since Sep 2018)</b><br/>"
        "Reviews: quarterly (Mar/Jun/Sep/Dec QIR)  ·  Poland ≈ 0.15-0.20% of FTSE All-World (~$600B+ AUM)  ·  "
        "Forced buying per Mid Cap Add: $50-120M [EST]<br/><br/>"
        "<font color='#2E7D32'><b>DUAL-INDEX PLAY:</b></font> Same stock appearing in BOTH MSCI and FTSE "
        "events within ~4-6 weeks = sequential forced buying = HIGHEST CONVICTION. "
        "XTB: ~$425M combined [EST]. Kruk: ~$315M combined [EST]."
    )
    cmp_t = Table([[Paragraph(cmp_text, S("cp", fontSize=8, leading=13, textColor=BLACK))]],
                  colWidths=[PAGE_W - 2 * MARGIN])
    cmp_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8F5E9")),
        ("BOX", (0, 0), (-1, -1), 1.5, GREEN),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    items.append(cmp_t)
    items.append(Spacer(1, 0.25 * cm))

    # ── KPI tile row ──
    def tile(label, val, sub, clr):
        return Table([
            [Paragraph(label, S("tl", fontSize=6.5, textColor=DGRAY, fontName="Helvetica-Bold",
                                alignment=TA_CENTER))],
            [Paragraph(str(val), S("tv", fontSize=20, textColor=clr, fontName="Helvetica-Bold",
                                   alignment=TA_CENTER))],
            [Paragraph(sub, S("ts", fontSize=6.5, textColor=DGRAY, alignment=TA_CENTER))],
        ], colWidths=[(PAGE_W - 2 * MARGIN) / 5 - 0.15 * cm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), LGRAY),
                               ("BOX", (0, 0), (-1, -1), 0.5, MGRAY),
                               ("TOPPADDING", (0, 0), (-1, -1), 4),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))

    tiles = Table([[
        tile("TOTAL TRADES", d["total_trades"], "MSCI + FTSE combined", NAVY),
        tile("DUAL-INDEX ★", d["dual_index"], "MSCI + FTSE same stock", GREEN),
        tile("MSCI ONLY", d["msci_only"], "MSCI Poland SAR events", BLUE),
        tile("FTSE ONLY", d["ftse_only"], "FTSE Dev Europe QIR events", PURPLE),
        tile("TOTAL FB $M", f"${d['total_est_forced_buying_usd_m']:.0f}M",
             "Est. combined forced buying", TEAL),
    ]], colWidths=[(PAGE_W - 2 * MARGIN) / 5] * 5)
    tiles.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    items.append(tiles)
    items.append(Spacer(1, 0.2 * cm))

    # ── Combined trade summary table ──
    items.append(Paragraph("All Trades — Ranked by Conviction + Forced Buying", ST["h2"]))
    hdr = ["Source", "Ticker", "Company", "Event", "Review", "Cap USD",
           "12M Ret", "FB $M", "Conviction"]
    rows = [hdr]
    for t in report.all_trades:
        fb_val = t.dual_total_forced_buying_usd_m if t.is_dual_index else t.est_forced_buying_usd_m
        rows.append([
            _source_badge(t.source),
            t.ticker,
            t.company[:28],
            t.event_type[:20],
            t.review_date[:22],
            f"${t.full_cap_usd_b:.2f}B",
            f"{t.return_12m_pct:+.0f}%",
            f"${fb_val:+.0f}M",
            _TIER_ICONS.get(t.conviction, t.conviction),
        ])

    col_r = [0.07, 0.06, 0.18, 0.15, 0.17, 0.08, 0.07, 0.07, 0.15]
    fmt = []
    for i, row in enumerate(rows):
        if i == 0:
            fmt.append([Paragraph(c, ST["cellb"]) for c in row])
        else:
            t = report.all_trades[i - 1]
            st_key = {"HIGH": "cellg", "MEDIUM": "celln", "WATCH": "cella",
                      "SHORT": "cellr"}.get(t.conviction, "cell")
            fmt.append([Paragraph(v, ST[st_key]) for v in row])
    items.append(_table(fmt, col_r))
    items.append(Spacer(1, 0.2 * cm))
    items.append(Paragraph(
        "Source legend: DUAL ★ = stock has both MSCI and FTSE events in 2026 (highest priority). "
        "MSCI = MSCI Poland Standard event only. FTSE = FTSE Developed Europe event only. "
        "FB $M = estimated forced buying (positive = inflows, negative = outflows). [EST] = estimated.",
        ST["small"]))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# 2. Dual-Index Section
# ─────────────────────────────────────────────────────────────────────────────
def dual_index_section(report: CombinedReport) -> list:
    items = []
    items.append(PageBreak())
    items.append(Paragraph("1. Dual-Index Plays — MSCI + FTSE (Highest Priority)", ST["h1"]))
    items.append(Paragraph(
        "These stocks have BOTH an MSCI Poland Standard event AND a FTSE Developed Europe "
        "event expected within ~4-6 weeks of each other in 2026. Sequential passive demand "
        "from two independent index families creates the strongest sustained price pressure.",
        ST["body"]))
    items.append(Spacer(1, 0.2 * cm))

    for t in report.dual_index_trades:
        # Header card
        hdr_text = (
            f"<b>{t.company}  ({t.ticker})</b>  ·  "
            f"<font color='#2E7D32'><b>DUAL-INDEX ★</b></font>  ·  "
            f"MSCI: {t.dual_msci_review}  |  FTSE: {t.dual_ftse_review}"
        )
        hdr_t = Table([[Paragraph(hdr_text, S("dh", fontSize=9, fontName="Helvetica-Bold",
                                               textColor=WHITE))]],
                      colWidths=[PAGE_W - 2 * MARGIN])
        hdr_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GREEN),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        items.append(KeepTogether([hdr_t]))

        # Metrics strip
        metrics = [
            ("Price PLN", f"PLN {t.price_pln:,.2f}"),
            ("Cap USD", f"${t.full_cap_usd_b:.2f}B"),
            ("Float-adj [EST]", f"${t.float_adj_cap_usd_b:.2f}B"),
            ("12M Return", f"{t.return_12m_pct:+.0f}%"),
            ("RS% [EST]", f"{t.rs_percentile:.0f}th"),
            ("200d MA [EST]", "▲ Above" if t.above_200d_ma else "▼ Below"),
            ("MSCI FB [EST]", f"${t.est_forced_buying_usd_m:.0f}M"),
            ("FTSE FB [EST]", f"${t.dual_total_forced_buying_usd_m - t.est_forced_buying_usd_m:.0f}M"),
            ("Combined FB", f"${t.dual_total_forced_buying_usd_m:.0f}M"),
            ("ADV days", f"{t.est_adv_days:.1f}d"),
        ]
        n = len(metrics)
        met_cells = []
        for m_label, m_val in metrics:
            is_combined = m_label == "Combined FB"
            bg = colors.HexColor("#E8F5E9") if is_combined else LGRAY
            val_clr = GREEN if is_combined else (RED if m_val.startswith("-") else
                       (GREEN if "▲" in m_val or (m_val.startswith("$") and "-" not in m_val
                                                   and m_label != "ADV days") else BLACK))
            met_cells.append(Table([
                [Paragraph(m_label, S("ml", fontSize=5.5, textColor=DGRAY,
                                      fontName="Helvetica-Bold", alignment=TA_CENTER))],
                [Paragraph(m_val, S("mv", fontSize=7.5, textColor=val_clr,
                                    fontName="Helvetica-Bold", alignment=TA_CENTER))],
            ], colWidths=[(PAGE_W - 2 * MARGIN) / n],
                style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg),
                                   ("BOX", (0, 0), (-1, -1), 0.3, MGRAY),
                                   ("TOPPADDING", (0, 0), (-1, -1), 2),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 2)])))
        met_t = Table([met_cells], colWidths=[(PAGE_W - 2 * MARGIN) / n] * n)
        met_t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        items.append(met_t)

        # Two-column body
        thesis_txt = t.thesis_summary.replace("\n", "<br/>")
        risks_txt  = "".join(f"• {r}<br/>" for r in t.key_risks[:5])
        check_txt  = "".join(f"{v}<br/>" for v in t.verify_checklist[:6])

        left = Paragraph(
            f"<b>Dual-index thesis:</b><br/>{thesis_txt}",
            S("lb", fontSize=7.5, leading=11))
        right = Table([
            [Paragraph("Key Risks", S("rh", fontSize=9, fontName="Helvetica-Bold",
                                      textColor=RED, spaceAfter=2))],
            [Paragraph(risks_txt, S("rb", fontSize=7.5, leading=11))],
            [Spacer(1, 0.1 * cm)],
            [Paragraph("Verification Checklist", S("vh", fontSize=9, fontName="Helvetica-Bold",
                                                    textColor=BLUE, spaceAfter=2))],
            [Paragraph(check_txt, S("vb", fontSize=7.5, leading=11,
                                    textColor=colors.HexColor("#1A237E")))],
        ], style=TableStyle([("TOPPADDING", (0, 0), (-1, -1), 0),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        body = Table([[left, right]],
                     colWidths=[(PAGE_W - 2 * MARGIN) * 0.52,
                                (PAGE_W - 2 * MARGIN) * 0.48])
        body.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBEFORE", (1, 0), (1, -1), 0.5, MGRAY),
        ]))
        items.append(body)

        # Entry / timeline footer
        entry_txt = (
            f"<b>MSCI Entry:</b> T-45 before {t.dual_msci_review}  ·  "
            f"<b>FTSE Entry:</b> hold through {t.dual_ftse_review} for second wave  ·  "
            f"<b>TP exit:</b> FTSE effective date  ·  "
            f"<b>FP exit (MSCI):</b> if NOT in SAR announcement, sell within 30 min  ·  "
            f"<b>FP exit (FTSE):</b> if NOT in QIR announcement, trim 50% of residual"
        )
        footer_t = Table([[Paragraph(entry_txt, S("ft", fontSize=7.5, leading=11))]],
                         colWidths=[PAGE_W - 2 * MARGIN])
        footer_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8F5E9")),
            ("BOX", (0, 0), (-1, -1), 0.5, GREEN),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        items.append(footer_t)
        items.append(Spacer(1, 0.5 * cm))

    return items


# ─────────────────────────────────────────────────────────────────────────────
# 3. MSCI-only section
# ─────────────────────────────────────────────────────────────────────────────
def msci_section(report: CombinedReport) -> list:
    items = []
    items.append(PageBreak())
    items.append(Paragraph("2. MSCI Poland Standard — Individual Trades", ST["h1"]))
    items.append(Paragraph(
        "MSCI Poland is part of MSCI Emerging Markets. Poland has ~1.1% weight in MSCI EM. "
        "Semi-annual reviews: May SAR (cut-off ~mid-April) and Nov SAR (cut-off ~mid-October). "
        "Standard Add creates the largest passive demand: EM Poland trackers + EM total-return trackers buy.",
        ST["body"]))
    items.append(Spacer(1, 0.2 * cm))

    # Review calendar
    items.append(Paragraph("MSCI 2026 Review Calendar", ST["h2"]))
    cal_rows = [
        ["Review", "Announcement Date", "Effective Date", "T-45 Entry Window", "Key Candidates"],
        ["May 2026 SAR", "~28 April 2026", "~29 May 2026", "~14 March 2026",
         "XTB (dual), Kruk (watch)"],
        ["Nov 2026 SAR", "~27 October 2026", "~27 Nov 2026", "~12 September 2026",
         "Kruk (dual), Diagnostyka (watch)"],
    ]
    fmt_cal = [[Paragraph(c, ST["cellb"] if i == 0 else ST["cell"]) for c in row]
               for i, row in enumerate(cal_rows)]
    items.append(_table(fmt_cal, [0.14, 0.18, 0.16, 0.18, 0.34], header_bg=BLUE))
    items.append(Spacer(1, 0.3 * cm))

    # Individual cards for MSCI-only candidates
    items.append(Paragraph("MSCI-Only Candidates (not in FTSE dual-index)", ST["h2"]))
    for c in sorted(report.msci_candidates,
                    key=lambda x: (_TIER_ORDER.get(x.conviction, 9), -x.full_cap_usd_b)):
        if c.ticker in {"XTB", "KRU"}:  # these are shown in dual section
            continue
        items += candidate_card(c, thesis_label="MSCI Inclusion Analysis",
                                checklist_label="MSCI Verification Checklist")

    # Table summary for dual-relevant MSCI trades
    items.append(Spacer(1, 0.2 * cm))
    items.append(Paragraph("All MSCI Trades Reference Table (including dual-index stocks)", ST["h2"]))
    hdr = ["Ticker", "Company", "Cap USD", "MSCI Status", "12M Ret",
           "FB $M [EST]", "ADV days", "Conviction", "Target SAR"]
    rows = [hdr]
    for c in sorted(report.msci_candidates,
                    key=lambda x: (_TIER_ORDER.get(x.conviction, 9), -x.full_cap_usd_b)):
        is_dual = c.ticker in {"XTB", "KRU", "ACP", "BDX", "MDVP"}
        dual_mark = " ★DUAL" if is_dual else ""
        rows.append([
            c.ticker + dual_mark,
            c.company[:26],
            f"${c.full_cap_usd_b:.2f}B",
            c.current_msci_status,
            f"{c.return_12m_pct:+.0f}%",
            f"${c.est_forced_buying_usd_m:+.0f}M",
            f"{c.est_adv_days:.1f}",
            _TIER_ICONS.get(c.conviction, c.conviction),
            c.target_review,
        ])
    col_r = [0.09, 0.18, 0.08, 0.11, 0.07, 0.09, 0.07, 0.14, 0.10]
    fmt = []
    for i, row in enumerate(rows):
        if i == 0:
            fmt.append([Paragraph(c, ST["cellb"]) for c in row])
        else:
            c_obj = sorted(report.msci_candidates,
                           key=lambda x: (_TIER_ORDER.get(x.conviction, 9),
                                          -x.full_cap_usd_b))[i - 1]
            sk = {"HIGH": "cellg", "MEDIUM": "celln", "WATCH": "cella",
                  "SHORT": "cellr"}.get(c_obj.conviction, "cell")
            fmt.append([Paragraph(v, ST[sk]) for v in row])
    items.append(_table(fmt, col_r))
    items.append(Spacer(1, 0.15 * cm))
    items.append(Paragraph(
        "★DUAL marks stocks that also have a FTSE event in 2026. "
        "FB $M = estimated passive forced buying (negative = forced selling on deletion). "
        "ADV days = estimated absorption time at average daily volume.",
        ST["small"]))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# 4. FTSE-only section
# ─────────────────────────────────────────────────────────────────────────────
def ftse_section(report: CombinedReport) -> list:
    items = []
    items.append(PageBreak())
    items.append(Paragraph("3. FTSE Developed Europe — Individual Trades", ST["h1"]))
    items.append(Paragraph(
        "Poland has been classified as a FTSE Developed Market since September 2018 — "
        "the first former communist country to achieve this status. Polish stocks are in "
        "FTSE Developed Europe (alongside UK, Germany, France). Quarterly QIRs determine "
        "tier promotions (Small Cap → Mid Cap) and weight changes.",
        ST["body"]))
    items.append(Spacer(1, 0.2 * cm))

    # FTSE context box
    ftse_cmp_text = (
        "<b>FTSE vs MSCI — Key Differences for Polish Stocks:</b><br/><br/>"
        "<b>MSCI:</b> Poland = Emerging Market (~1.1% MSCI EM weight). "
        "Standard Add → ~$200-340M forced buying. Semi-annual (May/Nov).<br/>"
        "<b>FTSE:</b> Poland = Developed Market (~0.15-0.20% FTSE All-World weight). "
        "Mid Cap Add → ~$50-120M forced buying. Quarterly (Mar/Jun/Sep/Dec).<br/><br/>"
        "FTSE events are smaller individually but CREATE ADDITIONAL DEMAND on top of MSCI. "
        "For dual-index stocks (XTB, Kruk), the FTSE event extends the buying window "
        "by ~4-6 weeks after the MSCI event, providing a 'second wave' of support."
    )
    ftse_box = Table([[Paragraph(ftse_cmp_text, S("fb", fontSize=8, leading=12, textColor=BLACK))]],
                     colWidths=[PAGE_W - 2 * MARGIN])
    ftse_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EDE7F6")),
        ("BOX", (0, 0), (-1, -1), 1, PURPLE),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    items.append(ftse_box)
    items.append(Spacer(1, 0.25 * cm))

    # FTSE 2026 review calendar
    items.append(Paragraph("FTSE 2026 Quarterly Review Calendar", ST["h2"]))
    cal_rows = [
        ["QIR", "Announcement", "Effective", "Key Candidates"],
        ["Mar 2026 QIR", "~4 Mar 2026", "~20 Mar 2026", "Weight changes only (too soon for new adds)"],
        ["Jun 2026 QIR", "~3 Jun 2026", "~22 Jun 2026",
         "XTB (dual ★), ACP weight inc., BDX weight inc."],
        ["Sep 2026 QIR", "~2 Sep 2026", "~19 Sep 2026",
         "Kruk (dual ★), Diagnostyka weight inc."],
        ["Dec 2026 QIR", "~2 Dec 2026", "~19 Dec 2026",
         "MDVP demotion watch, further weight rebalances"],
    ]
    fmt_cal = []
    for i, row in enumerate(cal_rows):
        if i == 0:
            fmt_cal.append([Paragraph(c, ST["cellb"]) for c in row])
        elif "★" in row[3]:
            fmt_cal.append([Paragraph(c, ST["cellg"]) for c in row])
        else:
            fmt_cal.append([Paragraph(c, ST["cell"]) for c in row])
    items.append(_table(fmt_cal, [0.14, 0.15, 0.14, 0.57], header_bg=PURPLE))
    items.append(Spacer(1, 0.3 * cm))

    # FTSE candidates reference table
    items.append(Paragraph("All FTSE Developed Europe Candidates", ST["h2"]))
    hdr = ["Ticker", "Company", "Cap USD", "Float-adj", "FTSE Tier Now",
           "Target Tier", "FB $M [EST]", "Conviction", "QIR"]
    rows = [hdr]
    for c in sorted(report.ftse_candidates,
                    key=lambda x: (_TIER_ORDER.get(x.conviction, 9), -x.full_cap_usd_b)):
        is_dual = c.ticker in {"XTB", "KRU", "ACP", "BDX", "MDVP"}
        dual_mark = " ★" if is_dual else ""
        rows.append([
            c.ticker + dual_mark,
            c.company[:24],
            f"${c.full_cap_usd_b:.2f}B",
            f"${c.float_adj_cap_usd_b:.2f}B",
            c.current_msci_status,
            getattr(c, "ftse_tier_target", "—"),
            f"${c.est_forced_buying_usd_m:+.0f}M",
            _TIER_ICONS.get(c.conviction, c.conviction),
            c.target_review,
        ])
    col_r = [0.07, 0.16, 0.08, 0.08, 0.14, 0.09, 0.09, 0.12, 0.13]
    fmt = []
    for i, row in enumerate(rows):
        if i == 0:
            fmt.append([Paragraph(c, ST["cellb"]) for c in row])
        else:
            c_obj = sorted(report.ftse_candidates,
                           key=lambda x: (_TIER_ORDER.get(x.conviction, 9),
                                          -x.full_cap_usd_b))[i - 1]
            sk = {"HIGH": "cellg", "MEDIUM": "celln", "WATCH": "cella",
                  "SHORT": "cellr"}.get(c_obj.conviction, "cell")
            fmt.append([Paragraph(v, ST[sk]) for v in row])
    items.append(_table(fmt, col_r, header_bg=PURPLE))
    items.append(Spacer(1, 0.15 * cm))
    items.append(Paragraph(
        "★ marks stocks that also have an MSCI event in 2026 (dual-index play). "
        "FTSE forced buying estimates are lower than MSCI because Poland has smaller weight "
        "in FTSE Developed World vs MSCI EM. Events are additive, not exclusive.",
        ST["small"]))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# 5. Individual stock cards (full detail for top picks)
# ─────────────────────────────────────────────────────────────────────────────
def stock_cards_section(report: CombinedReport) -> list:
    items = []
    items.append(PageBreak())
    items.append(Paragraph("4. Individual Stock Analysis — Full Detail", ST["h1"]))
    items.append(Paragraph(
        "Detailed MSCI-view cards for all candidates. "
        "Dual-index stocks are annotated with their FTSE event details. "
        "Left column: thesis + why 2026. Right column: risks + verification checklist. "
        "Prices verified March 6, 2026. [EST] fields need live verification before trading.",
        ST["body"]))
    items.append(Spacer(1, 0.25 * cm))

    # Annotate dual-index stocks in their thesis
    dual_tickers = {t.ticker: t for t in report.dual_index_trades}
    for c in sorted(report.msci_candidates,
                    key=lambda x: (_TIER_ORDER.get(x.conviction, 9), -x.full_cap_usd_b)):
        if c.ticker in dual_tickers:
            dt = dual_tickers[c.ticker]
            # Add a FTSE annotation banner before the card
            ftse_fb = dt.dual_total_forced_buying_usd_m - dt.est_forced_buying_usd_m
            banner_text = (
                f"<b>DUAL-INDEX ★</b>  This stock also has a FTSE Developed Europe event:  "
                f"FTSE {dt.dual_ftse_review}  ·  FTSE forced buying [EST] ${ftse_fb:.0f}M  ·  "
                f"Combined total [EST] ${dt.dual_total_forced_buying_usd_m:.0f}M"
            )
            banner = Table([[Paragraph(banner_text,
                                       S("db", fontSize=8, fontName="Helvetica-Bold",
                                         textColor=WHITE))]],
                           colWidths=[PAGE_W - 2 * MARGIN])
            banner.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), GREEN),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            items.append(banner)
        items += candidate_card(c, thesis_label="Analysis (MSCI view)",
                                checklist_label="Verification Checklist")
    return items


# ─────────────────────────────────────────────────────────────────────────────
# 6. Trade action table
# ─────────────────────────────────────────────────────────────────────────────
def trade_action_section(report: CombinedReport) -> list:
    items = []
    items.append(PageBreak())
    items.append(Paragraph("5. Trade Action List — All Actionable Trades 2026", ST["h1"]))
    items.append(Paragraph(
        "Consolidated action list for all trades, sorted by priority. "
        "Use this as the primary reference for managing positions. "
        "Entry: T-45 before the relevant review announcement. "
        "TP exit: hold to effective date. FP exit: exit within 30 min of announcement if not confirmed.",
        ST["body"]))
    items.append(Spacer(1, 0.2 * cm))

    hdr = ["Priority", "Source", "Ticker", "Company", "Action",
           "Entry Window", "TP Exit", "FB $M [EST]", "Notes"]
    rows = [hdr]

    _entry = {
        "May 2026 SAR":  "~14 Mar 2026 (T-45)",
        "Nov 2026 SAR":  "~12 Sep 2026 (T-45)",
        "Jun 2026 QIR":  "~3 May 2026 (T-45)",
        "Sep 2026 QIR":  "~2 Aug 2026 (T-45)",
        "Dec 2026 QIR":  "~2 Nov 2026 (T-45)",
    }
    _tp = {
        "May 2026 SAR":  "~29 May 2026",
        "Nov 2026 SAR":  "~27 Nov 2026",
        "Jun 2026 QIR":  "~22 Jun 2026",
        "Sep 2026 QIR":  "~19 Sep 2026",
        "Dec 2026 QIR":  "~19 Dec 2026",
    }

    # Only include HIGH/MEDIUM/SHORT (actionable) — filter out pure WATCH
    actionable = [t for t in report.all_trades if t.conviction in ("HIGH", "MEDIUM", "SHORT")]

    def _trade_sort_key(x):
        fb = x.dual_total_forced_buying_usd_m if x.is_dual_index else x.est_forced_buying_usd_m
        return (_TIER_ORDER.get(x.conviction, 9), -fb)

    priority = 0
    for t in sorted(actionable, key=_trade_sort_key):
        priority += 1
        fb = t.dual_total_forced_buying_usd_m if t.is_dual_index else t.est_forced_buying_usd_m

        # Determine entry / tp from review date
        review_key = None
        for k in _entry:
            if k.replace(" SAR", "").replace(" QIR", "") in t.review_date:
                review_key = k
                break
        if review_key is None:
            # Try parsing from dual review
            for k in _entry:
                if k in (t.dual_msci_review + " SAR" if t.dual_msci_review else ""):
                    review_key = k
                    break
        entry_str = _entry.get(review_key, "See review calendar")
        tp_str = _tp.get(review_key, "Effective date")

        if t.conviction == "SHORT":
            action = "SHORT / AVOID"
            entry_str = "T-45 before deletion SAR"
            tp_str = "Cover at effective date"
        elif t.is_dual_index:
            action = "BUY — hold through FTSE"
            tp_str = _tp.get(t.dual_ftse_review, tp_str) if t.dual_ftse_review else tp_str
        else:
            action = "BUY" if t.conviction in ("HIGH", "MEDIUM") else "AVOID"

        notes = "DUAL: hold for FTSE wave" if t.is_dual_index else (
            "SHORT thesis" if t.conviction == "SHORT" else "")

        rows.append([
            f"#{priority}",
            _source_badge(t.source),
            t.ticker,
            t.company[:22],
            action,
            entry_str,
            tp_str,
            f"${fb:+.0f}M",
            notes,
        ])

    col_r = [0.05, 0.07, 0.06, 0.15, 0.10, 0.15, 0.12, 0.08, 0.16]
    sorted_actionable = sorted(actionable, key=_trade_sort_key)
    fmt = [[Paragraph(c, ST["cellb"]) for c in rows[0]]]
    for i, row in enumerate(rows[1:]):
        trade_obj = sorted_actionable[i]
        sk = {"HIGH": "cellg", "MEDIUM": "celln", "SHORT": "cellr"}.get(trade_obj.conviction, "cell")
        fmt.append([Paragraph(v, ST[sk]) for v in row])
    items.append(_table(fmt, col_r))

    items.append(Spacer(1, 0.3 * cm))
    items.append(HRFlowable(width="100%", thickness=1, color=AMBER, spaceAfter=6))
    items.append(Paragraph(
        "⚠  DISCLAIMER: This report is for research and educational purposes only. "
        "It does not constitute investment advice or a solicitation to buy or sell any security. "
        "All [EST] figures must be independently verified from live market data before trading. "
        "Forced buying estimates assume full-replication passive funds; actual flows vary. "
        "MSCI retains committee discretion for borderline inclusion decisions. "
        "FTSE tier boundaries are approximate and subject to FTSE Russell methodology updates. "
        "PLN/USD rate used: 3.68 (March 6, 2026). Past backtest results do not guarantee future returns.",
        S("disc", fontSize=7.5, leading=11, textColor=AMBER, fontName="Helvetica-Oblique")))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# Main build
# ─────────────────────────────────────────────────────────────────────────────
def build_pdf(output_path: str = "/tmp/poland_combined_inclusion_2026.pdf") -> str:
    report = build_combined_report()
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=1.4 * cm,
        title="Poland Inclusion 2026 — Combined MSCI + FTSE",
        author="MZApp Research",
    )
    story = []
    story += cover(report)
    story += dual_index_section(report)
    story += msci_section(report)
    story += ftse_section(report)
    story += stock_cards_section(report)
    story += trade_action_section(report)
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return output_path


def run():
    print("Building combined MSCI + FTSE report...")
    path = build_pdf()
    print(f"PDF saved → {path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/poland_combined_inclusion_2026.pdf"
    path = build_pdf(out)
    print(f"PDF saved → {path}")
