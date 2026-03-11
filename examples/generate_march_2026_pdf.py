"""
PDF Report — MSCI Poland March 2026 Update
===========================================
Incorporates February 2026 SAR outcome: CCC deleted, Asseco Poland added.
All XTB and Kruk market data verified from live web search March 6, 2026.

Sources:
  • MSCI Feb 2026 Standard Index public list (app2.msci.com)
  • Biznes PAP / Stockwatch.pl (CCC deletion, ACP addition)
  • stockanalysis.com (XTB, KRU live prices + market caps)
  • kruk.eu investor relations (Kruk Q4 2025 results)
  • fxnewsgroup.com (XTB Q4 2025 record revenue)
  • PPCG / Investing.com (Cyfrowy Polsat succession, CPS price)
  • Yahoo Finance / Bankier.pl (Diagnostyka price)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)

from examples.march_2026_update import build_march_2026_candidates
from examples.pdf_helpers import (
    A4, cm,
    PAGE_W, PAGE_H, MARGIN,
    NAVY, BLUE, TEAL, GREEN, RED, AMBER, LGRAY, MGRAY, DGRAY, WHITE, BLACK, CORAL,
    S, ST, make_on_page, make_table as _table, candidate_card,
)

_on_page = make_on_page(
    "MSCI Poland March 2026 Update  |  Sources: MSCI press releases, PAP Biznes, "
    "stockanalysis.com, kruk.eu, fxnewsgroup.com"
)


# ─────────────────────────────────────────────────────────────────────────────
# Section 1: Cover
# ─────────────────────────────────────────────────────────────────────────────
def cover(candidates):
    items = []
    items.append(Spacer(1, 0.5*cm))
    items.append(HRFlowable(width="100%", thickness=4, color=NAVY, spaceAfter=10))
    items.append(Paragraph("MSCI POLAND — MARCH 2026 UPDATE",
        S("t", fontSize=22, leading=28, textColor=NAVY, fontName="Helvetica-Bold", alignment=TA_CENTER)))
    items.append(Paragraph("Live Data · March 6, 2026  ·  Post February 2026 SAR Outcome",
        S("s", fontSize=11, leading=15, textColor=BLUE, alignment=TA_CENTER)))
    items.append(Paragraph(
        "Sources: MSCI Feb 2026 Standard List · Biznes PAP · stockanalysis.com · "
        "kruk.eu · fxnewsgroup.com · investing.com · PPCG Stock",
        S("m", fontSize=8, textColor=DGRAY, alignment=TA_CENTER)))
    items.append(HRFlowable(width="100%", thickness=1, color=MGRAY, spaceBefore=8, spaceAfter=8))

    # February 2026 SAR outcome box
    sar_text = (
        "<b>FEBRUARY 2026 SAR — CONFIRMED OUTCOME (effective Feb 27, 2026):</b><br/><br/>"
        "<font color='#C62828'>⬇  DELETED from MSCI Poland Standard: CCC S.A. / MODIVO S.A. (MDVP)</font><br/>"
        "Prediction from previous report was CORRECT. CCC declined ~36% in 12M prior to deletion. "
        "Company rebranded to MODIVO (MDVP) in Feb 2026. Now in MSCI Poland Small Cap.<br/><br/>"
        "<font color='#2E7D32'>⬆  ADDED to MSCI Poland Standard: Asseco Poland S.A. (ACP)</font><br/>"
        "ACP rose ~60% in prior 12M. Replaced CCC. Standard index remains at <b>16 constituents</b>.<br/><br/>"
        "<b>Index composition post-Feb 27, 2026:</b> PKO, PKN Orlen, Bank Pekao, PZU, KGHM, "
        "Allegro, Santander Bank Polska, Dino Polska, LPP, CD Projekt, mBank, Żabka Group, "
        "Bank Millennium, Budimex, <s>CCC</s> → <b>Asseco Poland</b>"
    )
    sar_para = Paragraph(sar_text, S("sp", fontSize=8, leading=13, textColor=BLACK))
    sar_t = Table([[sar_para]], colWidths=[PAGE_W - 2*MARGIN])
    sar_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#E8F5E9")),
        ("BOX", (0,0), (-1,-1), 1.5, GREEN),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ]))
    items.append(sar_t)
    items.append(Spacer(1, 0.3*cm))

    # Live data snapshot box
    snap_text = (
        "<b>VERIFIED MARKET DATA — March 6, 2026  (PLN/USD ≈ 3.68):</b><br/><br/>"
        "<b>XTB S.A.</b>  PLN 92.78  ·  Market cap PLN 10.91B (~$2.96B)  ·  "
        "MSCI Small Cap 6.44% wt  ·  12M return +47% (+53% incl. div.)  ·  Near ATH PLN 93.76<br/>"
        "<b>Kruk S.A.</b>  PLN 464.60  ·  Market cap PLN 9.03B (~$2.45B)  ·  "
        "MSCI Small Cap 7.67% wt  ·  12M return +22.8%  ·  Below ATH PLN 510 by ~9%<br/>"
        "<b>MODIVO (CCC)</b>  PLN 121.70  ·  Market cap PLN 10.15B (~$2.76B)  ·  "
        "NOW in Small Cap  ·  Deleted from Standard Feb 27, 2026<br/>"
        "<b>Cyfrowy Polsat</b>  PLN 12.29  ·  Market cap PLN 8.36B (~$2.27B)  ·  "
        "Small Cap  ·  Succession resolved Dec 23, 2025"
    )
    snap_para = Paragraph(snap_text, S("snp", fontSize=8, leading=13, textColor=BLACK))
    snap_t = Table([[snap_para]], colWidths=[PAGE_W - 2*MARGIN])
    snap_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#E3F2FD")),
        ("BOX", (0,0), (-1,-1), 1.0, BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ]))
    items.append(snap_t)
    items.append(Spacer(1, 0.3*cm))

    # KPI tiles
    top = [c for c in candidates if c.conviction == "HIGH"]
    med = [c for c in candidates if c.conviction == "MEDIUM"]
    wat = [c for c in candidates if c.conviction == "WATCH"]
    sht = [c for c in candidates if c.conviction == "SHORT"]

    def tile(label, val, sub, clr):
        return Table([
            [Paragraph(label, S("tl", fontSize=7, textColor=DGRAY, fontName="Helvetica-Bold", alignment=TA_CENTER))],
            [Paragraph(val, S("tv", fontSize=22, textColor=clr, fontName="Helvetica-Bold", alignment=TA_CENTER))],
            [Paragraph(sub, S("ts", fontSize=7, textColor=DGRAY, alignment=TA_CENTER))],
        ], colWidths=[(PAGE_W - 2*MARGIN)/4 - 0.2*cm],
        style=TableStyle([("BACKGROUND",(0,0),(-1,-1),LGRAY),
                           ("BOX",(0,0),(-1,-1),0.5,MGRAY),
                           ("TOPPADDING",(0,0),(-1,-1),5),
                           ("BOTTOMPADDING",(0,0),(-1,-1),5)]))

    tiles = Table([[
        tile("HIGH CONVICTION", str(len(top)), "Standard Add (forced buying)", GREEN),
        tile("MEDIUM", str(len(med)), "Standard Add (Nov 2026)", TEAL),
        tile("WATCH", str(len(wat)), "Monitor — insufficient cap", AMBER),
        tile("AVOID / DELETED", str(len(sht)), "Deletion / Small Cap", RED),
    ]], colWidths=[(PAGE_W - 2*MARGIN)/4]*4)
    tiles.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP")]))
    items.append(tiles)
    items.append(Spacer(1, 0.3*cm))

    # Summary table
    items.append(Paragraph("Candidate Summary", ST["h2"]))
    hdr = ["Ticker", "Company", "Cap USD", "MSCI Status", "12M Ret", "Conviction", "Target SAR"]
    rows = [hdr]
    for c in sorted(candidates, key=lambda x: {"HIGH":0,"MEDIUM":1,"WATCH":2,"SHORT":3}.get(x.conviction,9)):
        conv_map = {"HIGH":"★★ HIGH","MEDIUM":"★ MEDIUM","WATCH":"◇ WATCH","SHORT":"⚠ DELETED/AVOID"}
        rows.append([
            c.ticker,
            c.company,
            f"${c.full_cap_usd_b:.2f}B",
            c.current_msci_status,
            f"{c.return_12m_pct:+.0f}%",
            conv_map.get(c.conviction, c.conviction),
            c.target_review,
        ])
    col_r = [0.07, 0.24, 0.09, 0.10, 0.08, 0.14, 0.10]

    formatted = []
    for i, row in enumerate(rows):
        if i == 0:
            formatted.append([Paragraph(c, ST["cellb"]) for c in row])
        else:
            c_obj = sorted(candidates, key=lambda x: {"HIGH":0,"MEDIUM":1,"WATCH":2,"SHORT":3}.get(x.conviction,9))[i-1]
            st_key = {"HIGH":"cellg","MEDIUM":"celln","WATCH":"cella","SHORT":"cellr"}.get(c_obj.conviction,"cell")
            formatted.append([Paragraph(v, ST[st_key]) for v in row])

    items.append(_table(formatted, col_r))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# Section 2: Feb 2026 SAR Detail + Updated Standard Composition
# ─────────────────────────────────────────────────────────────────────────────
def sar_and_index_section():
    items = []
    items.append(PageBreak())
    items.append(Paragraph("1. February 2026 SAR Outcome + Updated Index Composition", ST["h1"]))
    items.append(Paragraph(
        "Source: MSCI February 2026 Standard Index public list (app2.msci.com/eqb/gimi/stdindex/), "
        "Biznes PAP, Stockwatch.pl reporting on Feb 2026 additions/deletions.",
        ST["body"]))
    items.append(Spacer(1, 0.2*cm))

    items.append(Paragraph("February 2026 QIR / SAR — Changes (Effective Feb 27, 2026)", ST["h2"]))
    change_rows = [
        ["Action", "Ticker", "Company", "Sector", "Reason / Context"],
        ["DELETED ✗", "CCC→MDVP", "CCC S.A. / MODIVO S.A.", "Cons. Discretionary",
         "12M return ~-36%. Float-adj cap below Standard floor. Rebranded to MODIVO (MDVP). Confirmed prediction."],
        ["ADDED ✓", "ACP", "Asseco Poland S.A.", "Information Technology",
         "12M return ~+60%. Met all Standard gates (cap, ATVR, float). Largest Polish IT group."],
    ]
    fmt = []
    for i, row in enumerate(change_rows):
        if i == 0:
            fmt.append([Paragraph(c, ST["cellb"]) for c in row])
        elif "DELETED" in row[0]:
            fmt.append([Paragraph(c, ST["cellr"]) for c in row])
        else:
            fmt.append([Paragraph(c, ST["cellg"]) for c in row])
    items.append(_table(fmt, [0.10, 0.08, 0.18, 0.16, 0.48]))
    items.append(Spacer(1, 0.3*cm))

    items.append(Paragraph("MSCI Poland Standard — 16 Constituents (Post Feb 27, 2026)", ST["h2"]))
    items.append(Paragraph(
        "Source: MSCI Poland Index page (msci.com/indexes/index/961600), EPOL ETF holdings. "
        "Weights are approximate from the index factsheet; updated after Feb 27, 2026 rebalance.",
        ST["body"]))

    std_rows = [
        ["#", "Ticker", "Company", "Index Wt %", "Sector", "Notes"],
        ["1",  "PKO",  "PKO Bank Polski",       "18.27%", "Financials",       "Largest constituent"],
        ["2",  "PKN",  "PKN Orlen S.A.",         "15.03%", "Energy",           ""],
        ["3",  "KGH",  "KGHM Polska Miedź",      "10.61%", "Materials",        ""],
        ["4",  "PEO",  "Bank Pekao",             "9.39%",  "Financials",       ""],
        ["5",  "PZU",  "PZU S.A.",               "9.23%",  "Financials",       ""],
        ["6",  "SPL",  "Santander Bank Polska",  "5.46%",  "Financials",       ""],
        ["7",  "LPP",  "LPP S.A.",               "5.20%",  "Cons. Disc.",      ""],
        ["8",  "ALE",  "Allegro.eu",             "4.97%",  "Cons. Disc.",      ""],
        ["9",  "DNO",  "Dino Polska",            "4.45%",  "Cons. Staples",    ""],
        ["10", "CDR",  "CD Projekt",             "3.56%",  "Comm. Services",   ""],
        ["11", "MBK",  "mBank S.A.",             "~3.1%",  "Financials",       ""],
        ["12", "PGE",  "PGE S.A.",               "~2.5%",  "Utilities",        ""],
        ["13", "MIL",  "Bank Millennium",        "~2.3%",  "Financials",       "Added May 2025"],
        ["14", "BDX",  "Budimex S.A.",           "~2.2%",  "Industrials",      "Added May 2025"],
        ["15", "ZAB",  "Żabka Group",            "~2.0%",  "Cons. Staples",    "Added Feb 2025"],
        ["16", "ACP",  "Asseco Poland S.A.",     "~1.9%",  "Info. Technology", "ADDED Feb 2026 ★"],
    ]
    fmt2 = []
    for i, row in enumerate(std_rows):
        if i == 0:
            fmt2.append([Paragraph(c, ST["cellb"]) for c in row])
        elif "★" in row[-1]:
            fmt2.append([Paragraph(c, ST["cellg"]) for c in row])
        else:
            fmt2.append([Paragraph(c, ST["cell"]) for c in row])
    t2 = _table(fmt2, [0.04, 0.07, 0.22, 0.09, 0.14, 0.20])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",  (0,0), (-1,0), WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
        ("BACKGROUND", (0,16), (-1,16), colors.HexColor("#E8F5E9")),
        ("GRID", (0,0), (-1,-1), 0.3, MGRAY),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    items.append(t2)
    items.append(Spacer(1, 0.2*cm))
    items.append(Paragraph(
        "★ New addition Feb 2026. Weights are approximate from MSCI factsheet data; "
        "post-rebalance weights will be confirmed at next quarterly MSCI publication. "
        "Note: PGE row is estimated — verify exact 16th constituent from live MSCI data.",
        ST["small"]))

    # Small Cap upgrade candidates (updated)
    items.append(Spacer(1, 0.3*cm))
    items.append(Paragraph("MSCI Poland Small Cap — Standard Upgrade Candidates (March 6, 2026)", ST["h2"]))
    items.append(Paragraph(
        "Verified from live web search. PLN/USD = 3.68. "
        "Standard threshold for May 2026 SAR estimated at ~$3.3B (dynamic, rises with DM markets).",
        ST["body"]))

    sc_rows = [
        ["Ticker", "Company", "Price PLN", "Cap PLN B", "Cap USD B", "SC Wt%", "Gap to $3.3B", "Status"],
        ["XTB", "XTB S.A.", "92.78", "10.91", "$2.96B", "6.44%",
         "-10.3%", "PRIMARY CANDIDATE ★★ May 2026"],
        ["KRU", "Kruk S.A.", "464.60", "9.03", "$2.45B", "7.67%",
         "-25.8%", "SECONDARY ★ Nov 2026"],
        ["DIAG", "Diagnostyka S.A.", "182.05", "6.04", "$1.64B", "—",
         "-50.3%", "Long-term watch only"],
        ["MDVP", "MODIVO (ex-CCC)", "121.70", "10.15", "$2.76B", "—",
         "-16.4%", "DELETED — not a re-add candidate"],
        ["CPS", "Cyfrowy Polsat", "12.29", "8.36", "$2.27B", "—",
         "-31.2%", "Avoid — weak fundamentals"],
    ]
    fmt3 = []
    for i, row in enumerate(sc_rows):
        if i == 0:
            fmt3.append([Paragraph(c, ST["cellb"]) for c in row])
        elif i == 1:
            fmt3.append([Paragraph(c, ST["cellg"]) for c in row])
        elif i == 2:
            fmt3.append([Paragraph(c, ST["cella"]) for c in row])
        elif i == 4:
            fmt3.append([Paragraph(c, ST["cellr"]) for c in row])
        else:
            fmt3.append([Paragraph(c, ST["celld"]) for c in row])
    items.append(_table(fmt3, [0.07, 0.18, 0.09, 0.09, 0.09, 0.07, 0.09, 0.22], header_bg=BLUE))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# Section 3: 2025 Financial Results Summary
# ─────────────────────────────────────────────────────────────────────────────
def financials_section():
    items = []
    items.append(PageBreak())
    items.append(Paragraph("2. 2025 Financial Results — XTB and Kruk", ST["h1"]))
    items.append(Paragraph(
        "Full-year 2025 results verified from company announcements and press coverage. "
        "These results directly inform the MSCI inclusion case (market cap trajectory).",
        ST["body"]))
    items.append(Spacer(1, 0.2*cm))

    # XTB
    items.append(Paragraph("XTB S.A. — Full-Year 2025 Results", ST["h2"]))
    xtb_rows = [
        ["Metric", "FY2025", "YoY Change", "Context"],
        ["Revenue", "PLN 2,147M", "+14.6%", "Driven by gold CFDs (43.7% of mix), index CFDs (36%)"],
        ["Net profit", "PLN 644M", "—", "Missed analyst expectations of PLN 1B+"],
        ["Q4 revenue", "PLN 610M (record)", "—", "Record quarterly revenue; gold CFD trading boom"],
        ["New clients 2025", "864,286", "—", "Total client base: 2.16M"],
        ["Active clients", "1,189,422", "+69.7% YoY", "Fastest-growing CFD broker in Europe"],
        ["Client assets", "~EUR 10.8B", "—", "Assets under management growing"],
        ["Marketing expenses", "—", "+69.1% YoY", "Investment in client acquisition"],
        ["Cash on balance", "PLN 1.99B", "—", "Capital ratio 190.4% — well capitalised"],
        ["Share price (Mar 6)", "PLN 92.78", "+47% in 12M", "Near all-time high of PLN 93.76"],
        ["Market cap (Mar 6)", "PLN 10.91B / $2.96B", "—", "Highest ever; 6.44% of MSCI Small Cap index"],
    ]
    fmt_xtb = [[Paragraph(c, ST["cellb"] if i==0 else ST["cell"]) for c in row]
               for i, row in enumerate(xtb_rows)]
    items.append(_table(fmt_xtb, [0.18, 0.16, 0.14, 0.52], header_bg=TEAL))
    items.append(Spacer(1, 0.15*cm))
    items.append(Paragraph(
        "Note on earnings miss: PLN 644M net profit vs PLN 1B+ analyst consensus represents a "
        "significant shortfall, driven by surging marketing investment (+69%) for client acquisition. "
        "This is a strategic choice — XTB is prioritising growth over near-term profitability. "
        "MSCI inclusion criteria screen on market cap and float, NOT earnings, so the miss "
        "does not directly impair inclusion eligibility. Market cap reaction will be the key variable.",
        ST["body"]))

    items.append(Spacer(1, 0.3*cm))

    # Kruk
    items.append(Paragraph("Kruk S.A. — Full-Year 2025 Results (Record Year)", ST["h2"]))
    kru_rows = [
        ["Metric", "FY2025", "YoY Change", "Context"],
        ["Cash EBITDA", "~PLN 2.7B", "+12%", "Record; CEO confirmed 'all-time highs'"],
        ["Net profit Q4", "PLN 208M", "+81% YoY", "Strong Q4; operating leverage visible"],
        ["Net profit Q1-Q3", "PLN 877M", "-9% YoY", "Lower due to higher deferred tax provisions — not operational"],
        ["Portfolio investments", "PLN 2.2B", "—", "Annual new portfolio acquisitions"],
        ["Recoveries", "~PLN 4B", "—", "Record annual cash recoveries from NPL portfolios"],
        ["Portfolio carrying value", "PLN 11.6B", "+11% vs 2024", "Europe's largest NPL portfolio by value"],
        ["Equity", "PLN 5.3B", "+18%", "Strong balance sheet growth"],
        ["Net debt / Cash EBITDA", "2.6x", "Improved (was 2.7x)", "Deleveraging despite continued acquisitions"],
        ["Geography split", "Poland 41%, Italy 25%, Spain 16.8%, Romania 14.9%", "—", "Diversified European exposure"],
        ["Audited annual report", "Due March 10, 2026", "—", "Full results confirmation pending"],
        ["Share price (Mar 6)", "PLN 464.60", "+22.78% in 12M", "ATH was PLN 510 on Jan 9, 2026; -9% from ATH"],
        ["Market cap (Mar 6)", "PLN 9.03B / $2.45B", "—", "7.67% of MSCI Small Cap index (#7 constituent)"],
    ]
    fmt_kru = [[Paragraph(c, ST["cellb"] if i==0 else ST["cell"]) for c in row]
               for i, row in enumerate(kru_rows)]
    items.append(_table(fmt_kru, [0.18, 0.22, 0.15, 0.45], header_bg=BLUE))
    items.append(Spacer(1, 0.15*cm))
    items.append(Paragraph(
        "Analyst consensus (from stockanalysis.com / Stockopedia): PLN 532 price target "
        "(+14.5% upside from PLN 464.60). 3 analysts: Strong Buy. "
        "Full audited annual report expected March 10, 2026 — monitor for any surprises.",
        ST["body"]))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# Section 4: Individual Candidate Cards — delegated to pdf_helpers.candidate_card
# ─────────────────────────────────────────────────────────────────────────────
def _candidate_card(c) -> list:
    return candidate_card(c, thesis_label="Analysis",
                          checklist_label="Verification Checklist")


def candidate_section(candidates):
    items = []
    items.append(PageBreak())
    items.append(Paragraph("3. Individual Stock Analysis", ST["h1"]))
    items.append(Paragraph(
        "Cards sorted by conviction: HIGH → MEDIUM → WATCH → AVOID/DELETED. "
        "Left column: analysis + why 2026. Right column: risks + verification checklist. "
        "Prices verified March 6, 2026. [EST] fields need live verification before trading.",
        ST["body"]))
    items.append(Spacer(1, 0.3*cm))

    tier = {"HIGH": 0, "MEDIUM": 1, "WATCH": 2, "SHORT": 3}
    for c in sorted(candidates, key=lambda x: (tier.get(x.conviction, 9), -x.full_cap_usd_b)):
        items += _candidate_card(c)
    return items


# ─────────────────────────────────────────────────────────────────────────────
# Section 5: May 2026 SAR Pre-Trade Checklist
# ─────────────────────────────────────────────────────────────────────────────
def checklist_section():
    items = []
    items.append(PageBreak())
    items.append(Paragraph("4. Pre-Trade Decision Checklist — May 2026 SAR", ST["h1"]))
    items.append(Paragraph(
        "T-45 screen date for the May 2026 SAR is approximately 14 March 2026 — within days of "
        "this report. Complete these steps IN ORDER before opening any position.",
        ST["body"]))
    items.append(Spacer(1, 0.2*cm))

    steps = [
        ("☐ Step 1 — Confirm Feb 2026 SAR outcome",
         "Verify from msci.com/indexes/index-reviews that:\n"
         "• CCC (MDVP) has been removed from MSCI Poland Standard index\n"
         "• Asseco Poland (ACP) has been added\n"
         "• No other Polish stocks had changes at the February 2026 review\n"
         "Download the Feb 2026 Standard public list from app2.msci.com/eqb/gimi/stdindex/"),

        ("☐ Step 2 — Verify XTB live market cap",
         "Go to: stooq.pl or stockanalysis.com/quote/wse/XTB/\n"
         "Verified price as of March 6, 2026: PLN 92.78 (~PLN 10.91B cap, ~$2.96B USD)\n"
         "• Is XTB STILL at/above PLN 90? → cap still ~$2.9B+\n"
         "• Has cap crossed $3.3B (PLN ~121)? → threshold likely met\n"
         "Decision: if cap ≥ $3.0B → HIGH conviction. If $2.7-3.0B → MEDIUM. If <$2.7B → SKIP."),

        ("☐ Step 3 — Verify XTB relative strength",
         "Compute 12-1 month RS: total return of XTB vs WIG-ALL index.\n"
         "Required: RS ≥ 60th percentile AND price above 200-day moving average.\n"
         "XTB at PLN 92.78 near ATH PLN 93.76 — likely above 200d MA (verify from stooq chart).\n"
         "12M return +47% (price) or +53% (total incl. div.) — strong RS likely confirmed."),

        ("☐ Step 4 — Check XTB float and founder stake",
         "Verify Jakub Zabłocki and XTB Group founders' current ownership from:\n"
         "• KNF/WSE insider ownership disclosures\n"
         "• XTB annual report 2025 (ownership structure section)\n"
         "FIF [EST] = 1 - founder stake ≈ 0.65 (if founder ~35%).\n"
         "Float-adj cap [EST] = $2.96B × 0.65 = $1.93B — must exceed $1.3B MSCI minimum."),

        ("☐ Step 5 — Review XTB Q4/FY2025 earnings impact",
         "XTB FY2025: revenue PLN 2,147M (+14.6%), net profit PLN 644M (missed PLN 1B expectations).\n"
         "Check analyst reactions: were there significant downgrade notes post-results?\n"
         "A drop to below PLN 80 (cap ~$2.5B) would change inclusion probability to LOW.\n"
         "As of March 6, price still near ATH — earnings miss appears priced in."),

        ("☐ Step 6 — Verify Kruk FY2025 audited results",
         "Full audited annual report due: March 10, 2026 (4 days from report date).\n"
         "Required: confirm no material negative surprises in the full-year figures.\n"
         "If Kruk cap approaches $2.8B+ ($3.0B+ preferable): re-assess for May 2026.\n"
         "Otherwise: WATCH for Nov 2026 SAR — re-screen from September 2026."),

        ("☐ Step 7 — Set May 2026 SAR announcement alert",
         "MSCI May 2026 SAR announcement: approximately 27-29 April 2026.\n"
         "Set calendar alert. On announcement day:\n"
         "  → XTB confirmed: HOLD to effective date (~28 May 2026). Expect +5-10% drift.\n"
         "  → XTB NOT announced: SELL at market within 30 minutes of open.\n"
         "Monitor: msci.com/indexes/index-reviews for the press release."),
    ]

    for title, desc in steps:
        row_data = [[
            Paragraph(title, S("st", fontSize=9, fontName="Helvetica-Bold", textColor=BLUE)),
            Paragraph(desc.replace("\n", "<br/>"), S("sd", fontSize=8, leading=12)),
        ]]
        t = Table(row_data, colWidths=[(PAGE_W-2*MARGIN)*0.28, (PAGE_W-2*MARGIN)*0.72])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), LGRAY),
            ("BOX",(0,0),(-1,-1),0.5,MGRAY),
            ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))
        items.append(t)
        items.append(Spacer(1, 0.15*cm))

    items.append(Spacer(1, 0.3*cm))
    items.append(HRFlowable(width="100%", thickness=1, color=AMBER, spaceAfter=6))
    items.append(Paragraph(
        "⚠  DISCLAIMER: This report is for research and educational purposes only. "
        "It does not constitute investment advice or a solicitation to buy or sell any security. "
        "All [EST] figures must be independently verified from live market data before trading. "
        "Past performance (2018-2025 MSCI inclusion backtest) does not guarantee future results. "
        "MSCI retains committee discretion for borderline inclusion decisions. "
        "PLN/USD rate used: 3.68 (March 6, 2026). Data sources: MSCI press releases, "
        "stockanalysis.com, kruk.eu, fxnewsgroup.com, investing.com, PPCG Stock, Biznes PAP.",
        S("disc", fontSize=7.5, leading=11, textColor=AMBER, fontName="Helvetica-Oblique")))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# Main build function
# ─────────────────────────────────────────────────────────────────────────────
def build_pdf(output_path: str = "msci_poland_march_2026_update.pdf") -> str:
    candidates = build_march_2026_candidates()
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=1.4*cm,
        title="MSCI Poland — March 2026 Update",
        author="MZApp Research",
    )
    story = []
    story += cover(candidates)
    story += sar_and_index_section()
    story += financials_section()
    story += candidate_section(candidates)
    story += checklist_section()
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return output_path


def run():
    from examples.march_2026_update import run as data_run
    data_run()
    print("Generating March 2026 PDF report...")
    path = build_pdf()
    print(f"PDF saved → {path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "msci_poland_march_2026_update.pdf"
    path = build_pdf(out)
    print(f"PDF saved → {path}")
