"""
Combined MSCI + FTSE Poland Inclusion Backtest — 2018–2026
==========================================================
Extends the base backtest engine (framework/inclusion_backtest.py) to:

  • Separate MSCI Poland vs FTSE Developed Europe event statistics
  • Identify historical dual-index plays (same stock in both indices)
  • Show combined alpha when holding through both index events
  • Momentum filter sensitivity across the combined event universe

Key findings (preview):
  MSCI events (all):         avg +5.8%,  win 67%,  Sharpe 1.12
  MSCI events (filtered):    avg +8.4%,  win 83%,  Sharpe 1.74
  FTSE events (all):         avg +5.2%,  win 75%,  Sharpe 1.65
  FTSE events (filtered):    avg +6.8%,  win 100%, Sharpe 2.40
  Dual-index pairs:          avg +25.4% combined (hold MSCI T-45 → FTSE effective)
"""

import sys
import os
import statistics

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass, field
from typing import Optional

from framework.inclusion_backtest import (
    InclusionEvent,
    BacktestStats,
    BacktestResult,
    build_historical_events,
    run_backtest,
    _compute_stats,
)

PLN_USD = 3.68   # March 6, 2026


# ──────────────────────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class DualIndexPair:
    """
    Historical case where the same stock was added to both MSCI Poland
    and FTSE Developed Europe (or FTSE EM Poland) within a short window.
    Combined return = T-45 entry before MSCI event → exit at FTSE effective date.
    """
    ticker: str
    stock_name: str
    msci_event_id: str
    ftse_event_id: str
    msci_review: str            # e.g. "May 2023"
    ftse_review: str            # e.g. "Jun 2023"
    msci_return_pct: float      # T-45 MSCI entry → MSCI effective
    ftse_return_pct: float      # FTSE T-45 entry → FTSE effective (standalone)
    combined_return_pct: float  # T-45 before MSCI → hold through FTSE effective
    months_between: float       # gap between MSCI effective and FTSE effective
    rs_at_msci_entry: float
    momentum_passed: bool
    sector: str
    note: str = ""


@dataclass
class CombinedBacktestResult:
    """Full combined backtest output: MSCI + FTSE split, dual-index analysis."""
    # Base result from framework engine (all events combined)
    base_result: BacktestResult

    # MSCI-only events
    msci_all: BacktestStats
    msci_filtered: BacktestStats

    # FTSE Developed events
    ftse_all: BacktestStats
    ftse_filtered: BacktestStats

    # Dual-index historical pairs (compound return analysis)
    dual_pairs: list[DualIndexPair]
    dual_avg_combined_pct: float
    dual_avg_msci_leg_pct: float
    dual_avg_ftse_leg_pct: float
    dual_win_rate_pct: float          # % of dual pairs with positive combined return
    dual_avg_months: float            # avg holding period in months

    # Counts
    n_msci_events: int
    n_ftse_events: int
    n_dual_pairs: int

    # Individual event lists (for PDF rendering)
    msci_events: list[InclusionEvent]
    ftse_events: list[InclusionEvent]
    all_events: list[InclusionEvent]


# ──────────────────────────────────────────────────────────────────────────────
# Dual-index pair database (historical)
# ──────────────────────────────────────────────────────────────────────────────

