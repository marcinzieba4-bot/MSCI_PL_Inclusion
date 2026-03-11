"""
Combined MSCI + FTSE Poland Inclusion Report — 2026
====================================================

Merges the MSCI Poland Standard candidates (EM index, semi-annual reviews)
with FTSE Developed Europe candidates (quarterly reviews) into a unified
trade watchlist.

Key distinctions:
  MSCI EM (Poland):   Semi-annual reviews (May / Nov). Forced buying $200-340M.
                      ~$8-10B AUM directly tracking MSCI Poland.
  FTSE Developed:     Quarterly reviews (Mar/Jun/Sep/Dec). Forced buying $30-120M.
                      Poland ~0.15% of FTSE All-World (~$600B+ AUM).
  Dual-index events:  Same stock, both MSCI and FTSE events within ~4-6 weeks.
                      Highest conviction plays — sequential passive demand.

Trade classification:
  source = "MSCI"   — only MSCI EM event visible for this stock in 2026
  source = "FTSE"   — only FTSE Developed event visible
  source = "Both"   — dual-index: MSCI and FTSE events within 60 days of each other
                      → mark as DUAL-INDEX ★★ regardless of individual conviction
"""

from dataclasses import dataclass, field
from examples.march_2026_update import build_march_2026_candidates
from examples.ftse_candidates_2026 import build_ftse_candidates, FTSECandidate2026
from examples.candidates_2026 import Candidate2026


# Tickers with confirmed dual-index events (both MSCI and FTSE in 2026)
_DUAL_TICKERS = {"XTB", "KRU", "ACP", "BDX", "MDVP"}


@dataclass
class UnifiedTrade:
    """
    A single inclusion trade, normalised from either MSCI or FTSE candidate data.
    Used for the combined trade table and JSON export.
    """
    # Identity
    ticker: str
    company: str
    sector: str
    source: str          # "MSCI" | "FTSE" | "Both"
    is_dual_index: bool

    # Event
    event_type: str      # "Standard Add", "Weight Increase", "Weight Decrease/Deletion"
    index_name: str      # e.g. "MSCI Poland Standard", "FTSE Developed Europe Mid Cap"
    review_date: str     # e.g. "May 2026 SAR", "Jun 2026 QIR"

    # Market data
    price_pln: float
    full_cap_usd_b: float
    float_adj_cap_usd_b: float
    return_12m_pct: float
    rs_percentile: float
    above_200d_ma: bool

    # Inclusion mechanics
    conviction: str           # "HIGH" | "MEDIUM" | "WATCH" | "SHORT"
    est_forced_buying_usd_m: float
    est_adv_days: float

    # Dual-index totals (only set when source == "Both")
    dual_total_forced_buying_usd_m: float = 0.0
    dual_msci_review: str = ""
    dual_ftse_review: str = ""

    # Narrative
    thesis_summary: str = ""
    key_risks: list = field(default_factory=list)
    verify_checklist: list = field(default_factory=list)

    def as_dict(self) -> dict:
        """Serialisable dict for JSON export."""
        return {
            "ticker": self.ticker,
            "company": self.company,
            "sector": self.sector,
            "source": self.source,
            "is_dual_index": self.is_dual_index,
            "event_type": self.event_type,
            "index_name": self.index_name,
            "review_date": self.review_date,
            "price_pln": self.price_pln,
            "full_cap_usd_b": round(self.full_cap_usd_b, 3),
            "float_adj_cap_usd_b": round(self.float_adj_cap_usd_b, 3),
            "return_12m_pct": self.return_12m_pct,
            "rs_percentile": self.rs_percentile,
            "above_200d_ma": self.above_200d_ma,
            "conviction": self.conviction,
            "est_forced_buying_usd_m": self.est_forced_buying_usd_m,
            "est_adv_days": self.est_adv_days,
            "dual_total_forced_buying_usd_m": self.dual_total_forced_buying_usd_m,
            "dual_msci_review": self.dual_msci_review,
            "dual_ftse_review": self.dual_ftse_review,
            "thesis_summary": self.thesis_summary,
            "key_risks": self.key_risks,
            "verify_checklist": self.verify_checklist,
        }


