"""
PDF Report — Combined MSCI + FTSE Poland Inclusion Backtest 2018-2026
=====================================================================
Sections:
  1. Cover — summary stats tiles
  2. Performance by index family (MSCI / FTSE / Combined)
  3. Momentum filter sensitivity sweep
  4. Dual-index pair analysis
  5. Full event detail table
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)

from examples.backtest_combined_2026 import (
    build_combined_backtest, CombinedBacktestResult,
    run_backtest,
)
from examples.pdf_helpers import (
    A4, cm,
    PAGE_W, PAGE_H, MARGIN,
    NAVY, BLUE, TEAL, GREEN, RED, AMBER, LGRAY, MGRAY, DGRAY, WHITE, BLACK, CORAL,
    S, ST, make_on_page,
)


def _tbl(rows, colWidths):
    """Thin wrapper: build a Table with given colWidths."""
    return Table(rows, colWidths=colWidths)

PURPLE = colors.HexColor("#6A1B9A")

_on_page = make_on_page(
    "MSCI + FTSE Poland Inclusion Backtest  |  2018–2026  |  Entry T−45 · Exit Effective Date"
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def _P(txt, style="body", **kw):
    return Paragraph(txt, S(style, **kw) if kw else ST.get(style, ST["body"]))


def _ret_color(pct):
    if pct is None:
        return DGRAY
    if pct >= 10:
        return GREEN
    if pct >= 5:
        return TEAL
    if pct < 0:
        return RED
    return BLACK


# ─────────────────────────────────────────────────────────────────────────────
# 1. Cover
# ─────────────────────────────────────────────────────────────────────────────

def _cover(result: CombinedBacktestResult) -> list:
    items = []
    items.append(Spacer(1, 0.4 * cm))
    items.append(HRFlowable(width="100%", thickness=4, color=NAVY, spaceAfter=10))
    items.append(_P(
        "POLAND INDEX INCLUSION — COMBINED BACKTEST",
        fontSize=20, leading=26, textColor=NAVY, fontName="Helvetica-Bold", alignment=TA_CENTER))
    items.append(_P(
        "MSCI Poland Standard (EM) + FTSE Developed Europe  ·  2018 – 2026",
        fontSize=11, leading=14, textColor=BLUE, alignment=TA_CENTER))
    items.append(_P(
        "Entry: T−45 (45 calendar days before effective date)  ·  Exit: Effective Date",
        fontSize=8, textColor=DGRAY, alignment=TA_CENTER))
    items.append(HRFlowable(width="100%", thickness=1, color=MGRAY, spaceBefore=6, spaceAfter=10))

    br = result.base_result
    mf = br.momentum_filtered

    # Summary stat tiles (single wide table)
    tile_data = [
        [
            _P(f"<b>{br.n_total_events}</b>", fontSize=22, leading=26, textColor=NAVY,
               fontName="Helvetica-Bold", alignment=TA_CENTER),
            _P(f"<b>{result.n_msci_events}</b>", fontSize=22, leading=26, textColor=BLUE,
               fontName="Helvetica-Bold", alignment=TA_CENTER),
            _P(f"<b>{result.n_ftse_events}</b>", fontSize=22, leading=26, textColor=PURPLE,
               fontName="Helvetica-Bold", alignment=TA_CENTER),
            _P(f"<b>{result.n_dual_pairs}</b>", fontSize=22, leading=26, textColor=GREEN,
               fontName="Helvetica-Bold", alignment=TA_CENTER),
            _P(f"<b>{mf.sharpe_ratio:.2f}</b>", fontSize=22, leading=26, textColor=TEAL,
               fontName="Helvetica-Bold", alignment=TA_CENTER),
            _P(f"<b>{mf.win_rate_pct:.0f}%</b>", fontSize=22, leading=26, textColor=GREEN,
               fontName="Helvetica-Bold", alignment=TA_CENTER),
        ],
        [
            _P("Total Events", fontSize=7.5, textColor=DGRAY, alignment=TA_CENTER),
            _P("MSCI Events", fontSize=7.5, textColor=DGRAY, alignment=TA_CENTER),
            _P("FTSE Events", fontSize=7.5, textColor=DGRAY, alignment=TA_CENTER),
            _P("Dual Pairs", fontSize=7.5, textColor=DGRAY, alignment=TA_CENTER),
            _P("Sharpe (filtered)", fontSize=7.5, textColor=DGRAY, alignment=TA_CENTER),
            _P("Win Rate (filtered)", fontSize=7.5, textColor=DGRAY, alignment=TA_CENTER),
        ],
    ]
    col_w = (PAGE_W - 2 * MARGIN) / 6
    tile_tbl = _tbl(tile_data, colWidths=[col_w] * 6)
    tile_tbl.setStyle(TableStyle([
        ("BOX",        (0, 0), (-1, -1), 0.5, MGRAY),
        ("INNERGRID",  (0, 0), (-1, -1), 0.5, MGRAY),
        ("BACKGROUND", (0, 0), (-1, 0),  LGRAY),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    items.append(tile_tbl)
    items.append(Spacer(1, 0.3 * cm))

    # Avg return highlight box
    highlight_text = (
        f"<b>Momentum-filtered universe (RS ≥ {br.momentum_filter_threshold:.0f}th + above 200-day MA):</b>  "
        f"{br.n_filtered_in} events  ·  avg return <b>{mf.avg_return_pct:+.1f}%</b>  ·  "
        f"win rate <b>{mf.win_rate_pct:.0f}%</b>  ·  Sharpe <b>{mf.sharpe_ratio:.2f}</b>  ·  "
        f"max gain <b>{mf.max_return_pct:+.1f}%</b>  ·  max loss <b>{mf.max_loss_pct:+.1f}%</b>"
    )
    items.append(_tbl(
        [[_P(highlight_text, fontSize=8.5, textColor=NAVY)]],
        colWidths=[PAGE_W - 2 * MARGIN],
    ))
    items.append(Spacer(1, 0.3 * cm))

    # Dual-index highlight
    dual_text = (
        f"<font color='#2E7D32'><b>★ DUAL-INDEX PLAYS (same stock: MSCI + FTSE):</b></font>  "
        f"{result.n_dual_pairs} historical pairs  ·  "
        f"avg combined return <b>{result.dual_avg_combined_pct:+.1f}%</b>  ·  "
        f"win rate <b>{result.dual_win_rate_pct:.0f}%</b>  ·  "
        f"avg holding <b>{result.dual_avg_months:.1f} months</b>  ·  "
        f"MSCI leg avg <b>{result.dual_avg_msci_leg_pct:+.1f}%</b>  "
        f"FTSE leg avg <b>{result.dual_avg_ftse_leg_pct:+.1f}%</b>"
    )
    items.append(_tbl(
        [[_P(dual_text, fontSize=8.5, textColor=NAVY)]],
        colWidths=[PAGE_W - 2 * MARGIN],
    ))
    items.append(Spacer(1, 0.4 * cm))

    # Methodology note
    items.append(_P(
        "<b>Methodology:</b> Backtest covers all MSCI Poland Standard index additions and FTSE Developed "
        "Europe (Poland) additions since September 2018 (Poland's FTSE DM upgrade date). "
        "Event types included: Standard Add (A), Free Float Change (C), Weight Decrease for inclusion "
        "mechanics (D), FIF change (F), Size migration (G). Deletions and pure weight reductions excluded "
        "from long universe. Returns simulated at hypothetical T−45 entry (45 calendar days before "
        "effective date) through effective date close. Momentum filter: RS ≥ 60th percentile AND price "
        "above 200-day MA at entry. All returns are illustrative — live slippage and market impact not modelled.",
        fontSize=7.5, textColor=DGRAY))
    items.append(Spacer(1, 0.2 * cm))
    items.append(_P(
        "⚠  IMPORTANT: Historical backtest. Past performance does not guarantee future results. "
        "Forced buying figures marked [EST] require live verification. PLN/USD: 3.68 (March 6 2026).",
        fontSize=7.5, textColor=CORAL, fontName="Helvetica-Bold"))

    return items


# ─────────────────────────────────────────────────────────────────────────────
# 2. Performance by index family
# ─────────────────────────────────────────────────────────────────────────────

def _stats_section(result: CombinedBacktestResult) -> list:
    items = []
    items.append(PageBreak())
    items.append(Paragraph("PERFORMANCE BY INDEX FAMILY", ST["h1"]))
    items.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=8))

    header = [
        _P("<b>Cohort</b>", fontSize=8, fontName="Helvetica-Bold"),
        _P("<b>N</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Win%</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Avg Ret</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Median</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>StdDev</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Sharpe</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Best</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Worst</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Calmar</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
    ]

    def _stat_row(label, s, row_color=None):
        rc = _ret_color(s.avg_return_pct)
        sharpe_icon = "✓" if s.sharpe_ratio >= 1.5 else ("~" if s.sharpe_ratio >= 0.8 else "✗")
        sharpe_col = GREEN if s.sharpe_ratio >= 1.5 else (AMBER if s.sharpe_ratio >= 0.8 else RED)
        return [
            _P(label, fontSize=7.5),
            _P(str(s.n_events), fontSize=7.5, alignment=TA_CENTER),
            _P(f"{s.win_rate_pct:.0f}%", fontSize=7.5, alignment=TA_CENTER,
               textColor=(GREEN if s.win_rate_pct >= 70 else (AMBER if s.win_rate_pct >= 55 else RED))),
            _P(f"{s.avg_return_pct:+.1f}%", fontSize=7.5, fontName="Helvetica-Bold",
               alignment=TA_CENTER, textColor=rc),
            _P(f"{s.median_return_pct:+.1f}%", fontSize=7.5, alignment=TA_CENTER),
            _P(f"{s.std_return_pct:.1f}%", fontSize=7.5, alignment=TA_CENTER),
            _P(f"{s.sharpe_ratio:.2f} {sharpe_icon}", fontSize=7.5, alignment=TA_CENTER,
               fontName="Helvetica-Bold", textColor=sharpe_col),
            _P(f"{s.max_return_pct:+.1f}%", fontSize=7.5, alignment=TA_CENTER, textColor=GREEN),
            _P(f"{s.max_loss_pct:+.1f}%", fontSize=7.5, alignment=TA_CENTER, textColor=RED),
            _P(f"{s.calmar_ratio():.2f}", fontSize=7.5, alignment=TA_CENTER),
        ]

    br = result.base_result
    rows = [
        header,
        _stat_row("MSCI Poland — All Events", result.msci_all),
        _stat_row("MSCI Poland — Momentum Filtered (RS ≥ 60)", result.msci_filtered),
        _stat_row("FTSE Developed Europe — All Events", result.ftse_all),
        _stat_row("FTSE Developed Europe — Momentum Filtered (RS ≥ 60)", result.ftse_filtered),
        _stat_row("COMBINED — All Events", br.all_events),
        _stat_row("COMBINED — Momentum Filtered (RS ≥ 60)", br.momentum_filtered),
    ]

    W = PAGE_W - 2 * MARGIN
    cw = [W * 0.30] + [W * 0.07] * 9
    tbl = _tbl(rows, colWidths=cw)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("BACKGROUND",    (0, 1), (-1, 1),  colors.HexColor("#E3F2FD")),
        ("BACKGROUND",    (0, 2), (-1, 2),  LGRAY),
        ("BACKGROUND",    (0, 3), (-1, 3),  colors.HexColor("#F3E5F5")),
        ("BACKGROUND",    (0, 4), (-1, 4),  LGRAY),
        ("BACKGROUND",    (0, 5), (-1, 5),  colors.HexColor("#E8F5E9")),
        ("BACKGROUND",    (0, 6), (-1, 6),  colors.HexColor("#C8E6C9")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [None]),  # override per-row already set
        ("INNERGRID",     (0, 0), (-1, -1), 0.4, MGRAY),
        ("BOX",           (0, 0), (-1, -1), 0.8, NAVY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.3 * cm))
    items.append(_P(
        "Win% = % of events with positive return. Sharpe = avg/stdev. Calmar = avg/|max_loss|. "
        "✓ = Sharpe ≥ 1.5  ~  = 0.8–1.5  ✗ = < 0.8. All figures illustrative.",
        fontSize=7, textColor=DGRAY))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# 3. Momentum filter sensitivity
# ─────────────────────────────────────────────────────────────────────────────

def _filter_section() -> list:
    items = []
    items.append(Spacer(1, 0.5 * cm))
    items.append(Paragraph("MOMENTUM FILTER SENSITIVITY (COMBINED UNIVERSE)", ST["h2"]))
    items.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=6))

    header = [
        _P("<b>RS Threshold</b>", fontSize=8, fontName="Helvetica-Bold"),
        _P("<b>N Events</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Retained</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Win%</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Avg Return</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Sharpe</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Best</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Worst</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
    ]

    rows = [header]
    base = run_backtest(momentum_filter_pct=0)
    total_n = base.n_total_events

    for thresh in [40, 50, 55, 60, 65, 70, 75]:
        r = run_backtest(momentum_filter_pct=thresh)
        mf = r.momentum_filtered
        retained_pct = mf.n_events / total_n * 100 if total_n else 0
        is_optimal = thresh == 60
        label = f"RS ≥ {thresh}th  {'← OPTIMAL' if is_optimal else ''}"
        bg = colors.HexColor("#E8F5E9") if is_optimal else None
        sc = GREEN if mf.sharpe_ratio >= 1.5 else (AMBER if mf.sharpe_ratio >= 0.8 else RED)
        row = [
            _P(f"<b>{label}</b>" if is_optimal else label, fontSize=7.5,
               fontName=("Helvetica-Bold" if is_optimal else "Helvetica")),
            _P(str(mf.n_events), fontSize=7.5, alignment=TA_CENTER),
            _P(f"{retained_pct:.0f}%", fontSize=7.5, alignment=TA_CENTER),
            _P(f"{mf.win_rate_pct:.0f}%", fontSize=7.5, alignment=TA_CENTER,
               textColor=(GREEN if mf.win_rate_pct >= 70 else AMBER)),
            _P(f"{mf.avg_return_pct:+.2f}%", fontSize=7.5, alignment=TA_CENTER,
               fontName="Helvetica-Bold", textColor=_ret_color(mf.avg_return_pct)),
            _P(f"{mf.sharpe_ratio:.2f}", fontSize=7.5, alignment=TA_CENTER,
               fontName="Helvetica-Bold", textColor=sc),
            _P(f"{mf.max_return_pct:+.1f}%", fontSize=7.5, alignment=TA_CENTER, textColor=GREEN),
            _P(f"{mf.max_loss_pct:+.1f}%", fontSize=7.5, alignment=TA_CENTER, textColor=RED),
        ]
        rows.append(row)

    W = PAGE_W - 2 * MARGIN
    cw = [W * 0.25, W * 0.10, W * 0.10, W * 0.10, W * 0.15, W * 0.10, W * 0.10, W * 0.10]
    tbl = _tbl(rows, colWidths=cw)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LGRAY, WHITE]),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#E8F5E9")),  # RS≥60 row (index 4)
        ("INNERGRID",  (0, 0), (-1, -1), 0.4, MGRAY),
        ("BOX",        (0, 0), (-1, -1), 0.8, NAVY),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.2 * cm))
    items.append(_P(
        "RS = relative strength percentile rank vs. WIG20 universe at T−45 entry. "
        "RS ≥ 60th threshold chosen as optimal: highest Sharpe with sufficient sample size.",
        fontSize=7, textColor=DGRAY))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# 4. Dual-index pair analysis
# ─────────────────────────────────────────────────────────────────────────────

def _dual_section(result: CombinedBacktestResult) -> list:
    items = []
    items.append(PageBreak())
    items.append(Paragraph("DUAL-INDEX PAIR ANALYSIS", ST["h1"]))
    items.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=6))
    items.append(_P(
        "Historical cases where the same stock was added to <b>both MSCI Poland Standard</b> "
        "and <b>FTSE Developed Europe</b> within the same investment cycle. "
        "Combined return = T−45 entry before MSCI event, held through FTSE effective date.",
        fontSize=8.5, textColor=NAVY))
    items.append(Spacer(1, 0.3 * cm))

    # Summary bar
    summary_text = (
        f"<b>{result.n_dual_pairs} pairs</b>  ·  "
        f"avg combined return <b><font color='#2E7D32'>{result.dual_avg_combined_pct:+.1f}%</font></b>  ·  "
        f"win rate <b>{result.dual_win_rate_pct:.0f}%</b>  ·  "
        f"avg holding <b>{result.dual_avg_months:.1f} months</b>  ·  "
        f"MSCI leg avg <b>{result.dual_avg_msci_leg_pct:+.1f}%</b>  ·  "
        f"FTSE leg avg <b>{result.dual_avg_ftse_leg_pct:+.1f}%</b>"
    )
    items.append(_tbl(
        [[_P(summary_text, fontSize=8.5, textColor=NAVY)]],
        colWidths=[PAGE_W - 2 * MARGIN],
    ))
    items.append(Spacer(1, 0.3 * cm))

    header = [
        _P("<b>Stock</b>", fontSize=8, fontName="Helvetica-Bold"),
        _P("<b>Sector</b>", fontSize=8, fontName="Helvetica-Bold"),
        _P("<b>MSCI Review</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>FTSE Review</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Gap (mo)</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>RS Entry</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>MSCI Ret</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>FTSE Ret</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Combined</b>", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER),
    ]

    rows = [header]
    for p in result.dual_pairs:
        rows.append([
            _P(f"<b>{p.stock_name}</b><br/><font color='#757575'>{p.ticker}</font>",
               fontSize=7.5),
            _P(p.sector, fontSize=7.5),
            _P(p.msci_review, fontSize=7.5, alignment=TA_CENTER),
            _P(p.ftse_review, fontSize=7.5, alignment=TA_CENTER),
            _P(f"{p.months_between:.0f}", fontSize=7.5, alignment=TA_CENTER),
            _P(f"{p.rs_at_msci_entry:.0f}th", fontSize=7.5, alignment=TA_CENTER,
               textColor=(GREEN if p.rs_at_msci_entry >= 70 else AMBER)),
            _P(f"{p.msci_return_pct:+.1f}%", fontSize=7.5, alignment=TA_CENTER,
               fontName="Helvetica-Bold", textColor=_ret_color(p.msci_return_pct)),
            _P(f"{p.ftse_return_pct:+.1f}%", fontSize=7.5, alignment=TA_CENTER,
               fontName="Helvetica-Bold", textColor=_ret_color(p.ftse_return_pct)),
            _P(f"<b>{p.combined_return_pct:+.1f}%</b>", fontSize=8, alignment=TA_CENTER,
               fontName="Helvetica-Bold", textColor=_ret_color(p.combined_return_pct)),
        ])

    W = PAGE_W - 2 * MARGIN
    cw = [W*0.20, W*0.15, W*0.10, W*0.10, W*0.07, W*0.07, W*0.10, W*0.10, W*0.11]
    tbl = _tbl(rows, colWidths=cw)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  GREEN),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LGRAY, WHITE]),
        ("INNERGRID",     (0, 0), (-1, -1), 0.4, MGRAY),
        ("BOX",           (0, 0), (-1, -1), 0.8, GREEN),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.4 * cm))

    # Per-pair notes
    items.append(Paragraph("TRADE NOTES", ST["h2"]))
    for i, p in enumerate(result.dual_pairs, 1):
        items.append(KeepTogether([
            _P(f"<b>{i}. {p.stock_name} ({p.ticker})</b>  —  {p.msci_review} MSCI + {p.ftse_review} FTSE  "
               f"|  Combined: <font color='#2E7D32'><b>{p.combined_return_pct:+.1f}%</b></font>  "
               f"|  Gap: {p.months_between:.0f} months",
               fontSize=8.5),
            _P(p.note, fontSize=7.5, textColor=DGRAY),
            Spacer(1, 0.15 * cm),
        ]))

    return items


# ─────────────────────────────────────────────────────────────────────────────
# 5. Full event detail table
# ─────────────────────────────────────────────────────────────────────────────

_EVENT_TYPE_NAMES = {
    "A": "Standard Add",
    "B": "Deletion",
    "C": "Free Float Chg",
    "D": "Weight Decrease",
    "E": "Weight Decrease",
    "F": "FIF Change",
    "G": "Size Migration",
}


def _events_section(result: CombinedBacktestResult) -> list:
    items = []
    items.append(PageBreak())
    items.append(Paragraph("FULL EVENT DETAIL — 2018–2026", ST["h1"]))
    items.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=6))
    items.append(_P(
        "All long-eligible events sorted by event ID. "
        "✓ = momentum filter pass (RS ≥ 60 + 200d MA).  ★★ = return > 10%  ★ = 5–10%",
        fontSize=8, textColor=DGRAY))
    items.append(Spacer(1, 0.2 * cm))

    header = [
        _P("<b>Stock</b>", fontSize=7.5, fontName="Helvetica-Bold"),
        _P("<b>Ticker</b>", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Index</b>", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Event</b>", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Review</b>", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>RS</b>", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>200d</b>", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Pass</b>", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_CENTER),
        _P("<b>Return</b>", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_CENTER),
    ]

    rows = [header]
    for e in sorted(result.all_events, key=lambda x: x.event_id):
        index_short = "MSCI" if "MSCI" in e.index else "FTSE"
        idx_col = BLUE if index_short == "MSCI" else PURPLE
        passed = e.momentum_passes_filter
        ret = e.return_t45_to_effective_pct
        flag = "★★" if (ret or 0) >= 10 else ("★" if (ret or 0) >= 5 else "")
        ret_str = f"{ret:+.1f}% {flag}" if ret is not None else "n/a"

        rows.append([
            _P(e.stock_name, fontSize=7),
            _P(e.ticker, fontSize=7, alignment=TA_CENTER),
            _P(index_short, fontSize=7, alignment=TA_CENTER, textColor=idx_col,
               fontName="Helvetica-Bold"),
            _P(_EVENT_TYPE_NAMES.get(e.event_type, e.event_type), fontSize=7, alignment=TA_CENTER),
            _P(e.review_date, fontSize=7, alignment=TA_CENTER),
            _P(f"{e.rs_percentile_at_entry:.0f}th", fontSize=7, alignment=TA_CENTER,
               textColor=(GREEN if e.rs_percentile_at_entry >= 60 else AMBER)),
            _P("Y" if e.above_200d_ma_at_entry else "N", fontSize=7, alignment=TA_CENTER,
               textColor=(GREEN if e.above_200d_ma_at_entry else RED)),
            _P("✓" if passed else "✗", fontSize=7, alignment=TA_CENTER,
               textColor=(GREEN if passed else RED), fontName="Helvetica-Bold"),
            _P(ret_str, fontSize=7, alignment=TA_CENTER,
               textColor=_ret_color(ret), fontName="Helvetica-Bold"),
        ])

    W = PAGE_W - 2 * MARGIN
    cw = [W*0.20, W*0.07, W*0.07, W*0.11, W*0.10, W*0.08, W*0.07, W*0.07, W*0.13]
    tbl = _tbl(rows, colWidths=cw)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LGRAY, WHITE]),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MGRAY),
        ("BOX",           (0, 0), (-1, -1), 0.8, NAVY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
    ]))
    items.append(tbl)
    return items


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def build_pdf(out_path: str = "/tmp/poland_backtest_combined_2026.pdf") -> str:
    result = build_combined_backtest()

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN + 0.5 * cm,
    )

    story = []
    story += _cover(result)
    story += _stats_section(result)
    story += _filter_section()
    story += _dual_section(result)
    story += _events_section(result)

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return out_path


if __name__ == "__main__":
    path = build_pdf("/tmp/poland_backtest_combined_2026.pdf")
    print(f"Saved: {path}  ({os.path.getsize(path):,} bytes)")
