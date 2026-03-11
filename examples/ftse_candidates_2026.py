"""
FTSE Developed Europe — Poland Inclusion Watchlist 2026
=======================================================

IMPORTANT CONTEXT:
  Poland was reclassified by FTSE Russell from Advanced Emerging Market to
  DEVELOPED MARKET in September 2018. Polish stocks trade in the FTSE
  Developed Europe index family — NOT FTSE Emerging Markets.

FTSE Developed Europe relevant index tiers (by AUM):
  • FTSE All-World (Developed)       ~$600B+ global AUM tracking
  • FTSE Developed Europe            ~$180B AUM
  • FTSE Developed Europe Mid Cap    ~$60B AUM
  • FTSE Developed Europe Small Cap  ~$25B AUM
  • FTSE All-Share (Poland subset)   small

  Poland's weight in FTSE Developed World ≈ 0.15–0.20%.
  Total FTSE-tracked AUM exposed to Poland ≈ ~$1.5B–2.5B.
  Forced buying per new addition: typically $30M–$120M depending on tier.
  (Lower than MSCI EM, but FTSE and MSCI events are additive for stocks in both.)

FTSE 2026 Quarterly Index Review (QIR) calendar:
  Mar 2026 QIR: Announcement ~4 Mar 2026   | Effective ~20 Mar 2026
  Jun 2026 QIR: Announcement ~3 Jun 2026   | Effective ~22 Jun 2026
  Sep 2026 QIR: Announcement ~2 Sep 2026   | Effective ~19 Sep 2026
  Dec 2026 QIR: Announcement ~2 Dec 2026   | Effective ~19 Dec 2026

FTSE size bands (Developed World, approximate thresholds Mar 2026):
  Large Cap:  Float-adj cap > ~$8B
  Mid Cap:    Float-adj cap  $1.5B – $8B
  Small Cap:  Float-adj cap  $200M – $1.5B
  Minimum for All-World inclusion: float-adj cap ≥ ~$200M

Polish stocks currently in FTSE Developed World (partial list, largest):
  PKO, PKN Orlen, PZU, Bank Pekao, KGHM, Allegro, LPP, Dino, CD Projekt,
  Santander BP, mBank, Żabka, Bank Millennium, Budimex, Asseco Poland.
  XTB and Kruk: status to be verified (may be in FTSE Developed Small Cap or not yet included).

Sources: FTSE Russell country classification (ftserussell.com), Bloomberg FTSE All-World
         constituent lists, interactive brokers FTSE index analytics March 2026.
"""

from dataclasses import dataclass, field
from examples.candidates_2026 import Candidate2026


@dataclass
class FTSECandidate2026(Candidate2026):
    """
    Extends Candidate2026 with FTSE Developed-specific metadata.
    The base class fields are reused as follows:
      current_msci_status  → repurposed as current_ftse_tier
      target_review        → FTSE QIR date (e.g. "Jun 2026 QIR")
    Additional FTSE fields:
      index_source         "FTSE"
      ftse_tier_target     target FTSE tier after event ("Mid Cap", "Small Cap", etc.)
      ftse_aum_usd_b       estimated AUM of the target FTSE index in USD billions
      ftse_poland_weight   estimated weight in FTSE Developed Europe after inclusion (%)
    """
    index_source: str = "FTSE"
    ftse_tier_target: str = "Mid Cap"
    ftse_aum_usd_b: float = 60.0       # AUM of the target FTSE index
    ftse_poland_weight: float = 0.0    # estimated weight after event (%)


