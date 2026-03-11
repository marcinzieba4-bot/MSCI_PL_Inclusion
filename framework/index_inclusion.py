"""
Index Inclusion / Exclusion Strategy Module
============================================

Captures the systematic alpha generated when stocks are added to (or deleted
from) major indices (S&P 500, MSCI).  Passive-fund AUM has grown to >$15 trillion,
so forced buying on inclusion and forced selling on exclusion creates predictable
price pressure that active managers can front-run.

Key academic finding: stocks added to S&P 500 gain on average +3.4% on the
announcement day and a further +1.8% into the effective date (Chen, Noronha &
Singal 2004; updated studies through 2023 show similar magnitudes).

MSCI EM additions average +2.9% cumulative abnormal return in the 10 days
surrounding announcement (MSCI semi-annual reviews in May & November).

This module provides:
  1. SP500InclusionScreen   — rules-based eligibility gate for S&P 500
  2. MSCIInclusionScreen    — free-float / liquidity gate for MSCI indices
  3. MomentumProfile        — price momentum as confirmation signal
  4. PreAnnouncementWindow  — optimal entry sizing & timing guide
  5. IndexInclusionCandidate — composite dataclass linking all above
  6. score_inclusion_candidate() — returns InclusionScore (0–10) + conviction tier
  7. print_inclusion_report()    — formatted terminal output

Methodology — Buying Before Publication Date
─────────────────────────────────────────────
Phase 0  T−90 to T−45  │ SCREEN — stock crosses eligibility threshold
Phase 1  T−45 to T−20  │ ACCUMULATE — smart money starts building position
Phase 2  T−20 to T−5   │ SIZE UP — stock clearly near-threshold, momentum positive
Phase 3  T−5  to T+0   │ ANNOUNCEMENT — gap up 3–8%; late entry high-risk
Phase 4  T+0  to T+5   │ EFFECTIVE DATE — passive funds forced to buy
Phase 5  T+5  to T+30  │ FADE — arb unwind, partial reversal (trim position)

Optimal entry: Phase 1–2.  Target exit: Phase 4 (before full reversal).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ──────────────────────────────────────────────
# Enumerations
# ──────────────────────────────────────────────

class IndexFamily(Enum):
    SP500          = "S&P 500"
    SP400          = "S&P 400 MidCap"
    SP600          = "S&P 600 SmallCap"
    MSCI_EM        = "MSCI Emerging Markets"
    MSCI_WORLD     = "MSCI World"
    MSCI_EM_SMALL  = "MSCI EM Small Cap"
    MSCI_POLAND    = "MSCI Poland"
    WIG20          = "WIG20"
    MWIG40         = "mWIG40"
    SWIG80         = "sWIG80"


class InclusionPhase(Enum):
    """Where the stock sits in the pre-announcement lifecycle."""
    SCREEN      = "Phase 0 — Screen (T−90 to T−45)"
    ACCUMULATE  = "Phase 1 — Accumulate (T−45 to T−20)"   # BEST ENTRY
    SIZE_UP     = "Phase 2 — Size Up (T−20 to T−5)"        # GOOD ENTRY
    ANNOUNCEMENT= "Phase 3 — Announcement (T−5 to T+0)"   # HIGH RISK / HOLD
    EFFECTIVE   = "Phase 4 — Effective Date (T+0 to T+5)"  # TRIM
    FADE        = "Phase 5 — Fade / Trim (T+5 to T+30)"    # EXIT


class ReviewCycle(Enum):
    """Index review cadence."""
    CONTINUOUS  = "Continuous (event-driven)"   # S&P 500 — triggered by deletions
    QUARTERLY   = "Quarterly"                   # MSCI — Feb, May, Aug, Nov
    SEMI_ANNUAL = "Semi-Annual"                 # MSCI standard — May, Nov (most impactful)
    ANNUAL      = "Annual"                      # Some regional indices


class MomentumStrength(Enum):
    STRONG_POSITIVE  = "strong_positive"   # RS > 80th pct, trend accelerating
    POSITIVE         = "positive"          # RS 60–80th pct, trending up
    NEUTRAL          = "neutral"           # RS 40–60th pct, sideways
    NEGATIVE         = "negative"          # RS < 40th pct, underperforming
    STRONG_NEGATIVE  = "strong_negative"   # RS < 20th pct, distribution


# ──────────────────────────────────────────────
# S&P 500 Eligibility Screen
# ──────────────────────────────────────────────

@dataclass
class SP500EligibilityScreen:
    """
    Replicates the S&P 500 Index Committee's published eligibility rules.
    All criteria must pass for inclusion consideration.

    Reference: S&P U.S. Indices Methodology (Jan 2025 edition).

    Notes on committee discretion:
    - Even passing all quantitative gates does NOT guarantee inclusion.
    - Committee weighs sector representation, investability, and stability.
    - Stocks are usually added when an existing member is deleted (via M&A,
      bankruptcy, or market-cap drop below floor).  Slots open irregularly.
    """

    # ── Identity ──
    company_name: str
    ticker: str
    exchange: str                             # "NYSE" | "NASDAQ" | "CBOE"
    us_domicile: bool                         # Incorporated in US, HQ in US

    # ── Size ──
    market_cap_usd_bn: float                  # Total market cap in $B (2025 threshold ≈ $18B)
    float_adjusted_market_cap_usd_bn: float   # Free-float-adjusted market cap

    # ── Liquidity ──
    annual_dollar_value_traded_usd_bn: float  # ADVT × trading days
    float_pct: float                          # Free float as % of shares out (must be ≥ 50%)

    # ── Profitability (GAAP) ──
    recent_quarter_earnings_positive: bool    # Most recent quarter net income > 0
    trailing_4q_earnings_positive: bool       # Sum of 4 trailing quarters net income > 0

    # ── Seasoning ──
    months_listed: float                      # Must be ≥ 12 months since IPO/listing

    # ── Optional context ──
    ipoq_date: Optional[str] = None
    sector_gics: Optional[str] = None        # GICS sector classification
    current_index_membership: Optional[str] = None  # e.g. "S&P 400" (promotes naturally)
    analyst_coverage_count: int = 0

    def passes_all_gates(self) -> tuple[bool, list[str]]:
        """
        Returns (True, []) if all hard gates pass.
        Returns (False, [reasons]) if any gate fails.
        """
        fails = []

        if not self.us_domicile:
            fails.append("Not US-domiciled (foreign private issuer not eligible)")
        if self.exchange not in ("NYSE", "NASDAQ", "CBOE", "NYSE ARCA", "NYSE MKT"):
            fails.append(f"Exchange '{self.exchange}' not eligible (OTC/pink-sheet excluded)")
        if self.market_cap_usd_bn < 18.0:
            fails.append(f"Market cap ${self.market_cap_usd_bn:.1f}B < $18B threshold")
        if self.float_pct < 50.0:
            fails.append(f"Float {self.float_pct:.0f}% < 50% minimum")
        if self.annual_dollar_value_traded_usd_bn < self.float_adjusted_market_cap_usd_bn:
            ratio = self.annual_dollar_value_traded_usd_bn / self.float_adjusted_market_cap_usd_bn
            fails.append(f"Liquidity ratio {ratio:.2f}x < 1.0x required (ADVT / float-adj mktcap)")
        if not self.recent_quarter_earnings_positive:
            fails.append("Most recent quarter GAAP earnings negative")
        if not self.trailing_4q_earnings_positive:
            fails.append("Trailing 4-quarter sum of GAAP earnings negative")
        if self.months_listed < 12:
            fails.append(f"Only {self.months_listed:.0f} months listed — needs ≥ 12 months")

        return (len(fails) == 0), fails

    def eligibility_score(self) -> float:
        """
        Partial score 0–10 even when some gates fail.
        Useful for 'how close is this stock?' ranking.
        """
        score = 0.0

        # Market cap (0–3 pts)
        if self.market_cap_usd_bn >= 50:
            score += 3.0
        elif self.market_cap_usd_bn >= 25:
            score += 2.0
        elif self.market_cap_usd_bn >= 18:
            score += 1.5
        elif self.market_cap_usd_bn >= 12:
            score += 0.5   # Close

        # Float (0–2 pts)
        if self.float_pct >= 80:
            score += 2.0
        elif self.float_pct >= 60:
            score += 1.5
        elif self.float_pct >= 50:
            score += 1.0
        elif self.float_pct >= 40:
            score += 0.3

        # Liquidity ratio (0–2 pts)
        ratio = (self.annual_dollar_value_traded_usd_bn /
                 max(self.float_adjusted_market_cap_usd_bn, 0.001))
        if ratio >= 3.0:
            score += 2.0
        elif ratio >= 1.5:
            score += 1.5
        elif ratio >= 1.0:
            score += 1.0
        elif ratio >= 0.7:
            score += 0.3

        # Profitability (0–2 pts)
        if self.recent_quarter_earnings_positive:
            score += 1.0
        if self.trailing_4q_earnings_positive:
            score += 1.0

        # Seasoning (0–1 pt)
        if self.months_listed >= 24:
            score += 1.0
        elif self.months_listed >= 12:
            score += 0.7

        # Bonus: already in S&P family (S&P 400 → S&P 500 is most common promotion path)
        if self.current_index_membership and "S&P 400" in self.current_index_membership:
            score += 1.0

        return min(score, 10.0)


# ──────────────────────────────────────────────
# MSCI Eligibility Screen
# ──────────────────────────────────────────────

@dataclass
class MSCIEligibilityScreen:
    """
    MSCI Global Investable Market Indices (GIMI) Methodology eligibility screen.

    Key thresholds for MSCI Emerging Markets (Standard Index):
      Full Market Cap        ≥ $2,500M  (reviewed semi-annually, May & Nov)
      Float-Adj Market Cap   ≥ $1,300M
      Foreign Inclusion Factor (FIF) ≥ 0.15
      3-Month ATVR           ≥ 20%      (Annualised Traded Value Ratio)

    For MSCI EM Small Cap:
      Full Market Cap        ≥ $127M
      Float-Adj Market Cap   ≥ $95M
      3-Month ATVR           ≥ 15%

    For MSCI Poland (already subset of MSCI EM):
      Same thresholds as MSCI EM Standard.
      Polish stocks are evaluated relative to the Poland country universe.
      Key dynamic: stocks crossing the Standard threshold get added to MSCI Poland
      AND MSCI EM simultaneously — double passive-fund demand.

    MSCI Semi-Annual Reviews (SAR) — May & November:
      - Announcement:  ~4 weeks before effective date
      - Effective date: last business day of May / November
      - Quarterly reviews (Feb & Aug) handle only deletions and cap changes.
    """

    # ── Identity ──
    company_name: str
    ticker: str
    exchange: str                          # "WSE" | "NYSE" | "LSE" etc.
    country: str                           # Market classification (e.g. "Poland")
    msci_market_classification: str        # "Frontier" | "Emerging" | "Developed"
    target_index: IndexFamily

    # ── Size (in USD) ──
    full_market_cap_usd_m: float           # Total market cap (USD millions)
    float_adj_market_cap_usd_m: float      # Free-float-adjusted market cap (USD millions)

    # ── Foreign accessibility ──
    foreign_inclusion_factor: float        # FIF — 0.0 to 1.0 (proportion accessible to foreigners)
    foreign_room_pct: float                # Headroom before foreign ownership limit (%)

    # ── Liquidity ──
    atvr_3m_pct: float                    # 3-month annualised traded value ratio (%)
    avg_daily_volume_usd_m: float         # USD millions per day

    # ── Review context ──
    next_review_cycle: ReviewCycle = ReviewCycle.SEMI_ANNUAL
    next_review_month: Optional[str] = None   # e.g. "May 2025"
    months_to_next_review: Optional[float] = None

    # ── Optional ──
    sector_gics: Optional[str] = None
    current_msci_membership: Optional[str] = None  # e.g. "MSCI EM Small Cap"
    analyst_coverage_count: int = 0

    def _thresholds(self) -> dict:
        """Return relevant thresholds for the target index."""
        if self.target_index in (IndexFamily.MSCI_EM, IndexFamily.MSCI_POLAND,
                                  IndexFamily.MSCI_WORLD):
            return {
                "full_cap_m": 2500,
                "float_cap_m": 1300,
                "atvr_pct": 20,
                "fif": 0.15,
                "label": "Standard",
            }
        elif self.target_index == IndexFamily.MSCI_EM_SMALL:
            return {
                "full_cap_m": 127,
                "float_cap_m": 95,
                "atvr_pct": 15,
                "fif": 0.15,
                "label": "Small Cap",
            }
        else:
            return {
                "full_cap_m": 2500,
                "float_cap_m": 1300,
                "atvr_pct": 20,
                "fif": 0.15,
                "label": "Standard",
            }

    def passes_all_gates(self) -> tuple[bool, list[str]]:
        """Returns (True, []) if all quantitative gates pass."""
        t = self._thresholds()
        fails = []

        if self.full_market_cap_usd_m < t["full_cap_m"]:
            fails.append(
                f"Full mktcap ${self.full_market_cap_usd_m:.0f}M < ${t['full_cap_m']}M threshold"
            )
        if self.float_adj_market_cap_usd_m < t["float_cap_m"]:
            fails.append(
                f"Float-adj mktcap ${self.float_adj_market_cap_usd_m:.0f}M < ${t['float_cap_m']}M"
            )
        if self.foreign_inclusion_factor < t["fif"]:
            fails.append(
                f"FIF {self.foreign_inclusion_factor:.2f} < {t['fif']} minimum"
            )
        if self.atvr_3m_pct < t["atvr_pct"]:
            fails.append(
                f"3-month ATVR {self.atvr_3m_pct:.1f}% < {t['atvr_pct']}% required"
            )

        return (len(fails) == 0), fails

    def eligibility_score(self) -> float:
        """Partial score 0–10 showing how close the stock is to inclusion."""
        t = self._thresholds()
        score = 0.0

        # Full market cap (0–3 pts)
        ratio = self.full_market_cap_usd_m / t["full_cap_m"]
        if ratio >= 2.0:
            score += 3.0
        elif ratio >= 1.5:
            score += 2.5
        elif ratio >= 1.0:
            score += 2.0
        elif ratio >= 0.85:
            score += 1.0   # Close — could qualify with currency/price move
        elif ratio >= 0.70:
            score += 0.5

        # Float-adj cap (0–2 pts)
        fratio = self.float_adj_market_cap_usd_m / t["float_cap_m"]
        if fratio >= 1.5:
            score += 2.0
        elif fratio >= 1.0:
            score += 1.5
        elif fratio >= 0.85:
            score += 0.7

        # ATVR liquidity (0–2 pts)
        lratio = self.atvr_3m_pct / t["atvr_pct"]
        if lratio >= 2.0:
            score += 2.0
        elif lratio >= 1.0:
            score += 1.5
        elif lratio >= 0.8:
            score += 0.5

        # FIF accessibility (0–2 pts)
        if self.foreign_inclusion_factor >= 0.5:
            score += 2.0
        elif self.foreign_inclusion_factor >= 0.25:
            score += 1.5
        elif self.foreign_inclusion_factor >= 0.15:
            score += 1.0

        # Bonus: already in a smaller MSCI index (upgrade path)
        if self.current_msci_membership and "Small Cap" in self.current_msci_membership:
            score += 1.0   # Upgrade from small cap to standard is very impactful

        return min(score, 10.0)

    def headline_gap_summary(self) -> str:
        """One-line summary of largest gap to threshold."""
        t = self._thresholds()
        cap_gap = self.full_market_cap_usd_m / t["full_cap_m"]
        liq_gap = self.atvr_3m_pct / t["atvr_pct"]
        fif_ok  = self.foreign_inclusion_factor >= t["fif"]

        if cap_gap < 1.0:
            gap_pct = (1 - cap_gap) * 100
            return f"Cap gap: need +{gap_pct:.0f}% in market cap (${t['full_cap_m']}M threshold)"
        if liq_gap < 1.0:
            return f"Liquidity gap: ATVR {self.atvr_3m_pct:.1f}% vs {t['atvr_pct']}% required"
        if not fif_ok:
            return f"FIF too low: {self.foreign_inclusion_factor:.2f} vs {t['fif']} minimum"
        return "All gates cleared — eligible for next review"


# ──────────────────────────────────────────────
# Momentum Profile
# ──────────────────────────────────────────────

@dataclass
class MomentumProfile:
    """
    Price momentum analysis.  Used as a confirmation signal — we want stocks
    that are approaching index inclusion thresholds AND have positive momentum
    (price trend supporting further appreciation into announcement).

    Classic momentum factor = 12-1 momentum:
      Return from T−12 months to T−1 month (excluding most recent month
      to avoid short-term reversal contamination).

    Relative Strength = stock's 12-1 momentum vs. benchmark universe.
    """

    # ── Raw returns ──
    return_1m_pct: float        # 1-month total return
    return_3m_pct: float        # 3-month total return
    return_6m_pct: float        # 6-month total return
    return_12m_pct: float       # 12-month total return

    # ── Relative strength ──
    rs_percentile: float        # Percentile rank vs universe (0–100); >70 = attractive
    benchmark_return_12m_pct: float  # Index return for comparison (e.g. WIG, S&P 500)

    # ── Trend quality ──
    above_50d_ma: bool          # Price > 50-day moving average
    above_200d_ma: bool         # Price > 200-day moving average (long-term uptrend)
    volume_trend: str           # "expanding" | "contracting" | "neutral"
    # Expanding volume on up-days signals institutional accumulation

    # ── Short-term entry timing ──
    distance_from_52w_high_pct: float   # How far from 52-week high (negative = below high)
    distance_from_52w_low_pct: float    # How far from 52-week low (positive = above low)

    @property
    def momentum_12_1(self) -> float:
        """Classic 12-1 momentum: 12-month minus 1-month (reversal-adjusted)."""
        return self.return_12m_pct - self.return_1m_pct

    @property
    def strength(self) -> MomentumStrength:
        rs = self.rs_percentile
        mom = self.momentum_12_1
        if rs >= 80 and mom > 20 and self.above_200d_ma:
            return MomentumStrength.STRONG_POSITIVE
        elif rs >= 60 and mom > 5 and self.above_50d_ma:
            return MomentumStrength.POSITIVE
        elif rs >= 40 or (mom > -5 and rs >= 30):
            return MomentumStrength.NEUTRAL
        elif rs >= 20:
            return MomentumStrength.NEGATIVE
        else:
            return MomentumStrength.STRONG_NEGATIVE

    def momentum_score(self) -> tuple[float, list[str]]:
        """
        Returns (score 0–10, explanatory notes).
        For index inclusion plays, we use momentum as a FILTER not a primary driver.
        Minimum acceptable: MomentumStrength.NEUTRAL (RS ≥ 40th percentile).
        """
        score = 0.0
        notes = []

        # Relative strength (0–4 pts)
        if self.rs_percentile >= 90:
            score += 4.0
            notes.append(f"RS {self.rs_percentile:.0f}th pct — top decile momentum")
        elif self.rs_percentile >= 80:
            score += 3.5
            notes.append(f"RS {self.rs_percentile:.0f}th pct — strong outperformer")
        elif self.rs_percentile >= 70:
            score += 2.5
            notes.append(f"RS {self.rs_percentile:.0f}th pct — above-average")
        elif self.rs_percentile >= 60:
            score += 1.5
            notes.append(f"RS {self.rs_percentile:.0f}th pct — mild outperformance")
        elif self.rs_percentile >= 40:
            score += 0.5
            notes.append(f"RS {self.rs_percentile:.0f}th pct — neutral momentum")
        else:
            score -= 1.0
            notes.append(f"RS {self.rs_percentile:.0f}th pct — underperforming (caution)")

        # 12-month return vs benchmark (0–3 pts)
        excess = self.return_12m_pct - self.benchmark_return_12m_pct
        if excess > 30:
            score += 3.0
            notes.append(f"+{excess:.0f}% excess return vs benchmark — major outperformance")
        elif excess > 15:
            score += 2.0
            notes.append(f"+{excess:.0f}% excess return — solid outperformance")
        elif excess > 5:
            score += 1.0
            notes.append(f"+{excess:.0f}% excess return — modest outperformance")
        elif excess < -10:
            score -= 1.5
            notes.append(f"{excess:.0f}% excess — lagging benchmark, momentum risk")

        # Trend structure (0–2 pts)
        if self.above_200d_ma:
            score += 1.0
            notes.append("Above 200d MA — long-term uptrend intact")
        if self.above_50d_ma:
            score += 0.5
            notes.append("Above 50d MA — short-term trend positive")

        # Volume confirmation (0–1 pt)
        if self.volume_trend == "expanding":
            score += 1.0
            notes.append("Volume expanding — institutional accumulation likely")
        elif self.volume_trend == "contracting":
            score -= 0.5
            notes.append("Volume contracting — weak conviction in move")

        # Distance from highs (0–1 pt bonus for breakout proximity)
        if -5 <= self.distance_from_52w_high_pct <= 0:
            score += 0.5
            notes.append(f"Near 52-week high ({self.distance_from_52w_high_pct:.1f}%) — potential breakout")

        return round(min(max(score, 0), 10), 2), notes


# ──────────────────────────────────────────────
# Pre-announcement Window Analysis
# ──────────────────────────────────────────────

@dataclass
class PreAnnouncementWindow:
    """
    Characterises where a candidate sits in the pre-announcement timeline
    and derives entry/exit guidance.

    The key insight: passive funds track indices mechanically. They MUST buy
    when a stock is added. Active managers can anticipate this forced demand.

    Timeline for S&P 500 (event-driven):
      - No fixed schedule: replacement announced same day as deletion
      - Announcement → Effective Date: typically 5–10 business days
      - Optimal entry: 30–90 days BEFORE announcement when stock is
        clearly approaching eligibility

    Timeline for MSCI (scheduled):
      - Semi-annual reviews: announcement ~4 weeks before effective date
      - May effective date: announcement in late April
      - November effective date: announcement in late October
      - Quarterly reviews: announcement ~2 weeks before effective date

    Passive AUM impact:
      S&P 500 addition: ~$14B average forced buying (full index weight × tracked AUM)
      MSCI EM Standard addition: ~$800M–$3B depending on country and stock weight
      MSCI Poland (upgrade to Standard): typically $200M–$500M forced buying
    """

    # ── Current position in timeline ──
    current_phase: InclusionPhase
    estimated_days_to_announcement: Optional[int] = None  # None if already announced
    estimated_days_to_effective_date: Optional[int] = None

    # ── Passive AUM impact estimate ──
    estimated_forced_buying_usd_m: float = 0.0   # How much passive $ must buy
    estimated_index_weight_pct: float = 0.0       # Projected weight in target index
    adv_days_to_absorb: float = 0.0              # Days of ADV needed to fill passive demand

    # ── Historical analogue return ──
    avg_announcement_day_return_pct: float = 3.4   # Historical average
    avg_pre_announcement_drift_pct: float = 2.5    # Drift in 30 days before announcement
    avg_effective_date_bump_pct: float = 1.5       # Final squeeze on effective date
    avg_30d_post_reversal_pct: float = -1.8        # Typical reversal after effective date

    @property
    def total_expected_alpha_pct(self) -> float:
        """
        Total expected alpha from Phase 1 entry through Phase 4 exit.
        = pre-announcement drift + announcement gap + effective date bump.
        Excludes post-reversal (which you capture by selling at effective date).
        """
        return (self.avg_pre_announcement_drift_pct +
                self.avg_announcement_day_return_pct +
                self.avg_effective_date_bump_pct)

    def entry_guidance(self) -> dict:
        """Returns structured entry/exit/sizing guidance for the current phase."""
        guidance = {
            InclusionPhase.SCREEN: {
                "action": "WATCH — Begin researching; do not build position yet",
                "sizing": "0% — no position",
                "rationale": "Stock just crossed screening threshold. 90-45 days to likely announcement. "
                             "Probability of inclusion still uncertain. Monitor criteria convergence.",
                "risk": "Criteria may not be met by review date; price may not move without catalyst",
            },
            InclusionPhase.ACCUMULATE: {
                "action": "BUY — Best risk/reward entry window",
                "sizing": "25–50% of target position",
                "rationale": "Stock clearly approaching eligibility. Smart money beginning to accumulate. "
                             "Pre-announcement drift averages +2.5% over this period. "
                             "Entry here captures full alpha window at lowest crowding risk.",
                "risk": "Index may include a different stock; eligibility criteria may not be met",
            },
            InclusionPhase.SIZE_UP: {
                "action": "ADD — Size up if momentum confirms",
                "sizing": "50–100% of target position",
                "rationale": "Stock clearly on inclusion radar. Momentum should be positive by now. "
                             "20-5 days before announcement: higher probability, but also higher crowding. "
                             "Enter remaining position if momentum signal is POSITIVE or STRONG_POSITIVE.",
                "risk": "Some pre-announcement drift already realised; late entry compresses risk/reward",
            },
            InclusionPhase.ANNOUNCEMENT: {
                "action": "HOLD — Do not chase; trim if >8% gap on announcement day",
                "sizing": "Hold existing; no new money",
                "rationale": "Gap-up on announcement averages +3.4%. Buying into the gap is poor R/R. "
                             "If you already own: hold through effective date for the final +1.5%.",
                "risk": "Gap reversals can occur if market expects a different stock; do not chase",
            },
            InclusionPhase.EFFECTIVE: {
                "action": "TRIM — Begin reducing position",
                "sizing": "Sell 50–75% of position at/around effective date",
                "rationale": "Passive funds complete buying on effective date. Post-addition reversal "
                             "averages −1.8% over next 30 days as arb books unwind. "
                             "Secure the pre-announcement + announcement gains.",
                "risk": "If stock is added to additional indices later, hold-through may be better",
            },
            InclusionPhase.FADE: {
                "action": "EXIT — Close remaining position",
                "sizing": "Sell remaining 25–50% over 5–10 days post-effective",
                "rationale": "Reversal phase. Post-inclusion alpha exhausted. "
                             "Rotate capital to next pre-announcement opportunity.",
                "risk": "Some stocks sustain post-inclusion re-rating if fundamentals improve — "
                        "reassess whether a separate fundamental thesis justifies holding",
            },
        }
        return guidance.get(self.current_phase, {})


# ──────────────────────────────────────────────
# Composite Candidate Profile
# ──────────────────────────────────────────────

@dataclass
class IndexInclusionCandidate:
    """
    Master profile for an index inclusion/exclusion candidate.
    Aggregates eligibility, momentum, and pre-announcement analysis.
    """

    # ── Identity ──
    company_name: str
    ticker: str
    exchange: str
    sector: str
    country: str
    target_index: IndexFamily

    # ── Market data ──
    current_price: float
    currency: str
    market_cap_local_m: float       # Local currency millions
    market_cap_usd_m: float         # USD millions (for cross-index comparison)

    # ── Eligibility screens ──
    sp500_screen: Optional[SP500EligibilityScreen] = None
    msci_screen: Optional[MSCIEligibilityScreen] = None

    # ── Momentum ──
    momentum: Optional[MomentumProfile] = None

    # ── Pre-announcement ──
    pre_announcement: Optional[PreAnnouncementWindow] = None

    # ── Thesis ──
    thesis_summary: str = ""
    key_risks: list[str] = field(default_factory=list)
    catalyst_date: Optional[str] = None      # e.g. "May 2025 MSCI SAR" or "Q3 2025"

    # ── Additional fundamental quality ──
    revenue_growth_yoy_pct: Optional[float] = None
    ebitda_margin_pct: Optional[float] = None
    net_debt_to_ebitda: Optional[float] = None
    roe_pct: Optional[float] = None

    # ── Computed (filled by score_inclusion_candidate) ──
    inclusion_score: Optional[float] = None
    conviction_tier: Optional[str] = None


# ──────────────────────────────────────────────
# Scoring Engine
# ──────────────────────────────────────────────

@dataclass
class InclusionScore:
    """Full scoring output for an index inclusion candidate."""
    company_name: str
    target_index: str
    inclusion_score: float              # 0–10
    conviction_tier: str                # HIGH / MEDIUM / WATCH / PASS
    eligibility_score: float            # 0–10
    momentum_score: float               # 0–10
    timing_score: float                 # 0–10 (phase quality)
    passive_impact_score: float         # 0–10 (AUM forced buying magnitude)
    phase: str
    entry_action: str
    estimated_alpha_pct: float
    eligibility_notes: list[str]
    momentum_notes: list[str]
    key_risks: list[str]


def score_inclusion_candidate(candidate: IndexInclusionCandidate) -> InclusionScore:
    """
    Score an index inclusion candidate across four dimensions:
      1. Eligibility score     (40% weight) — how clearly does it meet index criteria?
      2. Momentum score        (30% weight) — is price trending right direction?
      3. Timing score          (20% weight) — are we in the optimal entry phase?
      4. Passive impact score  (10% weight) — how much forced buying will occur?

    Returns InclusionScore with conviction tier and entry action.
    """

    # ── 1. Eligibility ──
    elig_score = 0.0
    elig_notes: list[str] = []

    if candidate.sp500_screen is not None:
        elig_score = candidate.sp500_screen.eligibility_score()
        passes, fails = candidate.sp500_screen.passes_all_gates()
        if passes:
            elig_notes.append("All S&P 500 gates cleared")
        else:
            elig_notes.extend(fails)
        if candidate.sp500_screen.current_index_membership:
            elig_notes.append(f"Current index: {candidate.sp500_screen.current_index_membership}")

    elif candidate.msci_screen is not None:
        elig_score = candidate.msci_screen.eligibility_score()
        passes, fails = candidate.msci_screen.passes_all_gates()
        if passes:
            elig_notes.append(f"All {candidate.msci_screen.target_index.value} gates cleared")
            if candidate.msci_screen.next_review_month:
                elig_notes.append(f"Next review: {candidate.msci_screen.next_review_month}")
        else:
            elig_notes.extend(fails)
        elig_notes.append(candidate.msci_screen.headline_gap_summary())

    # ── 2. Momentum ──
    mom_score = 5.0   # Default neutral if no momentum data
    mom_notes: list[str] = []

    if candidate.momentum is not None:
        mom_score, mom_notes = candidate.momentum.momentum_score()
        mom_notes.insert(0, f"Strength: {candidate.momentum.strength.value}")
        # Disqualify if momentum is strongly negative — index inclusion alpha
        # often requires price to be rising (passive funds buy at market, not limit)
        if candidate.momentum.strength == MomentumStrength.STRONG_NEGATIVE:
            mom_score = min(mom_score, 2.0)
            mom_notes.insert(0, "WARNING: Strong negative momentum — inclusion alpha at risk")

    # ── 3. Timing ──
    timing_map = {
        InclusionPhase.SCREEN:       3.0,   # Too early, uncertain
        InclusionPhase.ACCUMULATE:   9.0,   # OPTIMAL entry
        InclusionPhase.SIZE_UP:      7.5,   # Good entry
        InclusionPhase.ANNOUNCEMENT: 4.0,   # Hold only, no new entry
        InclusionPhase.EFFECTIVE:    2.5,   # Trim
        InclusionPhase.FADE:         1.0,   # Exit
    }
    timing_score = 5.0   # Default if no pre-announcement data
    phase_name = "Unknown"
    entry_action = "Analyse further"

    if candidate.pre_announcement is not None:
        timing_score = timing_map.get(candidate.pre_announcement.current_phase, 5.0)
        phase_name = candidate.pre_announcement.current_phase.value
        guidance = candidate.pre_announcement.entry_guidance()
        entry_action = guidance.get("action", "Analyse further")

    # ── 4. Passive impact ──
    passive_score = 5.0
    if candidate.pre_announcement is not None:
        forced = candidate.pre_announcement.estimated_forced_buying_usd_m
        adv_days = candidate.pre_announcement.adv_days_to_absorb

        if forced >= 5000:
            passive_score = 10.0      # $5B+ forced buying — massive impact
        elif forced >= 2000:
            passive_score = 8.5
        elif forced >= 500:
            passive_score = 7.0
        elif forced >= 100:
            passive_score = 5.5
        elif forced >= 20:
            passive_score = 4.0
        else:
            passive_score = 2.5

        # ADV absorption: if passive demand = many days of ADV, price impact is larger
        if adv_days >= 20:
            passive_score = min(passive_score + 1.5, 10)
        elif adv_days >= 10:
            passive_score = min(passive_score + 0.75, 10)

    # ── Weighted composite ──
    inclusion_score = (
        elig_score   * 0.40 +
        mom_score    * 0.30 +
        timing_score * 0.20 +
        passive_score * 0.10
    )
    inclusion_score = round(inclusion_score, 2)

    # Conviction tier
    if inclusion_score >= 7.5:
        tier = "HIGH"
    elif inclusion_score >= 5.5:
        tier = "MEDIUM"
    elif inclusion_score >= 3.5:
        tier = "WATCH"
    else:
        tier = "PASS"

    # Write back to candidate
    candidate.inclusion_score = inclusion_score
    candidate.conviction_tier = tier

    # Estimated alpha
    alpha = 0.0
    if candidate.pre_announcement is not None:
        alpha = candidate.pre_announcement.total_expected_alpha_pct

    return InclusionScore(
        company_name=candidate.company_name,
        target_index=candidate.target_index.value,
        inclusion_score=inclusion_score,
        conviction_tier=tier,
        eligibility_score=round(elig_score, 2),
        momentum_score=round(mom_score, 2),
        timing_score=round(timing_score, 2),
        passive_impact_score=round(passive_score, 2),
        phase=phase_name,
        entry_action=entry_action,
        estimated_alpha_pct=round(alpha, 1),
        eligibility_notes=elig_notes,
        momentum_notes=mom_notes,
        key_risks=candidate.key_risks,
    )


# ──────────────────────────────────────────────
# Report Formatter
# ──────────────────────────────────────────────

def _bar(score: float, width: int = 20) -> str:
    """ASCII progress bar for a 0–10 score."""
    filled = int(round((score / 10.0) * width))
    return "█" * filled + "░" * (width - filled)


TIER_STYLES = {
    "HIGH":   ("▲ HIGH CONVICTION", "═"),
    "MEDIUM": ("◆ MEDIUM",          "─"),
    "WATCH":  ("◇ WATCH",           "─"),
    "PASS":   ("✕ PASS",            "─"),
}


def print_inclusion_report(result: InclusionScore, candidate: IndexInclusionCandidate) -> None:
    """Print a formatted terminal report for an index inclusion candidate."""
    label, sep_char = TIER_STYLES.get(result.conviction_tier, ("? UNKNOWN", "─"))
    width = 72

    print()
    print(sep_char * width)
    print(f" INDEX INCLUSION ANALYSIS — {candidate.company_name} ({candidate.ticker})")
    print(f" Target: {result.target_index}  |  Exchange: {candidate.exchange}")
    print(sep_char * width)

    # Scores
    print(f"\n  Inclusion Score    {result.inclusion_score:5.2f}/10  {_bar(result.inclusion_score)}")
    print(f"  ├─ Eligibility     {result.eligibility_score:5.2f}/10  {_bar(result.eligibility_score)}")
    print(f"  ├─ Momentum        {result.momentum_score:5.2f}/10  {_bar(result.momentum_score)}")
    print(f"  ├─ Timing          {result.timing_score:5.2f}/10  {_bar(result.timing_score)}")
    print(f"  └─ Passive Impact  {result.passive_impact_score:5.2f}/10  {_bar(result.passive_impact_score)}")

    print(f"\n  Conviction:  {label}")
    print(f"  Phase:       {result.phase}")
    print(f"  Entry:       {result.entry_action}")
    print(f"  Exp. Alpha:  +{result.estimated_alpha_pct:.1f}% (pre-announcement → effective date)")

    if candidate.thesis_summary:
        print(f"\n  Thesis:")
        for line in candidate.thesis_summary.split("\n"):
            if line.strip():
                print(f"    {line.strip()}")

    if result.eligibility_notes:
        print("\n  Eligibility Notes:")
        for note in result.eligibility_notes:
            print(f"    • {note}")

    if result.momentum_notes:
        print("\n  Momentum:")
        for note in result.momentum_notes:
            print(f"    • {note}")

    if candidate.momentum:
        m = candidate.momentum
        print(f"\n  Price Performance:")
        print(f"    1M: {m.return_1m_pct:+.1f}%   "
              f"3M: {m.return_3m_pct:+.1f}%   "
              f"6M: {m.return_6m_pct:+.1f}%   "
              f"12M: {m.return_12m_pct:+.1f}%")
        print(f"    RS percentile vs universe: {m.rs_percentile:.0f}th")
        print(f"    52w range: {m.distance_from_52w_low_pct:+.1f}% from low  |  "
              f"{m.distance_from_52w_high_pct:+.1f}% from high")

    if candidate.pre_announcement:
        pa = candidate.pre_announcement
        print(f"\n  Passive Demand Estimate:")
        print(f"    Forced buying:  ~${pa.estimated_forced_buying_usd_m:,.0f}M")
        print(f"    Index weight:   ~{pa.estimated_index_weight_pct:.2f}%")
        print(f"    ADV days:       ~{pa.adv_days_to_absorb:.1f} days to absorb demand")
        if pa.estimated_days_to_announcement:
            print(f"    Est. announcement: ~{pa.estimated_days_to_announcement} business days")

    if candidate.catalyst_date:
        print(f"\n  Catalyst Date:  {candidate.catalyst_date}")

    if result.key_risks:
        print("\n  Key Risks:")
        for risk in result.key_risks:
            print(f"    ⚠  {risk}")

    print()
    print(sep_char * width)
    print()
