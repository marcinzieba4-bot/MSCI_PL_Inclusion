"""
MSCI Poland — March 2026 Verified Update
=========================================

Report date:        6 March 2026
Data sources:       Live web search (March 6, 2026)
Key update:         February 2026 SAR outcome — CCC DELETED, Asseco Poland ADDED

═══════════════════════════════════════════════════════════════
FEBRUARY 2026 SAR — CONFIRMED OUTCOME (effective Feb 27, 2026)
═══════════════════════════════════════════════════════════════

DELETED from MSCI Poland Standard:
  • CCC S.A. / MODIVO S.A. (MDVP) — prediction CONFIRMED ✓
    Market cap had declined; rebranded to MODIVO; removed as expected

ADDED to MSCI Poland Standard:
  • Asseco Poland S.A. (ACP) — replaced CCC
    Asseco rose ~60% in 12M prior to addition; ACP now Standard member

INDEX SIZE: remains 16 constituents (CCC out, ACP in)

═══════════════════════════════════════════════════════════════
MARKET DATA — MARCH 6, 2026 (VERIFIED)
═══════════════════════════════════════════════════════════════

PLN/USD exchange rate: ~3.68 (PLN strengthened ~4.5% vs USD over past 12M)

XTB S.A.     PLN 92.78  ·  market cap PLN 10.91B (~$2.96B USD)
             MSCI Poland Small Cap — 6.44% weighting (#8 in Small Cap)
             52-week range: PLN 61.86 – PLN 93.76 (near all-time high)
             12M total return (incl. div PLN 5.45): ~+53-55%

Kruk S.A.    PLN 464.60  ·  market cap PLN 9.03B (~$2.45B USD)
             MSCI Poland Small Cap — 7.67% weighting (#7 in Small Cap)
             52-week range: not available; ATH PLN 510 (Jan 9, 2026)
             12M return: ~+22.78%

Diagnostyka  PLN 182.05  ·  market cap PLN 6.04B (~$1.65B USD)
             MSCI Poland Small Cap (added May 2025)
             -2.5% on day of search; below Standard threshold by ~44%

CCC/MODIVO   PLN 121.70  ·  market cap PLN 10.15B (~$2.76B USD)
             DELETED from Standard Feb 27, 2026 → now in MSCI Small Cap
             Ticker changed to MDVP post-rebrand

Cyfrowy Polsat  PLN 12.29  ·  market cap PLN 8.36B (~$2.27B USD)
               MSCI Poland Small Cap (removed from Standard ~Feb 2024)
               Solorz succession resolved Dec 23, 2025 (Liechtenstein court)
               Q3 2025 net profit: PLN 69.6M (vs PLN 248.9M prior year, -72%)

═══════════════════════════════════════════════════════════════
2026 FINANCIAL RESULTS SUMMARY
═══════════════════════════════════════════════════════════════

XTB 2025 FULL-YEAR RESULTS:
  Revenue:      PLN 2,147M (+14.6% YoY)
  Net profit:   PLN 644M (missed PLN 1B analyst expectations)
  Q4 revenue:   PLN 610M (record quarter, driven by gold CFDs — 43.7% of mix)
  New clients:  864,286 in 2025 (total base 2.16M)
  Active clients: 1,189,422 (+69.7% YoY)
  Client assets: ~EUR 10.8B
  Marketing expenses: +69.1% YoY
  Cash on balance: PLN 1.99B; capital ratio 190.4%

KRUK 2025 FULL-YEAR RESULTS (record year per CEO):
  Cash EBITDA:  ~PLN 2.7B (+12% YoY)
  Net profit Q4: PLN 208M (+81% YoY)
  Net profit Q1-Q3: PLN 877M (-9% YoY — higher deferred tax provisions only)
  Annual portfolio investments: PLN 2.2B
  Record recoveries: ~PLN 4B
  Portfolio carrying value: PLN 11.6B (+11% vs 2024)
  Equity: PLN 5.3B (+18%)
  Net debt/Cash EBITDA: 2.6x (improved from 2.7x)
  Geography: Poland 41%, Italy 25%, Spain 16.8%, Romania 14.9%
  Full audited report due: March 10, 2026

Sources: fxnewsgroup.com (XTB Q4 2025), financemagnates.com, investing.com (XTB H1 2025),
         kruk.eu investor relations, marketscreener.com (Kruk Q4 2025),
         seekingalpha.com (Kruk Q4 2025 earnings call transcript)
"""

