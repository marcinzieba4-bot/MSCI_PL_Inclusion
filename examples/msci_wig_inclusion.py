"""
MSCI Index Inclusion Strategy — WIG / Warsaw Stock Exchange Companies
======================================================================

This example applies the index inclusion methodology to Polish companies
(Warsaw Stock Exchange — WSE / GPW) that are candidates for:
  A) MSCI Poland Standard Index (currently ~15 constituents)
  B) MSCI EM Small Cap Index (Polish small-cap tier)

Polish context:
  • Poland is classified as MSCI Emerging Market (elevated from Frontier in 2018)
  • The Polish index universe sits within MSCI EM, meaning a Polish stock added
    to MSCI Standard gets buying from BOTH MSCI Poland trackers AND MSCI EM trackers
  • MSCI Poland has ~$8–10B AUM tracking it directly
  • MSCI EM weight of Poland ≈ 0.35% of $850B EM AUM ≈ ~$3B directly allocated
  • Addition to MSCI Poland Standard from MSCI EM Small Cap = two-step re-rating

Key MSCI review dates (2025–2026):
  • Feb 2025 SAR announced Nov 2024 → effective last business day Feb 2025
  • May 2025 SAR announced Apr 2025 → effective last business day May 2025   ← CURRENT FOCUS
  • Aug 2025 quarterly (deletions/rebalances only, less impactful)
  • Nov 2025 SAR announced Oct 2025 → effective last business day Nov 2025

MSCI Standard thresholds (EM market, Poland):
  Full Market Cap        ≥ $2,500M
  Float-Adj Market Cap   ≥ $1,300M
  FIF (Foreign Inclusion Factor) ≥ 0.15
  3-Month ATVR           ≥ 20%

MSCI EM Small Cap thresholds:
  Full Market Cap        ≥ $127M
  Float-Adj Market Cap   ≥ $95M
  3-Month ATVR           ≥ 15%

WIG companies analysed (as of early 2026):
  1. Allegro.eu      (ALE) — E-commerce leader; near MSCI Standard threshold
  2. PKO BP          (PKO) — Largest bank; already in MSCI Poland; size reference
  3. CD Projekt      (CDR) — Gaming; MSCI Poland member; monitors for weight changes
  4. Dino Polska     (DNO) — Retail food; crossing Standard threshold
  5. Żabka Group     (ZAB) — Convenience retail IPO 2024; MSCI EM Small Cap candidate

Momentum context for WIG:
  WIG index 2024 return: +18% (PLN terms)
  EUR/PLN tailwind: PLN strengthened ~4% vs EUR in 2025 (USD-denominated MSCI thresholds benefit)
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
    score_inclusion_candidate,
    print_inclusion_report,
)


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 1 — Allegro.eu (ALE) — E-commerce, Near MSCI Standard Threshold
# ─────────────────────────────────────────────────────────────────────────────
# Allegro is Poland's dominant e-commerce marketplace (Amazon-equivalent in CEE).
# Market cap: ~$5–7B depending on PLN/USD rate. This is near but fluctuates around
# the $2,500M full cap / $1,300M float-adj threshold.
# Key thesis: as Polish zloty strengthens vs USD and Allegro grows, it will
# cross the USD-denominated threshold in 2025–2026.
# Already in MSCI EM Small Cap — upgrade to Standard is highly impactful.

def analyse_allegro() -> None:
    """Allegro.eu — MSCI Standard upgrade candidate (from MSCI EM Small Cap)."""

    screen = MSCIEligibilityScreen(
        company_name="Allegro.eu S.A.",
        ticker="ALE",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_POLAND,
        full_market_cap_usd_m=5_800,          # At ~PLN 24 and EUR/PLN 4.25, USD/PLN ~4.1
        float_adj_market_cap_usd_m=2_400,     # ~41% float (founder/PE still own ~59%)
        foreign_inclusion_factor=0.41,         # FIF limited by non-Polish ownership structure
        foreign_room_pct=28.0,
        atvr_3m_pct=32.0,                     # Good liquidity for Polish market
        avg_daily_volume_usd_m=18.0,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="May 2025",
        months_to_next_review=2.5,
        sector_gics="Consumer Discretionary — E-Commerce & Marketplace",
        current_msci_membership="MSCI EM Small Cap",   # KEY: upgrade path
        analyst_coverage_count=24,
    )

    momentum = MomentumProfile(
        return_1m_pct=6.5,
        return_3m_pct=18.0,
        return_6m_pct=35.0,
        return_12m_pct=52.0,
        rs_percentile=83,
        benchmark_return_12m_pct=18.0,        # WIG 2025 return (PLN)
        above_50d_ma=True,
        above_200d_ma=True,
        volume_trend="expanding",
        distance_from_52w_high_pct=-7.0,
        distance_from_52w_low_pct=+88.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.SIZE_UP,  # Review in ~2.5 months; stock eligible now
        estimated_days_to_announcement=35,
        estimated_days_to_effective_date=65,
        estimated_forced_buying_usd_m=820,     # MSCI Poland trackers + EM weight
        estimated_index_weight_pct=1.85,       # Projected weight in MSCI Poland
        adv_days_to_absorb=18.0,              # High ADV impact for WSE standards
        avg_announcement_day_return_pct=2.9,  # MSCI EM average
        avg_pre_announcement_drift_pct=2.0,
        avg_effective_date_bump_pct=1.2,
        avg_30d_post_reversal_pct=-1.2,
    )

    candidate = IndexInclusionCandidate(
        company_name="Allegro.eu S.A.",
        ticker="ALE:WSE",
        exchange="WSE (Warsaw Stock Exchange)",
        sector="Consumer Discretionary — E-Commerce & Marketplace",
        country="Poland",
        target_index=IndexFamily.MSCI_POLAND,
        current_price=24.20,
        currency="PLN",
        market_cap_local_m=23_800,            # PLN millions
        market_cap_usd_m=5_800,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "Allegro is Poland's #1 e-commerce platform (~50% GMV market share in Poland). "
            "Already in MSCI EM Small Cap — upgrade to MSCI Standard is the key event. "
            "Full mktcap $5.8B >> $2.5B threshold; float-adj $2.4B >> $1.3B threshold. "
            "All MSCI gates cleared for the May 2025 Semi-Annual Review. "
            "MSCI EM Small Cap → MSCI Poland Standard upgrade creates DOUBLE demand: "
            "  (1) MSCI Poland-specific trackers must buy new weight  "
            "  (2) MSCI EM trackers rebalance away from small cap, into standard. "
            "Estimated ~$820M forced passive demand on a stock averaging $18M ADV. "
            "ADV absorption = 18 days — highly significant price impact expected. "
            "Momentum: RS 83rd pct, 12M +52% vs WIG +18% — institutional accumulation visible."
        ),
        key_risks=[
            "FIF may be re-assessed: if parent entities reclassified, FIF could drop <0.15",
            "PLN/USD FX: if zloty weakens >8% vs USD, full cap could fall below $2.5B threshold",
            "GMV growth slowdown: Q4 results key; MSCI uses latest market data at cut-off",
            "Amazon.eu expansion into Poland could pressure long-term earnings growth story",
            "Liquidity concentration: top 5 shareholders own >60% — actual float is limited",
        ],
        catalyst_date="May 2025 MSCI Semi-Annual Review (announcement ~late April 2025)",
        revenue_growth_yoy_pct=12.0,
        ebitda_margin_pct=28.0,
        net_debt_to_ebitda=2.5,
        roe_pct=22.0,
    )

    result = score_inclusion_candidate(candidate)
    print_inclusion_report(result, candidate)


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 2 — Dino Polska (DNO) — Food Retail, MSCI Poland Inclusion
# ─────────────────────────────────────────────────────────────────────────────
# Dino Polska is a rapidly expanding discount food retailer (think Biedronka-lite)
# focused on rural and suburban Poland. Founded 2002, IPO 2017.
# Excellent growth story: ~600 new stores/year. Crosses MSCI Poland threshold.
# Currently in MSCI EM Small Cap — approaching Standard upgrade.

def analyse_dino_polska() -> None:
    """Dino Polska — MSCI Poland Standard upgrade from EM Small Cap."""

    screen = MSCIEligibilityScreen(
        company_name="Dino Polska S.A.",
        ticker="DNO",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_POLAND,
        full_market_cap_usd_m=4_100,
        float_adj_market_cap_usd_m=1_850,     # Founder Tomasz Biernacki owns ~51%
        foreign_inclusion_factor=0.49,
        foreign_room_pct=35.0,
        atvr_3m_pct=28.0,
        avg_daily_volume_usd_m=12.5,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="Nov 2025",
        months_to_next_review=8.5,
        sector_gics="Consumer Staples — Food & Staples Retailing",
        current_msci_membership="MSCI EM Small Cap",
        analyst_coverage_count=18,
    )

    momentum = MomentumProfile(
        return_1m_pct=3.5,
        return_3m_pct=8.0,
        return_6m_pct=22.0,
        return_12m_pct=38.0,
        rs_percentile=74,
        benchmark_return_12m_pct=18.0,
        above_50d_ma=True,
        above_200d_ma=True,
        volume_trend="neutral",
        distance_from_52w_high_pct=-12.0,
        distance_from_52w_low_pct=+55.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.ACCUMULATE,   # Nov 2025 review ~8 months away — start building
        estimated_days_to_announcement=175,
        estimated_days_to_effective_date=205,
        estimated_forced_buying_usd_m=620,
        estimated_index_weight_pct=1.35,
        adv_days_to_absorb=20.0,
        avg_announcement_day_return_pct=2.9,
        avg_pre_announcement_drift_pct=1.5,     # Lower: longer accumulation period
        avg_effective_date_bump_pct=1.0,
        avg_30d_post_reversal_pct=-1.0,
    )

    candidate = IndexInclusionCandidate(
        company_name="Dino Polska S.A.",
        ticker="DNO:WSE",
        exchange="WSE (Warsaw Stock Exchange)",
        sector="Consumer Staples — Discount Food Retail",
        country="Poland",
        target_index=IndexFamily.MSCI_POLAND,
        current_price=385.0,
        currency="PLN",
        market_cap_local_m=16_900,
        market_cap_usd_m=4_100,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "Dino Polska: fastest-growing Polish food retailer, targeting rural/suburban Poland. "
            "~2,400 stores (Feb 2026) growing at ~550–650 stores/year — highly capital efficient. "
            "Full mktcap $4.1B, float-adj $1.85B — comfortably above MSCI Standard thresholds. "
            "Founder Tomasz Biernacki holds ~51%, limiting float to ~49% but FIF = 0.49. "
            "FIF × float-adj mktcap = $1.85B >> $1.3B requirement. All gates pass. "
            "Nov 2025 SAR is the target review. ACCUMULATE phase: 8 months to review = "
            "lower time pressure but also lower near-term catalyst. Build position gradually. "
            "Strong fundamental story (EBITDA margin 14%, 20%+ SSSG, 0.9x ND/EBITDA) "
            "provides support independent of index event. This is a high-quality compounder "
            "where MSCI inclusion is an incremental catalyst, not the primary thesis."
        ),
        key_risks=[
            "Founder 51% stake: FIF could be recalculated lower if MSCI methodology changes",
            "PLN weakness vs USD: $4.1B at current rate; needs to stay above $2.5B threshold",
            "Competition: Jeronimo Martins (Biedronka) could accelerate rural store openings",
            "Margin pressure: food inflation normalisation + cost of new store build-out",
            "Long lead time to Nov 2025 review: 8 months = capital at risk if momentum fades",
        ],
        catalyst_date="Nov 2025 MSCI Semi-Annual Review (announcement ~late October 2025)",
        revenue_growth_yoy_pct=22.0,
        ebitda_margin_pct=14.0,
        net_debt_to_ebitda=0.9,
        roe_pct=28.0,
    )

    result = score_inclusion_candidate(candidate)
    print_inclusion_report(result, candidate)


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 3 — Żabka Group (ZAB) — Convenience Retail, MSCI EM Small Cap
# ─────────────────────────────────────────────────────────────────────────────
# Żabka is Poland's largest convenience store chain (~10,000+ stores).
# IPO October 2024 (largest Polish IPO in years). CVC Capital Partners exit.
# Target: MSCI EM Small Cap inclusion at Feb 2025 quarterly review (fast track).
# This is a RECENTLY LISTED candidate — seasoning check important.
# MSCI has no 12-month seasoning rule (unlike S&P 500) — can be added immediately
# after IPO if market cap and liquidity criteria met.

def analyse_zabka() -> None:
    """Żabka Group — MSCI EM Small Cap inclusion candidate post-IPO 2024."""

    screen = MSCIEligibilityScreen(
        company_name="Żabka Group S.A.",
        ticker="ZAB",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_EM_SMALL,
        full_market_cap_usd_m=2_850,           # At IPO price PLN 21.5/share
        float_adj_market_cap_usd_m=550,        # CVC retains >80% initially; low float
        foreign_inclusion_factor=0.22,          # Limited by CVC lock-up overhang
        foreign_room_pct=60.0,
        atvr_3m_pct=18.5,                      # Borderline on liquidity
        avg_daily_volume_usd_m=4.5,
        next_review_cycle=ReviewCycle.QUARTERLY,
        next_review_month="Feb 2025",
        months_to_next_review=2.0,
        sector_gics="Consumer Staples — Food & Staples Retailing",
        current_msci_membership=None,           # Not yet in any MSCI index
        analyst_coverage_count=12,
    )

    momentum = MomentumProfile(
        return_1m_pct=-4.0,
        return_3m_pct=-12.0,
        return_6m_pct=-18.0,      # Typical post-IPO pressure / CVC overhang
        return_12m_pct=-18.0,
        rs_percentile=28,
        benchmark_return_12m_pct=18.0,
        above_50d_ma=False,
        above_200d_ma=False,
        volume_trend="contracting",
        distance_from_52w_high_pct=-22.0,
        distance_from_52w_low_pct=+5.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.SCREEN,   # Monitoring — ATVR borderline
        estimated_days_to_announcement=25,
        estimated_days_to_effective_date=50,
        estimated_forced_buying_usd_m=85,      # Small cap index — limited forced buying
        estimated_index_weight_pct=0.45,       # Weight within MSCI EM Small Cap
        adv_days_to_absorb=7.5,
        avg_announcement_day_return_pct=2.1,   # Smaller for small cap index
        avg_pre_announcement_drift_pct=1.0,
        avg_effective_date_bump_pct=0.8,
        avg_30d_post_reversal_pct=-0.8,
    )

    candidate = IndexInclusionCandidate(
        company_name="Żabka Group S.A.",
        ticker="ZAB:WSE",
        exchange="WSE (Warsaw Stock Exchange)",
        sector="Consumer Staples — Convenience Retail",
        country="Poland",
        target_index=IndexFamily.MSCI_EM_SMALL,
        current_price=17.0,                    # PLN (below IPO price of 21.5)
        currency="PLN",
        market_cap_local_m=11_800,
        market_cap_usd_m=2_850,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "Żabka: Poland's dominant convenience chain with 10,000+ stores. "
            "IPO Oct 2024 at PLN 21.5 (PLN 6.5B raised). CVC Capital Partners exit vehicle. "
            "For MSCI EM Small Cap: full mktcap $2.85B >> $127M threshold — easily clears size. "
            "PROBLEM: float-adj mktcap only ~$550M >> $95M threshold (passes), "
            "but ATVR at 18.5% is borderline vs 15% threshold. "
            "BIGGER PROBLEM: negative momentum (RS 28th pct, -18% from high). "
            "CVC overhang: lock-up expiry in April 2025 = further selling pressure risk. "
            "CURRENT RECOMMENDATION: SCREEN/WATCH only. "
            "Wait for: (1) lock-up expiry resolved, (2) momentum turns positive. "
            "Target entry: if stock stabilises post-lock-up and RS recovers to >50th pct. "
            "MSCI EM Small Cap inclusion likely in May or Aug 2025 if momentum recovers."
        ),
        key_risks=[
            "CVC lock-up expires April 2025 — potential large block sale overhangs price",
            "Post-IPO negative momentum (RS 28th pct) = inclusion alpha likely muted",
            "ATVR borderline at 18.5% vs 15% minimum — any volume decline = gate failure",
            "Convenience retail margin pressure from rising labour costs (min wage hikes in PL)",
            "Autonomous store concept ('Żabka Nano') is capital-intensive — execution risk",
            "MSCI EM Small Cap addition: forced buying only ~$85M — limited price impact",
        ],
        catalyst_date="Est. May 2025 MSCI SAR (if momentum and lock-up situation resolves)",
        revenue_growth_yoy_pct=28.0,
        ebitda_margin_pct=10.5,
        net_debt_to_ebitda=3.2,
    )

    result = score_inclusion_candidate(candidate)
    print_inclusion_report(result, candidate)


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 4 — PKO BP (PKO) — Reference: Existing MSCI Poland Member
# ─────────────────────────────────────────────────────────────────────────────
# PKO BP is the largest Polish bank and the largest constituent of MSCI Poland.
# This reference case shows what a well-established MSCI member looks like,
# and sets the benchmark for weight changes within the index.
# MSCI weight changes (rebalancing) also create forced buying/selling —
# a sub-strategy distinct from new additions.

def analyse_pko_bp_reference() -> None:
    """PKO BP — established MSCI Poland member; reference case for weight rebalancing."""

    screen = MSCIEligibilityScreen(
        company_name="PKO Bank Polski S.A.",
        ticker="PKO",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_POLAND,
        full_market_cap_usd_m=15_500,          # Largest Polish company
        float_adj_market_cap_usd_m=7_400,      # Polish State Treasury ~29%, float ~71%
        foreign_inclusion_factor=0.71,
        foreign_room_pct=45.0,
        atvr_3m_pct=52.0,                      # Very liquid by WSE standards
        avg_daily_volume_usd_m=45.0,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="May 2025",
        months_to_next_review=2.5,
        sector_gics="Financials — Banking",
        current_msci_membership="MSCI Poland Standard (largest constituent, ~28% weight)",
        analyst_coverage_count=32,
    )

    momentum = MomentumProfile(
        return_1m_pct=4.0,
        return_3m_pct=14.0,
        return_6m_pct=32.0,
        return_12m_pct=55.0,
        rs_percentile=85,
        benchmark_return_12m_pct=18.0,
        above_50d_ma=True,
        above_200d_ma=True,
        volume_trend="expanding",
        distance_from_52w_high_pct=-4.5,
        distance_from_52w_low_pct=+88.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.ACCUMULATE,
        estimated_days_to_announcement=35,
        estimated_days_to_effective_date=65,
        estimated_forced_buying_usd_m=280,     # Weight increase forced buying
        estimated_index_weight_pct=28.5,       # MSCI Poland weight (largest member)
        adv_days_to_absorb=3.0,               # Very liquid — absorbed quickly
        avg_announcement_day_return_pct=1.2,  # Weight change = smaller move than new addition
        avg_pre_announcement_drift_pct=0.8,
        avg_effective_date_bump_pct=0.5,
        avg_30d_post_reversal_pct=-0.5,
    )

    candidate = IndexInclusionCandidate(
        company_name="PKO Bank Polski S.A.",
        ticker="PKO:WSE",
        exchange="WSE (Warsaw Stock Exchange)",
        sector="Financials — Universal Banking",
        country="Poland",
        target_index=IndexFamily.MSCI_POLAND,
        current_price=58.0,
        currency="PLN",
        market_cap_local_m=63_700,
        market_cap_usd_m=15_500,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "PKO BP REFERENCE CASE: already the largest MSCI Poland constituent (~28% weight). "
            "No 'new inclusion' alpha here. However: MSCI weight increases also generate "
            "forced passive buying. If PKO's market cap grows relative to other MSCI Poland members, "
            "weight increases at each semi-annual review create incremental demand. "
            "Primary thesis is FUNDAMENTAL + WEIGHT INCREASE: "
            "Polish rate cycle is supportive (NBP holding rates high), NIM expanding. "
            "Strong 12M momentum (+55% vs WIG +18%) = institutional re-rating in progress. "
            "LESSON: for established index members, monitor weight change direction "
            "and size positions around semi-annual reviews if stock approaching index-cap weight limits. "
            "May 2025 SAR: PKO weight likely increases by ~1.5pp due to mktcap growth."
        ),
        key_risks=[
            "Polish Treasury (29% owner): political risk of adverse pricing in capital actions",
            "CHF mortgage legacy: Swiss franc legal risk tail (smaller than mBank but present)",
            "Rate cut cycle: NBP cutting rates would compress NIM",
            "Already 28% of MSCI Poland — weight cap may limit further forced buying",
        ],
        catalyst_date="May 2025 MSCI SAR — weight increase in MSCI Poland and MSCI EM rebalance",
        revenue_growth_yoy_pct=12.0,
        ebitda_margin_pct=58.0,   # Banking: NIM-based margin
        net_debt_to_ebitda=None,  # Banks not valued on net debt
        roe_pct=18.5,
    )

    result = score_inclusion_candidate(candidate)
    print_inclusion_report(result, candidate)


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE 5 — Pepco Group (PEP) — CEE Value Retail, MSCI EM Small Cap Candidate
# ─────────────────────────────────────────────────────────────────────────────
# Pepco Group is a CEE discount retailer listed on WSE.
# Operates Pepco (value fashion/homeware) and Dealz brands across ~2,800 stores in CEE.
# Currently below MSCI Standard threshold; near MSCI EM Small Cap.

def analyse_pepco() -> None:
    """Pepco Group — MSCI EM Small Cap upgrade candidate; CEE value retail."""

    screen = MSCIEligibilityScreen(
        company_name="Pepco Group N.V.",
        ticker="PEP",
        exchange="WSE",
        country="Poland",
        msci_market_classification="Emerging",
        target_index=IndexFamily.MSCI_EM_SMALL,
        full_market_cap_usd_m=1_450,
        float_adj_market_cap_usd_m=1_080,      # STEINHOFF still has some stake but reduced
        foreign_inclusion_factor=0.74,
        foreign_room_pct=55.0,
        atvr_3m_pct=22.0,
        avg_daily_volume_usd_m=5.5,
        next_review_cycle=ReviewCycle.SEMI_ANNUAL,
        next_review_month="May 2025",
        months_to_next_review=2.5,
        sector_gics="Consumer Discretionary — Value Retail",
        current_msci_membership="MSCI EM Small Cap",  # Already in — monitor weight
        analyst_coverage_count=14,
    )

    momentum = MomentumProfile(
        return_1m_pct=8.0,
        return_3m_pct=22.0,
        return_6m_pct=48.0,
        return_12m_pct=75.0,     # Recovery from 2022 Steinhoff overhang collapse
        rs_percentile=87,
        benchmark_return_12m_pct=18.0,
        above_50d_ma=True,
        above_200d_ma=True,
        volume_trend="expanding",
        distance_from_52w_high_pct=-8.0,
        distance_from_52w_low_pct=+120.0,
    )

    pre_ann = PreAnnouncementWindow(
        current_phase=InclusionPhase.ACCUMULATE,
        estimated_days_to_announcement=35,
        estimated_days_to_effective_date=65,
        estimated_forced_buying_usd_m=95,      # Reweighting within EM Small Cap
        estimated_index_weight_pct=0.65,
        adv_days_to_absorb=7.0,
        avg_announcement_day_return_pct=2.1,
        avg_pre_announcement_drift_pct=1.5,
        avg_effective_date_bump_pct=0.8,
        avg_30d_post_reversal_pct=-0.7,
    )

    candidate = IndexInclusionCandidate(
        company_name="Pepco Group N.V.",
        ticker="PEP:WSE",
        exchange="WSE (Warsaw Stock Exchange)",
        sector="Consumer Discretionary — CEE Value Retail",
        country="Poland",
        target_index=IndexFamily.MSCI_EM_SMALL,
        current_price=44.0,
        currency="PLN",
        market_cap_local_m=5_950,
        market_cap_usd_m=1_450,
        msci_screen=screen,
        momentum=momentum,
        pre_announcement=pre_ann,
        thesis_summary=(
            "Pepco Group: CEE's answer to Primark, operating ~2,800 stores in 20+ countries. "
            "Already in MSCI EM Small Cap — approaching MSCI Standard threshold ($2.5B needed). "
            "At current growth rate (stores +10%/yr, LFL recovery), could reach Standard threshold "
            "by Nov 2025 or May 2026 if PLN strengthens further vs USD. "
            "IMMEDIATE TRADE: within MSCI EM Small Cap, Pepco's rising market cap increases "
            "its index weight → forced buying at each semi-annual review. "
            "MEDIUM TERM: potential MSCI Standard upgrade in 2026 = much larger event. "
            "Steinhoff overhang cleared (Steinhoff restructured 2023): removes legacy fear discount. "
            "Strong momentum: RS 87th pct, 12M +75% recovery from 2022 lows. "
            "CEE consumer recovery + value retail positioning = excellent fundamental backdrop."
        ),
        key_risks=[
            "MSCI Standard threshold needs $2.5B full cap — currently $1.45B, needs +72% more",
            "Dutch incorporation may affect FIF calculation in some MSCI screens",
            "Primark / Shein competition intensifying in Western Europe (Poland exposure limited)",
            "Currency: Pepco reports in EUR but WSE trades in PLN — FX creates price noise",
            "Former Steinhoff connection may cause some governance-focused funds to avoid",
        ],
        catalyst_date="May 2025 MSCI SAR (weight increase within EM Small Cap); "
                      "MSCI Standard upgrade: est. 2026",
        revenue_growth_yoy_pct=15.0,
        ebitda_margin_pct=11.5,
        net_debt_to_ebitda=1.8,
        roe_pct=16.0,
    )

    result = score_inclusion_candidate(candidate)
    print_inclusion_report(result, candidate)


# ─────────────────────────────────────────────────────────────────────────────
# WIG-SPECIFIC METHODOLOGY GUIDE
# ─────────────────────────────────────────────────────────────────────────────

def print_msci_wig_methodology() -> None:
    """Print the complete MSCI/WIG inclusion screening methodology."""
    print()
    print("═" * 72)
    print("  MSCI INDEX INCLUSION STRATEGY — WIG / WARSAW STOCK EXCHANGE")
    print("  Complete Methodology for Polish Equity Index Inclusion Plays")
    print("═" * 72)
    print("""
  CONTEXT: WHY POLISH MSCI INCLUSION MATTERS
  ─────────────────────────────────────────────
  • Poland is MSCI Emerging Market (since 2018 reclassification from Frontier)
  • MSCI Poland has ~$8–10B AUM tracking it directly
  • MSCI EM allocates ~0.35% weight to Poland (~$3B at current EM AUM)
  • Total passive demand pool: ~$11–13B for Polish equities via MSCI
  • Adding to MSCI Poland Standard = MANDATORY buy by ALL EM index trackers
  • The MSCI EM Small Cap → Standard upgrade is the highest-impact event

  REVIEW CALENDAR (KEY DATES)
  ────────────────────────────
  Semi-Annual Reviews (most impactful — new additions/deletions to Standard):
    • May SAR:  Cut-off ~mid-April  |  Announcement ~last week April
                Effective date: last business day of May
    • Nov SAR:  Cut-off ~mid-October | Announcement ~last week October
                Effective date: last business day of November

  Quarterly Reviews (size/ATVR changes, Small Cap additions only):
    • Feb QIR:  Effective last business day of February
    • Aug QIR:  Effective last business day of August

  PRE-TRADE SCREENING CHECKLIST (Run monthly)
  ─────────────────────────────────────────────
  Step 1: Update USD market caps for all WIG20 + mWIG40 + top sWIG80 names
    □ Use USD market cap (NOT PLN) — all MSCI thresholds are USD-denominated
    □ Monitor EUR/PLN and USD/PLN — a 5% currency move can push stocks in/out

  Step 2: For MSCI Standard candidates ($1.5B–$4B full mktcap range):
    □ Full mktcap vs $2,500M threshold — where does it sit?
    □ Float-adj mktcap vs $1,300M — what is the FIF?
    □ ATVR (3-month annualised) vs 20% minimum
    □ Foreign room: if foreign ownership near cap, FIF at risk

  Step 3: For MSCI EM Small Cap candidates ($95M–$300M float-adj range):
    □ Full mktcap vs $127M — rarely an issue for listed WIG stocks
    □ Float-adj mktcap vs $95M
    □ ATVR vs 15% — more often the binding constraint for small caps
    □ Free float must be clean (no lock-ups, no OFE holdings in FIF calc)

  Step 4: Momentum filter
    □ Minimum: RS percentile ≥ 55th vs WIG (all-share) universe
    □ Preferred: RS ≥ 70th, above 200d MA in PLN terms
    □ Check USD-denominated chart (MSCI uses USD prices) — PLN chart can mislead

  POSITION SIZING FRAMEWORK FOR MSCI PLAYS
  ──────────────────────────────────────────
  Phase 1 ACCUMULATE (T−45 to T−20 before announcement):
    → Initial position: 30–50% of target
    → Trigger: eligibility clearly met + RS > 60th pct

  Phase 2 SIZE UP (T−20 to T−5):
    → Add to 75–100% of target
    → Trigger: confirmation in volume data, no adverse FX move

  Phase 3 ANNOUNCEMENT (T−5 to T+0):
    → Hold only; announcement gap averages +2.9% for MSCI EM
    → Do NOT chase if stock opens >5% above prior close

  Phase 4 EFFECTIVE DATE (T+0 to T+5):
    → Sell 50–75% into the passive buying pressure
    → Passive funds must buy at closing prices on effective date

  Phase 5 FADE (T+5 to T+30):
    → Exit remaining if no other fundamental thesis supports holding

  EXPECTED ALPHA DECOMPOSITION (MSCI EM AVERAGE)
  ─────────────────────────────────────────────────
  Pre-announcement drift    (Phase 1–2):  +2.0% avg
  Announcement gap          (Phase 3):    +2.9% avg
  Effective date squeeze    (Phase 4):    +1.2% avg
  Post-reversal             (Phase 5):   −1.2% avg
  ──────────────────────────────────────────────────
  Total captured (entry Phase 1, exit Phase 4):  ~6.1% avg
  Holding period: ~6–8 weeks → annualised ~50–55% IRR

  UPGRADE PATHS (HIGHEST TO LOWEST PROBABILITY)
  ───────────────────────────────────────────────
  1. MSCI EM Small Cap → MSCI Poland Standard:
     Most predictable; happens when float-adj cap crosses ~$1.3B
     FORCED BUYING: both MSCI Poland trackers AND MSCI EM rebalance
     Expected stocks to monitor: Allegro (done), Dino Polska, Pepco

  2. Not-in-MSCI → MSCI EM Small Cap (new addition):
     Happens at quarterly reviews; lower price impact
     Recent example: Żabka Group, Mabion, some fintech listings

  3. MSCI Poland Standard → Higher weight:
     Market cap outperformance vs peers increases index weight
     Semi-annual rebalancing creates proportional forced buying

  4. NOT-IN-INDEX → MSCI Poland Standard (direct):
     Very rare — requires company to cross Standard threshold immediately
     Usually only via transformative M&A or FX-driven cap increase

  FX SENSITIVITY TABLE (USD threshold = $2,500M full cap)
  ─────────────────────────────────────────────────────────
  PLN/USD    Required PLN mktcap for $2,500M threshold
  ───────────────────────────────────────────────────
  3.80       PLN 9,500M
  4.00       PLN 10,000M
  4.20       PLN 10,500M   ← current approx.
  4.40       PLN 11,000M
  4.60       PLN 11,500M

  KEY INSIGHT: If PLN strengthens 5% vs USD, a PLN 10.5B mktcap stock
  goes from $2,500M → $2,630M — creating a natural inclusion catalyst
  from currency alone. Monitor NBP monetary policy and EUR/PLN carefully.
""")
    print("═" * 72)
    print()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def run() -> None:
    """Run all MSCI/WIG inclusion analyses."""
    print_msci_wig_methodology()
    analyse_allegro()
    analyse_dino_polska()
    analyse_zabka()
    analyse_pko_bp_reference()
    analyse_pepco()


if __name__ == "__main__":
    run()