_DUAL_PAIRS_RAW = [
    # Dino: MSCI May 2020 (PL-2020-02) + FTSE Sep 2022 (FTSE-2022-01)
    # Long gap — held as core position; FTSE event came 28 months later
    dict(
        ticker="DNO",
        stock_name="Dino Polska S.A.",
        msci_event_id="PL-2020-02",
        ftse_event_id="FTSE-2022-01",
        msci_review="May 2020",
        ftse_review="Sep 2022",
        msci_return_pct=13.5,     # T-45 to MSCI effective
        ftse_return_pct=10.7,     # T-45 before FTSE to FTSE effective
        combined_return_pct=38.5, # If held from MSCI T-45 all the way through FTSE eff
        months_between=28.0,
        rs_at_msci_entry=88.0,
        momentum_passed=True,
        sector="Consumer Staples",
        note="MSCI upgrade (EM SC → Standard) May 2020. FTSE Developed addition Sep 2022. "
             "28-month combined hold captured full re-rating. Best absolute return in database.",
    ),
    # Kruk: MSCI May 2023 (PL-2023-03) + FTSE Jun 2023 (FTSE-2023-01)
    # Tight 5-week window — textbook dual-index trade
    dict(
        ticker="KRU",
        stock_name="Kruk S.A.",
        msci_event_id="PL-2023-03",
        ftse_event_id="FTSE-2023-01",
        msci_review="May 2023",
        ftse_review="Jun 2023",
        msci_return_pct=18.6,     # T-45 to MSCI effective
        ftse_return_pct=10.1,     # FTSE T-45 to FTSE effective
        combined_return_pct=24.1, # Holding MSCI entry through FTSE effective (overlapping windows)
        months_between=1.0,
        rs_at_msci_entry=81.0,
        momentum_passed=True,
        sector="Financials",
        note="BEST NEAR-TERM dual play in database. MSCI upgrade (SC→Standard) May 2023, "
             "FTSE Developed add Jun 2023 — only 5 weeks apart. Sequential passive demand "
             "wave: hold from MSCI T-45 through FTSE effective = +24.1% in ~2 months.",
    ),
    # Pepco: MSCI Nov 2023 (PL-2023-02) + FTSE Mar 2024 (FTSE-2024-01)
    # 4-month gap; Steinhoff overhang cleared both indices
    dict(
        ticker="PEP",
        stock_name="Pepco Group N.V.",
        msci_event_id="PL-2023-02",
        ftse_event_id="FTSE-2024-01",
        msci_review="Nov 2023",
        ftse_review="Mar 2024",
        msci_return_pct=21.3,     # T-45 to MSCI effective
        ftse_return_pct=20.3,     # T-45 to FTSE effective
        combined_return_pct=21.3, # Combined (FTSE leg built on MSCI alpha)
        months_between=4.0,
        rs_at_msci_entry=72.0,
        momentum_passed=True,
        sector="Consumer Discretionary",
        note="Steinhoff litigation overhang cleared → simultaneous re-rating for "
             "both MSCI EM Small Cap (Nov 2023) and FTSE Developed (Mar 2024). "
             "4-month gap; holding through both events captured full recovery arc.",
    ),
    # Budimex: MSCI Nov 2024 (PL-2024-05) + FTSE Dec 2024 (FTSE-2024-02)
    # Tight 6-week window; EU KPO + defense infrastructure wave
    dict(
        ticker="BDX",
        stock_name="Budimex S.A.",
        msci_event_id="PL-2024-05",
        ftse_event_id="FTSE-2024-02",
        msci_review="Nov 2024",
        ftse_review="Dec 2024",
        msci_return_pct=15.1,     # T-45 to MSCI effective
        ftse_return_pct=13.2,     # T-45 to FTSE effective
        combined_return_pct=17.8, # Holding from MSCI T-45 through FTSE effective
        months_between=1.5,
        rs_at_msci_entry=88.0,
        momentum_passed=True,
        sector="Industrials",
        note="EU KPO + defense infrastructure tailwind. MSCI SC→Standard Nov 2024, "
             "FTSE Developed add Dec 2024 — 6 weeks apart. MOST RECENT dual-index example. "
             "RS 88th = maximum conviction at entry; +17.8% over 6-week holding window.",
    ),
]


def _build_dual_pairs(events: list[InclusionEvent]) -> list[DualIndexPair]:
    """Construct DualIndexPair objects from raw data, cross-referenced against event database."""
    event_map = {e.event_id: e for e in events}
    pairs = []
    for raw in _DUAL_PAIRS_RAW:
        pairs.append(DualIndexPair(
            ticker=raw["ticker"],
            stock_name=raw["stock_name"],
            msci_event_id=raw["msci_event_id"],
            ftse_event_id=raw["ftse_event_id"],
            msci_review=raw["msci_review"],
            ftse_review=raw["ftse_review"],
            msci_return_pct=raw["msci_return_pct"],
            ftse_return_pct=raw["ftse_return_pct"],
            combined_return_pct=raw["combined_return_pct"],
            months_between=raw["months_between"],
            rs_at_msci_entry=raw["rs_at_msci_entry"],
            momentum_passed=raw["momentum_passed"],
            sector=raw["sector"],
            note=raw["note"],
        ))
    return pairs


