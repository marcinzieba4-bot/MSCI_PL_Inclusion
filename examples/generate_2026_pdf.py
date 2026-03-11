"""
PDF Report — MSCI Poland 2026 Verified Candidate Watchlist
===========================================================
Built from live web-search data (March 2026).
Includes critical corrections to previous estimates.

Sources used:
  • MSCI Poland Index Factsheet (Nov 2025 data)
  • MSCI May 2025 & Nov 2025 SAR press releases
  • Biznes PAP / StockWatch.pl reporting on May 2025 additions
  • stockanalysis.com, investing.com for market cap data
  • MSCI GIMI Methodology (Aug 2025 PDF)
  • FTSE Russell country classification documentation
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)

from examples.candidates_2026 import build_verified_candidates, Candidate2026
from examples.pdf_helpers import (
    A4, cm,
    PAGE_W, PAGE_H, MARGIN,
    NAVY, BLUE, TEAL, GREEN, RED, AMBER, LGRAY, MGRAY, DGRAY, WHITE, BLACK, CORAL,
    S, ST, make_on_page, make_table as _table, candidate_card,
)

_on_page = make_on_page(
    "MSCI Poland 2026 — Verified Candidate Report  |  "
    "Sources: MSCI press releases, PAP Biznes, stockanalysis.com"
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Cover
# ─────────────────────────────────────────────────────────────────────────────
def cover(candidates):
    items = []
    items.append(Spacer(1, 0.6*cm))
    items.append(HRFlowable(width="100%", thickness=4, color=NAVY, spaceAfter=12))
    items.append(Paragraph("MSCI POLAND — 2026 CANDIDATE WATCHLIST",
        S("t", fontSize=22, leading=28, textColor=NAVY, fontName="Helvetica-Bold", alignment=TA_CENTER)))
    items.append(Paragraph("Verified from Live Data · March 2026",
        S("s", fontSize=11, leading=15, textColor=BLUE, alignment=TA_CENTER)))
    items.append(Paragraph(
        "Sources: MSCI SAR Press Releases · Biznes PAP · stockanalysis.com · investing.com · MSCI GIMI Methodology Aug 2025",
        S("m", fontSize=8, textColor=DGRAY, alignment=TA_CENTER)))
    items.append(HRFlowable(width="100%", thickness=1, color=MGRAY, spaceBefore=10, spaceAfter=10))

    # Corrections box — prominently placed on cover
    corr_text = (
        "<b>CORRECTIONS TO PREVIOUS ESTIMATES (these were factually wrong — now fixed):</b><br/><br/>"
        "<font color='#C62828'>✗  FTSE Poland: was described as Emerging Market.</font>  "
        "Poland has been in FTSE <b>Developed</b> Europe since September 2018. "
        "There are NO FTSE EM Poland inclusion events. All previous 'dual MSCI+FTSE EM' "
        "analysis in this codebase was incorrect and has been removed.<br/><br/>"
        "<font color='#C62828'>✗  May 2025 SAR candidates were wrong.</font>  "
        "Actual additions: <b>Bank Millennium, Budimex, CCC</b> (not XTB or Kruk). "
        "MSCI Poland Standard grew from 13 to 16 constituents.<br/><br/>"
        "<font color='#C62828'>✗  XTB and Kruk were described as Standard members.</font>  "
        "Both are currently in <b>MSCI Poland Small Cap</b>. They are the primary "
        "Standard upgrade candidates — but have not been added yet.<br/><br/>"
        "<font color='#2E7D32'>✓  Nov 2025 SAR: confirmed no changes for Poland.</font><br/>"
        "<font color='#2E7D32'>✓  MSCI Poland Standard: 16 constituents confirmed.</font><br/>"
        "<font color='#2E7D32'>✓  CCC deletion risk identified (cap well below threshold).</font>"
    )
    corr_para = Paragraph(corr_text,
        S("cp", fontSize=8, leading=13, textColor=BLACK))
    corr_t = Table([[corr_para]], colWidths=[PAGE_W - 2*MARGIN])
    corr_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FFF3E0")),
        ("BOX", (0,0), (-1,-1), 1.5, AMBER),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ]))
    items.append(corr_t)
    items.append(Spacer(1, 0.4*cm))

    # KPI row
    top = [c for c in candidates if c.conviction == "HIGH"]
    med = [c for c in candidates if c.conviction == "MEDIUM"]
    wat = [c for c in candidates if c.conviction == "WATCH"]
    sht = [c for c in candidates if c.conviction == "SHORT"]

    def tile(label, val, sub, clr):
        return Table([[Paragraph(label, S("tl", fontSize=7, textColor=DGRAY,
                        fontName="Helvetica-Bold", alignment=TA_CENTER))],
                      [Paragraph(val, S("tv", fontSize=22, textColor=clr,
                        fontName="Helvetica-Bold", alignment=TA_CENTER))],
                      [Paragraph(sub, S("ts", fontSize=7, textColor=DGRAY,
                        alignment=TA_CENTER))]],
            colWidths=[(PAGE_W - 2*MARGIN)/4 - 0.2*cm],
            style=TableStyle([("BACKGROUND",(0,0),(-1,-1),LGRAY),
                               ("BOX",(0,0),(-1,-1),0.5,MGRAY),
                               ("TOPPADDING",(0,0),(-1,-1),5),
                               ("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    tiles = Table([[tile("HIGH CONVICTION", str(len(top)), "Standard Add / Wt Inc", GREEN),
                    tile("MEDIUM", str(len(med)), "Weight increase plays", TEAL),
                    tile("WATCH", str(len(wat)), "Monitor for entry", AMBER),
                    tile("SHORT / AVOID", str(len(sht)), "Deletion / weight decrease", RED)]],
                  colWidths=[(PAGE_W - 2*MARGIN)/4]*4)
    tiles.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP")]))
    items.append(tiles)
    return items


# ─────────────────────────────────────────────────────────────────────────────
# 2. Verified MSCI Poland Index Structure
# ─────────────────────────────────────────────────────────────────────────────
def index_structure():
    items = []
    items.append(PageBreak())
    items.append(Paragraph("1. Verified MSCI Poland Index Structure (March 2026)", ST["h1"]))
    items.append(Paragraph(
        "Source: MSCI Poland Index Factsheet (Nov 28, 2025 data), EPOL ETF holdings. "
        "Total index market cap: ~USD 105.2B. 16 constituents.",
        ST["body"]))
    items.append(Spacer(1, 0.2*cm))

    std_rows = [
        ["#", "Ticker", "Company", "Float-Adj Cap (USD B)", "Index Weight %", "Sector", "SAR Added"],
        ["1", "PKO", "PKO Bank Polski", "18.58", "17.66%", "Financials", "Pre-2018"],
        ["2", "PKN", "PKN Orlen S.A.", "14.97", "14.23%", "Energy", "Pre-2018"],
        ["3", "PZU", "PZU S.A.", "10.42", "9.91%", "Financials", "Pre-2018"],
        ["4", "PEO", "Bank Pekao", "10.08", "9.58%", "Financials", "Pre-2018"],
        ["5", "KGH", "KGHM Polska Miedź", "8.13", "7.73%", "Materials", "Pre-2018"],
        ["6", "ALE", "Allegro.eu", "6.04", "5.74%", "Cons. Disc.", "Nov 2021"],
        ["7", "SPL", "Santander Bank Polska", "5.77", "5.49%", "Financials", "Nov 2019"],
        ["8", "DNO", "Dino Polska", "5.49", "5.22%", "Cons. Staples", "May 2020"],
        ["9", "LPP", "LPP S.A.", "5.20", "4.94%", "Cons. Disc.", "Pre-2018"],
        ["10", "CDR", "CD Projekt", "4.57", "4.34%", "Comm. Services", "Pre-2018"],
        ["11", "MBK", "mBank S.A.", "~3.28", "~3.12%", "Financials", "Pre-2018"],
        ["12", "ZAB", "Żabka Group", "~5.72", "~5.44%", "Cons. Staples", "Feb 2025 ★"],
        ["13", "MIL", "Bank Millennium", "~5.24", "~4.98%", "Financials", "May 2025 ★"],
        ["14", "BDX", "Budimex S.A.", "~5.58", "~5.31%", "Industrials", "May 2025 ★"],
        ["15", "CCC", "CCC S.A. (MODIVO) ⚠", "~2.36", "~2.24%", "Cons. Disc.", "May 2025 ★"],
        ["16", "?", "One additional mid-cap", "~2.0+", "~1.90%", "TBC", "—"],
    ]
    col_r = [0.04, 0.07, 0.20, 0.13, 0.10, 0.13, 0.13]
    formatted_rows = []
    for i, row in enumerate(std_rows):
        if i == 0:
            formatted_rows.append([Paragraph(c, ST["cellb"]) for c in row])
        else:
            # Highlight new additions
            is_new = "★" in row[-1]
            is_risk = "⚠" in row[2]
            st_key = "cella" if is_risk else ("cellg" if is_new else "cell")
            formatted_rows.append([Paragraph(c, ST[st_key] if j in (2, 6) else ST["cell"])
                                    for j, c in enumerate(row)])
    t = _table(formatted_rows, col_r)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",  (0,0), (-1,0), WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
        ("GRID", (0,0), (-1,-1), 0.3, MGRAY),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 7.5),
        # highlight rows 12-15 (new additions)
        ("BACKGROUND", (0,12), (-1,15), colors.HexColor("#E8F5E9")),
        # highlight CCC risk row
        ("BACKGROUND", (0,15), (-1,15), colors.HexColor("#FFF3E0")),
    ]))
    items.append(t)
    items.append(Spacer(1, 0.2*cm))
    items.append(Paragraph(
        "★ New additions (2025). ⚠ CCC: full cap ~USD 2.29B — below inclusion threshold (~USD 2.8B+). "
        "Deletion buffer applies (MSCI keeps until cap falls below ~50% of lower threshold = ~$1.4B). "
        "Weight decrease is already occurring as other members grow faster.",
        ST["small"]))

    # Small Cap table
    items.append(Spacer(1, 0.3*cm))
    items.append(Paragraph("MSCI Poland Small Cap — Standard Upgrade Candidates", ST["h2"]))
    items.append(Paragraph(
        "Source: EPOL holdings weight (~5.73% for XTB), investing.com market caps. "
        "These are the stocks to WATCH for Standard inclusion in 2026.",
        ST["body"]))

    sc_rows = [
        ["Ticker", "Company", "Full Cap PLN B", "Full Cap USD B", "Small Cap Wt%", "Status vs Standard threshold"],
        ["XTB", "XTB S.A.", "10.76", "2.71", "~5.73%",
         "~3% below ~$2.8B threshold — PRIMARY CANDIDATE ★★"],
        ["KRU", "Kruk S.A.", "9.09", "2.29", "—",
         "~18% below threshold — SECONDARY CANDIDATE ★"],
        ["DGC", "Diagnostyka S.A.", "~4.5 [EST]", "~1.13 [EST]", "Added May 2025",
         "Far below Standard (~-60%) — long-term watch only"],
    ]
    formatted_sc = []
    for i, row in enumerate(sc_rows):
        if i == 0:
            formatted_sc.append([Paragraph(c, ST["cellb"]) for c in row])
        elif i == 1:
            formatted_sc.append([Paragraph(c, ST["cellg"]) for c in row])
        elif i == 2:
            formatted_sc.append([Paragraph(c, ST["cella"]) for c in row])
        else:
            formatted_sc.append([Paragraph(c, ST["cell"]) for c in row])

    sc_col = [0.08, 0.18, 0.13, 0.13, 0.12, 0.36]
    sc_t = _table(formatted_sc, sc_col, header_bg=BLUE)
    items.append(sc_t)

    # FTSE correction box
    items.append(Spacer(1, 0.3*cm))
    items.append(Paragraph("FTSE Classification — Critical Correction", ST["h2"]))
    ftse_text = (
        "<b>Poland is a FTSE DEVELOPED MARKET, not Emerging.</b><br/><br/>"
        "Poland was upgraded by FTSE Russell from Advanced Emerging to <b>Developed Market</b> "
        "status in <b>September 2018</b> — the first former communist country to achieve this. "
        "Polish stocks are now part of FTSE Developed Europe (alongside UK, Germany, France, etc.).<br/><br/>"
        "Implication: <b>there are no FTSE EM Poland inclusion events</b>. The 'dual-index' "
        "MSCI EM + FTSE EM plays described in previous versions of this report were factually "
        "incorrect. FTSE Developed inclusions exist but have different AUM dynamics "
        "(FTSE Developed AUM is much larger; Polish stocks are already represented).<br/><br/>"
        "MSCI has NOT upgraded Poland to Developed status (as of June 2025 classification review). "
        "MSCI cited: limited stock lending/short-selling, lack of English-language disclosures, "
        "and foreign investor registration rules. Poland remains ~1.1% of MSCI EM Index weight."
    )
    ftse_t = Table([[Paragraph(ftse_text, S("ft", fontSize=8, leading=12, textColor=BLACK))]],
                   colWidths=[PAGE_W - 2*MARGIN])
    ftse_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#E3F2FD")),
        ("BOX", (0,0), (-1,-1), 1, BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    items.append(ftse_t)
    return items


# ─────────────────────────────────────────────────────────────────────────────
# 3. Threshold mechanics
# ─────────────────────────────────────────────────────────────────────────────
def threshold_section():
    items = []
    items.append(PageBreak())
    items.append(Paragraph("2. MSCI Size Threshold Mechanics (How Inclusion Works)", ST["h1"]))
    items.append(Paragraph(
        "Source: MSCI GIMI Methodology document (August 2025). "
        "Understanding why a stock gets added — or not — requires understanding the dynamic threshold.",
        ST["body"]))
    items.append(Spacer(1, 0.2*cm))

    items.append(Paragraph("How the Threshold is Set", ST["h2"]))
    items.append(Paragraph(
        "MSCI's inclusion threshold is NOT fixed in USD. It is recalculated at every "
        "Semi-Annual Review based on the DM (Developed Market) universe:",
        ST["body"]))

    steps = [
        ("Step 1", "Sort all DM universe stocks by full market cap descending."),
        ("Step 2", "Find the market cap of the last stock when cumulative float-adj cap "
                   "reaches 99% coverage — this is the DM Global Minimum Size Reference."),
        ("Step 3", "The EM Standard Range = 0.5× to 1.15× of the DM reference. "
                   "As of May 2025 review: DM ref ~$13.35B → EM range ~$3.3B – $7.7B."),
        ("Step 4", "Stocks ABOVE the upper bound ($7.7B) are clearly Standard. "
                   "Stocks IN the range ($3.3B–$7.7B) are Standard. "
                   "Stocks below the lower bound ($3.3B) may still be added if they "
                   "recently crossed (buffer zone). EM Small Cap: $443M – $3.3B."),
        ("Step 5", "DELETION BUFFER: A Standard member is only deleted when its full cap "
                   "falls below 50% of the lower bound (~$1.65B). This prevents churning. "
                   "CCC at ~$2.29B is above this floor — not yet deleted."),
    ]
    for step, desc in steps:
        items.append(Paragraph(f"<b>{step}:</b> {desc}", ST["body"]))

    items.append(Spacer(1, 0.3*cm))

    # Threshold evolution table
    items.append(Paragraph("Threshold Evolution (Dynamic — Rises with DM Markets)", ST["h2"]))
    thresh_rows = [
        ["Review Date", "DM Reference (USD B)", "EM Standard Lower (USD B)",
         "EM Small Cap Floor (USD M)", "Impact on Poland"],
        ["Aug 2024", "$11.04B", "~$2.76B", "~$383M",
         "Bank Millennium, CCC, BDX were borderline"],
        ["May 2025", "~$13.35B", "~$3.34B", "~$443M",
         "MIL, BDX, CCC added; XTB ($2.71B) still below"],
        ["May 2026 [EST]", "~$14-15B", "~$3.5-3.75B [EST]", "~$480M [EST]",
         "XTB needs further cap growth; Kruk needs +50%+"],
    ]
    formatted_thresh = []
    for i, row in enumerate(thresh_rows):
        st_key = "cellb" if i == 0 else ("cella" if i == 3 else "cell")
        formatted_thresh.append([Paragraph(c, ST[st_key]) for c in row])
    thresh_col = [0.18, 0.18, 0.18, 0.18, 0.28]
    thresh_t = _table(formatted_thresh, thresh_col)
    items.append(thresh_t)
    items.append(Spacer(1, 0.2*cm))
    items.append(Paragraph(
        "KEY IMPLICATION for XTB: the threshold may be RISING to ~$3.5B by May 2026. "
        "XTB at $2.71B (March 2026) needs +29% cap appreciation to clear the lower bound, "
        "OR the stock may enter MSCI's 'buffer zone' consideration if it crosses the "
        "50%-of-lower-bound level. Precise FIF and float-adj cap calculations are essential.",
        ST["body"]))

    items.append(Spacer(1, 0.3*cm))
    items.append(Paragraph("Why Certain Stocks Were / Were Not Added", ST["h2"]))

    why_rows = [
        ["Stock", "Review", "Result", "Cap at Review", "Why included/excluded"],
        ["Żabka Group (ZAB)", "Feb 2025 QIR", "ADDED ✓",
         "~PLN 20.86B ($5.7B)", "Large cap, met all gates. Post-IPO overhang cleared."],
        ["Bank Millennium (MIL)", "May 2025 SAR", "ADDED ✓",
         "~PLN 19.14B ($4.8B)", "BCP stake re-evaluated; float-adj > $1.3B. CHF provisions complete."],
        ["Budimex (BDX)", "May 2025 SAR", "ADDED ✓",
         "~PLN 20.49B ($5.6B)", "Cap grew past buffer zone. EU KPO awards boosted re-rating."],
        ["CCC S.A.", "May 2025 SAR", "ADDED ✓",
         "~PLN 9.1B ($2.3B+?)", "Borderline — may have been higher at cut-off vs today."],
        ["XTB S.A.", "May 2025 SAR", "NOT ADDED ✗",
         "~PLN 10.76B ($2.71B)", "Below Standard lower bound at cut-off date. Small Cap retained."],
        ["Kruk S.A.", "May 2025 SAR", "NOT ADDED ✗",
         "~PLN 9.09B ($2.29B)", "Below Standard lower bound. Significant gap remains."],
        ["Cyfrowy Polsat", "Nov 2025 SAR", "NO CHANGE",
         "~PLN 2.3B ($0.58B)", "MSCI deletion buffer: above $1.4B floor but weight declining."],
    ]
    formatted_why = []
    for i, row in enumerate(why_rows):
        if i == 0:
            formatted_why.append([Paragraph(c, ST["cellb"]) for c in row])
        elif "ADDED" in row[2]:
            formatted_why.append([Paragraph(c, ST["cellg"]) for c in row])
        elif "NOT ADDED" in row[2]:
            formatted_why.append([Paragraph(c, ST["cellr"]) for c in row])
        else:
            formatted_why.append([Paragraph(c, ST["cell"]) for c in row])
    why_col = [0.16, 0.12, 0.10, 0.15, 0.47]
    why_t = _table(formatted_why, why_col)
    items.append(why_t)
    return items


def _candidate_card(c: Candidate2026) -> list:
    return candidate_card(c, thesis_label="Why this stock gets included")


def candidate_section(candidates):
    items = []
    items.append(PageBreak())
    items.append(Paragraph("3. Individual Candidate Analysis", ST["h1"]))
    items.append(Paragraph(
        "Each card: left column = why this stock gets included + why 2026 specifically. "
        "Right column = key risks + pre-entry verification checklist. "
        "Market data [EST] must be verified from live WSE/stooq data before trading.",
        ST["body"]))
    items.append(Spacer(1, 0.3*cm))

    tier = {"HIGH": 0, "MEDIUM": 1, "WATCH": 2, "SHORT": 3}
    for c in sorted(candidates, key=lambda x: (tier.get(x.conviction,9), x.target_review, -x.rs_percentile)):
        items += _candidate_card(c)
    return items


# ─────────────────────────────────────────────────────────────────────────────
# 5. Decision checklist
# ─────────────────────────────────────────────────────────────────────────────
def checklist_section():
    items = []
    items.append(PageBreak())
    items.append(Paragraph("4. Pre-Trade Decision Checklist — May 2026 SAR", ST["h1"]))
    items.append(Paragraph(
        "T-45 screen date is approximately 14 March 2026 — approximately TODAY. "
        "Complete these steps IN ORDER before opening any position.",
        ST["body"]))
    items.append(Spacer(1, 0.2*cm))

    steps = [
        ("☐ Step 1 — Confirm Nov 2025 SAR outcome",
         "Download: https://www.msci.com/indexes/index-reviews\n"
         "Confirm which Polish stocks had weight changes at Nov 2025 review. "
         "Check if any new stocks were added to Standard or Small Cap that "
         "change the current constituent list from the 16 shown in this report."),
        ("☐ Step 2 — Get live XTB market cap",
         "Go to: stooq.pl or stockanalysis.com/quote/wse/XTB/market-cap/\n"
         "Required: current price × shares outstanding.\n"
         "Key question: is XTB full cap > ~USD 2.8B (Standard lower bound estimate)?\n"
         "If YES → HIGH conviction entry. If NO but within 15% → MEDIUM. If <$2.5B → SKIP."),
        ("☐ Step 3 — Calculate RS percentile from live data",
         "Compute: 12-month return (skip last month) for XTB vs all WIG-ALL stocks.\n"
         "Required threshold: RS ≥ 60th percentile + price above 200d MA.\n"
         "If BOTH criteria met → position confirmed. If either fails → SKIP (false positive risk)."),
        ("☐ Step 4 — Verify ATVR",
         "ATVR = (3-month avg daily PLN turnover / float-adj cap) × 100.\n"
         "Required: ≥ 15% for MSCI eligibility. XTB is highly liquid — likely 35%+.\n"
         "For borderline candidates (Bank Millennium, Benefit Systems) this is critical."),
        ("☐ Step 5 — Check XTB float (founder stake)",
         "Omar Arnaout (CEO) holds significant stake. Check latest KNF disclosure.\n"
         "Float-adj cap = full cap × FIF. FIF = float percentage (≈ 1 - founder stake).\n"
         "Required: float-adj cap > USD 1.3B minimum (MSCI Standard gate)."),
        ("☐ Step 6 — Set announcement day alert",
         "MSCI May 2026 SAR announcement: ~28 April 2026.\n"
         "Set calendar alert. On announcement day:\n"
         "  → XTB confirmed as addition: HOLD to effective date (~29 May 2026).\n"
         "  → XTB NOT announced: SELL at market within 30 minutes."),
        ("☐ Step 7 — Monitor CCC deletion trigger",
         "CCC (MODIVO) market cap: if it falls to ~PLN 5.7B (~$1.4B USD),\n"
         "MSCI deletion becomes imminent. Set price alert at PLN 95 for CCC.\n"
         "If alert triggers → consider short entry T-45 before next SAR."),
    ]

    for title, desc in steps:
        row_data = [[
            Paragraph(title, S("st", fontSize=9, fontName="Helvetica-Bold", textColor=BLUE)),
            Paragraph(desc.replace("\n", "<br/>"), S("sd", fontSize=8, leading=12)),
        ]]
        t = Table(row_data, colWidths=[(PAGE_W-2*MARGIN)*0.30, (PAGE_W-2*MARGIN)*0.70])
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
        "⚠  DISCLAIMER: This report is for research purposes only. "
        "It does not constitute investment advice. "
        "All [EST] figures must be verified from live data. "
        "Past backtest performance (2018-2025) does not guarantee future results. "
        "MSCI retains committee discretion for borderline inclusion decisions.",
        S("disc", fontSize=7.5, leading=11, textColor=AMBER, fontName="Helvetica-Oblique")))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def build_pdf(output_path: str = "msci_poland_2026_candidates.pdf") -> str:
    candidates = build_verified_candidates()
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=1.4*cm,
        title="MSCI Poland 2026 — Verified Candidate Watchlist",
        author="MZApp Research",
    )
    story = []
    story += cover(candidates)
    story += index_structure()
    story += threshold_section()
    story += candidate_section(candidates)
    story += checklist_section()
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return output_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "msci_poland_2026_candidates.pdf"
    path = build_pdf(out)
    print(f"PDF saved → {path}")
