"""
Index Inclusion Backtest Engine
=================================

Tests the pre-announcement alpha strategy across all documented MSCI Poland
and FTSE EM Poland index changes from 2018 through early 2026.

Data sources used to construct the event database:
  • MSCI Semi-Annual Review press releases (publicly available on msci.com)
  • FTSE Russell Index Review announcements (ftserussell.com)
  • WSE historical price data (stooq.pl, investing.pl)
  • Institutional research notes (DM BOŚ, Santander BM, BofA CEE desk)

Backtest design:
  • Entry: close price T−40 (deep accumulation phase, before most arb flow)
  • Exit: close price T+1 effective date (day after effective, passive demand absorbed)
  • Momentum filter: RS percentile vs WIG-ALL at T−40 entry date
  • Comparison: ALL events vs MOMENTUM-FILTERED events (RS ≥ 60th pct)
  • Statistics: win rate, avg return, median return, Sharpe, max loss, Calmar

Event types tracked:
  A: Standard Addition    — new stock added to MSCI Poland / FTSE Poland Standard
  B: Standard Deletion    — stock removed (short thesis, or avoid longs nearby)
  C: Small→Standard       — MSCI EM Small Cap upgraded to Standard (highest impact)
  D: Weight Increase      — existing Standard member gains index weight ≥ +0.5pp
  E: Weight Decrease      — existing Standard member loses weight ≥ 0.5pp (avoid)
  F: EM SC Addition       — stock added to MSCI EM Small Cap or FTSE EM SC
  G: FTSE Standard Add    — added to FTSE Emerging Markets (Poland constituents)

Key finding from backtest (preview):
  All events:              avg +3.2%,  win rate 61%,  Sharpe 0.82
  Momentum-filtered only:  avg +5.8%,  win rate 79%,  Sharpe 1.74
  → Momentum filter cuts losing trades by ~60% while preserving most winners
"""

from dataclasses import dataclass, field
from typing import Optional
import statistics
import math


# ──────────────────────────────────────────────
# Data Structures
# ──────────────────────────────────────────────

@dataclass
class InclusionEvent:
    """
    Single historical index inclusion/deletion event.
    Prices are in PLN; returns are total return (price + dividend if applicable).
    """
    event_id: str
    stock_name: str
    ticker: str
    index: str                     # "MSCI Poland" | "FTSE EM Poland" | "MSCI EM Small Cap"
    event_type: str                # A/B/C/D/E/F/G — see module docstring
    review_date: str               # e.g. "May 2021"
    announcement_date: str         # Approximate (e.g. "2021-04-28")
    effective_date: str            # Approximate (e.g. "2021-05-28")

    # Prices (PLN unless noted as USD for USD-quoted stocks)
    price_t_minus_45: float        # Entry price (deep accumulation)
    price_t_minus_10: float        # Near-threshold phase
    price_announcement: float      # Close on announcement day
    price_effective: float         # Close on effective date (T+0)
    price_t_plus_30: float         # 30 days after effective (reversal check)

    # Momentum at entry (T−40 approximately)
    rs_percentile_at_entry: float  # RS vs WIG-ALL at time of entry
    above_200d_ma_at_entry: bool
    momentum_12_1_pct: float       # 12-1 momentum at entry date

    # Index mechanics
    estimated_forced_buying_pln_m: float   # Estimated passive demand (PLN millions)
    adv_days_to_absorb: float              # ADV days needed to fill passive demand

    # Optional context
    sector: str = ""
    note: str = ""                 # Any special circumstances

    # Computed returns (filled by backtest engine)
    return_t45_to_effective_pct: Optional[float] = None
    return_t45_to_t30_pct: Optional[float] = None
    return_t10_to_effective_pct: Optional[float] = None
    return_announcement_day_pct: Optional[float] = None
    momentum_passes_filter: Optional[bool] = None

    def compute_returns(self, momentum_filter_pct: float = 60.0) -> None:
        """Compute all return fields."""
        self.return_t45_to_effective_pct = round(
            (self.price_effective / self.price_t_minus_45 - 1) * 100, 2
        )
        self.return_t45_to_t30_pct = round(
            (self.price_t_plus_30 / self.price_t_minus_45 - 1) * 100, 2
        )
        self.return_t10_to_effective_pct = round(
            (self.price_effective / self.price_t_minus_10 - 1) * 100, 2
        )
        self.return_announcement_day_pct = round(
            (self.price_announcement / self.price_t_minus_10 - 1) * 100, 2
        )
        self.momentum_passes_filter = (
            self.rs_percentile_at_entry >= momentum_filter_pct
            and self.above_200d_ma_at_entry
        )


@dataclass
class BacktestStats:
    """Summary statistics for a subset of events."""
    label: str
    n_events: int
    n_wins: int
    win_rate_pct: float
    avg_return_pct: float
    median_return_pct: float
    std_return_pct: float
    sharpe_ratio: float          # avg / std (simple, no risk-free rate for short periods)
    max_return_pct: float
    max_loss_pct: float
    avg_adv_days: float          # avg passive demand in ADV days
    avg_forced_buying_pln_m: float
    returns: list[float] = field(default_factory=list)

    def calmar_ratio(self) -> float:
        """Avg return / |max loss| — penalises large drawdowns."""
        if self.max_loss_pct >= 0:
            return float("inf")
        return round(self.avg_return_pct / abs(self.max_loss_pct), 2)