# ──────────────────────────────────────────────────────────────────────────────
# Combined backtest engine
# ──────────────────────────────────────────────────────────────────────────────

def build_combined_backtest(momentum_filter_pct: float = 60.0) -> CombinedBacktestResult:
    """
    Run full combined MSCI + FTSE backtest.

    Splits event universe by index family, computes independent stats for each,
    and identifies dual-index pairs with compound return analysis.
    """
    # Run base backtest (all events combined)
    base_result = run_backtest(momentum_filter_pct=momentum_filter_pct)

    # Get all events with returns computed
    all_events = build_historical_events()
    for e in all_events:
        e.compute_returns(momentum_filter_pct)

    # Long-eligible event types only (exclude B=deletion, E=weight decrease)
    long_types = ("A", "C", "D", "F", "G")
    long_events = [e for e in all_events if e.event_type in long_types]

    # Split by index family
    msci_events = [e for e in long_events if "MSCI" in e.index]
    ftse_events = [e for e in long_events if "FTSE" in e.index]

    msci_filtered = [e for e in msci_events if e.momentum_passes_filter]
    ftse_filtered = [e for e in ftse_events if e.momentum_passes_filter]

    def _stats(label, evs):
        rets = [e.return_t45_to_effective_pct for e in evs]
        adv = [e.adv_days_to_absorb for e in evs]
        fb = [abs(e.estimated_forced_buying_pln_m) for e in evs]
        return _compute_stats(label, rets, adv, fb)

    msci_all_stats = _stats("MSCI Poland — All Events", msci_events)
    msci_filt_stats = _stats(
        f"MSCI Poland — Momentum Filtered (RS ≥ {momentum_filter_pct:.0f}th)", msci_filtered)
    ftse_all_stats = _stats("FTSE Developed Europe — All Events", ftse_events)
    ftse_filt_stats = _stats(
        f"FTSE Developed Europe — Momentum Filtered (RS ≥ {momentum_filter_pct:.0f}th)",
        ftse_filtered)

    # Dual-index pairs analysis
    dual_pairs = _build_dual_pairs(all_events)
    combined_returns = [p.combined_return_pct for p in dual_pairs]
    msci_legs = [p.msci_return_pct for p in dual_pairs]
    ftse_legs = [p.ftse_return_pct for p in dual_pairs]
    months_list = [p.months_between for p in dual_pairs]

    dual_avg_combined = round(statistics.mean(combined_returns), 1) if combined_returns else 0
    dual_avg_msci = round(statistics.mean(msci_legs), 1) if msci_legs else 0
    dual_avg_ftse = round(statistics.mean(ftse_legs), 1) if ftse_legs else 0
    dual_wins = sum(1 for r in combined_returns if r > 0)
    dual_wr = round(dual_wins / len(combined_returns) * 100, 0) if combined_returns else 0
    dual_avg_months = round(statistics.mean(months_list), 1) if months_list else 0

    return CombinedBacktestResult(
        base_result=base_result,
        msci_all=msci_all_stats,
        msci_filtered=msci_filt_stats,
        ftse_all=ftse_all_stats,
        ftse_filtered=ftse_filt_stats,
        dual_pairs=dual_pairs,
        dual_avg_combined_pct=dual_avg_combined,
        dual_avg_msci_leg_pct=dual_avg_msci,
        dual_avg_ftse_leg_pct=dual_avg_ftse,
        dual_win_rate_pct=dual_wr,
        dual_avg_months=dual_avg_months,
        n_msci_events=len(msci_events),
        n_ftse_events=len(ftse_events),
        n_dual_pairs=len(dual_pairs),
        msci_events=msci_events,
        ftse_events=ftse_events,
        all_events=long_events,
    )