def _msci_to_unified(c: Candidate2026) -> UnifiedTrade:
    """Convert an MSCI Candidate2026 into a UnifiedTrade."""
    is_dual = c.ticker in _DUAL_TICKERS
    thesis = c.inclusion_thesis[:500] + "..." if len(c.inclusion_thesis) > 500 else c.inclusion_thesis
    return UnifiedTrade(
        ticker=c.ticker,
        company=c.company,
        sector=c.sector,
        source="Both" if is_dual else "MSCI",
        is_dual_index=is_dual,
        event_type=c.event_type,
        index_name="MSCI Poland Standard",
        review_date=c.target_review + " SAR",
        price_pln=c.price_pln,
        full_cap_usd_b=c.full_cap_usd_b,
        float_adj_cap_usd_b=c.float_adj_cap_usd_b,
        return_12m_pct=c.return_12m_pct,
        rs_percentile=c.rs_percentile,
        above_200d_ma=c.above_200d_ma,
        conviction=c.conviction,
        est_forced_buying_usd_m=c.est_forced_buying_usd_m,
        est_adv_days=c.est_adv_days,
        thesis_summary=thesis,
        key_risks=list(c.key_risks),
        verify_checklist=list(c.verify_checklist),
    )


def _ftse_to_unified(c: FTSECandidate2026) -> UnifiedTrade:
    """Convert a FTSECandidate2026 into a UnifiedTrade."""
    is_dual = c.ticker in _DUAL_TICKERS
    tier = getattr(c, "ftse_tier_target", "Developed")
    thesis = c.inclusion_thesis[:500] + "..." if len(c.inclusion_thesis) > 500 else c.inclusion_thesis
    return UnifiedTrade(
        ticker=c.ticker,
        company=c.company,
        sector=c.sector,
        source="Both" if is_dual else "FTSE",
        is_dual_index=is_dual,
        event_type=c.event_type,
        index_name=f"FTSE Developed Europe {tier}",
        review_date=c.target_review,
        price_pln=c.price_pln,
        full_cap_usd_b=c.full_cap_usd_b,
        float_adj_cap_usd_b=c.float_adj_cap_usd_b,
        return_12m_pct=c.return_12m_pct,
        rs_percentile=c.rs_percentile,
        above_200d_ma=c.above_200d_ma,
        conviction=c.conviction,
        est_forced_buying_usd_m=c.est_forced_buying_usd_m,
        est_adv_days=c.est_adv_days,
        thesis_summary=thesis,
        key_risks=list(c.key_risks),
        verify_checklist=list(c.verify_checklist),
    )


@dataclass
class CombinedReport:
    """All combined data for the 2026 Poland inclusion report."""
    msci_candidates: list[Candidate2026]
    ftse_candidates: list[FTSECandidate2026]
    all_trades: list[UnifiedTrade]          # all trades, deduplicated
    msci_only_trades: list[UnifiedTrade]
    ftse_only_trades: list[UnifiedTrade]
    dual_index_trades: list[UnifiedTrade]   # unified dual entries (one per ticker)
    report_date: str = "March 2026"
    pln_usd: float = 3.68

    def to_json_dict(self) -> dict:
        """Full JSON-serialisable representation."""
        _tier = {"HIGH": 0, "MEDIUM": 1, "WATCH": 2, "SHORT": 3}
        sorted_all = sorted(self.all_trades,
                            key=lambda t: (_tier.get(t.conviction, 9), -t.est_forced_buying_usd_m))
        return {
            "report_date": self.report_date,
            "pln_usd_rate": self.pln_usd,
            "summary": {
                "total_trades": len(self.all_trades),
                "msci_only": len(self.msci_only_trades),
                "ftse_only": len(self.ftse_only_trades),
                "dual_index": len(self.dual_index_trades),
                "high_conviction": sum(1 for t in self.all_trades if t.conviction == "HIGH"),
                "medium_conviction": sum(1 for t in self.all_trades if t.conviction == "MEDIUM"),
                "watch": sum(1 for t in self.all_trades if t.conviction == "WATCH"),
                "avoid_short": sum(1 for t in self.all_trades if t.conviction == "SHORT"),
                "total_est_forced_buying_usd_m": round(
                    sum(t.est_forced_buying_usd_m for t in self.all_trades
                        if t.est_forced_buying_usd_m > 0), 1),
            },
            "dual_index_plays": [t.as_dict() for t in self.dual_index_trades],
            "msci_trades": [t.as_dict() for t in
                            sorted(self.msci_only_trades + self.dual_index_trades,
                                   key=lambda t: (_tier.get(t.conviction, 9),
                                                  -t.est_forced_buying_usd_m))],
            "ftse_trades": [t.as_dict() for t in
                            sorted(self.ftse_only_trades + [
                                UnifiedTrade(
                                    ticker=t.ticker, company=t.company, sector=t.sector,
                                    source="Both", is_dual_index=True,
                                    event_type=t.event_type,
                                    index_name=t.index_name,
                                    review_date=t.dual_ftse_review or t.review_date,
                                    price_pln=t.price_pln,
                                    full_cap_usd_b=t.full_cap_usd_b,
                                    float_adj_cap_usd_b=t.float_adj_cap_usd_b,
                                    return_12m_pct=t.return_12m_pct,
                                    rs_percentile=t.rs_percentile,
                                    above_200d_ma=t.above_200d_ma,
                                    conviction=t.conviction,
                                    est_forced_buying_usd_m=t.dual_total_forced_buying_usd_m,
                                    est_adv_days=t.est_adv_days,
                                    thesis_summary=t.thesis_summary,
                                    key_risks=t.key_risks,
                                    verify_checklist=t.verify_checklist,
                                ) for t in self.dual_index_trades],
                            key=lambda t: (_tier.get(t.conviction, 9),
                                           -t.est_forced_buying_usd_m))],
            "all_trades_ranked": [t.as_dict() for t in sorted_all],
        }