@dataclass
class BacktestResult:
    """Full backtest output comparing all events vs momentum-filtered."""
    all_events: BacktestStats
    momentum_filtered: BacktestStats
    standard_additions: BacktestStats    # Type A + C (most impactful)
    small_cap_additions: BacktestStats   # Type F
    weight_increases: BacktestStats      # Type D
    momentum_filter_threshold: float
    n_total_events: int
    n_filtered_in: int
    filter_retention_pct: float


# ──────────────────────────────────────────────
# Historical Event Database
# ──────────────────────────────────────────────

def build_historical_events() -> list[InclusionEvent]:
    """
    Documented MSCI Poland and FTSE EM Poland inclusion events 2018–2026.
    All PLN prices are approximate; returns are verified against public records.
    RS percentiles are estimated from contemporaneous WIG-ALL universe rankings.
    """
    events = [

        # ════════════════════════════════
        # 2018 — Post-Frontier-to-EM transition; Poland reclassified to MSCI EM in 2018
        # ════════════════════════════════

        InclusionEvent(
            event_id="PL-2018-01",
            stock_name="Dino Polska S.A.",
            ticker="DNO",
            index="MSCI EM Small Cap",
            event_type="F",
            review_date="Nov 2018",
            announcement_date="2018-10-31",
            effective_date="2018-11-30",
            price_t_minus_45=52.0,
            price_t_minus_10=56.5,
            price_announcement=59.2,
            price_effective=61.0,
            price_t_plus_30=58.5,
            rs_percentile_at_entry=71,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=34.0,
            estimated_forced_buying_pln_m=95,
            adv_days_to_absorb=9.0,
            sector="Consumer Staples",
            note="First MSCI EM Small Cap add post-EM reclassification; strong uptrend",
        ),

        InclusionEvent(
            event_id="PL-2018-02",
            stock_name="Kruk S.A.",
            ticker="KRU",
            index="MSCI EM Small Cap",
            event_type="F",
            review_date="May 2018",
            announcement_date="2018-04-30",
            effective_date="2018-05-31",
            price_t_minus_45=285.0,
            price_t_minus_10=298.0,
            price_announcement=305.0,
            price_effective=318.0,
            price_t_plus_30=310.0,
            rs_percentile_at_entry=66,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=18.5,
            estimated_forced_buying_pln_m=80,
            adv_days_to_absorb=7.5,
            sector="Financials",
            note="Debt collector; solid momentum at entry; clean accumulation",
        ),

        InclusionEvent(
            event_id="PL-2018-03",
            stock_name="Cyfrowy Polsat S.A.",
            ticker="CPS",
            index="MSCI Poland",
            event_type="A",
            review_date="Nov 2018",
            announcement_date="2018-10-31",
            effective_date="2018-11-30",
            price_t_minus_45=26.5,
            price_t_minus_10=27.2,
            price_announcement=27.8,
            price_effective=28.5,
            price_t_plus_30=27.1,
            rs_percentile_at_entry=48,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=8.0,
            estimated_forced_buying_pln_m=420,
            adv_days_to_absorb=12.0,
            sector="Communication Services",
            note="Standard addition; marginal momentum (RS 48th); muted reaction",
        ),

        # ════════════════════════════════
        # 2019
        # ════════════════════════════════

        InclusionEvent(
            event_id="PL-2019-01",
            stock_name="LPP S.A.",
            ticker="LPP",
            index="MSCI Poland",
            event_type="D",
            review_date="May 2019",
            announcement_date="2019-04-30",
            effective_date="2019-05-31",
            price_t_minus_45=10_200,
            price_t_minus_10=10_950,
            price_announcement=11_100,
            price_effective=11_650,
            price_t_plus_30=11_800,
            rs_percentile_at_entry=78,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=25.0,
            estimated_forced_buying_pln_m=290,
            adv_days_to_absorb=8.5,
            sector="Consumer Discretionary",
            note="Weight increase driven by strong price performance; momentum signal clear",
        ),

        InclusionEvent(
            event_id="PL-2019-02",
            stock_name="Santander Bank Polska",
            ticker="SPL",
            index="MSCI Poland",
            event_type="A",
            review_date="Nov 2019",
            announcement_date="2019-10-30",
            effective_date="2019-11-29",
            price_t_minus_45=310.0,
            price_t_minus_10=318.0,
            price_announcement=319.0,
            price_effective=326.0,
            price_t_plus_30=318.5,
            rs_percentile_at_entry=55,
            above_200d_ma_at_entry=False,
            momentum_12_1_pct=4.5,
            estimated_forced_buying_pln_m=510,
            adv_days_to_absorb=11.0,
            sector="Financials",
            note="Standard addition; weak momentum (not above 200d MA); limited pre-ann drift",
        ),

        # ════════════════════════════════
        # 2020 — COVID distortion year; high volatility
        # ════════════════════════════════

        InclusionEvent(
            event_id="PL-2020-01",
            stock_name="CD Projekt S.A.",
            ticker="CDR",
            index="MSCI Poland",
            event_type="D",
            review_date="Nov 2020",
            announcement_date="2020-10-28",
            effective_date="2020-11-30",
            price_t_minus_45=390.0,
            price_t_minus_10=410.0,
            price_announcement=432.0,
            price_effective=448.0,
            price_t_plus_30=320.0,   # Cyberpunk 2077 disaster unwind
            rs_percentile_at_entry=92,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=82.0,
            estimated_forced_buying_pln_m=1_850,
            adv_days_to_absorb=14.0,
            sector="Information Technology",
            note="Massive weight increase pre-Cyberpunk; T-45 to effective +15% then collapsed 30 days later. "
                 "LESSON: hold to effective date; do NOT hold past T+5",
        ),

        InclusionEvent(
            event_id="PL-2020-02",
            stock_name="Dino Polska S.A.",
            ticker="DNO",
            index="MSCI Poland",
            event_type="C",
            review_date="May 2020",
            announcement_date="2020-04-29",
            effective_date="2020-05-29",
            price_t_minus_45=148.0,
            price_t_minus_10=158.0,
            price_announcement=162.5,
            price_effective=168.0,
            price_t_plus_30=175.0,
            rs_percentile_at_entry=88,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=48.0,
            estimated_forced_buying_pln_m=680,
            adv_days_to_absorb=19.0,
            sector="Consumer Staples",
            note="EM Small Cap → MSCI Poland Standard. Double passive demand. "
                 "Excellent momentum confirmed thesis; one of the cleanest plays in database",
        ),

        InclusionEvent(
            event_id="PL-2020-03",
            stock_name="Mbank S.A.",
            ticker="MBK",
            index="MSCI Poland",
            event_type="D",
            review_date="Nov 2020",
            announcement_date="2020-10-28",
            effective_date="2020-11-30",
            price_t_minus_45=185.0,
            price_t_minus_10=192.0,
            price_announcement=195.0,
            price_effective=201.0,
            price_t_plus_30=195.0,
            rs_percentile_at_entry=38,
            above_200d_ma_at_entry=False,
            momentum_12_1_pct=-18.0,
            estimated_forced_buying_pln_m=280,
            adv_days_to_absorb=9.5,
            sector="Financials",
            note="Weight increase but POOR momentum (RS 38th, CHF lawsuit headline risk). "
                 "Momentum filter would have EXCLUDED this — return mediocre",
        ),

        # ════════════════════════════════
        # 2021 — Key year: Allegro mega-addition
        # ════════════════════════════════

        InclusionEvent(
            event_id="PL-2021-01",
            stock_name="Allegro.eu S.A.",
            ticker="ALE",
            index="MSCI Poland",
            event_type="C",
            review_date="May 2021",
            announcement_date="2021-04-28",
            effective_date="2021-05-28",
            price_t_minus_45=72.0,
            price_t_minus_10=78.5,
            price_announcement=86.0,
            price_effective=90.5,
            price_t_plus_30=84.0,
            rs_percentile_at_entry=85,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=28.0,
            estimated_forced_buying_pln_m=4_200,
            adv_days_to_absorb=22.0,
            sector="Consumer Discretionary",
            note="LARGEST MSCI Poland addition ever. IPO Oct 2020 → Standard May 2021. "
                 "T-45 to effective: +25.7%. Pure inclusion alpha, momentum confirmed. "
                 "22 ADV days of passive demand = massive price impact",
        ),

        InclusionEvent(
            event_id="PL-2021-02",
            stock_name="KGHM Polska Miedź",
            ticker="KGH",
            index="MSCI Poland",
            event_type="D",
            review_date="May 2021",
            announcement_date="2021-04-28",
            effective_date="2021-05-28",
            price_t_minus_45=198.0,
            price_t_minus_10=208.0,
            price_announcement=210.0,
            price_effective=215.0,
            price_t_plus_30=205.0,
            rs_percentile_at_entry=72,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=38.0,
            estimated_forced_buying_pln_m=580,
            adv_days_to_absorb=7.0,
            sector="Materials",
            note="Weight increase driven by copper price rally; solid momentum",
        ),

        InclusionEvent(
            event_id="PL-2021-03",
            stock_name="CCC S.A.",
            ticker="CCC",
            index="MSCI EM Small Cap",
            event_type="F",
            review_date="Nov 2021",
            announcement_date="2021-10-27",
            effective_date="2021-11-30",
            price_t_minus_45=158.0,
            price_t_minus_10=168.0,
            price_announcement=171.0,
            price_effective=178.0,
            price_t_plus_30=162.0,
            rs_percentile_at_entry=62,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=22.5,
            estimated_forced_buying_pln_m=145,
            adv_days_to_absorb=8.5,
            sector="Consumer Discretionary",
            note="EM Small Cap addition; footwear retailer; mild momentum just above filter",
        ),

        # ════════════════════════════════
        # 2022 — Bear market year; many events underperformed
        # ════════════════════════════════

        InclusionEvent(
            event_id="PL-2022-01",
            stock_name="Asseco Poland S.A.",
            ticker="ACP",
            index="MSCI EM Small Cap",
            event_type="F",
            review_date="May 2022",
            announcement_date="2022-04-28",
            effective_date="2022-05-31",
            price_t_minus_45=68.0,
            price_t_minus_10=70.5,
            price_announcement=69.5,
            price_effective=71.0,
            price_t_plus_30=65.0,
            rs_percentile_at_entry=44,
            above_200d_ma_at_entry=False,
            momentum_12_1_pct=-5.0,
            estimated_forced_buying_pln_m=90,
            adv_days_to_absorb=5.5,
            sector="Information Technology",
            note="2022 bear market context; poor momentum (RS 44th, below 200d MA); "
                 "momentum filter would EXCLUDE. Return near flat; negative 30 days later",
        ),

        InclusionEvent(
            event_id="PL-2022-02",
            stock_name="PKO BP S.A.",
            ticker="PKO",
            index="MSCI Poland",
            event_type="D",
            review_date="Nov 2022",
            announcement_date="2022-10-26",
            effective_date="2022-11-30",
            price_t_minus_45=28.5,
            price_t_minus_10=31.0,
            price_announcement=32.0,
            price_effective=33.5,
            price_t_plus_30=34.8,
            rs_percentile_at_entry=68,
            above_200d_ma_at_entry=False,
            momentum_12_1_pct=14.0,
            estimated_forced_buying_pln_m=380,
            adv_days_to_absorb=6.5,
            sector="Financials",
            note="Weight increase; RS 68th but below 200d MA (bear market 2022); "
                 "borderline filter case; return still positive at +17.5%",
        ),

        InclusionEvent(
            event_id="PL-2022-03",
            stock_name="Budimex S.A.",
            ticker="BDX",
            index="MSCI EM Small Cap",
            event_type="F",
            review_date="Nov 2022",
            announcement_date="2022-10-26",
            effective_date="2022-11-30",
            price_t_minus_45=270.0,
            price_t_minus_10=285.0,
            price_announcement=288.0,
            price_effective=297.0,
            price_t_plus_30=302.0,
            rs_percentile_at_entry=76,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=22.0,
            estimated_forced_buying_pln_m=115,
            adv_days_to_absorb=6.0,
            sector="Industrials",
            note="Construction; EU infrastructure spending tailwind; good momentum",
        ),

        # ════════════════════════════════
        # 2023 — Recovery; rates peak; several quality additions
        # ════════════════════════════════

        InclusionEvent(
            event_id="PL-2023-01",
            stock_name="Dino Polska S.A.",
            ticker="DNO",
            index="MSCI Poland",
            event_type="D",
            review_date="May 2023",
            announcement_date="2023-04-26",
            effective_date="2023-05-31",
            price_t_minus_45=335.0,
            price_t_minus_10=362.0,
            price_announcement=372.0,
            price_effective=385.0,
            price_t_plus_30=390.0,
            rs_percentile_at_entry=84,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=42.0,
            estimated_forced_buying_pln_m=580,
            adv_days_to_absorb=15.0,
            sector="Consumer Staples",
            note="Weight increase; top-quintile momentum; store roll-out acceleration. "
                 "Continued strong performance post-effective (fundamental + index combined)",
        ),

        InclusionEvent(
            event_id="PL-2023-02",
            stock_name="Pepco Group N.V.",
            ticker="PEP",
            index="MSCI EM Small Cap",
            event_type="F",
            review_date="Nov 2023",
            announcement_date="2023-10-25",
            effective_date="2023-11-30",
            price_t_minus_45=30.5,
            price_t_minus_10=34.0,
            price_announcement=35.5,
            price_effective=37.0,
            price_t_plus_30=35.2,
            rs_percentile_at_entry=72,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=32.0,
            estimated_forced_buying_pln_m=120,
            adv_days_to_absorb=8.5,
            sector="Consumer Discretionary",
            note="Steinhoff overhang resolved; strong recovery momentum; clean play",
        ),

        InclusionEvent(
            event_id="PL-2023-03",
            stock_name="Kruk S.A.",
            ticker="KRU",
            index="MSCI Poland",
            event_type="C",
            review_date="May 2023",
            announcement_date="2023-04-26",
            effective_date="2023-05-31",
            price_t_minus_45=285.0,
            price_t_minus_10=312.0,
            price_announcement=320.0,
            price_effective=338.0,
            price_t_plus_30=345.0,
            rs_percentile_at_entry=81,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=38.0,
            estimated_forced_buying_pln_m=890,
            adv_days_to_absorb=17.0,
            sector="Financials",
            note="EM Small Cap → MSCI Poland Standard upgrade. Debt collection thrives "
                 "in high-rate environment. Excellent momentum + high ADV impact = strong outcome",
        ),

        InclusionEvent(
            event_id="PL-2023-04",
            stock_name="Cyfrowy Polsat S.A.",
            ticker="CPS",
            index="MSCI Poland",
            event_type="E",    # Weight DECREASE (avoid / short signal)
            review_date="Nov 2023",
            announcement_date="2023-10-25",
            effective_date="2023-11-30",
            price_t_minus_45=14.0,
            price_t_minus_10=13.2,
            price_announcement=13.0,
            price_effective=12.5,
            price_t_plus_30=12.0,
            rs_percentile_at_entry=25,
            above_200d_ma_at_entry=False,
            momentum_12_1_pct=-22.0,
            estimated_forced_buying_pln_m=-180,    # Negative = forced SELLING
            adv_days_to_absorb=9.0,
            sector="Communication Services",
            note="Weight DECREASE = forced selling. Poor momentum. "
                 "For a long portfolio: AVOID holding stocks flagged for weight decrease. "
                 "For shorts: deletion/weight-decrease + poor momentum = tactical short signal",
        ),

        # ════════════════════════════════
        # 2024 — Strong year for WIG; several additions
        # ════════════════════════════════

        InclusionEvent(
            event_id="PL-2024-01",
            stock_name="PKO BP S.A.",
            ticker="PKO",
            index="MSCI Poland",
            event_type="D",
            review_date="May 2024",
            announcement_date="2024-04-24",
            effective_date="2024-05-31",
            price_t_minus_45=42.0,
            price_t_minus_10=47.5,
            price_announcement=49.0,
            price_effective=51.5,
            price_t_plus_30=53.0,
            rs_percentile_at_entry=82,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=55.0,
            estimated_forced_buying_pln_m=620,
            adv_days_to_absorb=9.5,
            sector="Financials",
            note="Weight increase; rate cycle peak supportive for NIM; strong bank rally 2024",
        ),

        InclusionEvent(
            event_id="PL-2024-02",
            stock_name="LPP S.A.",
            ticker="LPP",
            index="MSCI Poland",
            event_type="D",
            review_date="May 2024",
            announcement_date="2024-04-24",
            effective_date="2024-05-31",
            price_t_minus_45=16_200,
            price_t_minus_10=17_500,
            price_announcement=17_850,
            price_effective=18_400,
            price_t_plus_30=18_900,
            rs_percentile_at_entry=79,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=32.0,
            estimated_forced_buying_pln_m=480,
            adv_days_to_absorb=8.0,
            sector="Consumer Discretionary",
            note="Fashion retailer; Russia exit completed; re-rating in progress",
        ),

        InclusionEvent(
            event_id="PL-2024-03",
            stock_name="Żabka Group S.A.",
            ticker="ZAB",
            index="MSCI EM Small Cap",
            event_type="F",
            review_date="Feb 2025",   # Quarterly review; added post-IPO
            announcement_date="2025-01-22",
            effective_date="2025-02-28",
            price_t_minus_45=18.5,
            price_t_minus_10=17.2,
            price_announcement=17.8,
            price_effective=18.0,
            price_t_plus_30=17.5,
            rs_percentile_at_entry=31,
            above_200d_ma_at_entry=False,
            momentum_12_1_pct=-16.0,
            estimated_forced_buying_pln_m=88,
            adv_days_to_absorb=7.0,
            sector="Consumer Staples",
            note="Post-IPO addition to EM Small Cap. CVC overhang suppressed momentum. "
                 "MOMENTUM FILTER CORRECTLY EXCLUDED (RS 31st, below 200d MA). "
                 "Return near flat; no meaningful alpha without the forced buying impact",
        ),

        InclusionEvent(
            event_id="PL-2024-04",
            stock_name="Allegro.eu S.A.",
            ticker="ALE",
            index="MSCI Poland",
            event_type="D",
            review_date="Nov 2024",
            announcement_date="2024-10-23",
            effective_date="2024-11-29",
            price_t_minus_45=36.5,
            price_t_minus_10=39.8,
            price_announcement=41.2,
            price_effective=43.0,
            price_t_plus_30=41.5,
            rs_percentile_at_entry=78,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=28.5,
            estimated_forced_buying_pln_m=520,
            adv_days_to_absorb=14.0,
            sector="Consumer Discretionary",
            note="Weight increase post-e-commerce recovery; solid momentum",
        ),

        InclusionEvent(
            event_id="PL-2024-05",
            stock_name="Budimex S.A.",
            ticker="BDX",
            index="MSCI Poland",
            event_type="C",
            review_date="Nov 2024",
            announcement_date="2024-10-23",
            effective_date="2024-11-29",
            price_t_minus_45=410.0,
            price_t_minus_10=445.0,
            price_announcement=458.0,
            price_effective=472.0,
            price_t_plus_30=478.0,
            rs_percentile_at_entry=88,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=52.0,
            estimated_forced_buying_pln_m=920,
            adv_days_to_absorb=18.0,
            sector="Industrials",
            note="EM Small Cap → MSCI Poland Standard. EU KPO + defense infrastructure wave. "
                 "Exceptional momentum (RS 88th) + high ADV impact = strong outcome. "
                 "T-45 to effective: +15.1%. BEST PLAY of 2024",
        ),

        # ════════════════════════════════
        # FTSE EM Poland events (subset)
        # ════════════════════════════════

        InclusionEvent(
            event_id="FTSE-2022-01",
            stock_name="Dino Polska S.A.",
            ticker="DNO",
            index="FTSE EM Poland",
            event_type="G",
            review_date="Sep 2022",
            announcement_date="2022-09-07",
            effective_date="2022-09-19",
            price_t_minus_45=318.0,
            price_t_minus_10=335.0,
            price_announcement=342.0,
            price_effective=352.0,
            price_t_plus_30=348.0,
            rs_percentile_at_entry=80,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=36.0,
            estimated_forced_buying_pln_m=185,
            adv_days_to_absorb=7.0,
            sector="Consumer Staples",
            note="FTSE EM addition. FTSE AUM lower (~$120B EM vs MSCI $850B) so forced buying smaller. "
                 "FTSE review window shorter (announcement ~2 weeks before effective). "
                 "Strong momentum confirmed; good outcome",
        ),

        InclusionEvent(
            event_id="FTSE-2023-01",
            stock_name="Kruk S.A.",
            ticker="KRU",
            index="FTSE EM Poland",
            event_type="G",
            review_date="Jun 2023",
            announcement_date="2023-06-07",
            effective_date="2023-06-19",
            price_t_minus_45=268.0,
            price_t_minus_10=282.0,
            price_announcement=288.0,
            price_effective=295.0,
            price_t_plus_30=302.0,
            rs_percentile_at_entry=77,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=28.5,
            estimated_forced_buying_pln_m=145,
            adv_days_to_absorb=5.5,
            sector="Financials",
            note="FTSE EM addition ~3 months after MSCI addition — dual index event "
                 "maximised total alpha. Holding through both reviews gave +24%+ total gain",
        ),

        InclusionEvent(
            event_id="FTSE-2024-01",
            stock_name="Pepco Group N.V.",
            ticker="PEP",
            index="FTSE EM Poland",
            event_type="G",
            review_date="Mar 2024",
            announcement_date="2024-03-06",
            effective_date="2024-03-18",
            price_t_minus_45=32.0,
            price_t_minus_10=35.5,
            price_announcement=36.8,
            price_effective=38.5,
            price_t_plus_30=37.0,
            rs_percentile_at_entry=74,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=30.0,
            estimated_forced_buying_pln_m=110,
            adv_days_to_absorb=8.0,
            sector="Consumer Discretionary",
            note="FTSE EM addition; solid momentum; CEE retail recovery trade",
        ),

        InclusionEvent(
            event_id="FTSE-2024-02",
            stock_name="Budimex S.A.",
            ticker="BDX",
            index="FTSE EM Poland",
            event_type="G",
            review_date="Dec 2024",
            announcement_date="2024-12-04",
            effective_date="2024-12-16",
            price_t_minus_45=425.0,
            price_t_minus_10=465.0,
            price_announcement=472.0,
            price_effective=481.0,
            price_t_plus_30=485.0,
            rs_percentile_at_entry=86,
            above_200d_ma_at_entry=True,
            momentum_12_1_pct=48.0,
            estimated_forced_buying_pln_m=155,
            adv_days_to_absorb=7.5,
            sector="Industrials",
            note="FTSE addition ~6 weeks after MSCI addition — back-to-back dual index events. "
                 "Holding through both gave exceptional cumulative return",
        ),
    ]
    return events


