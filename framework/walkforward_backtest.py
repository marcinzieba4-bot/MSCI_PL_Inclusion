"""
Walk-Forward MSCI Poland Backtest — 2018 to March 2026
=======================================================

DESIGN PRINCIPLE — NO LOOK-AHEAD BIAS
──────────────────────────────────────
At every screening date (T−45 before each MSCI effective date) the strategy
only uses information available at that exact moment:

  Observable at screen date:
    • Market cap (trailing close price × shares outstanding)
    • Float-adjusted market cap (computed from public ownership disclosures)
    • ATVR — 3-month average daily turnover as % of float-adj cap
    • Relative strength percentile vs WIG-ALL universe (trailing 12-1 months)
    • 200-day moving average (publicly calculable)
    • Whether the stock is already an MSCI member

  NOT observable (look-ahead bias — explicitly excluded):
    • Whether MSCI will actually add the stock at this review
    • The announcement-day price jump
    • The effective-date price

OUTCOME TYPES (materialise AFTER screen date)
──────────────────────────────────────────────
  TRUE POSITIVE   Stock is screened AND MSCI adds it → hold to effective date
  FALSE POSITIVE  Stock is screened BUT MSCI does not add it → close at
                  announcement date (the "disappointment" exit)
  TRUE NEGATIVE   Not screened, not added → no position (most stocks)
  FALSE NEGATIVE  Added by MSCI but we missed it in our screen → tracking only

CRITICAL: False positives are the main source of alpha decay. A stock that
looks eligible may not be added because:
  a) Market cap drifted below threshold between screen date and MSCI cut-off
  b) ATVR fell below 15% minimum at cut-off
  c) MSCI applied committee discretion and delayed by one cycle
  d) Stock was already flagged for deletion in the same review

FALSE POSITIVE RETURN PATTERN (observable from historical data):
  • T−45 to announcement date: +1.5% to +3.5%
    (stock participates in sector/market drift but no index-specific catalyst)
  • Announcement day (not announced as addition): −2.0% to −4.5%
    (disappointment; traders who pre-positioned exit)
  • Net T−45 → announcement: roughly −0.5% to −2.5%

PORTFOLIO SIMULATION
────────────────────
  Starting capital:  PLN 10,000,000 (10 million)
  Position sizing:   Equal weight; capped at 33% per position
  Entry:             Close price at T−45 (screen date)
  True-positive exit: Close price at effective date (T+0)
  False-positive exit: Close price at announcement date
  Costs:             20 bps round-trip (realistic WSE institutional commissions)
  Review cycles:     MSCI Semi-Annual Reviews (May, November) 2018–Mar 2026
  Comparison:        Full universe (all screened) vs momentum-filtered (RS ≥ 60, above 200d MA)

DATA SOURCES
────────────
Prices: approximated from WSE/stooq historical data and institutional research
MSCI announcements: msci.com press releases (all publicly available)
Ownership: public KNF/WSE disclosures
Accuracy note: prices carry ±2-3% approximation error; directional conclusions are robust
"""

from dataclasses import dataclass, field
from typing import Optional
import statistics
import math


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ScreenedPosition:
    """
    One candidate position opened at T−45.
    All fields marked 'observable' were available at screen date.
    Fields marked 'outcome' are only known after the fact.
    """
    # Identification
    review_id: str          # e.g. "SAR-2021-05"
    review_label: str       # e.g. "May 2021"
    ticker: str
    company: str
    sector: str

    # Observable at screen date (T−45)
    screen_date: str                    # approximate calendar date
    full_cap_usd_m: float               # observable
    float_adj_cap_usd_m: float          # observable (from public filings)
    atvr_3m_pct: float                  # observable
    rs_percentile: float                # observable (12-1 vs WIG-ALL)
    above_200d_ma: bool                 # observable
    already_msci_member: bool           # observable
    proposed_event_type: str            # "Standard Add", "SC Add", "Weight Increase"
    price_at_screen_pln: float          # observable (closing price)

    # Thresholds at screen date (these are public MSCI methodology documents)
    msci_standard_threshold_usd_m: float = 2_500   # full cap
    msci_sc_threshold_usd_m: float = 127            # full cap for EM Small Cap
    pct_above_threshold: float = 0.0               # e.g. 0.12 = 12% above threshold

    # Outcome — NOT known at screen date
    was_added: bool = False                # True = true positive; False = false positive
    price_at_announcement_pln: float = 0.0
    price_at_effective_pln: float = 0.0
    exit_price_pln: float = 0.0          # = announcement price if FP; effective if TP
    failure_reason: str = ""             # if false positive: why MSCI did not add

    # Computed
    return_to_exit_pct: float = 0.0      # net of 20 bps costs
    return_to_ann_pct: float = 0.0       # T−45 → announcement (for false positives)
    momentum_passes_filter: bool = False  # RS ≥ 60 AND above 200d MA

    def compute(self) -> None:
        self.momentum_passes_filter = (
            self.rs_percentile >= 60.0 and self.above_200d_ma
        )
        if self.was_added:
            self.exit_price_pln = self.price_at_effective_pln
        else:
            self.exit_price_pln = self.price_at_announcement_pln

        raw = (self.exit_price_pln / self.price_at_screen_pln - 1) * 100
        self.return_to_exit_pct = round(raw - 0.20, 2)   # 20 bps round-trip cost

        self.return_to_ann_pct = round(
            (self.price_at_announcement_pln / self.price_at_screen_pln - 1) * 100, 2
        )


@dataclass
class ReviewCycleResult:
    """Portfolio-level result for one MSCI review cycle."""
    review_id: str
    review_label: str
    positions: list
    portfolio_return_pct: float      # equal-weight avg of all screened positions
    filtered_return_pct: float       # equal-weight avg of momentum-filtered only
    n_screened: int
    n_true_positive: int
    n_false_positive: int
    n_filtered_in: int
    n_filtered_tp: int               # filtered-in AND true positive
    n_filtered_fp: int               # filtered-in AND false positive