def build_ftse_candidates() -> list[FTSECandidate2026]:
    """
    FTSE Developed Europe — Poland inclusion candidates for 2026.
    PLN/USD ≈ 3.68 (March 2026).
    """
    PLN_USD = 3.68
    candidates: list[FTSECandidate2026] = []

    # ─────────────────────────────────────────────────────────────────────
    # 1. XTB S.A. — FTSE Developed Europe Mid Cap Addition Candidate
    # Current status: Likely FTSE Developed Small Cap or not yet included.
    # At float-adj ~$1.93B, XTB straddles the Small/Mid cap boundary.
    # ─────────────────────────────────────────────────────────────────────
    xtb = FTSECandidate2026(
        ticker="XTB",
        company="XTB S.A.",
        sector="Financials — Online CFD / Brokerage Platform",
        target_review="Jun 2026 QIR",
        event_type="Standard Add",          # repurposed: new tier addition
        current_msci_status="FTSE Dev Small Cap (est.)",
        current_index_weight_pct=0.0,

        full_cap_pln_b=10.91,
        full_cap_usd_b=10.91 / PLN_USD,     # $2.96B verified
        float_adj_cap_usd_b=1.93,           # [EST] ~65% float (founder ~35%)
        atvr_3m_pct=42.0,
        msci_standard_threshold_usd_b=1.5,  # FTSE Mid Cap lower bound ≈ $1.5B float-adj
        price_pln=92.78,

        return_12m_pct=47.0,
        rs_percentile=82,
        above_200d_ma=True,

        est_forced_buying_usd_m=85,         # FTSE Developed Europe Mid Cap addition
        est_adv_days=4.5,

        ftse_tier_target="Mid Cap",
        ftse_aum_usd_b=60.0,
        ftse_poland_weight=0.18,

        inclusion_thesis=(
            "XTB S.A. is Poland's fastest-growing retail brokerage/CFD platform. "
            "With a verified float-adj cap of ~$1.93B [EST] as of March 2026, XTB "
            "sits at the FTSE Developed Europe Small/Mid boundary (~$1.5B threshold).\n\n"
            "FTSE EVENT TYPE: Tier upgrade from FTSE Developed Small Cap to "
            "FTSE Developed Mid Cap (if currently in Small Cap), OR new addition "
            "to FTSE All-World Developed if not yet included.\n\n"
            "FORCED BUYING ESTIMATE: $85M [EST] from FTSE Developed Europe Mid Cap "
            "and All-World trackers. Lower than MSCI EM forced buying ($340M) but "
            "ADDITIVE — if both MSCI and FTSE events occur near simultaneously, "
            "the combined passive demand is ~$425M+ in a stock with 14 ADV days.\n\n"
            "FTSE REVIEW TIMING: FTSE QIRs are quarterly. The Jun 2026 QIR "
            "(announcement ~3 June, effective ~22 June) is the most actionable "
            "if XTB's float-adj cap remains above $1.5B at the May cut-off."
        ),
        why_now_in_2026=(
            "• Float-adj cap [EST] $1.93B crosses the FTSE Mid Cap floor of ~$1.5B.\n"
            "• FTSE reviews XTB at every quarterly review — Jun 2026 QIR is next major window.\n"
            "• Dual-index thesis: MSCI EM Standard (May 2026) + FTSE Mid Cap (Jun 2026) "
            "= sequential forced buying events within ~4 weeks of each other.\n"
            "• FTSE inclusion alpha is smaller but complementary: adds ~$85M net demand "
            "on top of the ~$340M MSCI demand, sustaining price support through June.\n"
            "• XTB near ATH PLN 93.76 — strong momentum filter pass for FTSE screening too."
        ),
        key_risks=[
            "Float-adj cap $1.93B [EST] is above $1.5B FTSE Mid Cap threshold but needs live verify.",
            "FTSE forced buying ($85M) is much smaller than MSCI ($340M) — not standalone thesis.",
            "FTSE Mid Cap additions have shorter drift windows than MSCI (QIR less predictable).",
            "If MSCI inclusion is delayed to Nov 2026, the FTSE event may already be priced in.",
        ],
        verify_checklist=[
            "☐ Verify XTB is currently in FTSE Developed Small Cap (check FTSE All-World constituents)",
            "☐ Confirm float-adj cap > $1.5B FTSE Mid Cap floor — live from WSE/FTSE data",
            "☐ Jun 2026 QIR announcement date: ftserussell.com/indexes/index-reviews",
            "☐ Check if MSCI May 2026 SAR and FTSE Jun 2026 QIR create overlapping demand window",
        ],

        index_source="FTSE",
    )
    xtb.compute()
    candidates.append(xtb)

    # ─────────────────────────────────────────────────────────────────────
    # 2. Kruk S.A. — FTSE Developed Europe Mid Cap Candidate
    # Float-adj ~$1.62B [EST] — above Mid Cap floor of ~$1.5B
    # ─────────────────────────────────────────────────────────────────────
    kru = FTSECandidate2026(
        ticker="KRU",
        company="Kruk S.A.",
        sector="Financials — Debt Collection / NPL Portfolio Purchasing",
        target_review="Sep 2026 QIR",
        event_type="Standard Add",
        current_msci_status="FTSE Dev Small Cap (est.)",
        current_index_weight_pct=0.0,

        full_cap_pln_b=9.03,
        full_cap_usd_b=9.03 / PLN_USD,
        float_adj_cap_usd_b=1.62,           # [EST] founder ~31%; float ~69%
        atvr_3m_pct=28.0,
        msci_standard_threshold_usd_b=1.5,
        price_pln=464.60,

        return_12m_pct=22.78,
        rs_percentile=60,
        above_200d_ma=True,

        est_forced_buying_usd_m=70,
        est_adv_days=3.5,

        ftse_tier_target="Mid Cap",
        ftse_aum_usd_b=60.0,
        ftse_poland_weight=0.14,

        inclusion_thesis=(
            "Kruk S.A. — Europe's largest NPL portfolio purchaser by carrying value. "
            "Float-adj cap [EST] ~$1.62B is above the FTSE Mid Cap floor of ~$1.5B. "
            "If currently in FTSE Developed Small Cap, the Sep 2026 QIR is the "
            "realistic window for a tier upgrade to FTSE Developed Mid Cap.\n\n"
            "FTSE FORCED BUYING [EST]: $70M from FTSE Developed Europe Mid Cap "
            "and FTSE All-World trackers. While smaller than the MSCI EM event, "
            "this is additional demand on top of MSCI Nov 2026 SAR potential.\n\n"
            "COMBINED PLAY: If both MSCI Standard addition (Nov 2026) and FTSE "
            "Mid Cap tier upgrade (Sep/Dec 2026) occur within 60 days, total "
            "passive demand ≈ $245M (MSCI) + $70M (FTSE) = ~$315M.\n\n"
            "RECORD 2025 RESULTS confirm fundamentals: Cash EBITDA PLN 2.7B (+12%), "
            "Q4 net profit PLN 208M (+81% YoY), portfolio PLN 11.6B (+11%)."
        ),
        why_now_in_2026=(
            "• Float-adj cap $1.62B [EST] above FTSE Mid Cap threshold of ~$1.5B.\n"
            "• Sep 2026 QIR timing aligns with MSCI Nov 2026 SAR pre-window.\n"
            "• ECB + NBP rate normalisation: improves Kruk funding cost while NPL portfolio "
            "yields remain fixed — spread expansion supports cap growth in H2 2026.\n"
            "• Record 2025: Cash EBITDA PLN 2.7B, equity PLN 5.3B (+18%), "
            "net debt/EBITDA improved to 2.6x. Analyst target PLN 532 (+14.5%).\n"
            "• Near its ATH of PLN 510 (Jan 2026) — recovery trajectory intact."
        ),
        key_risks=[
            "Float-adj cap $1.62B [EST] only marginally above $1.5B — verify live.",
            "FTSE event ($70M) is smaller than MSCI ($245M) — standalone FTSE play has low alpha.",
            "PLN strengthening vs USD compresses float-adj USD cap → threshold risk.",
            "Sep 2026 QIR timing is uncertain; FTSE may defer to Dec 2026 QIR.",
        ],
        verify_checklist=[
            "☐ Confirm Kruk current FTSE tier — check FTSE All-World Poland constituents",
            "☐ Float-adj cap vs $1.5B FTSE Mid Cap floor",
            "☐ Sep 2026 QIR cut-off date from ftserussell.com",
            "☐ Check alignment with MSCI Nov 2026 SAR window for combined trade timing",
        ],

        index_source="FTSE",
    )
    kru.compute()
    candidates.append(kru)

    # ─────────────────────────────────────────────────────────────────────
    # 3. Diagnostyka S.A. — FTSE Developed Small Cap Weight Increase
    # Added to MSCI Poland Small Cap June 2025.
    # Float-adj ~$1.15B [EST] — in FTSE Developed Small Cap range.
    # ─────────────────────────────────────────────────────────────────────
    diag = FTSECandidate2026(
        ticker="DIAG",
        company="Diagnostyka S.A.",
        sector="Health Care — Medical Laboratory / Diagnostics Services",
        target_review="Dec 2026 QIR",
        event_type="Weight Increase",
        current_msci_status="FTSE Dev Small Cap (est.)",
        current_index_weight_pct=0.0,

        full_cap_pln_b=6.04,
        full_cap_usd_b=6.04 / PLN_USD,
        float_adj_cap_usd_b=1.15,
        atvr_3m_pct=16.0,
        msci_standard_threshold_usd_b=1.5,
        price_pln=182.05,

        return_12m_pct=0.0,
        rs_percentile=45,
        above_200d_ma=True,

        est_forced_buying_usd_m=20,
        est_adv_days=2.0,

        ftse_tier_target="Small Cap",
        ftse_aum_usd_b=25.0,
        ftse_poland_weight=0.08,

        inclusion_thesis=(
            "Diagnostyka S.A. is Poland's largest private medical lab network, "
            "added to MSCI Poland Small Cap in June 2025. Float-adj cap ~$1.15B [EST] "
            "places it in FTSE Developed Small Cap range.\n\n"
            "FTSE EVENT: Weight increase in FTSE Developed Small Cap as cap grows. "
            "Forced buying [EST] $20M — small event, not a standalone trade thesis.\n\n"
            "MONITOR ONLY: Diagnostyka is a long-term hold in the Polish healthcare "
            "structural theme. FTSE small-cap weight increases are low-alpha events "
            "at this cap level. Include in the combined report for completeness; "
            "not an actionable 2026 trade."
        ),
        why_now_in_2026=(
            "• Recent MSCI Small Cap addition (Jun 2025) may trigger FTSE review.\n"
            "• Polish private healthcare market growing: NFZ outsourcing + aging demographics.\n"
            "• Float-adj cap of $1.15B [EST] comfortably above FTSE Small Cap floor (~$200M).\n"
            "• WATCH for 2027 when cap growth may trigger FTSE Mid Cap consideration."
        ),
        key_risks=[
            "Very small FTSE forced buying ($20M) — not a tradeable FTSE event alone.",
            "NFZ government reimbursement risk.",
            "PE overhang may limit float expansion.",
        ],
        verify_checklist=[
            "☐ Confirm DIAG is in FTSE Developed Small Cap constituent list",
            "☐ Any PE lockup expiry creating float increase",
        ],

        index_source="FTSE",
    )
    diag.compute()
    candidates.append(diag)

    # ─────────────────────────────────────────────────────────────────────
    # 4. Asseco Poland S.A. (ACP) — FTSE Developed Mid Cap Weight Increase
    # Added to MSCI Poland Standard Feb 2026. Float-adj ~$2.8B [EST].
    # FTSE Mid Cap member — weight increasing after +60% price run.
    # ─────────────────────────────────────────────────────────────────────
    acp = FTSECandidate2026(
        ticker="ACP",
        company="Asseco Poland S.A.",
        sector="Information Technology — Enterprise Software / IT Services",
        target_review="Jun 2026 QIR",
        event_type="Weight Increase",
        current_msci_status="FTSE Dev Mid Cap",
        current_index_weight_pct=0.22,      # [EST] small weight in FTSE Dev Europe

        full_cap_pln_b=18.0,
        full_cap_usd_b=18.0 / PLN_USD,
        float_adj_cap_usd_b=2.80,
        atvr_3m_pct=22.0,
        msci_standard_threshold_usd_b=1.5,
        price_pln=110.0,

        return_12m_pct=60.0,
        rs_percentile=92,
        above_200d_ma=True,

        est_forced_buying_usd_m=45,
        est_adv_days=3.5,

        ftse_tier_target="Mid Cap",
        ftse_aum_usd_b=60.0,
        ftse_poland_weight=0.28,

        inclusion_thesis=(
            "Asseco Poland was added to MSCI Poland Standard (Feb 2026) after a +60% "
            "price run. This same price momentum and cap growth will flow through to "
            "FTSE Developed Mid Cap weight increases at the Jun 2026 QIR.\n\n"
            "FTSE WEIGHT INCREASE: As Asseco's cap grew ~60%, its weight within "
            "FTSE Developed Europe Mid Cap increases proportionally. Passive FTSE "
            "Mid Cap trackers buy the weight increase at the quarterly rebalance.\n\n"
            "Forced buying [EST] $45M — lower than MSCI Standard addition ($280M) "
            "but the MSCI event (Feb 2026) already occurred; this is a second, "
            "smaller follow-on event from FTSE rebalancing."
        ),
        why_now_in_2026=(
            "• Post-MSCI Standard inclusion (Feb 2026), Asseco is a growing weight in both MSCI and FTSE.\n"
            "• AI/KPO digitisation tailwinds for Polish government IT spending.\n"
            "• Jun 2026 QIR rebalance: FTSE will adjust Asseco weight upwards after cap growth.\n"
            "• RS [EST] 92nd pct — top decile momentum supports continued outperformance."
        ),
        key_risks=[
            "Weight increase alpha is smaller than new addition — expect +2-5% above FTSE Poland.",
            "Post-MSCI inclusion mean reversion risk: forced selling once passive trackers finish.",
            "Government contract dependency — political risk.",
        ],
        verify_checklist=[
            "☐ Confirm ACP current FTSE Developed Mid Cap weight",
            "☐ Current Asseco price and cap — verify +60% gain from 12M ago holds",
            "☐ Jun 2026 QIR cut-off window from ftserussell.com",
        ],

        index_source="FTSE",
    )
    acp.compute()
    candidates.append(acp)

    # ─────────────────────────────────────────────────────────────────────
    # 5. Budimex S.A. (BDX) — FTSE Developed Mid Cap Weight Increase
    # Already in FTSE Developed Mid Cap (added Dec 2024).
    # Strong EU KPO contract pipeline supports continued cap growth.
    # ─────────────────────────────────────────────────────────────────────
    bdx = FTSECandidate2026(
        ticker="BDX",
        company="Budimex S.A.",
        sector="Industrials — General Contractor / Civil Engineering",
        target_review="Jun 2026 QIR",
        event_type="Weight Increase",
        current_msci_status="FTSE Dev Mid Cap",
        current_index_weight_pct=0.35,      # [EST] growing weight

        full_cap_pln_b=22.0,               # [EST] continues growing from EU contracts
        full_cap_usd_b=22.0 / PLN_USD,
        float_adj_cap_usd_b=2.50,          # [EST] Ferrovial ~53%; float ~47%
        atvr_3m_pct=30.0,
        msci_standard_threshold_usd_b=1.5,
        price_pln=535.0,                   # [EST] continued appreciation

        return_12m_pct=18.0,               # [EST] normalised after big 2024 move
        rs_percentile=70,
        above_200d_ma=True,

        est_forced_buying_usd_m=50,
        est_adv_days=4.0,

        ftse_tier_target="Mid Cap",
        ftse_aum_usd_b=60.0,
        ftse_poland_weight=0.30,

        inclusion_thesis=(
            "Budimex was added to FTSE Developed Mid Cap in December 2024 — the "
            "FTSE inclusion event has already occurred. The 2026 thesis is purely "
            "a weight increase story as Budimex's cap continues growing via EU KPO "
            "(PLN 76B infrastructure program) and Polish defence spending (4% GDP).\n\n"
            "FTSE WEIGHT INCREASE: As Budimex outperforms other FTSE Developed "
            "Europe Mid Cap members, its weight increases at each quarterly rebalance. "
            "Forced buying [EST] $50M at the Jun 2026 QIR — a modest secondary event "
            "on top of the MSCI Poland weight increase already occurring."
        ),
        why_now_in_2026=(
            "• EU KPO (Polish Recovery Fund) has PLN 76B to allocate in 2025-26 — "
            "Budimex wins a disproportionate share as Poland's #1 contractor.\n"
            "• NATO: Poland's 4% GDP defence budget = largest contractor in CEE for defence infrastructure.\n"
            "• FTSE weight increase is a secondary, lower-risk play vs the MSCI Standard inclusion.\n"
            "• Ferrovial (53% parent) potential stake reduction: increases float → bigger FTSE weight."
        ),
        key_risks=[
            "EU KPO disbursement delays from Brussels could defer project starts.",
            "Labour cost inflation in Poland compressing Budimex construction margins.",
            "Weight increase alpha is smaller than new addition — lower priority vs XTB/Kruk.",
            "Ferrovial stake (53%) limits FIF — if Ferrovial reduces stake, float increases (positive).",
        ],
        verify_checklist=[
            "☐ Current Budimex price and FTSE weight",
            "☐ EU KPO contract award announcements — confirms revenue pipeline",
            "☐ Ferrovial stake update — any WSE disclosure of stake changes",
        ],

        index_source="FTSE",
    )
    bdx.compute()
    candidates.append(bdx)

    # ─────────────────────────────────────────────────────────────────────
    # 6. MODIVO S.A. (MDVP, formerly CCC) — FTSE Developed Weight Decrease
    # Deleted from MSCI Standard Feb 2026. FTSE will follow with weight cut.
    # ─────────────────────────────────────────────────────────────────────
    mdvp = FTSECandidate2026(
        ticker="MDVP",
        company="MODIVO S.A. (formerly CCC S.A.)",
        sector="Consumer Discretionary — Footwear / Fashion Retail",
        target_review="Jun 2026 QIR",
        event_type="Weight Decrease/Deletion",
        current_msci_status="FTSE Dev Mid Cap (declining)",
        current_index_weight_pct=0.12,      # [EST] small and shrinking

        full_cap_pln_b=10.15,
        full_cap_usd_b=10.15 / PLN_USD,
        float_adj_cap_usd_b=1.71,
        atvr_3m_pct=18.0,
        msci_standard_threshold_usd_b=1.5,
        price_pln=121.70,

        return_12m_pct=-36.0,
        rs_percentile=15,
        above_200d_ma=False,

        est_forced_buying_usd_m=-30,       # forced selling as FTSE weight decreases
        est_adv_days=3.0,

        ftse_tier_target="Small Cap",       # potential demotion to Small Cap
        ftse_aum_usd_b=25.0,
        ftse_poland_weight=0.05,

        inclusion_thesis=(
            "CCC/MODIVO was deleted from MSCI Poland Standard effective Feb 27, 2026. "
            "The FTSE will reflect this through weight reductions and potential "
            "demotion from FTSE Developed Mid Cap to Small Cap.\n\n"
            "FTSE WEIGHT DECREASE / DEMOTION: As MODIVO's float-adj cap falls below "
            "the FTSE Mid Cap lower bound (~$1.5B float-adj), FTSE will demote it to "
            "Small Cap. The demotion creates forced selling by FTSE Mid Cap trackers "
            "and reduces buying from FTSE Small Cap trackers (lower AUM tier).\n\n"
            "Combined MSCI deletion + FTSE demotion = structural dual-index selling "
            "pressure on MODIVO throughout H1 2026."
        ),
        why_now_in_2026=(
            "• MSCI Standard deletion (Feb 27, 2026) already confirmed.\n"
            "• FTSE Mid Cap demotion expected at Jun 2026 QIR as float-adj cap falls.\n"
            "• Operating deterioration: revenue PLN 500M below plan, weak e-commerce.\n"
            "• AVOID in both MSCI and FTSE strategies — dual-index selling pressure."
        ),
        key_risks=[
            "Post-MSCI-deletion reversal: stocks often recover +5-10% in 30 days.",
            "Dariusz Milek buyout at premium: short squeeze risk.",
            "FTSE demotion may be delayed — only triggers if float-adj cap falls below $1.5B.",
        ],
        verify_checklist=[
            "☐ Current MDVP (ex-CCC) FTSE tier — Mid Cap or already demoted?",
            "☐ Float-adj cap vs $1.5B FTSE Mid Cap boundary",
            "☐ Any Milek buyout announcement",
        ],

        index_source="FTSE",
    )
    mdvp.compute()
    candidates.append(mdvp)

    return candidates


