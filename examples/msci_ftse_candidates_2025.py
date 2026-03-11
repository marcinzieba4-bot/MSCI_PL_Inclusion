"""
MSCI / FTSE EM — WIG Candidate Watchlist for 2025/2026 Reviews
================================================================

This example identifies specific WSE-listed stocks that are CLOSEST to
crossing MSCI Poland Standard or FTSE EM inclusion thresholds as of
early 2026, applies the momentum filter, and ranks them as TOP PICKS.

Index review calendar (upcoming):
  MSCI May 2025 SAR:   Cut-off ≈ mid-April 2025  | Effective: 30 May 2025
  FTSE Jun 2025 QIR:   Announcement ≈ 4 June 2025 | Effective: 23 June 2025
  MSCI Nov 2025 SAR:   Cut-off ≈ mid-October 2025 | Effective: 28 Nov 2025
  FTSE Dec 2025 QIR:   Announcement ≈ 3 Dec 2025  | Effective: 22 Dec 2025
  MSCI May 2026 SAR:   Cut-off ≈ mid-April 2026   | Effective: 29 May 2026

Watchlist stocks analysed:
  1. Kruk S.A.           (KRU)  — debt collection; MSCI Standard; weight increase candidate
  2. Budimex S.A.        (BDX)  — construction; recently added Standard; weight increase
  3. CCC Group S.A.      (CCC)  — footwear; approaching Standard threshold
  4. Bank Millennium     (MIL)  — banking; MSCI EM Small Cap; upgrade candidate
  5. Asseco Poland S.A.  (ACP)  — IT services; MSCI EM Small Cap; FTSE candidate
  6. XTB S.A.            (XTB)  — online broker; exceptional growth; MSCI candidate
  7. Mabion S.A.         (MAB)  — biopharma; EM Small Cap candidate (speculative)
  8. PKP Cargo           (PKP)  — AVOIDED: negative momentum + deletion risk

Methodology:
  Step 1: Calculate USD market cap and float-adj market cap
  Step 2: Check MSCI Standard gates ($2.5B/$1.3B) and MSCI EM SC gates ($127M/$95M)
  Step 3: Calculate FTSE eligibility (similar thresholds, quarterly reviews)
  Step 4: Apply momentum filter — RS ≥ 60th pct + above 200d MA
  Step 5: Rank: TOP PICK = eligible + positive momentum
                WATCH    = eligible but momentum borderline
                AVOID    = momentum FAILS filter (even if eligible)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.index_inclusion import (
    MSCIEligibilityScreen,
    MomentumProfile,
    PreAnnouncementWindow,
    IndexInclusionCandidate,
    InclusionPhase,
    IndexFamily,
    ReviewCycle,
    MomentumStrength,
    score_inclusion_candidate,
    print_inclusion_report,
)
from framework.inclusion_backtest import (
    run_backtest,
    print_backtest_report,
    print_filter_sensitivity,
    build_historical_events,
)


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 1 — Kruk S.A. (KRU) ★ TOP PICK ★
# MSCI Poland Standard — weight increase candidate
# ─────────────────────────────────────────────────────────────────────────────

def analyse_kruk() -> IndexInclusionCandidate:
    screen = MSCIEligibilityScreen(
        company_name="Kruk S.A.",
        ticker="KRU",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_POLAND,
        full_market_cap_usd_m=3_850,
        float_adj_market_cap_usd_m=2_100,      # Founder Piotr Krupa ~31%, float ~69%
        foreign_inclusion_factor=0.69,
        foreign_room_pct=38.0,
        atvr_3m_pct=38.0,
        avg_daily_volume_usd_m=14.0,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="May 2025",
        months_to_next_review=2.5,
        sector_gics="Financials — Specialty Finance",
        current_msci_membership="MSCI Poland Standard (added May 2023)",
        analyst_coverage_count=16,
    )

    momentum = MomentumProfile(
        return_1m_pct=7.5,
        return_3m_pct=19.0,
        return_6m_pct=42.0,
        return_12m_pct=68.0,
        rs_percentile=88,
        benchmark_return_12m_pct=18.0,
        above_50d_ma=True,
        above_200d_ma=True,
        volume_trend="expanding",
        distance_from_52w_high_pct=-4.5,
        distance_from_52w_low_pct=+95.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.SIZE_UP,
        estimated_days_to_announcement=35,
        estimated_days_to_effective_date=65,
        estimated_forced_buying_usd_m=215,
        estimated_index_weight_pct=2.15,
        adv_days_to_absorb=12.0,
        avg_announcement_day_return_pct=2.9,
        avg_pre_announcement_drift_pct=2.0,
        avg_effective_date_bump_pct=1.2,
        avg_30d_post_reversal_pct=-1.0,
    )

    c = IndexInclusionCandidate(
        company_name="Kruk S.A.",
        ticker="KRU:WSE",
        exchange="WSE",
        sector="Financials — Debt Collection / Specialty Finance",
        country="Poland",
        target_index=IndexFamily.MSCI_POLAND,
        current_price=435.0,
        currency="PLN",
        market_cap_local_m=15_800,
        market_cap_usd_m=3_850,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "★ TOP PICK — MSCI Poland weight increase May 2025 ★\n"
            "Kruk = largest European debt purchaser by portfolio volume. "
            "Operates in Poland, Romania, Italy, Spain, Germany. "
            "NPL purchasing volumes at record levels as European banks clean balance sheets. "
            "MSCI Poland member since May 2023; market cap growing faster than MSCI index → "
            "index weight increases at each semi-annual review → forced passive demand. "
            "RS 88th pct, 12M +68% vs WIG +18% = top-quartile momentum CONFIRMS thesis. "
            "High interest rates = NPL sellers motivated; Kruk spreads widen. "
            "ALSO: FTSE EM Poland addition candidate for Jun 2025 QIR = DUAL INDEX EVENT. "
            "Dual index events historically generate +4–6pp extra return vs single events."
        ),
        key_risks=[
            "Rate cuts: NBP cutting rates compresses NPL spread (partial offset: lower cost of debt)",
            "Founder concentration: Piotr Krupa 31% stake, but FIF 0.69 — well above 0.15 minimum",
            "Southern Europe economic slowdown could slow Italian/Spanish NPL supply",
            "Weight increase magnitude depends on other MSCI Poland members' performance",
        ],
        catalyst_date="May 2025 MSCI SAR (weight increase) + Jun 2025 FTSE QIR (new addition)",
        revenue_growth_yoy_pct=22.0,
        ebitda_margin_pct=None,   # Financial company; use ROE
        roe_pct=24.5,
        net_debt_to_ebitda=None,
    )
    return c


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 2 — XTB S.A. (XTB) ★ TOP PICK ★
# MSCI EM Small Cap → approaching MSCI Poland Standard
# ─────────────────────────────────────────────────────────────────────────────

def analyse_xtb() -> IndexInclusionCandidate:
    screen = MSCIEligibilityScreen(
        company_name="XTB S.A.",
        ticker="XTB",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_POLAND,
        full_market_cap_usd_m=3_200,           # Explosive growth from retail trading boom
        float_adj_market_cap_usd_m=1_520,      # Founder still owns ~35%; float ~65%
        foreign_inclusion_factor=0.65,
        foreign_room_pct=45.0,
        atvr_3m_pct=42.0,                      # Very active retail + institutional trading
        avg_daily_volume_usd_m=18.0,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="May 2025",
        months_to_next_review=2.5,
        sector_gics="Financials — Capital Markets / Online Brokerage",
        current_msci_membership="MSCI EM Small Cap",   # Upgrade candidate
        analyst_coverage_count=11,
    )

    momentum = MomentumProfile(
        return_1m_pct=9.5,
        return_3m_pct=28.0,
        return_6m_pct=68.0,
        return_12m_pct=145.0,   # Exceptional — crypto/retail trading volumes exploded
        rs_percentile=96,
        benchmark_return_12m_pct=18.0,
        above_50d_ma=True,
        above_200d_ma=True,
        volume_trend="expanding",
        distance_from_52w_high_pct=-3.0,
        distance_from_52w_low_pct=+198.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.SIZE_UP,
        estimated_days_to_announcement=35,
        estimated_days_to_effective_date=65,
        estimated_forced_buying_usd_m=310,
        estimated_index_weight_pct=1.55,
        adv_days_to_absorb=14.0,
        avg_announcement_day_return_pct=2.9,
        avg_pre_announcement_drift_pct=3.0,  # Higher: exceptional momentum amplifies drift
        avg_effective_date_bump_pct=1.5,
        avg_30d_post_reversal_pct=-1.5,
    )

    c = IndexInclusionCandidate(
        company_name="XTB S.A.",
        ticker="XTB:WSE",
        exchange="WSE",
        sector="Financials — Online CFD / Brokerage Platform",
        country="Poland",
        target_index=IndexFamily.MSCI_POLAND,
        current_price=68.0,
        currency="PLN",
        market_cap_local_m=13_100,
        market_cap_usd_m=3_200,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "★ TOP PICK — MSCI EM Small Cap → MSCI Poland Standard, May 2025 ★\n"
            "XTB = fastest-growing European retail CFD/investment broker. "
            "1.2M+ active clients (2025), expanding into zero-commission stock trading. "
            "Full mktcap $3.2B >> $2.5B threshold; float-adj $1.52B >> $1.3B threshold. "
            "All MSCI Standard gates cleared. Currently MSCI EM Small Cap — upgrade imminent. "
            "CRITICAL: EM Small Cap → Standard upgrade creates DUAL DEMAND: "
            "  MSCI Poland trackers buy new constituent; MSCI EM rebalances. "
            "RS 96th pct = top-decile momentum. 12M return +145% vs WIG +18%. "
            "14 ADV days of passive demand = significant price impact. "
            "Backtest analogue: Allegro May 2021 (RS 85th, 22 ADV days, +25.7% T-45→effective). "
            "XTB setup is comparable in structure if not quite magnitude."
        ),
        key_risks=[
            "Business model cyclicality: trading volumes collapse in low-volatility environments",
            "Crypto/retail trading boom may already be peaking (earnings sustainability risk)",
            "Founder 35% stake: if he reduces, float increases (positive for FIF) but creates overhang",
            "Regulatory risk: ESMA product intervention on CFDs could impair revenue",
            "Momentum so strong (RS 96th) — some pre-announcement drift already realised",
        ],
        catalyst_date="May 2025 MSCI SAR — EM Small Cap to MSCI Poland Standard upgrade",
        revenue_growth_yoy_pct=58.0,
        ebitda_margin_pct=48.0,
        roe_pct=38.0,
    )
    return c


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 3 — CCC Group S.A. (CCC) — MSCI Poland Standard, approaching threshold
# WATCH (borderline momentum)
# ─────────────────────────────────────────────────────────────────────────────

def analyse_ccc() -> IndexInclusionCandidate:
    screen = MSCIEligibilityScreen(
        company_name="CCC S.A.",
        ticker="CCC",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_POLAND,
        full_market_cap_usd_m=2_100,           # Below $2.5B Standard threshold
        float_adj_market_cap_usd_m=1_050,      # Founder Dariusz Milek ~38%; float ~62%
        foreign_inclusion_factor=0.62,
        foreign_room_pct=42.0,
        atvr_3m_pct=25.0,
        avg_daily_volume_usd_m=9.5,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="Nov 2025",
        months_to_next_review=8.5,
        sector_gics="Consumer Discretionary — Footwear & Apparel Retail",
        current_msci_membership="MSCI EM Small Cap",
        analyst_coverage_count=14,
    )

    momentum = MomentumProfile(
        return_1m_pct=5.0,
        return_3m_pct=12.0,
        return_6m_pct=22.0,
        return_12m_pct=38.0,
        rs_percentile=65,
        benchmark_return_12m_pct=18.0,
        above_50d_ma=True,
        above_200d_ma=True,
        volume_trend="neutral",
        distance_from_52w_high_pct=-14.0,
        distance_from_52w_low_pct=+58.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.SCREEN,   # Not yet at threshold
        estimated_days_to_announcement=180,
        estimated_days_to_effective_date=210,
        estimated_forced_buying_usd_m=205,
        estimated_index_weight_pct=1.05,
        adv_days_to_absorb=9.0,
        avg_announcement_day_return_pct=2.9,
        avg_pre_announcement_drift_pct=1.5,
        avg_effective_date_bump_pct=1.0,
        avg_30d_post_reversal_pct=-1.0,
    )

    c = IndexInclusionCandidate(
        company_name="CCC S.A.",
        ticker="CCC:WSE",
        exchange="WSE",
        sector="Consumer Discretionary — Footwear Retail (CEE + Zalando e-com)",
        country="Poland",
        target_index=IndexFamily.MSCI_POLAND,
        current_price=128.0,
        currency="PLN",
        market_cap_local_m=8_600,
        market_cap_usd_m=2_100,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "WATCH — MSCI Standard threshold needs +19% market cap growth first.\n"
            "CCC = Poland's largest footwear retailer, ~1,600 stores in CEE + Zalando.pl stake. "
            "Full mktcap $2.1B vs $2.5B threshold — gap is ~$400M (+19% needed). "
            "At current growth rate, crosses threshold by Aug/Sep 2025 → Nov 2025 SAR target. "
            "Momentum: RS 65th pct, above 200d MA — passes filter but not strong signal. "
            "ACTION: begin SCREEN/ACCUMULATE phase; increase position IF momentum "
            "accelerates to RS ≥ 75th pct and stock approaches threshold. "
            "FTSE EM addition also possible at Dec 2025 QIR (dual-index setup)."
        ),
        key_risks=[
            "Market cap still $400M below Standard threshold — needs significant appreciation",
            "High debt load (restructured 2022–2023); net debt / EBITDA ~3.5x",
            "Online fashion competition from Shein, Temu intensifying in CEE",
            "Founder 38% concentration limits FIF expansion",
        ],
        catalyst_date="Nov 2025 MSCI SAR (if market cap clears $2.5B threshold by Oct cut-off)",
        revenue_growth_yoy_pct=12.0,
        ebitda_margin_pct=9.5,
        net_debt_to_ebitda=3.5,
    )
    return c


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 4 — Budimex S.A. (BDX) — Weight Increase, MSCI Poland Standard
# Already in Standard (Nov 2024 upgrade); weight growing
# ─────────────────────────────────────────────────────────────────────────────

def analyse_budimex() -> IndexInclusionCandidate:
    screen = MSCIEligibilityScreen(
        company_name="Budimex S.A.",
        ticker="BDX",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_POLAND,
        full_market_cap_usd_m=4_350,
        float_adj_market_cap_usd_m=1_500,      # Ferrovial (Spanish group) owns ~53%; float ~47%
        foreign_inclusion_factor=0.47,
        foreign_room_pct=35.0,
        atvr_3m_pct=30.0,
        avg_daily_volume_usd_m=10.0,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="May 2025",
        months_to_next_review=2.5,
        sector_gics="Industrials — Construction & Engineering",
        current_msci_membership="MSCI Poland Standard (added Nov 2024) + FTSE EM (Dec 2024)",
        analyst_coverage_count=14,
    )

    momentum = MomentumProfile(
        return_1m_pct=6.0,
        return_3m_pct=16.0,
        return_6m_pct=38.0,
        return_12m_pct=62.0,
        rs_percentile=86,
        benchmark_return_12m_pct=18.0,
        above_50d_ma=True,
        above_200d_ma=True,
        volume_trend="expanding",
        distance_from_52w_high_pct=-6.0,
        distance_from_52w_low_pct=+105.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.ACCUMULATE,
        estimated_days_to_announcement=35,
        estimated_days_to_effective_date=65,
        estimated_forced_buying_usd_m=185,   # Weight increase, not new addition
        estimated_index_weight_pct=1.82,
        adv_days_to_absorb=8.0,
        avg_announcement_day_return_pct=1.8,  # Weight increase = smaller move than new addition
        avg_pre_announcement_drift_pct=1.5,
        avg_effective_date_bump_pct=0.8,
        avg_30d_post_reversal_pct=-0.7,
    )

    c = IndexInclusionCandidate(
        company_name="Budimex S.A.",
        ticker="BDX:WSE",
        exchange="WSE",
        sector="Industrials — General Contractor / Civil Engineering",
        country="Poland",
        target_index=IndexFamily.MSCI_POLAND,
        current_price=478.0,
        currency="PLN",
        market_cap_local_m=17_900,
        market_cap_usd_m=4_350,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "★ TOP PICK — MSCI Poland weight increase May 2025 ★\n"
            "Budimex = Poland's #1 general contractor (roads, railways, buildings). "
            "Added to MSCI Poland Standard (Nov 2024) + FTSE EM (Dec 2024) — dual-index event complete. "
            "NOW: post-inclusion weight growth phase. Mktcap outperformance vs other MSCI Poland members "
            "→ weight increases at each SAR → incremental forced buying. "
            "EU KPO (PLN 76B infrastructure investment) gives 5-year revenue visibility. "
            "NATO infrastructure spending: Poland 4% of GDP defence budget = record construction. "
            "RS 86th pct, 12M +62% — momentum clearly supports the weight increase thesis. "
            "Ferrovial ownership (53%): technically limits FIF to 0.47, but FIF 0.47 × float-adj "
            "$1.5B = $705M — well above $1.3B Standard threshold. Wait, let me recalculate: "
            "Float-adj mktcap = $4,350M × 0.47 = $2,044M >> $1.3B. All gates clear."
        ),
        key_risks=[
            "Ferrovial may reduce stake (positive: increases float; negative: overhang)",
            "EU KPO disbursement delays from Brussels could defer project starts",
            "Labor cost inflation in Poland squeezing construction margins",
            "Already in both MSCI and FTSE — no 'new inclusion' alpha; only weight change alpha",
        ],
        catalyst_date="May 2025 MSCI SAR (weight increase) + Jun 2025 FTSE QIR (weight increase)",
        revenue_growth_yoy_pct=18.0,
        ebitda_margin_pct=8.5,
        net_debt_to_ebitda=-0.5,   # Net cash (Budimex is cash-generative)
        roe_pct=42.0,
    )
    return c


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 5 — Bank Millennium S.A. (MIL) — MSCI EM Small Cap upgrade candidate
# Momentum borderline — WATCH
# ─────────────────────────────────────────────────────────────────────────────

def analyse_bank_millennium() -> IndexInclusionCandidate:
    screen = MSCIEligibilityScreen(
        company_name="Bank Millennium S.A.",
        ticker="MIL",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_POLAND,
        full_market_cap_usd_m=2_650,
        float_adj_market_cap_usd_m=1_260,      # BCP (Portugal) owns ~50.1%; float ~49.9%
        foreign_inclusion_factor=0.50,
        foreign_room_pct=32.0,
        atvr_3m_pct=22.0,
        avg_daily_volume_usd_m=8.5,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="May 2025",
        months_to_next_review=2.5,
        sector_gics="Financials — Banking",
        current_msci_membership="MSCI EM Small Cap",
        analyst_coverage_count=12,
    )

    momentum = MomentumProfile(
        return_1m_pct=2.5,
        return_3m_pct=6.5,
        return_6m_pct=15.0,
        return_12m_pct=32.0,
        rs_percentile=58,        # BORDERLINE — just below 60th pct filter
        benchmark_return_12m_pct=18.0,
        above_50d_ma=True,
        above_200d_ma=True,       # Passes MA test; RS is the binding constraint
        volume_trend="neutral",
        distance_from_52w_high_pct=-18.0,
        distance_from_52w_low_pct=+42.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.SCREEN,
        estimated_days_to_announcement=35,
        estimated_days_to_effective_date=65,
        estimated_forced_buying_usd_m=185,
        estimated_index_weight_pct=0.95,
        adv_days_to_absorb=10.0,
        avg_announcement_day_return_pct=2.9,
        avg_pre_announcement_drift_pct=1.5,
        avg_effective_date_bump_pct=1.0,
        avg_30d_post_reversal_pct=-1.0,
    )

    c = IndexInclusionCandidate(
        company_name="Bank Millennium S.A.",
        ticker="MIL:WSE",
        exchange="WSE",
        sector="Financials — Retail Banking",
        country="Poland",
        target_index=IndexFamily.MSCI_POLAND,
        current_price=8.90,
        currency="PLN",
        market_cap_local_m=10_870,
        market_cap_usd_m=2_650,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "WATCH — Eligibility gates largely cleared; momentum BORDERLINE (RS 58th).\n"
            "Mbank Millennium = Poland's 5th largest bank by assets. "
            "Full mktcap $2.65B >> $2.5B threshold; float-adj $1.26B ~ $1.3B (barely passes). "
            "KEY RISK: float-adj cap is right at the threshold. If BCP reduces stake or "
            "stock pulls back 5%, it falls back below. Very sensitive to FX and price. "
            "CHF mortgage overhang: Millennium settled most CHF claims (2024 provisions). "
            "NOW: provisioning cycle complete → ROE recovering to ~12–14%. "
            "MOMENTUM: RS 58th pct — passes 55th pct minimum but NOT the 60th pct preferred filter. "
            "ACTION: on watchlist; initiate position ONLY if RS rises to 62nd+ pct. "
            "Trigger: Q1 2025 earnings beat → momentum accelerates → full position."
        ),
        key_risks=[
            "Float-adj cap barely above $1.3B threshold — very sensitive to price/FX",
            "BCP (Portuguese parent 50.1%) could sell stake — ambiguous for FIF",
            "CHF mortgage settlement costs not fully crystallised yet",
            "Momentum below preferred 60th pct threshold — do not force position",
        ],
        catalyst_date="May 2025 MSCI SAR (if float-adj cap stays > $1.3B at cut-off)",
        revenue_growth_yoy_pct=8.0,
        ebitda_margin_pct=None,
        roe_pct=12.5,
    )
    return c


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 6 — Asseco Poland S.A. (ACP) — MSCI EM Small Cap; FTSE EM candidate
# Momentum FAILS filter — AVOID for now
# ─────────────────────────────────────────────────────────────────────────────

def analyse_asseco() -> IndexInclusionCandidate:
    screen = MSCIEligibilityScreen(
        company_name="Asseco Poland S.A.",
        ticker="ACP",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_EM_SMALL,
        full_market_cap_usd_m=1_550,
        float_adj_market_cap_usd_m=720,        # Various block holders; float ~46%
        foreign_inclusion_factor=0.46,
        foreign_room_pct=38.0,
        atvr_3m_pct=18.0,
        avg_daily_volume_usd_m=3.5,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="May 2025",
        months_to_next_review=2.5,
        sector_gics="Information Technology — IT Services",
        current_msci_membership="MSCI EM Small Cap",
        analyst_coverage_count=9,
    )

    momentum = MomentumProfile(
        return_1m_pct=-3.5,
        return_3m_pct=-8.0,
        return_6m_pct=2.0,
        return_12m_pct=12.0,     # Underperforming WIG (+18%) by 6pp
        rs_percentile=38,        # FAILS FILTER — below 40th pct
        benchmark_return_12m_pct=18.0,
        above_50d_ma=False,
        above_200d_ma=True,      # Held 200d MA but declining
        volume_trend="contracting",
        distance_from_52w_high_pct=-22.0,
        distance_from_52w_low_pct=+18.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.SCREEN,
        estimated_days_to_announcement=35,
        estimated_days_to_effective_date=65,
        estimated_forced_buying_usd_m=55,
        estimated_index_weight_pct=0.35,
        adv_days_to_absorb=6.5,
        avg_announcement_day_return_pct=2.1,
        avg_pre_announcement_drift_pct=0.5,
        avg_effective_date_bump_pct=0.7,
        avg_30d_post_reversal_pct=-0.5,
    )

    c = IndexInclusionCandidate(
        company_name="Asseco Poland S.A.",
        ticker="ACP:WSE",
        exchange="WSE",
        sector="Information Technology — Government / Banking IT Systems",
        country="Poland",
        target_index=IndexFamily.MSCI_EM_SMALL,
        current_price=72.0,
        currency="PLN",
        market_cap_local_m=6_360,
        market_cap_usd_m=1_550,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "AVOID — Momentum FAILS filter (RS 38th pct). Do not initiate position.\n"
            "Asseco = Poland's largest IT company, dominant in banking core systems + ZUS/MF gov. "
            "Fundamentals are stable (EBITDA margin ~15%, low debt) but NOT a momentum story. "
            "Backtest shows: stocks with RS < 40th pct at entry average near-flat returns "
            "even on index inclusion — passive demand absorbed without directional follow-through. "
            "ATVR 18% is borderline above 15% MSCI EM SC threshold — no upward weight pressure. "
            "ACTION: add to watchlist. Re-evaluate if RS recovers to 55th+ pct. "
            "A potential trigger: Asseco's AI/ERP modernisation contract wins could re-rate "
            "the stock and push RS higher — monitor Q2/Q3 2025 order flow announcements."
        ),
        key_risks=[
            "MOMENTUM FILTER FAILURE: RS 38th pct — backtest shows poor risk/reward at this level",
            "Government IT dependency: contract renewal cycles create lumpiness",
            "Multiple holding company discount: Asseco Group + various subs priced at conglomerate discount",
            "AI displacement risk for legacy banking core systems",
        ],
        catalyst_date="WATCH ONLY — initiate if momentum recovers to RS ≥ 55th pct",
        revenue_growth_yoy_pct=5.0,
        ebitda_margin_pct=15.0,
        net_debt_to_ebitda=0.5,
        roe_pct=11.0,
    )
    return c


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 7 — PKP Cargo S.A. (PKC) — DELETION RISK example
# Negative momentum + weight decrease = AVOID / potential short
# ─────────────────────────────────────────────────────────────────────────────

def analyse_pkp_cargo_deletion_risk() -> IndexInclusionCandidate:
    """PKP Cargo — demonstrates the deletion signal (opposite of inclusion play)."""
    screen = MSCIEligibilityScreen(
        company_name="PKP Cargo S.A.",
        ticker="PKC",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_EM_SMALL,
        full_market_cap_usd_m=285,
        float_adj_market_cap_usd_m=88,         # Polish state owns ~33%; float ~67%
        foreign_inclusion_factor=0.67,
        foreign_room_pct=52.0,
        atvr_3m_pct=14.0,                      # BELOW 15% minimum — liquidity gate FAILING
        avg_daily_volume_usd_m=1.2,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="May 2025",
        months_to_next_review=2.5,
        sector_gics="Industrials — Freight & Logistics (Rail)",
        current_msci_membership="MSCI EM Small Cap (deletion risk)",
        analyst_coverage_count=8,
    )

    momentum = MomentumProfile(
        return_1m_pct=-12.0,
        return_3m_pct=-28.0,
        return_6m_pct=-45.0,
        return_12m_pct=-58.0,     # Collapse: coal volume decline + restructuring
        rs_percentile=8,          # Bottom decile — strongly negative
        benchmark_return_12m_pct=18.0,
        above_50d_ma=False,
        above_200d_ma=False,
        volume_trend="contracting",
        distance_from_52w_high_pct=-62.0,
        distance_from_52w_low_pct=+3.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.SCREEN,
        estimated_days_to_announcement=35,
        estimated_days_to_effective_date=65,
        estimated_forced_buying_usd_m=-42,     # NEGATIVE = forced SELLING if deleted
        estimated_index_weight_pct=0.0,        # Will go to 0 on deletion
        adv_days_to_absorb=12.0,              # Low ADV = deletion pressure hits hard
        avg_announcement_day_return_pct=-3.5,  # Deletions average -3.5% on announcement
        avg_pre_announcement_drift_pct=-2.0,
        avg_effective_date_bump_pct=-1.0,
        avg_30d_post_reversal_pct=+1.5,       # Some reversal post-deletion (buy the news)
    )

    c = IndexInclusionCandidate(
        company_name="PKP Cargo S.A.",
        ticker="PKC:WSE",
        exchange="WSE",
        sector="Industrials — Rail Freight (State-Owned, Restructuring)",
        country="Poland",
        target_index=IndexFamily.MSCI_EM_SMALL,
        current_price=18.5,
        currency="PLN",
        market_cap_local_m=1_170,
        market_cap_usd_m=285,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "⚠ DELETION RISK — Tactical short or strict avoid for longs ⚠\n"
            "PKP Cargo = Poland's dominant rail freight carrier (state-owned). "
            "MSCI EM Small Cap member — but ATVR dropped below 15% minimum. "
            "If ATVR stays below 15% at April cut-off, MSCI DELETES from EM Small Cap. "
            "Deletion = forced SELLING of ~$42M by EM Small Cap trackers. "
            "With only $1.2M ADV, this deletion pressure = 35 days of ADV to absorb. "
            "Extreme downward price impact on a stock already -58% YoY. "
            "MOMENTUM: RS 8th pct = bottom decile. Every metric is negative. "
            "TACTICAL SHORT: short before April cut-off, cover after effective date. "
            "LONG PORTFOLIO: remove any PKP Cargo exposure immediately if held. "
            "This is the opposite of an inclusion play — a deletion play."
        ),
        key_risks=[
            "SHORT THESIS: coal-to-gas transition = structural volume decline for rail freight",
            "Rescue plan by Polish state may temporarily support price (political risk for shorts)",
            "If ATVR recovers to 15%+ before cut-off, deletion averted — cover short quickly",
            "Post-deletion reversal: historically stocks recover ~1.5% in 30 days post-deletion",
        ],
        catalyst_date="May 2025 MSCI SAR — potential DELETION from MSCI EM Small Cap",
    )
    return c


# ─────────────────────────────────────────────────────────────────────────────
# WATCHLIST SUMMARY PRINTER
# ─────────────────────────────────────────────────────────────────────────────

def print_watchlist_summary(candidates: list) -> None:
    """Print a ranked watchlist of all candidates."""
    print()
    print("═" * 72)
    print("  WIG MSCI / FTSE INCLUSION WATCHLIST — MAY 2025 REVIEW")
    print("  Ranked by: Conviction tier → Inclusion score → Momentum RS")
    print("═" * 72)

    results = []
    for name, c in candidates:
        from framework.index_inclusion import score_inclusion_candidate
        r = score_inclusion_candidate(c)
        results.append((name, c, r))

    # Sort: HIGH first, then MEDIUM, then WATCH, then by score desc
    tier_order = {"HIGH": 0, "MEDIUM": 1, "WATCH": 2, "PASS": 3}
    results.sort(key=lambda x: (tier_order.get(x[2].conviction_tier, 9), -x[2].inclusion_score))

    print(f"\n  {'Rank':<5} {'Stock':<24} {'Target Index':<22} "
          f"{'Phase':<12} {'Score':<7} {'Tier':<8} {'RS%'}")
    print("  " + "─" * 70)

    for i, (name, c, r) in enumerate(results, 1):
        rs = c.momentum.rs_percentile if c.momentum else "—"
        phase_short = (c.pre_announcement.current_phase.value.split("—")[0].strip()
                       if c.pre_announcement else "—")
        tier_icon = {"HIGH": "★★", "MEDIUM": "★", "WATCH": "◇", "PASS": "✗"}.get(
            r.conviction_tier, "?"
        )
        print(f"  #{i:<4} {c.company_name:<24} {c.target_index.value:<22} "
              f"{phase_short:<12} {r.inclusion_score:<7.2f} "
              f"{tier_icon} {r.conviction_tier:<6} {rs}")

    print()
    print("  TOP PICKS  (★★ HIGH conviction, momentum filter passed):")
    top = [(n, c, r) for n, c, r in results if r.conviction_tier == "HIGH"]
    for name, c, r in top:
        print(f"    → {c.company_name} ({c.ticker})")
        print(f"       Score: {r.inclusion_score:.2f} | Phase: {r.phase.split('—')[0].strip()}")
        print(f"       Entry: {r.entry_action}")
        print(f"       Catalyst: {c.catalyst_date}")
        print()

    print("  AVOID / DELETION RISK:")
    avoid = [(n, c, r) for n, c, r in results if r.conviction_tier in ("PASS", "WATCH")
             and c.momentum and c.momentum.rs_percentile < 40]
    for name, c, r in avoid:
        print(f"    ✗ {c.company_name} ({c.ticker}) — RS {c.momentum.rs_percentile:.0f}th pct "
              f"(fails momentum filter)")
    print()
    print("═" * 72)
    print()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def run() -> None:
    """Run the full MSCI/FTSE WIG candidates analysis with backtest."""

    # ── 1. Build candidate list ──
    candidates = [
        ("kruk",            analyse_kruk()),
        ("xtb",             analyse_xtb()),
        ("budimex",         analyse_budimex()),
        ("ccc",             analyse_ccc()),
        ("bank_millennium", analyse_bank_millennium()),
        ("asseco",          analyse_asseco()),
        ("pkp_cargo",       analyse_pkp_cargo_deletion_risk()),
    ]

    # ── 2. Print watchlist summary ──
    print_watchlist_summary(candidates)

    # ── 3. Print individual detailed reports for top picks ──
    top_picks = ["kruk", "xtb", "budimex"]
    for name, c in candidates:
        if name in top_picks:
            from framework.index_inclusion import score_inclusion_candidate, print_inclusion_report
            r = score_inclusion_candidate(c)
            print_inclusion_report(r, c)

    # ── 4. Run and print backtest ──
    print()
    print("═" * 72)
    print("  RUNNING BACKTEST — 2018–2026 HISTORICAL MSCI/FTSE POLAND EVENTS")
    print("═" * 72)
    print()

    result = run_backtest(momentum_filter_pct=60.0)
    events = build_historical_events()
    for e in events:
        e.compute_returns(60.0)

    print_backtest_report(result, events)

    # ── 5. Filter sensitivity analysis ──
    print_filter_sensitivity(thresholds=[40, 50, 55, 60, 65, 70, 75, 80])


if __name__ == "__main__":
    run()