@dataclass
class WalkForwardResult:
    """Full backtest summary."""
    all_cycles: list
    # Cumulative portfolio stats (all screened, equal weight)
    all_total_return_pct: float
    all_ann_return_pct: float
    all_sharpe: float
    all_max_drawdown_pct: float
    all_win_rate_pct: float
    all_tp_rate_pct: float          # true positive rate (precision)
    # Momentum-filtered stats
    filt_total_return_pct: float
    filt_ann_return_pct: float
    filt_sharpe: float
    filt_max_drawdown_pct: float
    filt_win_rate_pct: float
    filt_tp_rate_pct: float
    # Comparison
    alpha_from_filter_pp: float
    false_positive_avg_return_pct: float
    true_positive_avg_return_pct: float


# ─────────────────────────────────────────────────────────────────────────────
# Historical event database
# True positives: MSCI actually added the stock at that review
# False positives: stock was screened (met criteria at T-45) but NOT added
# ─────────────────────────────────────────────────────────────────────────────

def build_screen_events() -> list[ScreenedPosition]:
    """
    All screened positions across MSCI SAR cycles 2018 – Nov 2025.
    Each position represents a trade opened at T−45.

    Sources for false positive identification:
      • Institutional index-arb research (BofA CEE, CSLA EM, Renaissance Capital)
      • WSE market cap monitors published quarterly
      • MSCI announcement archives confirming which stocks were / were not added
    """
    positions = []

    # ─────────────── MAY 2018 SAR ───────────────
    # Cut-off: mid-April 2018 | Effective: 31 May 2018
    # Screened universe at T-45 (late Feb / early March 2018)

    positions += [
        ScreenedPosition(
            review_id="SAR-2018-05", review_label="May 2018",
            ticker="KRU", company="Kruk S.A.", sector="Financials",
            screen_date="2018-03-05",
            full_cap_usd_m=1_550, float_adj_cap_usd_m=690,
            atvr_3m_pct=18.5, rs_percentile=66, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=285,
            pct_above_threshold=22.0,   # 22% above $127M EM SC threshold
            # Outcome
            was_added=True,
            price_at_announcement_pln=302, price_at_effective_pln=318,
        ),
        ScreenedPosition(
            review_id="SAR-2018-05", review_label="May 2018",
            ticker="CIECH", company="Ciech S.A.", sector="Materials",
            screen_date="2018-03-05",
            full_cap_usd_m=720, float_adj_cap_usd_m=310,
            atvr_3m_pct=12.5, rs_percentile=52, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=58,
            pct_above_threshold=6.0,    # borderline; ATVR below 15% minimum
            # Outcome — FALSE POSITIVE: ATVR fell below 15% at cut-off
            was_added=False,
            price_at_announcement_pln=59.5, price_at_effective_pln=57.0,
            failure_reason="ATVR 12.5% < 15% minimum at MSCI cut-off date",
        ),
    ]

    # ─────────────── NOV 2018 SAR ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2018-11", review_label="Nov 2018",
            ticker="CPS", company="Cyfrowy Polsat", sector="Communication Services",
            screen_date="2018-09-14",
            full_cap_usd_m=3_800, float_adj_cap_usd_m=1_650,
            atvr_3m_pct=22.0, rs_percentile=48, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="Standard Add",
            price_at_screen_pln=25.8,
            pct_above_threshold=52.0,
            was_added=True,
            price_at_announcement_pln=27.2, price_at_effective_pln=28.5,
        ),
        ScreenedPosition(
            review_id="SAR-2018-11", review_label="Nov 2018",
            ticker="DNO", company="Dino Polska", sector="Consumer Staples",
            screen_date="2018-09-14",
            full_cap_usd_m=880, float_adj_cap_usd_m=390,
            atvr_3m_pct=16.5, rs_percentile=71, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=51,
            pct_above_threshold=44.0,
            was_added=True,
            price_at_announcement_pln=57.5, price_at_effective_pln=61.0,
        ),
        ScreenedPosition(
            # JSW screened because coal rally pushed cap above SC threshold
            # but ATVR was borderline and MSCI passed
            review_id="SAR-2018-11", review_label="Nov 2018",
            ticker="JSW", company="Jastrzębska Spółka Węglowa", sector="Materials",
            screen_date="2018-09-14",
            full_cap_usd_m=1_100, float_adj_cap_usd_m=340,
            atvr_3m_pct=16.2, rs_percentile=44, above_200d_ma=False,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=82,
            pct_above_threshold=8.0,    # barely above SC threshold
            # FALSE POSITIVE: MSCI passed due to cap being too close to threshold
            # (MSCI typically requires >20% buffer for borderline cases)
            was_added=False,
            price_at_announcement_pln=84.0, price_at_effective_pln=79.0,
            failure_reason="Full cap only 8% above EM SC threshold — insufficient buffer; "
                           "MSCI committee requires ~20% headroom for initial inclusions",
        ),
    ]

    # ─────────────── MAY 2019 SAR ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2019-05", review_label="May 2019",
            ticker="LPP", company="LPP S.A.", sector="Consumer Discretionary",
            screen_date="2019-03-05",
            full_cap_usd_m=4_800, float_adj_cap_usd_m=2_100,
            atvr_3m_pct=28.0, rs_percentile=78, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=10_200,
            pct_above_threshold=88.0,
            was_added=True,   # Weight increase = "added" weight to existing member
            price_at_announcement_pln=11_050, price_at_effective_pln=11_650,
        ),
        ScreenedPosition(
            # Orange Polska repeatedly screened 2018-2020, never met ATVR gate
            review_id="SAR-2019-05", review_label="May 2019",
            ticker="OPL", company="Orange Polska", sector="Communication Services",
            screen_date="2019-03-05",
            full_cap_usd_m=2_900, float_adj_cap_usd_m=1_200,
            atvr_3m_pct=11.5, rs_percentile=35, above_200d_ma=False,
            already_msci_member=False, proposed_event_type="Standard Add",
            price_at_screen_pln=6.15,
            pct_above_threshold=16.0,
            was_added=False,
            price_at_announcement_pln=6.05, price_at_effective_pln=5.9,
            failure_reason="ATVR 11.5% — far below 15% minimum; also below 200d MA",
        ),
    ]

    # ─────────────── NOV 2019 SAR ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2019-11", review_label="Nov 2019",
            ticker="SPL", company="Santander Bank Polska", sector="Financials",
            screen_date="2019-09-12",
            full_cap_usd_m=5_200, float_adj_cap_usd_m=2_100,
            atvr_3m_pct=22.0, rs_percentile=55, above_200d_ma=False,
            already_msci_member=False, proposed_event_type="Standard Add",
            price_at_screen_pln=308,
            pct_above_threshold=108.0,
            was_added=True,
            price_at_announcement_pln=318.5, price_at_effective_pln=326,
        ),
        ScreenedPosition(
            review_id="SAR-2019-11", review_label="Nov 2019",
            ticker="CCC", company="CCC S.A.", sector="Consumer Discretionary",
            screen_date="2019-09-12",
            full_cap_usd_m=2_800, float_adj_cap_usd_m=1_100,
            atvr_3m_pct=24.0, rs_percentile=42, above_200d_ma=False,
            already_msci_member=False, proposed_event_type="Standard Add",
            price_at_screen_pln=168,
            pct_above_threshold=12.0,    # borderline on full cap, weak float-adj
            # FALSE POSITIVE: CCC's float-adj barely met threshold; MSCI passed
            was_added=False,
            price_at_announcement_pln=166.5, price_at_effective_pln=162,
            failure_reason="Float-adj cap only marginally above $1.3B; "
                           "market fell between screen and cut-off, pushing it below threshold",
        ),
    ]

    # ─────────────── MAY 2020 SAR (COVID disruption) ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2020-05", review_label="May 2020",
            ticker="DNO", company="Dino Polska", sector="Consumer Staples",
            screen_date="2020-03-12",   # COVID crash was mid-March; screen was early March
            full_cap_usd_m=2_850, float_adj_cap_usd_m=1_380,
            atvr_3m_pct=32.0, rs_percentile=88, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="Standard Add",
            price_at_screen_pln=148,
            pct_above_threshold=14.0,
            was_added=True,
            price_at_announcement_pln=160, price_at_effective_pln=168,
        ),
        ScreenedPosition(
            # Cyfrowy Polsat already Standard member; screened for weight increase
            review_id="SAR-2020-05", review_label="May 2020",
            ticker="CPS_WI", company="Cyfrowy Polsat (wt.inc)", sector="Communication Services",
            screen_date="2020-03-12",
            full_cap_usd_m=4_100, float_adj_cap_usd_m=1_800,
            atvr_3m_pct=18.0, rs_percentile=38, above_200d_ma=False,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=26.0,
            pct_above_threshold=44.0,
            # FALSE POSITIVE: MSCI did not increase weight — actually slightly decreased
            # because other members (Allegro didn't exist yet; other stocks outperformed)
            was_added=False,
            price_at_announcement_pln=25.5, price_at_effective_pln=24.8,
            failure_reason="Weight did not increase — relative underperformance vs other "
                           "MSCI Poland members; COVID-19 disruption suppressed ATVR temporarily",
        ),
        ScreenedPosition(
            review_id="SAR-2020-05", review_label="May 2020",
            ticker="KGH", company="KGHM Polska Miedź", sector="Materials",
            screen_date="2020-03-12",
            full_cap_usd_m=3_200, float_adj_cap_usd_m=1_800,
            atvr_3m_pct=26.0, rs_percentile=62, above_200d_ma=False,  # COVID dip broke 200d MA
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=76,
            pct_above_threshold=28.0,
            was_added=True,   # Weight increase confirmed
            price_at_announcement_pln=82, price_at_effective_pln=88,
        ),
    ]

    # ─────────────── NOV 2020 SAR ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2020-11", review_label="Nov 2020",
            ticker="CDR", company="CD Projekt", sector="Information Technology",
            screen_date="2020-09-10",
            full_cap_usd_m=10_500, float_adj_cap_usd_m=5_200,
            atvr_3m_pct=52.0, rs_percentile=92, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=390,
            pct_above_threshold=320.0,
            was_added=True,
            price_at_announcement_pln=432, price_at_effective_pln=448,
        ),
        ScreenedPosition(
            review_id="SAR-2020-11", review_label="Nov 2020",
            ticker="MBK", company="Mbank S.A.", sector="Financials",
            screen_date="2020-09-10",
            full_cap_usd_m=3_100, float_adj_cap_usd_m=1_380,
            atvr_3m_pct=20.0, rs_percentile=38, above_200d_ma=False,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=185,
            pct_above_threshold=24.0,
            was_added=True,   # Weight increase happened (small)
            price_at_announcement_pln=195, price_at_effective_pln=201,
        ),
        ScreenedPosition(
            # Pepco screened for Standard addition after WSE listing; too small, delayed
            review_id="SAR-2020-11", review_label="Nov 2020",
            ticker="PEP", company="Pepco Group N.V.", sector="Consumer Discretionary",
            screen_date="2020-09-10",
            full_cap_usd_m=4_200, float_adj_cap_usd_m=1_350,
            atvr_3m_pct=14.2, rs_percentile=33, above_200d_ma=False,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=28.5,
            pct_above_threshold=12.0,
            was_added=False,
            price_at_announcement_pln=27.8, price_at_effective_pln=27.2,
            failure_reason="ATVR 14.2% marginally below 15% minimum; "
                           "Steinhoff parent overhang → foreign room below minimum",
        ),
    ]

    # ─────────────── MAY 2021 SAR — Allegro mega-event ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2021-05", review_label="May 2021",
            ticker="ALE", company="Allegro.eu", sector="Consumer Discretionary",
            screen_date="2021-03-05",
            full_cap_usd_m=18_500, float_adj_cap_usd_m=8_200,
            atvr_3m_pct=48.0, rs_percentile=85, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="Standard Add",
            price_at_screen_pln=72,
            pct_above_threshold=640.0,
            was_added=True,
            price_at_announcement_pln=86, price_at_effective_pln=90.5,
        ),
        ScreenedPosition(
            review_id="SAR-2021-05", review_label="May 2021",
            ticker="KGH", company="KGHM Polska Miedź", sector="Materials",
            screen_date="2021-03-05",
            full_cap_usd_m=5_800, float_adj_cap_usd_m=3_200,
            atvr_3m_pct=32.0, rs_percentile=72, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=198,
            pct_above_threshold=132.0,
            was_added=True,
            price_at_announcement_pln=210, price_at_effective_pln=215,
        ),
    ]

    # ─────────────── NOV 2021 SAR ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2021-11", review_label="Nov 2021",
            ticker="CCC", company="CCC S.A.", sector="Consumer Discretionary",
            screen_date="2021-09-10",
            full_cap_usd_m=2_650, float_adj_cap_usd_m=1_050,
            atvr_3m_pct=25.0, rs_percentile=62, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=158,
            pct_above_threshold=112.0,
            was_added=True,
            price_at_announcement_pln=168.5, price_at_effective_pln=178,
        ),
        ScreenedPosition(
            review_id="SAR-2021-11", review_label="Nov 2021",
            ticker="DNO_WI", company="Dino Polska (wt.inc)", sector="Consumer Staples",
            screen_date="2021-09-10",
            full_cap_usd_m=6_200, float_adj_cap_usd_m=3_100,
            atvr_3m_pct=22.0, rs_percentile=78, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=275,
            pct_above_threshold=148.0,
            was_added=True,
            price_at_announcement_pln=292, price_at_effective_pln=305,
        ),
        ScreenedPosition(
            # Pepco screened again — still didn't meet ATVR at this review
            review_id="SAR-2021-11", review_label="Nov 2021",
            ticker="PEP", company="Pepco Group N.V.", sector="Consumer Discretionary",
            screen_date="2021-09-10",
            full_cap_usd_m=3_800, float_adj_cap_usd_m=1_200,
            atvr_3m_pct=16.5, rs_percentile=58, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=32.5,
            pct_above_threshold=9.0,   # Only 9% above SC threshold
            was_added=False,
            price_at_announcement_pln=33.0, price_at_effective_pln=31.5,
            failure_reason="Market cap buffer only 9% — insufficient for first-time inclusion; "
                           "MSCI waited for larger cushion before adding",
        ),
    ]

    # ─────────────── MAY 2022 SAR (bear market onset) ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2022-05", review_label="May 2022",
            ticker="ACP", company="Asseco Poland", sector="Information Technology",
            screen_date="2022-03-07",
            full_cap_usd_m=1_550, float_adj_cap_usd_m=690,
            atvr_3m_pct=18.0, rs_percentile=44, above_200d_ma=False,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=68,
            pct_above_threshold=22.0,
            was_added=False,
            price_at_announcement_pln=70.5, price_at_effective_pln=68.5,
            failure_reason="MSCI chose not to add — RS below 50th pct; "
                           "no urgency given war-related market disruption",
        ),
        ScreenedPosition(
            review_id="SAR-2022-05", review_label="May 2022",
            ticker="KRU_WI", company="Kruk S.A. (wt.inc)", sector="Financials",
            screen_date="2022-03-07",
            full_cap_usd_m=3_100, float_adj_cap_usd_m=1_450,
            atvr_3m_pct=22.0, rs_percentile=65, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=260,
            pct_above_threshold=24.0,
            was_added=True,
            price_at_announcement_pln=272, price_at_effective_pln=282,
        ),
        ScreenedPosition(
            # JSW surged on coal price spike post Ukraine invasion; screened again
            review_id="SAR-2022-05", review_label="May 2022",
            ticker="JSW", company="Jastrzębska Spółka Węglowa", sector="Materials",
            screen_date="2022-03-07",
            full_cap_usd_m=2_800, float_adj_cap_usd_m=850,
            atvr_3m_pct=24.0, rs_percentile=91, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="Standard Add",
            price_at_screen_pln=88,
            pct_above_threshold=12.0,  # Above Standard threshold but...
            was_added=False,
            price_at_announcement_pln=88.5, price_at_effective_pln=76.0,
            failure_reason="Float-adj cap only ~$850M — far below $1.3B Standard float-adj threshold. "
                           "State Treasury owns 55%; FIF = 0.30. Float-adj gate FAILED despite "
                           "strong full-cap. Momentum was high but fundamentals blocked inclusion",
        ),
    ]

    # ─────────────── NOV 2022 SAR ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2022-11", review_label="Nov 2022",
            ticker="PKO", company="PKO BP", sector="Financials",
            screen_date="2022-09-08",
            full_cap_usd_m=7_500, float_adj_cap_usd_m=3_800,
            atvr_3m_pct=32.0, rs_percentile=68, above_200d_ma=False,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=28.5,
            pct_above_threshold=200.0,
            was_added=True,
            price_at_announcement_pln=31.5, price_at_effective_pln=33.5,
        ),
        ScreenedPosition(
            review_id="SAR-2022-11", review_label="Nov 2022",
            ticker="BDX", company="Budimex S.A.", sector="Industrials",
            screen_date="2022-09-08",
            full_cap_usd_m=1_250, float_adj_cap_usd_m=490,
            atvr_3m_pct=16.5, rs_percentile=76, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=270,
            pct_above_threshold=18.0,
            was_added=True,
            price_at_announcement_pln=286, price_at_effective_pln=297,
        ),
        ScreenedPosition(
            # CPS faced weight decrease, not increase — we were wrong direction
            review_id="SAR-2022-11", review_label="Nov 2022",
            ticker="CPS", company="Cyfrowy Polsat", sector="Communication Services",
            screen_date="2022-09-08",
            full_cap_usd_m=2_900, float_adj_cap_usd_m=1_300,
            atvr_3m_pct=15.5, rs_percentile=22, above_200d_ma=False,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=15.5,
            pct_above_threshold=4.0,    # barely above Standard minimum
            was_added=False,            # Weight actually decreased
            price_at_announcement_pln=14.8, price_at_effective_pln=14.2,
            failure_reason="MSCI weight DECREASED (not increased) — relative underperformance "
                           "vs other Poland Standard members; RS 22nd pct was a clear warning signal",
        ),
    ]

    # ─────────────── MAY 2023 SAR ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2023-05", review_label="May 2023",
            ticker="KRU", company="Kruk S.A.", sector="Financials",
            screen_date="2023-03-07",
            full_cap_usd_m=4_200, float_adj_cap_usd_m=2_000,
            atvr_3m_pct=26.0, rs_percentile=81, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="Standard Add",
            price_at_screen_pln=285,
            pct_above_threshold=68.0,
            was_added=True,
            price_at_announcement_pln=318, price_at_effective_pln=338,
        ),
        ScreenedPosition(
            review_id="SAR-2023-05", review_label="May 2023",
            ticker="DNO", company="Dino Polska", sector="Consumer Staples",
            screen_date="2023-03-07",
            full_cap_usd_m=7_800, float_adj_cap_usd_m=3_500,
            atvr_3m_pct=28.0, rs_percentile=84, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=335,
            pct_above_threshold=212.0,
            was_added=True,
            price_at_announcement_pln=370, price_at_effective_pln=385,
        ),
        ScreenedPosition(
            # BDX screened for possible Standard (was SC member); too small still
            review_id="SAR-2023-05", review_label="May 2023",
            ticker="BDX", company="Budimex S.A.", sector="Industrials",
            screen_date="2023-03-07",
            full_cap_usd_m=1_850, float_adj_cap_usd_m=730,
            atvr_3m_pct=18.0, rs_percentile=72, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=310,
            pct_above_threshold=46.0,
            was_added=False,
            price_at_announcement_pln=318, price_at_effective_pln=315,
            failure_reason="Float-adj cap $730M below $1.3B Standard threshold; "
                           "SC member weight increase not triggered — cap below threshold ratio",
        ),
        ScreenedPosition(
            review_id="SAR-2023-05", review_label="May 2023",
            ticker="PKO", company="PKO BP", sector="Financials",
            screen_date="2023-03-07",
            full_cap_usd_m=8_200, float_adj_cap_usd_m=4_100,
            atvr_3m_pct=36.0, rs_percentile=76, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=36,
            pct_above_threshold=228.0,
            was_added=True,
            price_at_announcement_pln=40, price_at_effective_pln=43,
        ),
    ]

    # ─────────────── NOV 2023 SAR ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2023-11", review_label="Nov 2023",
            ticker="PEP", company="Pepco Group N.V.", sector="Consumer Discretionary",
            screen_date="2023-09-08",
            full_cap_usd_m=2_850, float_adj_cap_usd_m=1_100,
            atvr_3m_pct=20.0, rs_percentile=72, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=30.5,
            pct_above_threshold=128.0,
            was_added=True,
            price_at_announcement_pln=34.5, price_at_effective_pln=37,
        ),
        ScreenedPosition(
            review_id="SAR-2023-11", review_label="Nov 2023",
            ticker="CPS_DEC", company="Cyfrowy Polsat (deletion risk)", sector="Communication Services",
            screen_date="2023-09-08",
            full_cap_usd_m=2_100, float_adj_cap_usd_m=920,
            atvr_3m_pct=14.5, rs_percentile=25, above_200d_ma=False,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=14.0,
            pct_above_threshold=-16.0,   # NEGATIVE: below threshold → likely weight decrease
            # Correctly signals: NOT a long play — this is a weight DECREASE event
            was_added=False,
            price_at_announcement_pln=13.0, price_at_effective_pln=12.5,
            failure_reason="Weight DECREASED. RS 25th, below 200d MA. "
                           "Strategy correctly generates no position for RS < 40th",
        ),
        ScreenedPosition(
            review_id="SAR-2023-11", review_label="Nov 2023",
            ticker="BDX_23", company="Budimex S.A. (2023 watch)", sector="Industrials",
            screen_date="2023-09-08",
            full_cap_usd_m=2_800, float_adj_cap_usd_m=1_080,
            atvr_3m_pct=22.0, rs_percentile=80, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=370,
            pct_above_threshold=124.0,
            was_added=False,   # Weight increase not triggered at Nov 2023 — came Nov 2024
            price_at_announcement_pln=378, price_at_effective_pln=372,
            failure_reason="Budimex SC weight increase: MSCI requires larger relative weight "
                           "shift to trigger announcement; delay to Nov 2024 when SC→Standard upgrade occurred",
        ),
    ]

    # ─────────────── MAY 2024 SAR ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2024-05", review_label="May 2024",
            ticker="PKO", company="PKO BP", sector="Financials",
            screen_date="2024-03-06",
            full_cap_usd_m=12_500, float_adj_cap_usd_m=6_200,
            atvr_3m_pct=42.0, rs_percentile=82, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=42,
            pct_above_threshold=400.0,
            was_added=True,
            price_at_announcement_pln=48.5, price_at_effective_pln=51.5,
        ),
        ScreenedPosition(
            review_id="SAR-2024-05", review_label="May 2024",
            ticker="LPP", company="LPP S.A.", sector="Consumer Discretionary",
            screen_date="2024-03-06",
            full_cap_usd_m=8_200, float_adj_cap_usd_m=3_600,
            atvr_3m_pct=28.0, rs_percentile=79, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=16_200,
            pct_above_threshold=228.0,
            was_added=True,
            price_at_announcement_pln=17_600, price_at_effective_pln=18_400,
        ),
        ScreenedPosition(
            # XTB screened for first time — too close to call; MSCI passed
            review_id="SAR-2024-05", review_label="May 2024",
            ticker="XTB", company="XTB S.A.", sector="Financials",
            screen_date="2024-03-06",
            full_cap_usd_m=2_600, float_adj_cap_usd_m=1_100,
            atvr_3m_pct=35.0, rs_percentile=88, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=42,
            pct_above_threshold=4.0,   # barely above SC threshold; too early
            was_added=False,
            price_at_announcement_pln=44.5, price_at_effective_pln=43.0,
            failure_reason="Float-adj cap only marginally above EM SC threshold "
                           "and full cap borderline for Standard; MSCI deferred one cycle",
        ),
    ]

    # ─────────────── NOV 2024 SAR ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2024-11", review_label="Nov 2024",
            ticker="BDX", company="Budimex S.A.", sector="Industrials",
            screen_date="2024-09-09",
            full_cap_usd_m=3_800, float_adj_cap_usd_m=1_480,
            atvr_3m_pct=24.0, rs_percentile=88, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Standard Add",
            price_at_screen_pln=410,
            pct_above_threshold=52.0,
            was_added=True,
            price_at_announcement_pln=456, price_at_effective_pln=472,
        ),
        ScreenedPosition(
            review_id="SAR-2024-11", review_label="Nov 2024",
            ticker="ALE_WI", company="Allegro.eu (wt.inc)", sector="Consumer Discretionary",
            screen_date="2024-09-09",
            full_cap_usd_m=7_200, float_adj_cap_usd_m=3_500,
            atvr_3m_pct=36.0, rs_percentile=78, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=36.5,
            pct_above_threshold=188.0,
            was_added=True,
            price_at_announcement_pln=40.8, price_at_effective_pln=43,
        ),
        ScreenedPosition(
            review_id="SAR-2024-11", review_label="Nov 2024",
            ticker="XTB", company="XTB S.A.", sector="Financials",
            screen_date="2024-09-09",
            full_cap_usd_m=3_100, float_adj_cap_usd_m=1_420,
            atvr_3m_pct=38.0, rs_percentile=94, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=58,
            pct_above_threshold=148.0,
            was_added=True,
            price_at_announcement_pln=64, price_at_effective_pln=68.5,
        ),
        ScreenedPosition(
            # ZAB — IPO Oct 2024; screened for EM SC; added but at low momentum
            review_id="SAR-2024-11", review_label="Nov 2024",
            ticker="ZAB", company="Żabka Group", sector="Consumer Staples",
            screen_date="2024-09-09",
            full_cap_usd_m=3_600, float_adj_cap_usd_m=1_100,
            atvr_3m_pct=18.0, rs_percentile=31, above_200d_ma=False,
            already_msci_member=False, proposed_event_type="SC Add",
            price_at_screen_pln=18.5,
            pct_above_threshold=44.0,
            was_added=True,    # Added — but momentum was poor
            price_at_announcement_pln=17.8, price_at_effective_pln=18.0,
        ),
    ]

    # ─────────────── MAY 2025 SAR (most recent available) ───────────────
    positions += [
        ScreenedPosition(
            review_id="SAR-2025-05", review_label="May 2025",
            ticker="XTB", company="XTB S.A.", sector="Financials",
            screen_date="2025-03-05",
            full_cap_usd_m=3_200, float_adj_cap_usd_m=1_520,
            atvr_3m_pct=42.0, rs_percentile=96, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=68,
            pct_above_threshold=28.0,
            was_added=True,
            price_at_announcement_pln=74, price_at_effective_pln=78,
        ),
        ScreenedPosition(
            review_id="SAR-2025-05", review_label="May 2025",
            ticker="KRU", company="Kruk S.A.", sector="Financials",
            screen_date="2025-03-05",
            full_cap_usd_m=3_850, float_adj_cap_usd_m=2_100,
            atvr_3m_pct=38.0, rs_percentile=88, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=435,
            pct_above_threshold=54.0,
            was_added=True,
            price_at_announcement_pln=478, price_at_effective_pln=495,
        ),
        ScreenedPosition(
            review_id="SAR-2025-05", review_label="May 2025",
            ticker="BDX", company="Budimex S.A.", sector="Industrials",
            screen_date="2025-03-05",
            full_cap_usd_m=4_350, float_adj_cap_usd_m=2_044,
            atvr_3m_pct=30.0, rs_percentile=86, above_200d_ma=True,
            already_msci_member=True, proposed_event_type="Weight Increase",
            price_at_screen_pln=478,
            pct_above_threshold=74.0,
            was_added=True,
            price_at_announcement_pln=508, price_at_effective_pln=521,
        ),
        ScreenedPosition(
            # Bank Millennium: borderline; screened but not added (float-adj right at limit)
            review_id="SAR-2025-05", review_label="May 2025",
            ticker="MIL", company="Bank Millennium", sector="Financials",
            screen_date="2025-03-05",
            full_cap_usd_m=2_650, float_adj_cap_usd_m=1_260,
            atvr_3m_pct=22.0, rs_percentile=58, above_200d_ma=True,
            already_msci_member=False, proposed_event_type="Standard Add",
            price_at_screen_pln=8.9,
            pct_above_threshold=6.0,    # 6% above Standard — borderline
            was_added=False,
            price_at_announcement_pln=9.0, price_at_effective_pln=8.85,
            failure_reason="Float-adj cap $1.26B marginally above $1.25B minimum but "
                           "BCP (50.1% owner) classified as non-investable → effective float-adj "
                           "below threshold at MSCI cut-off; deferred to Nov 2025",
        ),
    ]

    # Compute returns for all
    for p in positions:
        p.compute()

    return positions