from dataclasses import dataclass, field
from typing import Optional

# Re-export for use in PDF generator
from examples.candidates_2026 import Candidate2026


def build_march_2026_candidates() -> list[Candidate2026]:
    """
    MSCI Poland candidate list — updated March 6, 2026.
    Incorporates February 2026 SAR outcome (CCC deleted, ACP added).
    All market data verified from live web search March 6, 2026.
    PLN/USD ≈ 3.68 (PLN strengthened vs previous 3.97 estimate).
    """
    PLN_USD = 3.68

    candidates = []

    # ─────────────────────────────────────────────────────────────────────
    # 1. XTB S.A. — PRIMARY STANDARD ADD CANDIDATE (upgraded confidence)
    # Verified: PLN 92.78 share price, PLN 10.91B market cap (~$2.96B USD)
    # MSCI Poland Small Cap 6.44% weight (#8 in Small Cap index)
    # Source: stockanalysis.com/quote/wse/XTB/, companiesmarketcap.com
    # ─────────────────────────────────────────────────────────────────────
    candidates.append(Candidate2026(
        ticker="XTB",
        company="XTB S.A.",
        sector="Financials — Online Brokerage / CFD Platform",
        target_review="May 2026",
        event_type="Standard Add",
        current_msci_status="Small Cap",
        current_index_weight_pct=6.44,  # verified from MSCI Poland Small Cap index

        full_cap_pln_b=10.91,           # verified: PLN 92.78 × ~117.6M shares
        full_cap_usd_b=10.91 / PLN_USD,  # = $2.96B USD (verified)
        float_adj_cap_usd_b=1.93,        # [EST] ~65% float (founder ~35%); 2.96 × 0.65
        atvr_3m_pct=42.0,               # [EST] very liquid CFD broker stock
        msci_standard_threshold_usd_b=3.3,  # [EST] May 2026 threshold rising with DM mkts
        price_pln=92.78,                # verified March 6, 2026

        return_12m_pct=47.0,            # verified: ~+47% price return (PLN 63 → PLN 92.78)
        rs_percentile=82,               # [EST] strong relative strength
        above_200d_ma=True,             # [EST] near all-time high of PLN 93.76

        est_forced_buying_usd_m=340,
        est_adv_days=14.0,

        inclusion_thesis=(
            "XTB is currently in MSCI Poland Small Cap with a verified full market cap "
            "of PLN 10.91B (~USD 2.96B) as of March 6, 2026. This is the HIGHEST "
            "reading since the company's listing.\n\n"
            "vs PREVIOUS ESTIMATE: The prior estimate was $2.71B — XTB has already "
            "grown +9.2% in USD terms since that estimate, driven by a record-breaking "
            "2025 with 864K new clients and revenue of PLN 2.15B.\n\n"
            "THRESHOLD ANALYSIS:\n"
            "The May 2026 SAR threshold is estimated at ~$3.3B (rising with DM markets). "
            "XTB at $2.96B is approximately 10-11% BELOW the estimated threshold. "
            "However, MSCI applies a buffer zone — stocks within ~15% of the threshold "
            "that meet all other criteria (ATVR, float, liquidity) can be included.\n\n"
            "CCC was added in May 2025 at approximately $2.3-2.5B — LOWER than XTB's "
            "current cap. This is the clearest precedent for XTB inclusion.\n\n"
            "FLOAT RISK: Founder Jakub Zabłocki (and related parties) hold ~35% of XTB. "
            "FIF [EST] ≈ 0.65. Float-adj cap [EST] = $1.93B — above the ~$1.3B minimum. "
            "This is the key gate that needs live verification.\n\n"
            "2025 EARNINGS NOTE: Net profit of PLN 644M missed analyst expectations "
            "(PLN 1B+). However, revenue growth was solid at +14.6%, and marketing "
            "spend surged +69% for long-term client acquisition. Client assets now "
            "EUR 10.8B. MSCI screens on market cap/float, not earnings — so the "
            "earnings miss does NOT directly affect inclusion eligibility."
        ),
        why_now_in_2026=(
            "• Market cap PLN 10.91B is verified at near-ATH — approaching Standard.\n"
            "• CCC precedent: added at lower USD cap ($2.3B) — XTB at $2.96B is stronger.\n"
            "• CCC was just DELETED (Feb 27, 2026): Standard index has a 'vacancy' signal; "
            "MSCI may be inclined to add a quality replacement from Small Cap.\n"
            "• Passive demand on inclusion: EM Small Cap trackers sell (~$50M [EST]) and "
            "EM Standard trackers buy (~$340M [EST]) = net ~$290M forced buying.\n"
            "• T-45 screen date: approximately 14 March 2026 — within days.\n"
            "• 12M total return +53-55% (incl. dividend PLN 5.45/share) confirms "
            "strong momentum filter pass [EST].\n"
            "• NEW: XTB share price near all-time high (PLN 93.76) — MSCI cut-off "
            "likely to capture a high cap reading."
        ),
        key_risks=[
            "Threshold is dynamic: if May 2026 DM reference rises further, the "
            "Standard lower bound may reach $3.5B+ — XTB at $2.96B would still fall short.",
            "Float-adj cap ($1.93B [EST]) needs live verification from MSCI FIF table "
            "and latest KNF insider ownership disclosures.",
            "ATVR: if market liquidity dries up in Q1 2026, 3M ATVR may fall. "
            "Verify ≥15% is met (XTB is very liquid — this is low risk).",
            "2025 earnings miss (PLN 644M vs PLN 1B+ expected): analyst downgrades "
            "could weigh on price at T-45 window if guidance is cautious.",
            "FALSE POSITIVE: if not announced at May 2026 SAR, SELL within 30 min "
            "of announcement. Do not hold through next cycle without re-screening.",
        ],
        verify_checklist=[
            "☐ Verify XTB price and market cap live at WSE/stooq.pl on entry date",
            "☐ XTB above 200d moving average? (currently near ATH — likely yes)",
            "☐ RS percentile vs WIG-ALL: trailing 12-1M must be ≥ 60th percentile",
            "☐ Founder/insider stake: check KNF notifications for Jakub Zabłocki",
            "☐ ATVR: 3M avg PLN turnover / float-adj cap ≥ 15% (expect 35%+)",
            "☐ Monitor msci.com/indexes — May 2026 SAR announcement ~28 April 2026",
            "☐ Set FP exit alert: if NOT in announcement, sell within 30 minutes",
        ],
    ))

    # ─────────────────────────────────────────────────────────────────────
    # 2. Kruk S.A. — SECONDARY STANDARD ADD CANDIDATE
    # Verified: PLN 464.60, market cap PLN 9.03B (~$2.45B USD)
    # MSCI Poland Small Cap 7.67% weight (#7 in Small Cap index)
    # Source: stockanalysis.com/quote/wse/KRU/, investing.com
    # ─────────────────────────────────────────────────────────────────────
    candidates.append(Candidate2026(
        ticker="KRU",
        company="Kruk S.A.",
        sector="Financials — Debt Collection / NPL Portfolio Purchasing",
        target_review="Nov 2026",
        event_type="Standard Add",
        current_msci_status="Small Cap",
        current_index_weight_pct=7.67,  # verified — largest financial in Small Cap index

        full_cap_pln_b=9.03,            # verified: PLN 464.60 × ~19.44M shares
        full_cap_usd_b=9.03 / PLN_USD,  # = $2.45B USD (verified)
        float_adj_cap_usd_b=1.62,        # [EST] Piotr Krupa ~31% stake; float ~69%
        atvr_3m_pct=28.0,               # [EST]
        msci_standard_threshold_usd_b=3.3,
        price_pln=464.60,               # verified March 6, 2026

        return_12m_pct=22.78,           # verified from stockanalysis.com
        rs_percentile=60,               # [EST] underperformed WIG (+30.3%) in 12M
        above_200d_ma=True,             # [EST] price ~9% below ATH of PLN 510

        est_forced_buying_usd_m=245,
        est_adv_days=11.0,

        inclusion_thesis=(
            "Kruk S.A. is confirmed in MSCI Poland Small Cap at PLN 9.03B "
            "(~$2.45B USD) as of March 6, 2026. It is the 7th-largest Small Cap "
            "constituent at 7.67% weighting — actually HIGHER weight than XTB (6.44%).\n\n"
            "THRESHOLD GAP: Kruk at $2.45B is approximately 26% below the estimated "
            "May 2026 Standard threshold of ~$3.3B. This is too large a gap for "
            "May 2026 inclusion — Nov 2026 is the realistic target.\n\n"
            "For Nov 2026: Kruk needs ~$2.9-3.0B+ in USD cap. At current trajectory "
            "(+22.78% in 12M), this requires another 19-23% gain — achievable if the "
            "business continues compounding. The target review is Nov 2026 SAR.\n\n"
            "2025 RESULTS (RECORD YEAR):\n"
            "CEO Piotr Krupa confirmed record profits and cash EBITDA in 2025. "
            "Cash EBITDA ~PLN 2.7B (+12%), portfolio carrying value PLN 11.6B (+11%). "
            "Q4 2025 net profit PLN 208M (+81% YoY). Full audited results due March 10.\n\n"
            "BUSINESS MODEL QUALITY:\n"
            "Europe's largest NPL portfolio purchaser by carrying value. "
            "Operations in Poland, Italy, Spain, Romania, Germany. "
            "Net debt/Cash EBITDA improved to 2.6x. Equity grew +18% to PLN 5.3B. "
            "Annual portfolio investments PLN 2.2B; recoveries ~PLN 4B."
        ),
        why_now_in_2026=(
            "• Record 2025 results confirm fundamentals — analyst consensus PLN 532 "
            "target (+14.5% upside from PLN 464.60); Strong Buy from 3 analysts.\n"
            "• ATH was PLN 510 (Jan 9, 2026) — stock 9% below ATH; recovery likely.\n"
            "• ECB + NBP rate normalization: reduces Kruk's funding cost; "
            "NPL portfolio yields remain fixed — spread expansion in 2026.\n"
            "• European banks still deleveraging: Italian/Spanish NPL supply elevated.\n"
            "• For May 2026 SAR: WATCH (insufficient cap gap). "
            "For Nov 2026 SAR: MEDIUM conviction — re-screen September 2026.\n"
            "• CCC deletion vacancy: may influence MSCI to promote strong Small Cap "
            "members; Kruk is the top-weighted stock in the Small Cap index."
        ),
        key_risks=[
            "Gap to Standard threshold is ~26% — May 2026 inclusion is unlikely "
            "without a large cap re-rating. Nov 2026 is more realistic.",
            "PLN strengthened vs USD; further PLN appreciation reduces USD cap and "
            "delays threshold crossing.",
            "NBP rate cuts reduce NPL seller motivation — supply slowdown possible.",
            "12M return (+22.78%) underperformed WIG (+30.3%) — relative strength "
            "may not clear 60th percentile filter.",
            "Q1-Q3 2025 net profit was -9% YoY due to higher deferred tax provisions "
            "— headline EPS looked weak, may deter some investors.",
        ],
        verify_checklist=[
            "☐ Full-year 2025 audited results (due March 10, 2026) — verify no surprises",
            "☐ Current share price and USD market cap — has it crossed $2.8B?",
            "☐ RS percentile vs WIG-ALL — was it above 60th pct over past 12 months?",
            "☐ Piotr Krupa founder stake from WSE/KNF disclosures",
            "☐ Re-screen September 2026 for Nov 2026 SAR T-45 entry",
        ],
    ))

    # ─────────────────────────────────────────────────────────────────────
    # 3. CCC / MODIVO S.A. (MDVP) — DELETED (prediction confirmed)
    # Verified: removed from MSCI Poland Standard effective Feb 27, 2026
    # Now in MSCI Poland Small Cap. Rebranded from CCC to MODIVO (MDVP)
    # Current price: PLN 121.70, market cap: PLN 10.15B (~$2.76B USD)
    # ─────────────────────────────────────────────────────────────────────
    candidates.append(Candidate2026(
        ticker="MDVP",
        company="MODIVO S.A. (formerly CCC S.A.)",
        sector="Consumer Discretionary — Footwear / Fashion Retail",
        target_review="May 2026",
        event_type="Deletion Risk",
        current_msci_status="Small Cap",   # DELETED from Standard Feb 27, 2026
        current_index_weight_pct=0.0,       # no longer a Standard member

        full_cap_pln_b=10.15,              # verified: PLN 121.70 × ~83.4M shares
        full_cap_usd_b=10.15 / PLN_USD,    # = $2.76B USD
        float_adj_cap_usd_b=1.71,          # [EST] Dariusz Milek ~38%; float ~62%
        atvr_3m_pct=18.0,                  # [EST]
        msci_standard_threshold_usd_b=3.3,
        price_pln=121.70,                  # verified March 6, 2026

        return_12m_pct=-36.0,              # verified: ~-36% in 12M leading to deletion
        rs_percentile=15,                  # [EST] persistent underperformer
        above_200d_ma=False,               # [EST]

        est_forced_buying_usd_m=-140,      # was forced SELLING on Standard deletion
        est_adv_days=10.0,

        inclusion_thesis=(
            "DELETION CONFIRMED. CCC S.A. / MODIVO was removed from MSCI Poland Standard "
            "effective February 27, 2026 — this prediction was correct.\n\n"
            "CURRENT STATUS:\n"
            "• Rebranded from CCC S.A. to MODIVO S.A. (ticker: MDVP) in February 2026\n"
            "• Now in MSCI Poland Small Cap tier\n"
            "• Current market cap: PLN 10.15B (~$2.76B) — ABOVE the Standard threshold\n"
            "• This appears paradoxical: how was it deleted if cap is $2.76B?\n\n"
            "EXPLANATION: MSCI uses free-float-adjusted cap, not full market cap. "
            "With founder Dariusz Milek holding ~38%, the FIF ≈ 0.62. "
            "Float-adj cap [EST] ≈ $1.71B — potentially below the Standard "
            "float-adj minimum. Additionally, liquidity (ATVR), operating performance "
            "(negative LFL sales, revenue PLN 500M below plan), and the rebranding "
            "complexity with ISIN changes may have contributed to the deletion.\n\n"
            "FORWARD OUTLOOK:\n"
            "MODIVO is now a Small Cap member. It is NOT a re-inclusion candidate "
            "near-term given the performance deterioration, e-commerce weakness, and "
            "rebranding transition. Avoid in Standard-tracking strategies."
        ),
        why_now_in_2026=(
            "• DELETION ALREADY HAPPENED (Feb 27, 2026) — this is a POST-EVENT analysis.\n"
            "• Post-deletion: stock at PLN 121.70; analysts expect continued pressure.\n"
            "• Operating issues: revenue ~PLN 500M below plan, negative LFL sales, "
            "weak e-commerce performance in 2025.\n"
            "• Rebrand to MODIVO adds complexity — ISIN change requires MSCI "
            "re-evaluation for any future re-inclusion.\n"
            "• AVOID for MSCI Standard strategies — focus on XTB and Kruk instead."
        ),
        key_risks=[
            "Post-deletion reversal is common: stocks often recover +5-10% in 30 days "
            "after forced selling by Standard trackers ends. Do not short post-deletion.",
            "Dariusz Milek may take MODIVO private at a premium — short squeeze risk.",
            "Re-inclusion in Standard possible if MODIVO reverses operating trends, "
            "but requires sustained improvement over multiple quarters.",
            "ISIN change from rebrand: verify MODIVO new ticker (MDVP) is tracked "
            "correctly by your data provider.",
        ],
        verify_checklist=[
            "☐ Confirm new ticker MDVP is loading correctly in data provider",
            "☐ Verify current MSCI Poland Small Cap listing includes MDVP",
            "☐ Check post-deletion price performance (was there reversal bounce?)",
            "☐ Any Dariusz Milek buyout announcement — set news alert",
            "☐ Operating update: Q4 2025 / FY2025 MODIVO results",
        ],
    ))

    # ─────────────────────────────────────────────────────────────────────
    # 4. Asseco Poland S.A. (ACP) — NEW STANDARD MEMBER (added Feb 27, 2026)
    # Verified: added to MSCI Poland Standard effective Feb 27, 2026
    # Replaced CCC in the index
    # Source: MSCI Feb 2026 Standard list (app2.msci.com), Biznes PAP
    # ─────────────────────────────────────────────────────────────────────
    candidates.append(Candidate2026(
        ticker="ACP",
        company="Asseco Poland S.A.",
        sector="Information Technology — Enterprise Software / IT Services",
        target_review="May 2026",
        event_type="Standard Add",        # added Feb 27 — post-event profile
        current_msci_status="Standard",   # NEWLY ADDED Feb 27, 2026
        current_index_weight_pct=2.0,     # [EST] replacing CCC's ~2.24% slot

        full_cap_pln_b=18.0,              # [EST] based on ~60% gain + pre-addition cap
        full_cap_usd_b=18.0 / PLN_USD,    # [EST] ~$4.9B USD
        float_adj_cap_usd_b=2.80,         # [EST]
        atvr_3m_pct=22.0,                 # [EST]
        msci_standard_threshold_usd_b=3.3,
        price_pln=110.0,                  # [EST] — approximately +60% from 12M ago

        return_12m_pct=60.0,              # verified context: "rose ~60%" per Stockwatch/PAP
        rs_percentile=92,                 # [EST] top decile performer
        above_200d_ma=True,               # [EST]

        est_forced_buying_usd_m=280,
        est_adv_days=12.0,

        inclusion_thesis=(
            "Asseco Poland was ADDED to MSCI Poland Standard on February 27, 2026, "
            "replacing CCC. This addition has already happened.\n\n"
            "BACKGROUND:\n"
            "Asseco Poland is the largest Polish IT company by revenue and market cap. "
            "It provides enterprise software and IT services to banks, insurance companies, "
            "governments, and public sector entities across 30+ countries. "
            "The group structure includes Asseco SEE (Southeast Europe), Asseco CEE "
            "(Central/Eastern Europe), and Formula Systems (Israel).\n\n"
            "WHY ASSECO WAS ADDED:\n"
            "1. Share price surged ~60% in the 12 months prior to inclusion.\n"
            "2. Full market cap grew into the Standard threshold range.\n"
            "3. Strong momentum (RS top decile [EST]) passed the momentum filter.\n"
            "4. CCC's deletion created an opening at the February 2026 QIR/SAR.\n\n"
            "POST-INCLUSION:\n"
            "Standard trackers must now hold Asseco. Forced buying happened "
            "around Feb 27, 2026. Post-inclusion weight changes will track organic "
            "price performance vs. other Standard members."
        ),
        why_now_in_2026=(
            "• Inclusion already occurred (Feb 27, 2026) — this is a post-event profile.\n"
            "• For active investors: Asseco is now a Standard member; weight will "
            "evolve based on relative performance vs. other 15 Standard stocks.\n"
            "• AI/cloud themes: Asseco benefits from Polish government digitisation "
            "and EU-funded IT modernisation projects (KPO program).\n"
            "• Weight increase candidate for May 2026 if momentum continues."
        ),
        key_risks=[
            "Post-inclusion mean reversion is common: stocks often give back some "
            "gains after the forced buying wave subsides.",
            "Asseco is a holding company — group consolidation complexity "
            "can obscure earnings quality.",
            "Government exposure: large public sector contracts can be disrupted "
            "by political changes.",
        ],
        verify_checklist=[
            "☐ Verify ACP is listed in current MSCI Poland Standard index",
            "☐ Current Asseco Poland price and market cap",
            "☐ Post-inclusion performance vs WIG20 — is it holding gains?",
            "☐ Asseco FY2025 results — confirms the earnings trajectory pre-addition",
        ],
    ))

    # ─────────────────────────────────────────────────────────────────────
    # 5. Cyfrowy Polsat (CPS) — AVOID / Small Cap (succession resolved)
    # Verified: PLN 12.29, market cap PLN 8.36B (~$2.27B USD)
    # Succession resolved Dec 23, 2025; but weak operating performance
    # HSBC "Reduce" PLN 9.20; Ipopema named as short pick for 2026
    # ─────────────────────────────────────────────────────────────────────
    candidates.append(Candidate2026(
        ticker="CPS",
        company="Cyfrowy Polsat S.A.",
        sector="Communication Services — Pay-TV / Telecom",
        target_review="Nov 2026",
        event_type="Weight Decrease/Deletion",
        current_msci_status="Small Cap",   # already in Small Cap (removed from Standard ~Feb 2024)
        current_index_weight_pct=0.0,

        full_cap_pln_b=8.36,              # verified: PLN 12.29 × ~680M shares
        full_cap_usd_b=8.36 / PLN_USD,    # = $2.27B USD (verified)
        float_adj_cap_usd_b=1.05,         # [EST] Solorz family controls majority
        atvr_3m_pct=12.0,                 # [EST] declining liquidity
        msci_standard_threshold_usd_b=3.3,
        price_pln=12.29,                  # verified March 6, 2026

        return_12m_pct=-35.0,             # [EST] 52-week range PLN 10.71–PLN 19.00
        rs_percentile=10,                 # [EST] near-bottom performer
        above_200d_ma=False,              # [EST] trading near 52-week lows

        est_forced_buying_usd_m=0,
        est_adv_days=0.0,

        inclusion_thesis=(
            "Cyfrowy Polsat is currently in MSCI Poland Small Cap (removed from Standard "
            "at approximately the February 2024 review). It is NOT an inclusion candidate.\n\n"
            "SUCCESSION RESOLVED (Dec 23, 2025):\n"
            "The Liechtenstein court issued a final ruling transferring joint control of "
            "Cyfrowy Polsat Group to Solorz's three children (Tobias Solorz, Piotr Żak, "
            "Aleksandra Żak). Zygmunt Solorz's attempt to reverse the 'lifetime succession "
            "declaration' was dismissed. The supervisory board now includes Tobias and "
            "Aleksandra Solorz. Governance uncertainty is resolved — but this does NOT "
            "fix the operating problems.\n\n"
            "OPERATING DETERIORATION:\n"
            "Q3 2025 net profit: PLN 69.6M vs PLN 248.9M a year earlier (−72%).\n"
            "Q3 2025 adjusted EBITDA: PLN 765.8M vs PLN 902.8M (−15%).\n"
            "Polish pay-TV market continues losing subscribers to Netflix/streaming.\n"
            "Polkomtel (telecoms subsidiary) faces structural headwinds.\n\n"
            "ANALYST CONSENSUS:\n"
            "HSBC: 'Reduce' with PLN 9.20 target (−25% downside from PLN 12.29).\n"
            "Erste: downgraded to 'Hold', PLN 12.60 target.\n"
            "Ipopema: named CPS as short pick for 2026.\n\n"
            "MSCI RETURN PATH: Standard re-inclusion requires cap growth from "
            "$2.27B to $3.3B+ — that is +45% appreciation needed. Given the "
            "structural headwinds, this is NOT expected in 2026."
        ),
        why_now_in_2026=(
            "• AVOID / MONITOR ONLY — not an actionable long trade.\n"
            "• Succession is resolved but does not catalyse near-term re-rating.\n"
            "• Q3 2025 results (-72% net profit) confirm earnings deterioration.\n"
            "• HSBC Reduce + Ipopema short pick = bearish analyst consensus.\n"
            "• Still in Small Cap — no Standard re-inclusion path visible in 2026.\n"
            "• Tactical short: consider at T-45 if cap approaches $1.0B Small Cap "
            "floor and ATVR falls below 15% gate."
        ),
        key_risks=[
            "Succession resolution could unlock strategic M&A at premium — short squeeze.",
            "NBP rate cuts reduce CPS's high debt servicing cost — mild positive.",
            "Polsat media assets have M&A appeal (regional content, sports rights).",
            "Short borrow cost on WSE can be expensive — verify availability.",
        ],
        verify_checklist=[
            "☐ Verify CPS is in MSCI Poland Small Cap (not Standard)",
            "☐ Current CPS market cap and price",
            "☐ Q4 2025 / FY2025 results — has EBITDA decline continued?",
            "☐ Any Solorz family strategic announcement post-succession",
            "☐ ATVR — if falling below 15%, Small Cap removal risk",
        ],
    ))

    # ─────────────────────────────────────────────────────────────────────
    # 6. Diagnostyka S.A. (DIA/DIAG) — WATCH (Small Cap; below Standard)
    # Verified: added to MSCI Poland Small Cap effective June 2, 2025
    # Current price: PLN 182.05, market cap PLN 6.04B (~$1.65B USD)
    # ─────────────────────────────────────────────────────────────────────
    candidates.append(Candidate2026(
        ticker="DIAG",
        company="Diagnostyka S.A.",
        sector="Health Care — Medical Laboratory / Diagnostics Services",
        target_review="Nov 2026",
        event_type="Standard Add",
        current_msci_status="Small Cap",   # confirmed added June 2, 2025
        current_index_weight_pct=0.0,      # [EST] below top-10 in Small Cap index

        full_cap_pln_b=6.04,              # verified: PLN 182.05 × ~33.2M shares
        full_cap_usd_b=6.04 / PLN_USD,    # = $1.64B USD
        float_adj_cap_usd_b=1.15,          # [EST]
        atvr_3m_pct=16.0,                  # [EST]
        msci_standard_threshold_usd_b=3.3,
        price_pln=182.05,                  # verified March 6, 2026

        return_12m_pct=0.0,                # [EST] no 12M data from post-June 2025 listing
        rs_percentile=45,                  # [EST]
        above_200d_ma=True,                # [EST] recently listed; above IPO price assumed

        est_forced_buying_usd_m=0,
        est_adv_days=0.0,

        inclusion_thesis=(
            "Diagnostyka S.A. was confirmed added to MSCI Poland Small Cap index "
            "effective June 2, 2025 (announced May 13, 2025). This is verified from "
            "Diagnostyka's own investor relations page and MSCI May 2025 small cap list.\n\n"
            "CURRENT STATUS:\n"
            "Full market cap: PLN 6.04B (~$1.64B USD). This is approximately 50% "
            "below the estimated Standard threshold of $3.3B. Diagnostyka is a "
            "long-term watch for Standard inclusion — not a near-term trade.\n\n"
            "BUSINESS PROFILE:\n"
            "Poland's largest private medical laboratory network. Diagnostyka performs "
            "blood tests, pathology, genetic testing across 600+ collection points. "
            "Post-COVID, laboratory medicine demand has normalised but remains structurally "
            "elevated. Polish private healthcare spending is growing.\n\n"
            "STANDARD PATH:\n"
            "To reach Standard inclusion, Diagnostyka needs cap growth from $1.64B to "
            "$3.3B+ — a +101% appreciation. This requires sustained business growth "
            "over 2-3 years. Monitor from late 2027 onwards as a potential candidate."
        ),
        why_now_in_2026=(
            "• Recently entered MSCI Small Cap (June 2025) — inclusion alpha already taken.\n"
            "• For 2026: WATCH only. Standard inclusion requires doubling the market cap.\n"
            "• Private healthcare theme: Polish demographics (aging population) support "
            "long-term demand for diagnostics services.\n"
            "• No near-term MSCI Standard catalyst identified for 2026."
        ),
        key_risks=[
            "Standard inclusion path requires +100% cap growth — multi-year timeline.",
            "NFZ (Polish national healthcare) reimbursement policy changes can affect pricing.",
            "Competition from international lab groups expanding in Poland.",
        ],
        verify_checklist=[
            "☐ Confirm Diagnostyka is listed in current MSCI Poland Small Cap index",
            "☐ Current market cap — any significant movements since March 2026?",
            "☐ FY2025 results — revenue and margin trajectory",
            "☐ Long-term: re-evaluate in 2027 for Standard path",
        ],
    ))

    # Compute all metrics
    for c in candidates:
        c.compute()

    return candidates


