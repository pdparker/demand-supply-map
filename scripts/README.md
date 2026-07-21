# Data refresh — Demand & Supply Opportunity Map

`build_join.py` reads three live sources and emits `data.js` (window.DEMANDSUPPLY):
1. Student Interest Signals `assets/js/data.js` — `doe.app_share`/`applications` by ASCED broad
   field (domestic demand) and `commencements_acu_long.csv` (ACU enrolments by field).
2. CRICOS dashboard `index.html` — the embedded `const D` blob; net course change by broad field,
   computed at all-levels and higher-ed-only (Bachelor and above).
The join key is the ASCED broad field of education — native to all three, no crosswalk needed.
Re-run after any of the three source dashboards refreshes; copy data.js here, bump manifest.