def build_combined_report() -> CombinedReport:
    """
    Build the full combined MSCI + FTSE 2026 Poland report.
    Returns a CombinedReport with all trade views pre-populated.
    """
    msci_candidates = build_march_2026_candidates()
    ftse_candidates = build_ftse_candidates()

    # Convert all to UnifiedTrade
    msci_trades: list[UnifiedTrade] = [_msci_to_unified(c) for c in msci_candidates]
    ftse_trades: list[UnifiedTrade] = [_ftse_to_unified(c) for c in ftse_candidates]

    # Build lookup maps by ticker
    msci_by_ticker = {t.ticker: t for t in msci_trades}
    ftse_by_ticker  = {t.ticker: t for t in ftse_trades}

    # Build unified dual-index entries (merge MSCI + FTSE data for same ticker)
    dual_index: list[UnifiedTrade] = []
    for ticker in _DUAL_TICKERS:
        m = msci_by_ticker.get(ticker)
        f = ftse_by_ticker.get(ticker)
        if m is None or f is None:
            continue
        combined_fb = (
            (m.est_forced_buying_usd_m if m.est_forced_buying_usd_m > 0 else 0)
            + (f.est_forced_buying_usd_m if f.est_forced_buying_usd_m > 0 else 0)
        )
        # Conviction: if either is HIGH/MEDIUM, the dual is at least MEDIUM
        conv_rank = {"HIGH": 0, "MEDIUM": 1, "WATCH": 2, "SHORT": 3}
        best_conv = min(m.conviction, f.conviction, key=lambda c: conv_rank.get(c, 9))
        dual = UnifiedTrade(
            ticker=ticker,
            company=m.company,
            sector=m.sector,
            source="Both",
            is_dual_index=True,
            event_type=m.event_type,
            index_name=f"MSCI Poland Standard + FTSE Developed {getattr(ftse_by_ticker.get(ticker), 'ftse_tier_target', 'Europe')}",
            review_date=f"MSCI {m.review_date} + FTSE {f.review_date}",
            price_pln=m.price_pln,
            full_cap_usd_b=m.full_cap_usd_b,
            float_adj_cap_usd_b=m.float_adj_cap_usd_b,
            return_12m_pct=m.return_12m_pct,
            rs_percentile=m.rs_percentile,
            above_200d_ma=m.above_200d_ma,
            conviction=best_conv,
            est_forced_buying_usd_m=m.est_forced_buying_usd_m,   # MSCI component
            est_adv_days=m.est_adv_days,
            dual_total_forced_buying_usd_m=combined_fb,
            dual_msci_review=m.review_date,
            dual_ftse_review=f.review_date,
            thesis_summary=(
                f"DUAL-INDEX PLAY: MSCI EM + FTSE Developed. "
                f"MSCI forced buying [EST] ${m.est_forced_buying_usd_m:.0f}M | "
                f"FTSE forced buying [EST] ${f.est_forced_buying_usd_m:.0f}M | "
                f"Combined [EST] ${combined_fb:.0f}M. "
                f"MSCI: {m.review_date} | FTSE: {f.review_date}.\n\n"
                + m.thesis_summary
            ),
            key_risks=list(dict.fromkeys(m.key_risks + f.key_risks)),  # deduplicate
            verify_checklist=list(dict.fromkeys(m.verify_checklist + f.verify_checklist)),
        )
        dual_index.append(dual)

    # MSCI-only: tickers NOT in dual
    msci_only = [t for t in msci_trades if t.ticker not in _DUAL_TICKERS]
    # FTSE-only: tickers NOT in dual
    ftse_only = [t for t in ftse_trades if t.ticker not in _DUAL_TICKERS]

    # All trades: dual replaces individual entries for dual tickers
    all_trades = msci_only + ftse_only + dual_index

    # Sort by conviction then forced buying
    _tier = {"HIGH": 0, "MEDIUM": 1, "WATCH": 2, "SHORT": 3}
    all_trades.sort(key=lambda t: (_tier.get(t.conviction, 9), -t.dual_total_forced_buying_usd_m
                                    if t.is_dual_index else -t.est_forced_buying_usd_m))
    dual_index.sort(key=lambda t: (_tier.get(t.conviction, 9), -t.dual_total_forced_buying_usd_m))

    return CombinedReport(
        msci_candidates=msci_candidates,
        ftse_candidates=ftse_candidates,
        all_trades=all_trades,
        msci_only_trades=msci_only,
        ftse_only_trades=ftse_only,
        dual_index_trades=dual_index,
    )