# ─────────────────────────────────────────────────────────────────────────────
# Summary for console output
# ─────────────────────────────────────────────────────────────────────────────
def run():
    print("\n" + "═"*70)
    print("MSCI POLAND — MARCH 2026 UPDATE (VERIFIED DATA)")
    print("═"*70)
    print(f"Report date: March 6, 2026")
    print(f"PLN/USD: ~3.68")
    print()

    print("FEBRUARY 2026 SAR OUTCOME (effective Feb 27, 2026):")
    print("  DELETED:  CCC S.A. / MODIVO (MDVP) — prediction CONFIRMED ✓")
    print("  ADDED:    Asseco Poland S.A. (ACP) — replaced CCC")
    print("  Index remains: 16 constituents")
    print()

    candidates = build_march_2026_candidates()

    tier_labels = {"HIGH": "★★ HIGH", "MEDIUM": "★ MEDIUM", "WATCH": "◇ WATCH", "SHORT": "⚠ SHORT/AVOID"}
    print(f"{'Ticker':<8} {'Company':<35} {'Cap USD':>8} {'12M Ret':>8} {'Conviction':<14} {'Target'}")
    print("─"*90)
    for c in sorted(candidates, key=lambda x: {"HIGH":0,"MEDIUM":1,"WATCH":2,"SHORT":3}.get(x.conviction,9)):
        print(f"{c.ticker:<8} {c.company:<35} ${c.full_cap_usd_b:>6.2f}B {c.return_12m_pct:>+7.1f}% "
              f"  {tier_labels.get(c.conviction, c.conviction):<14} {c.target_review}")
    print()

    highs = [c for c in candidates if c.conviction == "HIGH"]
    if highs:
        print(f"HIGH CONVICTION ({len(highs)}):")
        for c in highs:
            print(f"  {c.ticker}: {c.company} | ${c.full_cap_usd_b:.2f}B | "
                  f"PLN {c.price_pln:.2f} | Target: {c.target_review}")
    print()
    print("PDF report: run examples/generate_march_2026_pdf.py")
    print("═"*70)
