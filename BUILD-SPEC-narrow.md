# BUILD SPEC ADDENDUM — 4-digit (narrow-field) drill-down for the Opportunity Map

Add a granularity control to the EXISTING `index.html` in this directory so the user can flip
the map from broad (2-digit) fields down to 4-digit sub-fields — but ONLY for the two broad
fields where 4-digit *demand* data exists (Health, Agriculture). This is a targeted extension of
the current dashboard, not a rebuild. Read the current `index.html` fully first and reuse its
existing quadrant-chart / ranking / detail rendering — do not duplicate or restyle it.

## Why it's scoped to two fields (state this in the UI, don't hide it)

The demand axis comes from DoE undergraduate application data, which is published at 4-digit only
for **Health** and **Agriculture**; the other 8 broad fields are broad-only. CRICOS supply exists
at 4-digit for everything, but the quadrant needs BOTH axes, so 4-digit is only meaningful for
those two. And ACU enrolments are broad-field only, so **there is NO ACU bubble overlay at 4-digit**
— markers are uniform at this level.

## New data (already in data.js — `window.DEMANDSUPPLY.narrow`)

```
narrow: {
  "Health": {
    "Nursing":        { demand:{ share_of_total:[15], share_latest, d5yr, d8yr, apps_latest }, supply:{ heNet, allNet, heNew, heRem, allNew, allRem } },
    "Medical Studies":{...}, "Dental Studies":{...}, "Veterinary Studies":{...}, "Health Other":{...}
  },
  "Agriculture, Environmental and Related Studies": {
    "Agriculture and other Related Studies":{...}, "Environmental Studies":{...}
  }
}
```
Same shape as the broad `demand`/`supply`, MINUS any acu key. `d5yr`/`d8yr` are Δ share-of-total
(percentage points); note narrow shares are small, so **the narrow quadrant axes must auto-scale
to the sub-field data** — do NOT reuse the broad map's axis range (bubbles would all collapse to
the origin). The existing `lens` (he/all) and `horizon` (5/8) toggles apply unchanged.

## UI change

- Add a **Granularity** segmented control to the masthead controls, alongside the existing Supply
  lens / Demand horizon toggles: **Broad fields** (default) · **Health sub-fields** · **Agriculture
  sub-fields**. (This is the "2-digit ↔ 4-digit flip" the user asked for, honestly scoped.)
- When a sub-field grain is active:
  - The **quadrant scatter**, **opportunity ranking**, and **field-detail** views all operate on
    that parent's narrow sub-fields instead of the 10 broad fields, using the same Open/Hot/
    Crowded/Fading logic, colours, lens/horizon toggles, and axis convention (supply inverted so
    OPEN = top-right). Auto-scale both axes to the sub-field values.
  - Bubbles are uniform size / no ACU overlay (data has no acu key here); show a small inline
    note in the chart caption: "No ACU overlay at 4-digit — ACU enrolments are broad-field only."
  - KPI row adapts to the sub-field set (e.g. clearest OPEN sub-field). If a KPI can't be computed
    at narrow (e.g. the ACU-largest-field KPI), replace it with a sensible narrow equivalent
    (e.g. largest sub-field by application share) rather than showing broad data.
  - The masthead subtitle or a small strip states the scope: "4-digit view — available for Health
    and Agriculture only; the DoE demand source publishes sub-field detail for just these two."
- **Broad fields** grain = today's behaviour, unchanged (ACU overlay intact).
- Persist grain in the URL as `grain` (values: `broad` [default] · `health` · `agriculture`);
  read all URL params before applying (existing pattern); it composes with `field`, `lens`,
  `horizon`. Keep the existing keys working.
- Extend the CSV export to include the narrow rows when a sub-field grain is active (or always
  append a grain column) — your call, but the export must reflect what's on screen.
- Add one line to the caveats card: 4-digit is available only for Health & Agriculture (DoE demand
  limit), and has no ACU overlay.

## Hand-checks (verify in browser on :8956)

- Granularity = Health sub-fields, defaults (he lens, 5-yr): 5 sub-fields plotted —
  - **Nursing**: share **10.66**, demand d5yr **+0.066**, heNet **−11** → **OPEN** (and it's by far
    the largest sub-field by share — a bigger slice of all applications than most whole broad fields).
  - **Health Other**: share **12.69**, d5yr **+0.627**, heNet **−21** → **OPEN**.
  - **Dental Studies**: **+0.473**, heNet **−2** → **OPEN**.
  - **Medical Studies**: **−0.036**, heNet **−7** → **FADING**.
  - **Veterinary Studies**: **−0.012**, heNet **−8** → **FADING**.
  - No ACU bubble sizing; axes auto-scaled (values much tighter than broad).
- Granularity = Agriculture sub-fields: 2 sub-fields (Agriculture and other Related **+0.220 / −13
  → OPEN**; Environmental Studies **+0.007 / −5 → OPEN**).
- Lens flip to All-levels changes the supply numbers (e.g. Nursing allNet **−11**, Medical **−9**).
- `?grain=health&lens=all&horizon=8` cold-load restores grain=health, all-levels, 8-yr.
- Switching back to Broad fields shows the original 10-field map with ACU overlay intact.
- Zero console errors.

Do NOT git commit / push. Only edit index.html. Do not touch data.js, manifest.json, or the spec
files. When done, kill the server (pkill -f "http.server 8956") and report each hand-check
observed-vs-expected + how you handled the axis auto-scaling and the ACU-overlay absence.