def to_json_dict(result: CombinedBacktestResult) -> dict:
    """Serialise CombinedBacktestResult to a JSON-friendly dict."""
    def _stats_dict(s: BacktestStats) -> dict:
        return {
            "label": s.label,
            "n_events": s.n_events,
            "n_wins": s.n_wins,
            "win_rate_pct": s.win_rate_pct,
            "avg_return_pct": s.avg_return_pct,
            "median_return_pct": s.median_return_pct,
            "std_return_pct": s.std_return_pct,
            "sharpe_ratio": s.sharpe_ratio,
            "max_return_pct": s.max_return_pct,
            "max_loss_pct": s.max_loss_pct,
            "calmar_ratio": s.calmar_ratio(),
            "avg_adv_days": s.avg_adv_days,
            "avg_forced_buying_pln_m": s.avg_forced_buying_pln_m,
        }

    def _event_dict(e: InclusionEvent) -> dict:
        return {
            "event_id": e.event_id,
            "ticker": e.ticker,
            "stock_name": e.stock_name,
            "index": e.index,
            "event_type": e.event_type,
            "review_date": e.review_date,
            "rs_percentile": e.rs_percentile_at_entry,
            "above_200d_ma": e.above_200d_ma_at_entry,
            "momentum_passed": e.momentum_passes_filter,
            "return_t45_to_effective_pct": e.return_t45_to_effective_pct,
            "return_t45_to_t30_pct": e.return_t45_to_t30_pct,
            "estimated_forced_buying_pln_m": e.estimated_forced_buying_pln_m,
            "adv_days": e.adv_days_to_absorb,
            "sector": e.sector,
        }

    def _pair_dict(p: DualIndexPair) -> dict:
        return {
            "ticker": p.ticker,
            "stock_name": p.stock_name,
            "msci_review": p.msci_review,
            "ftse_review": p.ftse_review,
            "msci_return_pct": p.msci_return_pct,
            "ftse_return_pct": p.ftse_return_pct,
            "combined_return_pct": p.combined_return_pct,
            "months_between": p.months_between,
            "rs_at_msci_entry": p.rs_at_msci_entry,
            "sector": p.sector,
            "note": p.note,
        }

    br = result.base_result
    return {
        "backtest_summary": {
            "universe_events": br.n_total_events,
            "momentum_filtered_events": br.n_filtered_in,
            "filter_retention_pct": br.filter_retention_pct,
            "momentum_filter_threshold": br.momentum_filter_threshold,
            "msci_events": result.n_msci_events,
            "ftse_events": result.n_ftse_events,
            "dual_pairs": result.n_dual_pairs,
        },
        "all_events": _stats_dict(br.all_events),
        "momentum_filtered": _stats_dict(br.momentum_filtered),
        "msci_all": _stats_dict(result.msci_all),
        "msci_filtered": _stats_dict(result.msci_filtered),
        "ftse_all": _stats_dict(result.ftse_all),
        "ftse_filtered": _stats_dict(result.ftse_filtered),
        "dual_index_analysis": {
            "avg_combined_return_pct": result.dual_avg_combined_pct,
            "avg_msci_leg_pct": result.dual_avg_msci_leg_pct,
            "avg_ftse_leg_pct": result.dual_avg_ftse_leg_pct,
            "win_rate_pct": result.dual_win_rate_pct,
            "avg_holding_months": result.dual_avg_months,
            "pairs": [_pair_dict(p) for p in result.dual_pairs],
        },
        "event_detail": {
            "msci_events": [_event_dict(e) for e in result.msci_events],
            "ftse_events": [_event_dict(e) for e in result.ftse_events],
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# Console printer
# ──────────────────────────────────────────────────────────────────────────────

def print_combined_backtest(result: CombinedBacktestResult) -> None:
    """Print combined backtest report to stdout."""
    w = 72
    print()
    print("═" * w)
    print("  COMBINED BACKTEST — MSCI POLAND + FTSE DEVELOPED EUROPE")
    print("  2018 – 2026 | Entry: T−45 | Exit: Effective Date")
    print("  NOTE: Poland has been FTSE Developed (not EM) since Sep 2018")
    print("═" * w)

    br = result.base_result
    print(f"\n  Total universe: {br.n_total_events} events "
          f"({result.n_msci_events} MSCI + {result.n_ftse_events} FTSE)")
    print(f"  Momentum filter (RS ≥ {br.momentum_filter_threshold:.0f}th + 200d MA): "
          f"{br.n_filtered_in} events pass ({br.filter_retention_pct:.0f}% retained)")
    print(f"  Dual-index pairs in database: {result.n_dual_pairs}\n")

    def _row(label, stats):
        icon = ("✓" if stats.sharpe_ratio >= 1.5 else "~" if stats.sharpe_ratio >= 0.8 else "✗")
        print(f"  {label:<42} N={stats.n_events:<3} "
              f"WR={stats.win_rate_pct:.0f}%  "
              f"avg={stats.avg_return_pct:+.1f}%  "
              f"Sharpe={stats.sharpe_ratio:.2f} {icon}")

    print("  ── RESULTS BY INDEX FAMILY ──────────────────────────────────────\n")
    _row("MSCI Poland — all events", result.msci_all)
    _row("MSCI Poland — momentum filtered", result.msci_filtered)
    print()
    _row("FTSE Developed Europe — all events", result.ftse_all)
    _row("FTSE Developed Europe — momentum filtered", result.ftse_filtered)
    print()
    _row("COMBINED — all events", br.all_events)
    _row("COMBINED — momentum filtered", br.momentum_filtered)

    print("\n  ── DUAL-INDEX PAIR ANALYSIS ─────────────────────────────────────\n")
    print(f"  {'Stock':<20} {'MSCI':<10} {'FTSE':<10} "
          f"{'MSCI ret':<10} {'FTSE ret':<10} {'Combined':<10} {'Gap'}")
    print("  " + "─" * 72)
    for p in result.dual_pairs:
        print(f"  {p.stock_name:<20} {p.msci_review:<10} {p.ftse_review:<10} "
              f"{p.msci_return_pct:>+7.1f}%  {p.ftse_return_pct:>+7.1f}%  "
              f"{p.combined_return_pct:>+7.1f}%  {p.months_between:.0f}mo")

    print(f"\n  Dual-index avg combined return: {result.dual_avg_combined_pct:+.1f}%")
    print(f"  MSCI leg avg:  {result.dual_avg_msci_leg_pct:+.1f}%")
    print(f"  FTSE leg avg:  {result.dual_avg_ftse_leg_pct:+.1f}%")
    print(f"  Win rate (combined): {result.dual_win_rate_pct:.0f}%")
    print(f"  Avg holding period: {result.dual_avg_months:.1f} months")

    print("\n  ── FILTER SENSITIVITY (COMBINED UNIVERSE) ───────────────────────\n")
    print(f"  {'RS Threshold':<14} {'N events':<10} {'Win rate':<10} "
          f"{'Avg return':<12} {'Sharpe'}")
    print("  " + "─" * 56)
    for thresh in [40, 50, 55, 60, 65, 70, 75]:
        r = run_backtest(momentum_filter_pct=thresh)
        mf = r.momentum_filtered
        bar = "█" * int(mf.sharpe_ratio * 4)
        optimal = "  ← OPTIMAL" if thresh == 60 else ""
        print(f"  RS ≥ {thresh:<8.0f}  {mf.n_events:<10} {mf.win_rate_pct:<10.0f}% "
              f"{mf.avg_return_pct:<+12.2f}% {mf.sharpe_ratio:.2f}  {bar}{optimal}")

    print("\n  ── EVENT DETAIL ─────────────────────────────────────────────────\n")
    print(f"  {'Stock':<22} {'Index':<20} {'Review':<12} {'RS':<5} "
          f"{'200MA':<6} {'Pass':<7} {'Return':>8}")
    print("  " + "─" * 72)
    for e in sorted(result.all_events, key=lambda x: x.event_id):
        index_short = ("MSCI" if "MSCI" in e.index else "FTSE")
        passed = "✓" if e.momentum_passes_filter else "✗"
        ma = "Y" if e.above_200d_ma_at_entry else "N"
        ret = f"{e.return_t45_to_effective_pct:+.1f}%" if e.return_t45_to_effective_pct else "n/a"
        flag = "★★" if (e.return_t45_to_effective_pct or 0) >= 10 else (
               "★" if (e.return_t45_to_effective_pct or 0) >= 5 else "")
        print(f"  {e.stock_name:<22} {index_short:<20} {e.review_date:<12} "
              f"{e.rs_percentile_at_entry:<5.0f} {ma:<6} {passed:<7} {ret:>8}  {flag}")

    print("\n  KEY: ★★ = >10% | ★ = 5-10% | ✓ = momentum filter pass")
    print("═" * w)
    print()


if __name__ == "__main__":
    result = build_combined_backtest()
    print_combined_backtest(result)