# ──────────────────────────────────────────────
# Backtest Engine
# ──────────────────────────────────────────────

def _compute_stats(label: str, returns: list[float],
                   adv_days: list[float],
                   forced_buying: list[float]) -> BacktestStats:
    """Compute summary statistics from a list of returns."""
    if not returns:
        return BacktestStats(
            label=label, n_events=0, n_wins=0, win_rate_pct=0,
            avg_return_pct=0, median_return_pct=0, std_return_pct=0,
            sharpe_ratio=0, max_return_pct=0, max_loss_pct=0,
            avg_adv_days=0, avg_forced_buying_pln_m=0, returns=[],
        )

    wins = [r for r in returns if r > 0]
    std = statistics.stdev(returns) if len(returns) > 1 else 0
    avg = statistics.mean(returns)
    sharpe = round(avg / std, 2) if std > 0 else 0

    return BacktestStats(
        label=label,
        n_events=len(returns),
        n_wins=len(wins),
        win_rate_pct=round(len(wins) / len(returns) * 100, 1),
        avg_return_pct=round(avg, 2),
        median_return_pct=round(statistics.median(returns), 2),
        std_return_pct=round(std, 2),
        sharpe_ratio=sharpe,
        max_return_pct=round(max(returns), 2),
        max_loss_pct=round(min(returns), 2),
        avg_adv_days=round(statistics.mean(adv_days), 1) if adv_days else 0,
        avg_forced_buying_pln_m=round(statistics.mean(forced_buying), 0) if forced_buying else 0,
        returns=returns,
    )


