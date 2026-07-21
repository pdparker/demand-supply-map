# BUILD SPEC — Demand & Supply Opportunity Map (dashboard #10, the Dean flagship)

Build a single-file `index.html` in THIS directory. It answers the education-product question:
**for each discipline, is domestic student demand rising or falling, is course supply expanding
or contracting, and therefore is the field OPEN (opportunity), HOT (competitive), CROWDED
(oversupplied) or FADING?** — with an overlay of where ACU's own portfolio already sits.
Audience: Dean of an education-product innovation unit / PVC. Executive, decision-oriented,
scrupulously honest that this joins two different markets.

## The framing (this is the whole point — get it exactly right)

Two momentum axes, joined on the ASCED broad field of education (native to both sources — no
crosswalk):
- **Demand momentum (x)** = change in that field's share of *domestic* university applications
  (Δ over the chosen horizon). Rising = students increasingly want it.
- **Supply momentum (y)** = net change in *CRICOS-registered* courses in that field (new − removed,
  2025→2026). Positive = providers adding courses; negative = providers cutting.

Quadrants:
- **OPEN** (demand ↑, supply ↓) — students want it, provider supply not keeping up → opportunity.
- **HOT / COMPETITIVE** (demand ↑, supply ↑) — both growing; move fast, expect competition.
- **CROWDED** (demand ↓, supply ↑) — providers piling in as domestic interest cools → caution.
- **FADING** (demand ↓, supply ↓) — both declining.

**The non-negotiable caveat, stated prominently (masthead + caveats card):** demand is *domestic
student appetite*; supply is *provider behaviour in the international-student register (CRICOS)*.
They are related proxies for a field's momentum but **NOT the same market** — read the map
directionally, never as a literal demand/supply ratio.

## Suite conventions (match siblings; read grant-outcomes/index.html for patterns — do NOT read its data blobs)

