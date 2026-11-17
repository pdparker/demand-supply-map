# Data refresh — Demand & Supply Opportunity Map

`build_join.py` reads three live sources and emits `data.js` (window.DEMANDSUPPLY):
1. Student Interest Signals `assets/js/data.js` — `doe.app_share`/`applications` by ASCED broad
   field (domestic demand) and `commencements_acu_long.csv` (ACU enrolments by field).
2. CRICOS dashboard `index.html` — the embedded `const D` blob; net course change by broad field,
   computed at all-levels and higher-ed-only (Bachelor and above).
The join key is the ASCED broad field of education — native to all three, no crosswalk needed.
Re-run after any of the three source dashboards refreshes; copy data.js here, bump manifest.

## Employer demand tab (4-digit FoE) — `build_employer.py` → `emp_data.js`

Joins two Jobs and Skills Australia files to ASCED narrow fields through the curated
`anzsco_asced_crosswalk.csv` (degree-level occupations only; weights per occupation must sum to 1 —
the build asserts this), and adds CRICOS higher-ed net course change by narrow field from the
CRICOS dashboard's embedded data.

```bash
curl -A "Mozilla/5.0" -o osl4.xlsx  https://www.jobsandskills.gov.au/sites/default/files/2026-10/2026_unit_group_shortage_list_-_4_digit_anzsco.xlsx
curl -A "Mozilla/5.0" -o proj.xlsx  https://www.jobsandskills.gov.au/sites/default/files/2025-11/employment_projections_-_may_2025_to_may_2035.xlsx
python3 scripts/build_employer.py --osl osl4.xlsx --proj proj.xlsx   # writes emp_data.js
```

Keep the xlsx files out of the repo. The OSL is annual (Oct); the URL embeds the release month, so
re-scrape https://www.jobsandskills.gov.au/node/19303 for the current link. Projections are
re-released roughly annually. Check the build's printout for occupations with no OSL rating
(ANZSCO 2022 vs v1.3 code changes) and for fields named by code only.

To replace the judgement crosswalk with evidence: Census 2021 TableBuilder, employed persons,
QALFP (field of highest non-school qualification, 4-digit) × OCCP (4-digit), convert each occupation
column to field shares, and write rows in the same `anzsco,occupation,asced_narrow,weight` shape.