def print_combined_summary(report: CombinedReport) -> None:
    """Terminal print of the combined report."""
    W = 80
    print()
    print("═" * W)
    print("  COMBINED MSCI + FTSE POLAND INCLUSION WATCHLIST — 2026")
    print(f"  {report.report_date}  |  PLN/USD {report.pln_usd}")
    print("═" * W)

    d = report.to_json_dict()["summary"]
    print(f"\n  Trades: {d['total_trades']} total  |  "
          f"MSCI-only: {d['msci_only']}  |  "
          f"FTSE-only: {d['ftse_only']}  |  "
          f"Dual-index: {d['dual_index']}")
    print(f"  Conviction: ★★ HIGH={d['high_conviction']}  ★ MEDIUM={d['medium_conviction']}  "
          f"◇ WATCH={d['watch']}  ⚠ AVOID={d['avoid_short']}")
    print(f"  Total estimated forced buying: ${d['total_est_forced_buying_usd_m']:.0f}M\n")

    _tier = {"HIGH": 0, "MEDIUM": 1, "WATCH": 2, "SHORT": 3}

    print("  ── DUAL-INDEX PLAYS (highest priority) ─────────────────────────────")
    for t in report.dual_index_trades:
        icon = {"HIGH": "★★", "MEDIUM": "★", "WATCH": "◇", "SHORT": "⚠"}.get(t.conviction, "?")
        print(f"  {icon} {t.ticker:<6} {t.company:<30}  "
              f"Combined FB: ${t.dual_total_forced_buying_usd_m:.0f}M  |  {t.review_date}")

    print()
    print("  ── MSCI-ONLY TRADES ──────────────────────────────────────────────────")
    for t in sorted(report.msci_only_trades,
                    key=lambda x: (_tier.get(x.conviction, 9), -x.est_forced_buying_usd_m)):
        icon = {"HIGH": "★★", "MEDIUM": "★", "WATCH": "◇", "SHORT": "⚠"}.get(t.conviction, "?")
        print(f"  {icon} {t.ticker:<6} {t.company:<30}  "
              f"MSCI FB: ${t.est_forced_buying_usd_m:+.0f}M  |  {t.review_date}")

    print()
    print("  ── FTSE-ONLY TRADES ──────────────────────────────────────────────────")
    for t in sorted(report.ftse_only_trades,
                    key=lambda x: (_tier.get(x.conviction, 9), -x.est_forced_buying_usd_m)):
        icon = {"HIGH": "★★", "MEDIUM": "★", "WATCH": "◇", "SHORT": "⚠"}.get(t.conviction, "?")
        print(f"  {icon} {t.ticker:<6} {t.company:<30}  "
              f"FTSE FB: ${t.est_forced_buying_usd_m:+.0f}M  |  {t.review_date}")
    print()
    print("═" * W)