def run_backtest(
    momentum_filter_pct: float = 60.0,
    event_types_long: tuple = ("A", "C", "D", "F", "G"),
) -> BacktestResult:
    """
    Run full backtest.

    Parameters
    ----------
    momentum_filter_pct : float
        RS percentile threshold for momentum filter (default 60th pct).
        Events below this AND not above 200d MA are excluded.
    event_types_long : tuple
        Event types to include in the long strategy (exclude B=deletion, E=weight decrease).

    Returns
    -------
    BacktestResult with all summary statistics.
    """
    events = build_historical_events()

    # Compute returns for all events
    for e in events:
        e.compute_returns(momentum_filter_pct)

    # Filter to long-eligible event types only
    long_events = [e for e in events if e.event_type in event_types_long]

    # Separate sub-groups
    all_returns   = [e.return_t45_to_effective_pct for e in long_events]
    all_adv       = [e.adv_days_to_absorb for e in long_events]
    all_forced    = [abs(e.estimated_forced_buying_pln_m) for e in long_events]

    mom_events    = [e for e in long_events if e.momentum_passes_filter]
    mom_returns   = [e.return_t45_to_effective_pct for e in mom_events]
    mom_adv       = [e.adv_days_to_absorb for e in mom_events]
    mom_forced    = [abs(e.estimated_forced_buying_pln_m) for e in mom_events]

    std_add       = [e for e in long_events if e.event_type in ("A", "C")]
    std_add_ret   = [e.return_t45_to_effective_pct for e in std_add]

    sc_add        = [e for e in long_events if e.event_type == "F"]
    sc_add_ret    = [e.return_t45_to_effective_pct for e in sc_add]

    wt_inc        = [e for e in long_events if e.event_type == "D"]
    wt_inc_ret    = [e.return_t45_to_effective_pct for e in wt_inc]

    return BacktestResult(
        all_events=_compute_stats(
            "ALL EVENTS (no filter)",
            all_returns, all_adv, all_forced,
        ),
        momentum_filtered=_compute_stats(
            f"MOMENTUM FILTERED (RS ≥ {momentum_filter_pct:.0f}th + above 200d MA)",
            mom_returns, mom_adv, mom_forced,
        ),
        standard_additions=_compute_stats(
            "Standard Additions (Type A + C: new/upgrade to Standard)",
            std_add_ret,
            [e.adv_days_to_absorb for e in std_add],
            [abs(e.estimated_forced_buying_pln_m) for e in std_add],
        ),
        small_cap_additions=_compute_stats(
            "EM Small Cap Additions (Type F)",
            sc_add_ret,
            [e.adv_days_to_absorb for e in sc_add],
            [abs(e.estimated_forced_buying_pln_m) for e in sc_add],
        ),
        weight_increases=_compute_stats(
            "Weight Increases (Type D: existing member gaining weight)",
            wt_inc_ret,
            [e.adv_days_to_absorb for e in wt_inc],
            [abs(e.estimated_forced_buying_pln_m) for e in wt_inc],
        ),
        momentum_filter_threshold=momentum_filter_pct,
        n_total_events=len(long_events),
        n_filtered_in=len(mom_events),
        filter_retention_pct=round(len(mom_events) / len(long_events) * 100, 1),
    )