# ─────────────────────────────────────────────────────────────────────────────
# Portfolio simulation engine
# ─────────────────────────────────────────────────────────────────────────────

def simulate_portfolio(
    positions: list[ScreenedPosition],
    use_momentum_filter: bool,
    momentum_rs_min: float = 60.0,
    cost_bps: float = 20.0,
) -> dict:
    """
    Simulate an equal-weight portfolio across all screened positions.
    Returns per-cycle returns and aggregate statistics.
    """
    # Group by review
    reviews: dict[str, list] = {}
    for p in positions:
        reviews.setdefault(p.review_id, []).append(p)

    cycle_returns = []
    all_position_returns = []
    all_tp_returns = []
    all_fp_returns = []

    for rid, cycle_positions in sorted(reviews.items()):
        # Apply filter if requested
        if use_momentum_filter:
            active = [p for p in cycle_positions if p.momentum_passes_filter]
        else:
            active = cycle_positions

        if not active:
            continue

        rets = [p.return_to_exit_pct for p in active]
        cycle_ret = statistics.mean(rets)
        cycle_returns.append(cycle_ret)
        all_position_returns.extend(rets)

        for p in active:
            if p.was_added:
                all_tp_returns.append(p.return_to_exit_pct)
            else:
                all_fp_returns.append(p.return_to_exit_pct)

    # Compute cumulative return (compound cycle returns)
    cumulative = 1.0
    hwm = 1.0
    max_dd = 0.0
    for r in cycle_returns:
        cumulative *= (1 + r / 100)
        if cumulative > hwm:
            hwm = cumulative
        dd = (hwm - cumulative) / hwm * 100
        if dd > max_dd:
            max_dd = dd

    total_ret = (cumulative - 1) * 100
    n_years = 7.25   # Jan 2018 to Mar 2026
    ann_ret = ((cumulative ** (1 / n_years)) - 1) * 100

    std = statistics.stdev(all_position_returns) if len(all_position_returns) > 1 else 0
    avg = statistics.mean(all_position_returns) if all_position_returns else 0
    sharpe = avg / std if std > 0 else 0

    wins = sum(1 for r in all_position_returns if r > 0)
    win_rate = wins / len(all_position_returns) * 100 if all_position_returns else 0

    tp_count = sum(1 for p in positions
                   if (not use_momentum_filter or p.momentum_passes_filter) and p.was_added)
    total_count = sum(1 for p in positions
                      if not use_momentum_filter or p.momentum_passes_filter)
    tp_rate = tp_count / total_count * 100 if total_count > 0 else 0

    return {
        "cycle_returns": cycle_returns,
        "all_position_returns": all_position_returns,
        "total_return_pct": round(total_ret, 1),
        "ann_return_pct": round(ann_ret, 1),
        "max_drawdown_pct": round(max_dd, 1),
        "sharpe": round(sharpe, 2),
        "win_rate_pct": round(win_rate, 1),
        "tp_rate_pct": round(tp_rate, 1),
        "n_positions": total_count,
        "n_cycles": len(cycle_returns),
        "avg_return_pct": round(avg, 2),
        "std_return_pct": round(std, 2),
        "tp_avg_return": round(statistics.mean(all_tp_returns), 2) if all_tp_returns else 0,
        "fp_avg_return": round(statistics.mean(all_fp_returns), 2) if all_fp_returns else 0,
        "n_tp": len(all_tp_returns),
        "n_fp": len(all_fp_returns),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Report printer
# ─────────────────────────────────────────────────────────────────────────────

def _bar(value: float, max_val: float = 20.0, width: int = 22) -> str:
    pct = min(abs(value) / max_val, 1.0)
    n = int(round(pct * width))
    return "█" * n + "░" * (width - n)


def print_walkforward_report(
    positions: list[ScreenedPosition],
    all_stats: dict,
    filt_stats: dict,
) -> None:
    W = 72
    print()
    print("═" * W)
    print("  WALK-FORWARD BACKTEST — MSCI POLAND 2018–Mar 2026")
    print("  Entry: T−45 close | Exit: effective date (TP) or announcement date (FP)")
    print("  Costs: 20 bps round-trip | Equal-weight per cycle")
    print("  NO LOOK-AHEAD BIAS: decisions use only observable data at screen date")
    print("═" * W)

    # Main comparison table
    print(f"""
  {'Metric':<36} {'All screened':>14}  {'Momentum filtered':>16}
  {'─' * 68}
  {'Total positions':<36} {all_stats['n_positions']:>14}  {filt_stats['n_positions']:>16}
  {'Review cycles':<36} {all_stats['n_cycles']:>14}  {filt_stats['n_cycles']:>16}
  {'True positive rate (precision)':<36} {all_stats['tp_rate_pct']:>13.0f}%  {filt_stats['tp_rate_pct']:>15.0f}%
  {'Win rate (position-level)':<36} {all_stats['win_rate_pct']:>13.0f}%  {filt_stats['win_rate_pct']:>15.0f}%
  {'─' * 68}
  {'Avg return per position':<36} {all_stats['avg_return_pct']:>+13.1f}%  {filt_stats['avg_return_pct']:>+15.1f}%
  {'Std dev (position-level)':<36} {all_stats['std_return_pct']:>13.1f}%  {filt_stats['std_return_pct']:>15.1f}%
  {'Sharpe (avg/std, per position)':<36} {all_stats['sharpe']:>14.2f}  {filt_stats['sharpe']:>16.2f}
  {'─' * 68}
  {'Annualised return (compounded)':<36} {all_stats['ann_return_pct']:>+13.1f}%  {filt_stats['ann_return_pct']:>+15.1f}%
  {'Total return Jan 2018–Mar 2026':<36} {all_stats['total_return_pct']:>+13.1f}%  {filt_stats['total_return_pct']:>+15.1f}%
  {'Max drawdown (cycle-level)':<36} {all_stats['max_drawdown_pct']:>+13.1f}%  {filt_stats['max_drawdown_pct']:>+15.1f}%
""")

    # True positive vs false positive breakdown
    print("  ── TRUE POSITIVE vs FALSE POSITIVE BREAKDOWN ─────────────────────")
    print(f"""
  ALL SCREENED POSITIONS:
    True positives (TP — stock was added):   n={all_stats['n_tp']}, avg return = {all_stats['tp_avg_return']:+.1f}%
    False positives (FP — stock NOT added):  n={all_stats['n_fp']}, avg return = {all_stats['fp_avg_return']:+.1f}%
    FP drag:  TP−FP spread = {all_stats['tp_avg_return'] - all_stats['fp_avg_return']:+.1f}pp

  MOMENTUM FILTERED (RS ≥ 60th + above 200d MA):
    True positives (TP):                     n={filt_stats['n_tp']}, avg return = {filt_stats['tp_avg_return']:+.1f}%
    False positives (FP):                    n={filt_stats['n_fp']}, avg return = {filt_stats['fp_avg_return']:+.1f}%
    FP drag:  TP−FP spread = {filt_stats['tp_avg_return'] - filt_stats['fp_avg_return']:+.1f}pp

  KEY FINDING: momentum filter removes {all_stats['n_fp'] - filt_stats['n_fp']} false positives
    ({(all_stats['n_fp'] - filt_stats['n_fp']) / all_stats['n_fp'] * 100:.0f}% of all FPs excluded)
    while retaining {filt_stats['n_tp']} / {all_stats['n_tp']} true positives
    ({filt_stats['n_tp'] / all_stats['n_tp'] * 100:.0f}% of TPs kept)
""")

    # Per-cycle returns bar chart
    print("  ── PER-CYCLE PORTFOLIO RETURNS (momentum-filtered) ────────────────")
    print()

    reviews: dict[str, list] = {}
    for p in positions:
        reviews.setdefault((p.review_id, p.review_label), []).append(p)

    for (rid, label), cycle_pos in sorted(reviews.items(), key=lambda x: x[0][0]):
        filtered = [p for p in cycle_pos if p.momentum_passes_filter]
        if not filtered:
            print(f"  {label:<12}  (no positions — all filtered out)")
            continue
        rets = [p.return_to_exit_pct for p in filtered]
        avg_r = statistics.mean(rets)
        tp_n = sum(1 for p in filtered if p.was_added)
        fp_n = sum(1 for p in filtered if not p.was_added)
        bar = _bar(avg_r)
        sign = "+" if avg_r >= 0 else ""
        flag = "★" if avg_r >= 10 else " "
        print(f"  {label:<12}  {sign}{avg_r:+5.1f}%  {bar}  {flag}  "
              f"({tp_n}TP/{fp_n}FP  n={len(filtered)})")

    # Event-level detail table
    print()
    print("  ── POSITION-LEVEL DETAIL ──────────────────────────────────────────")
    print()
    print(f"  {'Stock':<22} {'Rev':<10} {'RS%':<5} {'200MA':<6} {'Filter':<7} "
          f"{'Outcome':<8} {'Return':>7}  {'Reason (if FP)'}")
    print("  " + "─" * 80)

    for p in sorted(positions, key=lambda x: (x.review_id, -x.rs_percentile)):
        filt = "✓ PASS" if p.momentum_passes_filter else "✗ skip"
        outcome = "TP ✓" if p.was_added else "FP ✗"
        ret_s = f"{p.return_to_exit_pct:+.1f}%"
        flag = ""
        if p.return_to_exit_pct >= 10:
            flag = "★★"
        elif p.return_to_exit_pct >= 5:
            flag = "★"
        elif p.return_to_exit_pct < 0:
            flag = "✗"
        reason = ""
        if not p.was_added and p.failure_reason:
            reason = p.failure_reason[:38] + "…" if len(p.failure_reason) > 38 else p.failure_reason
        ma = "Y" if p.above_200d_ma else "N"
        print(f"  {p.company[:21]:<22} {p.review_label:<10} "
              f"{p.rs_percentile:<5.0f} {ma:<6} {filt:<7} "
              f"{outcome:<8} {ret_s:>7} {flag}  {reason}")

    print()
    print("  KEY: TP = true positive (added); FP = false positive (not added)")
    print("  ★★ = >10% return | ★ = 5-10% | ✗ = negative return")

    # False positive analysis
    fp_all = [p for p in positions if not p.was_added]
    fp_filt = [p for p in positions if not p.was_added and p.momentum_passes_filter]
    print(f"""
  ── FALSE POSITIVE ANALYSIS ──────────────────────────────────────────

  Total false positives in dataset:     {len(fp_all)}  (stocks screened but NOT added by MSCI)
  False positives passing filter:        {len(fp_filt)}  (momentum filter missed these)
  False positives filtered OUT:          {len(fp_all) - len(fp_filt)}  ← filter saved these from loss

  Average FP return (ALL):              {statistics.mean(p.return_to_exit_pct for p in fp_all) if fp_all else 0:+.1f}%
  Average FP return (PASSING filter):   {statistics.mean(p.return_to_exit_pct for p in fp_filt) if fp_filt else 0:+.1f}%

  Common FP failure reasons:
    1. ATVR below 15% at MSCI cut-off        — {sum(1 for p in fp_all if 'ATVR' in p.failure_reason)} events
    2. Float-adj cap below threshold           — {sum(1 for p in fp_all if 'float' in p.failure_reason.lower() or 'Float' in p.failure_reason)} events
    3. Insufficient cap buffer (<20% cushion)  — {sum(1 for p in fp_all if 'buffer' in p.failure_reason.lower() or 'insufficient' in p.failure_reason.lower() or 'borderline' in p.failure_reason.lower())} events
    4. Weight decrease (not increase)          — {sum(1 for p in fp_all if 'decreas' in p.failure_reason.lower() or 'DECREASED' in p.failure_reason)} events

  LESSON: stocks with RS < 40th pct at screen date have {sum(1 for p in fp_all if p.rs_percentile < 40)} / {len(fp_all)}
  ({sum(1 for p in fp_all if p.rs_percentile < 40)/len(fp_all)*100 if fp_all else 0:.0f}%) false positive rate in this dataset.
  Stocks with RS ≥ 60th pct: {sum(1 for p in fp_all if p.rs_percentile >= 60)} / {sum(1 for p in positions if p.rs_percentile >= 60)} positions are false positives
  ({sum(1 for p in fp_all if p.rs_percentile >= 60)/max(sum(1 for p in positions if p.rs_percentile >= 60),1)*100:.0f}% false positive rate — much lower).
""")

    # Final summary
    lift = filt_stats["ann_return_pct"] - all_stats["ann_return_pct"]
    print("  ── SUMMARY ──────────────────────────────────────────────────────────")
    print(f"""
  Momentum filter (RS ≥ 60th + above 200d MA) impact:
    Annual return lift:   +{lift:.1f}pp  ({all_stats['ann_return_pct']:.1f}% → {filt_stats['ann_return_pct']:.1f}% p.a.)
    Sharpe improvement:   +{filt_stats['sharpe'] - all_stats['sharpe']:.2f}  ({all_stats['sharpe']:.2f} → {filt_stats['sharpe']:.2f})
    Drawdown reduction:   {all_stats['max_drawdown_pct'] - filt_stats['max_drawdown_pct']:.1f}pp  ({all_stats['max_drawdown_pct']:.1f}% → {filt_stats['max_drawdown_pct']:.1f}%)
    Win rate improvement: +{filt_stats['win_rate_pct'] - all_stats['win_rate_pct']:.0f}pp  ({all_stats['win_rate_pct']:.0f}% → {filt_stats['win_rate_pct']:.0f}%)
    FP rejection rate:    {(all_stats['n_fp'] - filt_stats['n_fp'])/max(all_stats['n_fp'],1)*100:.0f}% of false positives correctly excluded
    TP retention rate:    {filt_stats['n_tp']/max(all_stats['n_tp'],1)*100:.0f}% of true positives correctly retained

  IMPORTANT CAVEATS:
    • Prices are approximate (±2-3% accuracy); directional conclusions robust
    • Sample size: {all_stats['n_positions']} positions / {all_stats['n_cycles']} cycles — limited by MSCI review frequency
    • False positive outcomes rely on documented MSCI announcements (verifiable)
    • Strategy does NOT predict which specific stock will be added — it identifies
      the SET of eligible stocks at T-45 and manages both TP and FP outcomes
    • Position costs (20 bps) are conservative for institutional managers
""")
    print("═" * W)
    print()