- Single self-contained `index.html`; data via `<script src="data.js"></script>` (present —
  `window.DEMANDSUPPLY`; schema below is authoritative, don't parse the file wholesale).
- `<head>` non-deferred: `<script src="https://pdparker.github.io/dashboard-commons/commons.js" data-dash="opportunity-map"></script>`
  (suite nav; the entry is registered separately — unhighlighted in local dev is fine).
- ACU brand identical to grant-outcomes: purple `#3C1053` masthead, red `#F2120C` accents, sand
  `#FBF6F0`/white, Manrope headings, Arial body. Reuse `.masthead`/`.kpi`/`.card`/`.bar-row`/
  `.chip` idioms.
- Chart.js 4.5.1 (same pinned CDN + SRI) for the quadrant scatter/bubble and the per-field
  trend line. Ranked bars = pure CSS/HTML.
- URL state via `DashCommons.state`; CSV export; print stylesheet. Registry not needed.

## Data schema (`window.DEMANDSUPPLY`)

```
{
  generated, fields: [10 ASCED broad fields], years_demand: [2010..2024], supply_period: "2025 → 2026",
  demand: { <field>: { app_share:[15], applications:[15], share_latest, d5yr, d8yr, vol_latest, vol_d5yr } },
      // d5yr = Δ app_share 2019→2024 ; d8yr = Δ 2016→2024 (both percentage-POINT changes)
  supply: { <field>: { allNet, allNew, allRem, heNet, heNew, heRem } },
      // "he" = higher-education levels only (Bachelor and above); "all" = every CRICOS level
  acu:    { <field>: { series:{yr:count}, latest, latest_year, first, first_year } },  // ACU commencing enrolments; absent fields (Eng/Arch/Ag) simply not keyed OR latest 0
  meta: { demand_source, supply_source, acu_source, caveat_market, caveat_level, caveat_horizon }
}
```

Quadrant is DERIVED, not stored: `demandMomentum = demand[f][horizon]` (d5yr default),
`supplyMomentum = supply[f][lens]Net` (heNet default). Sign of each → quadrant.

## Views (top to bottom)

1. **Masthead** (purple). Title "Demand & Supply Opportunity Map". Subtitle: for each discipline,
   domestic demand momentum vs CRICOS course-supply momentum → Open/Hot/Crowded/Fading, with the
   market-mismatch caveat in one clause. Controls: **Supply lens** toggle — "Higher-ed degrees"
   (default, `heNet`) / "All CRICOS levels" (`allNet`); **Demand horizon** toggle — "5-year"
   (default, `d5yr`) / "8-year" (`d8yr`); CSV export.
2. **KPI / callout row (4)**, all reactive to the toggles: clearest OPEN field (highest demand↑
   with supply↓ — Health under defaults); clearest CROWDED/FADING (Society & Culture, demand
   falling fastest); ACU's largest field + its quadrant (Health, ~4,607 commencing, OPEN); a
   "rising demand, ACU absent" flag (Engineering / IT).
3. **The quadrant scatter** (CENTREPIECE) — Chart.js bubble: x = demand momentum, y = supply
   momentum (per lens), each field a bubble **sized by ACU commencing enrolments** (fields ACU
   doesn't offer = small hollow marker), coloured by quadrant. Draw the two zero axes and label
   the four quadrants (Open top-left region [demand+, supply−], Hot top-right, Crowded
   bottom-right... note: put supply on y with supply DOWN = opportunity, so OPEN = demand+/supply−
   = lower-right? Decide a clear axis convention and LABEL it unambiguously in-chart; the honest
   requirement is that "demand up + supply down = OPEN" is visually obvious and labelled). Hover
   shows field, both momenta, ACU enrolment, quadrant.
4. **Opportunity ranking** — CSS bars, fields ranked by an opportunity score (demand momentum
   minus a normalised supply momentum, so demand-rising/supply-contracting tops the list). Mark
   ACU-present fields; show each field's quadrant tag.
5. **Field detail** (select a field, default Health): its demand trend (app_share line 2010-2024,
   Chart.js, + latest application volume), supply detail (new/removed at higher-ed AND all levels
   — surface that they can diverge, e.g. Architecture), ACU commencement trend, and a
   plain-English read ("Health: domestic demand rising (+1.1pp/5yr), degree-level CRICOS supply
   contracting (−49 net) — an opportunity gap; ACU's largest field at ~4,607 commencing"). Field
   selection persists in the URL.
6. **ACU alignment** — ACU's fields listed/plotted against their quadrant, sized by enrolment, so
   "where ACU's portfolio sits vs the opportunity map" is legible: it's concentrated in Health
   (Open) and Education (Hot), present in a Fading field (Society & Culture), and absent from a
   Hot one (Engineering).
7. **Caveats card** (mandatory, verbatim intent): (a) demand = domestic applications, supply =
   international CRICOS register — different markets, read directionally; (b) CRICOS all-levels is
   VET-dominated, hence the higher-ed lens is the university read and the two can diverge sharply
   (Architecture +246 all vs −14 degree); (c) supply is one-year momentum (a 2025→2026 snapshot
   pair) while demand is a multi-year share trend, and demand is a SHARE (can rise while total
   applications fall); (d) join key = ASCED broad field of education; (e) ACU figure is domestic
   commencing enrolments, a portfolio-presence proxy.
8. **CSV export** — one row per field: field, demand d5yr, demand d8yr, share_latest, heNet,
   allNet, acu_latest, quadrant(current lens/horizon).
9. **Sources footer** — Student Interest Signals (demand + ACU), CRICOS dashboard (supply); part
   of Phil's suite; cross-link those two dashboards.

## URL state keys

`field` (detail, default "Health"), `lens` (he|all, default he), `horizon` (5|8, default 5).
Read ALL params before applying any; sync on change; restore on load.

## Verification (before finishing)

Serve `python3 -m http.server 8956`; browser tools:
- zero console errors.
- Hand-checks (defaults: higher-ed lens, 5-yr horizon):
  - Health: demand **+1.11**, heNet **−49**, allNet **−64**, ACU **4,607** → **OPEN**.
  - Society & Culture: demand **−2.96** (steepest fall), heNet **−43** → FADING; flip lens to
    All levels → allNet **+178** → it moves to **CROWDED** (demonstrates the toggle matters).
  - Engineering: demand **+1.81** (strongest rise), heNet **+1**, ACU **0** (hollow marker).
  - IT: demand **+1.44**, heNet **+37**, ACU **45** → HOT.
  - Education: demand **+0.55**, heNet **+4**, ACU **3,442** → HOT.
  - Quadrant scatter renders 10 bubbles; Health/Education are the big ACU bubbles.
- `?field=Society and Culture&lens=all&horizon=8` cold-load restores all three.
- CSV intercept has 10 field rows + header with a quadrant column.
Kill the server. Do NOT git commit / push / create repos — the parent deploys. Only create
index.html; don't touch data.js, manifest.json, or this spec.