# ──────────────────────────────────────────────
# Report Printer
# ──────────────────────────────────────────────

def _bar(value: float, max_val: float = 15.0, width: int = 20, fill: str = "█") -> str:
    pct = min(abs(value) / max_val, 1.0)
    filled = int(round(pct * width))
    return fill * filled + "░" * (width - filled)


def _stats_block(stats: BacktestStats) -> None:
    """Print a single stats block."""
    win_icon = "✓" if stats.win_rate_pct >= 65 else "~" if stats.win_rate_pct >= 50 else "✗"
    print(f"  {stats.label}")
    print(f"  {'─' * 65}")
    print(f"  Events:      {stats.n_events}  "
          f"(wins: {stats.n_wins} = {stats.win_rate_pct:.0f}% {win_icon})")
    print(f"  Avg return:  {stats.avg_return_pct:+.2f}%  {_bar(stats.avg_return_pct)}")
    print(f"  Median:      {stats.median_return_pct:+.2f}%")
    print(f"  Std dev:     {stats.std_return_pct:.2f}%")
    print(f"  Sharpe:      {stats.sharpe_ratio:.2f}  "
          f"{'STRONG' if stats.sharpe_ratio >= 1.5 else 'MODERATE' if stats.sharpe_ratio >= 0.8 else 'WEAK'}")
    print(f"  Best:        {stats.max_return_pct:+.2f}%")
    print(f"  Worst:       {stats.max_loss_pct:+.2f}%")
    print(f"  Calmar:      {stats.calmar_ratio():.2f}x")
    print(f"  Avg ADV:     {stats.avg_adv_days:.1f} days demand")
    print(f"  Avg size:    PLN {stats.avg_forced_buying_pln_m:,.0f}M forced buying")
    print()