def print_ftse_summary(candidates: list[FTSECandidate2026]) -> None:
    """Terminal summary of FTSE Developed Europe 2026 candidates."""
    W = 72
    print()
    print("═" * W)
    print("  FTSE DEVELOPED EUROPE — POLAND 2026 WATCHLIST")
    print("  Poland: FTSE Developed Market since Sep 2018 | QIRs quarterly")
    print("═" * W)
    print()
    print("  NOTE: Poland is FTSE DEVELOPED (not EM). Forced buying is ~$30-120M per")
    print("  event (vs $200-340M for MSCI EM Standard add). FTSE events are ADDITIVE.")
    print()

    tier_order = {"HIGH": 0, "MEDIUM": 1, "WATCH": 2, "SHORT": 3}
    sorted_c = sorted(candidates, key=lambda x: (tier_order.get(x.conviction, 9),
                                                  x.target_review, -x.rs_percentile))

    print(f"  {'#':<3} {'Company':<26} {'Event':<22} {'Review':<14} "
          f"{'Cap USD':<10} {'FB $M':<8} {'Conv.'}")
    print("  " + "─" * 72)
    for i, c in enumerate(sorted_c, 1):
        icon = {"HIGH": "★★", "MEDIUM": "★", "WATCH": "◇", "SHORT": "⚠"}.get(c.conviction, "?")
        fb = f"${c.est_forced_buying_usd_m:+.0f}M"
        print(f"  {i:<3} {c.company[:25]:<26} {c.event_type:<22} {c.target_review:<14} "
              f"${c.full_cap_usd_b:<9.2f} {fb:<8} {icon} {c.conviction}")

    print()
    print("  DUAL-INDEX CANDIDATES (MSCI + FTSE):")
    print("  → XTB: MSCI May 2026 SAR + FTSE Jun 2026 QIR  = combined ~$425M demand")
    print("  → Kruk: MSCI Nov 2026 SAR + FTSE Sep 2026 QIR = combined ~$315M demand")
    print()
    print("═" * W)