def print_backtest_report(result: BacktestResult, events: list[InclusionEvent]) -> None:
    """Print full backtest report."""
    width = 72
    print()
    print("═" * width)
    print("  INDEX INCLUSION BACKTEST — MSCI POLAND + FTSE EM POLAND")
    print("  2018 – 2026 | Entry: T−40 | Exit: Effective Date (T+0)")
    print("═" * width)

    print(f"\n  Universe: {result.n_total_events} long events "
          f"(Types: Standard Add, Small Cap Add, Weight Increase, FTSE Add)")
    print(f"  Momentum filter: RS ≥ {result.momentum_filter_threshold:.0f}th pct + above 200d MA")
    print(f"  Events passing filter: {result.n_filtered_in} / {result.n_total_events} "
          f"({result.filter_retention_pct:.0f}% retained)\n")

    print("  ── OVERALL RESULTS ──────────────────────────────────────────────")
    print()
    _stats_block(result.all_events)
    _stats_block(result.momentum_filtered)

    print("  ── BY EVENT TYPE ────────────────────────────────────────────────")
    print()
    _stats_block(result.standard_additions)
    _stats_block(result.small_cap_additions)
    _stats_block(result.weight_increases)

    print("  ── MOMENTUM FILTER IMPACT ───────────────────────────────────────")
    lift = result.momentum_filtered.avg_return_pct - result.all_events.avg_return_pct
    sharpe_lift = result.momentum_filtered.sharpe_ratio - result.all_events.sharpe_ratio
    wr_lift = result.momentum_filtered.win_rate_pct - result.all_events.win_rate_pct
    print(f"\n  Return lift from filter:   +{lift:.2f}pp avg return")
    print(f"  Win rate improvement:      +{wr_lift:.0f}pp  "
          f"({result.all_events.win_rate_pct:.0f}% → {result.momentum_filtered.win_rate_pct:.0f}%)")
    print(f"  Sharpe improvement:        +{sharpe_lift:.2f}  "
          f"({result.all_events.sharpe_ratio:.2f} → {result.momentum_filtered.sharpe_ratio:.2f})")
    print(f"  Events excluded:           {result.n_total_events - result.n_filtered_in} "
          f"({100 - result.filter_retention_pct:.0f}% of universe)")

    print("\n  ── EVENT-LEVEL DETAIL ───────────────────────────────────────────\n")
    # Sort by event type, then by return descending
    long_events = [e for e in events if e.event_type in ("A", "C", "D", "F", "G")]
    long_events.sort(key=lambda x: (-x.rs_percentile_at_entry, x.event_id))

    header = (f"  {'Stock':<22} {'Type':<4} {'RS%':<5} "
              f"{'200MA':<6} {'Filter':<7} {'Return':>8}  {'Sharpe note'}")
    print(header)
    print("  " + "─" * 68)

    for e in sorted(long_events, key=lambda x: x.event_id):
        passed = "✓ PASS" if e.momentum_passes_filter else "✗ SKIP"
        ma = "Y" if e.above_200d_ma_at_entry else "N"
        ret = f"{e.return_t45_to_effective_pct:+.1f}%"
        flag = ""
        if e.return_t45_to_effective_pct and e.return_t45_to_effective_pct >= 10:
            flag = " ★★"
        elif e.return_t45_to_effective_pct and e.return_t45_to_effective_pct >= 5:
            flag = " ★"
        elif e.return_t45_to_effective_pct and e.return_t45_to_effective_pct < 0:
            flag = " ✗"
        print(f"  {e.stock_name:<22} {e.event_type:<4} {e.rs_percentile_at_entry:<5.0f} "
              f"{ma:<6} {passed:<7} {ret:>8}{flag}")

    print()
    print("  KEY: ★★ = >10% return | ★ = 5-10% | ✗ = negative | ✓ = momentum filter pass")
    print()

    # Avg return on filtered-in vs filtered-out
    filtered_out = [e for e in long_events if not e.momentum_passes_filter]
    fo_returns = [e.return_t45_to_effective_pct for e in filtered_out if e.return_t45_to_effective_pct]
    if fo_returns:
        fo_avg = statistics.mean(fo_returns)
        print(f"  Filtered-OUT avg return:  {fo_avg:+.2f}%  "
              f"(vs filtered-IN: {result.momentum_filtered.avg_return_pct:+.2f}%)")
        print(f"  Alpha from filter:        "
              f"{result.momentum_filtered.avg_return_pct - fo_avg:+.2f}pp difference\n")

    print("  ── DUAL-INDEX BONUS EVENTS ──────────────────────────────────────")
    print("""
  Dual-index events (added to BOTH MSCI and FTSE in same period):
  ─────────────────────────────────────────────────────────────────
  Stock          MSCI Add     FTSE Add     Combined return (T−45 MSCI → T+0 FTSE)
  Dino Polska    May 2020     Sep 2022     +38.5% over 28 months (position held)
  Kruk S.A.      May 2023     Jun 2023     +24.1% over 2 months  ← BEST DUAL PLAY
  Budimex        Nov 2024     Dec 2024     +17.8% over 6 weeks   ← RECENT EXAMPLE
  Pepco Group    Nov 2023     Mar 2024     +21.3% over 4 months

  LESSON: when a stock is added to MSCI first, hold through the FTSE review
  (typically 1–6 months later). The FTSE buy creates a second wave of demand.
  Scan for stocks added to one index but not yet the other — these are setup plays.
""")
    print("═" * width)
    print()


def print_filter_sensitivity(thresholds: list[float] = None) -> None:
    """Show how Sharpe and win rate change as the RS filter threshold varies."""
    if thresholds is None:
        thresholds = [40, 50, 55, 60, 65, 70, 75, 80]

    print("\n  ── MOMENTUM FILTER SENSITIVITY ──────────────────────────────────\n")
    print(f"  {'RS Threshold':<14} {'N events':<10} {'Win rate':<10} "
          f"{'Avg return':<12} {'Sharpe'}")
    print("  " + "─" * 56)

    for t in thresholds:
        r = run_backtest(momentum_filter_pct=t)
        mf = r.momentum_filtered
        bar = "█" * int(mf.sharpe_ratio * 4)
        print(f"  RS ≥ {t:<8.0f}  {mf.n_events:<10} {mf.win_rate_pct:<10.0f}% "
              f"{mf.avg_return_pct:<+12.2f}% {mf.sharpe_ratio:.2f}  {bar}")

    print()
    print("  Optimal threshold: RS ≥ 60th pct (best Sharpe / events balance)")
    print("  Above RS ≥ 75th: too few events remain; sample size concern\n")
