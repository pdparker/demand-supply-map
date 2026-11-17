"""Employer-demand layer by ASCED narrow (4-digit) field of education -> emp_data.js (window.EMPDEMAND).

Inputs (Jobs and Skills Australia, both open downloads; pass local paths):
  --osl   2026 Unit Group Shortage List, 4-digit ANZSCO 2022
          https://www.jobsandskills.gov.au/sites/default/files/2026-10/2026_unit_group_shortage_list_-_4_digit_anzsco.xlsx
  --proj  Employment Projections May 2025 - May 2035, Table 6 (ANZSCO 4-digit unit groups)
          https://www.jobsandskills.gov.au/sites/default/files/2025-11/employment_projections_-_may_2025_to_may_2035.xlsx
  --cricos  CRICOS dashboard index.html (embedded `const D`), for 4-digit higher-ed supply

The bridge from occupation to field is scripts/anzsco_asced_crosswalk.csv: a CURATED concordance
of skill-level-1 (degree-level) unit groups to the ASCED narrow field(s) that train for them, with
split weights where an occupation draws on more than one field. Judgement, not measured flows.
Deliberately excluded as field-agnostic: 1111-1113 (CEOs, general managers, legislators), 1325 R&D
managers, 139x defence/other specialist managers, 2421 university lecturers, 2422 VET teachers,
2492 private tutors. To replace the judgement with evidence, build a Census 2021 TableBuilder
table QALFP (4-digit) x OCCP (4-digit) for employed persons, convert each occupation's column to
shares, and write it in the same anzsco,asced_narrow,weight shape.

Run:  python3 scripts/build_employer.py --osl osl4.xlsx --proj proj.xlsx
"""
import argparse, csv, json, os, re
from collections import defaultdict
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--osl', required=True)
ap.add_argument('--proj', required=True)
ap.add_argument('--cricos', default=os.path.join(HERE, '..', '..', 'cricos-dashboard-2025-2026', 'index.html'))
ap.add_argument('--out', default=os.path.join(HERE, '..', 'emp_data.js'))
a = ap.parse_args()

# ---- Employment projections, Table 6 (ANZSCO v1.3 unit groups, '000 persons)
wb = openpyxl.load_workbook(a.proj, read_only=True, data_only=True)
ug = {}
for r in wb['Table_6 Occupation Unit Group'].iter_rows(values_only=True):
    if r and r[0] == 4 and r[1] == 'N':
        ug[str(r[2])] = dict(name=r[3], skill=r[4], emp=float(r[5]), e35=float(r[7]))

# ---- OSL 2026 unit-group national rating (ANZSCO 2022)
wb = openpyxl.load_workbook(a.osl, read_only=True, data_only=True)
osl = {}
for r in wb['2026 Unit group Shortage List'].iter_rows(values_only=True):
    if r and isinstance(r[0], (int, float)) and 1000 <= r[0] <= 9999:
        osl[str(int(r[0]))] = dict(name=r[1], rating=(r[2] or '').strip(), driver=r[3])

# ---- CRICOS higher-ed supply by narrow field (same HE level set as build_join.py)
HE = {'Bachelor Degree', 'Bachelor Honours Degree', 'Associate Degree', 'Graduate Certificate',
      'Graduate Diploma', 'Masters Degree (Coursework)', 'Masters Degree (Research)',
      'Masters Degree (Extended)', 'Doctoral Degree'}
html = open(a.cricos).read()
# ASCED narrow fields with no CRICOS course in the snapshot pair, so not named by the register
names = {'0505': 'Forestry Studies', '0507': 'Fisheries Studies', '0609': 'Optical Science'}
sup = defaultdict(lambda: {'heNew': 0, 'heRem': 0})
for code, nm, cl, st in re.findall(r'"nf":"(\d{4}) - ([^"]+)","df":"[^"]*","cl":"([^"]+)","st":"(\w+)"', html):
    names.setdefault(code, nm.strip())
    if cl in HE:
        sup[code]['heNew' if st == 'new' else 'heRem'] += 1
for code, nm in re.findall(r'"bf":"(\d{2}) - ([^"]+)"', html):
    names[code + '00'] = nm.strip()

# ---- Crosswalk -> per-field aggregates
xw = list(csv.DictReader(open(os.path.join(HERE, 'anzsco_asced_crosswalk.csv'))))
wsum = defaultdict(float)
for x in xw:
    wsum[x['anzsco']] += float(x['weight'])
bad = {k: v for k, v in wsum.items() if abs(v - 1) > 0.02}
assert not bad, f'crosswalk weights must sum to 1 per occupation: {bad}'

F = defaultdict(lambda: {'emp': 0.0, 'e35': 0.0, 'S': 0.0, 'RM': 0.0, 'rated': 0.0, 'occs': []})
unrated, missing = [], []
for x in xw:
    c, f, w = x['anzsco'], x['asced_narrow'], float(x['weight'])
    u = ug.get(c)
    if not u:
        missing.append(c); continue
    rating = osl.get(c, {}).get('rating')
    if not rating:
        unrated.append(c)
    d = F[f]
    d['emp'] += w * u['emp']; d['e35'] += w * u['e35']
    if rating:
        d['rated'] += w * u['emp']
        if rating == 'S': d['S'] += w * u['emp']
        elif rating in ('R', 'M'): d['RM'] += w * u['emp']
    d['occs'].append({'code': c, 'name': u['name'], 'w': w, 'emp': round(u['emp'], 1),
                      'g10': round((u['e35'] / u['emp'] - 1) * 100, 1) if u['emp'] else None,
                      'rating': rating or None,
                      'driver': osl.get(c, {}).get('driver')})

fields = {}
for f, d in F.items():
    if d['emp'] <= 0: continue
    s = sup.get(f, {'heNew': 0, 'heRem': 0})
    fields[f] = {
        'name': names.get(f, f), 'broad': f[:2], 'broadName': names.get(f[:2] + '00', ''),
        'emp': round(d['emp'], 1),
        'g10': round((d['e35'] / d['emp'] - 1) * 100, 2),
        'add10': round(d['e35'] - d['emp'], 1),
        'shortS': round(d['S'] / d['rated'] * 100, 1) if d['rated'] else None,
        'shortAny': round((d['S'] + d['RM']) / d['rated'] * 100, 1) if d['rated'] else None,
        'ratedPct': round(d['rated'] / d['emp'] * 100),
        'heNew': s['heNew'], 'heRem': s['heRem'], 'heNet': s['heNew'] - s['heRem'],
        'occs': sorted(d['occs'], key=lambda o: -o['emp'] * o['w']),
    }

out = {
    'generated': __import__('datetime').date.today().isoformat(),
    'sources': {
        'osl': 'Jobs and Skills Australia, 2026 Occupation Shortage List — unit group (4-digit ANZSCO 2022) national rating, released Oct 2026',
        'proj': 'Jobs and Skills Australia / Victoria University, Employment Projections May 2025 – May 2035, Table 6 (4-digit ANZSCO v1.3)',
        'cricos': 'CRICOS course register, 2025 vs 2026 snapshot pair, higher-education levels (Bachelor and above) — from the CRICOS dashboard',
        'crosswalk': 'Curated concordance of degree-level (skill level 1) occupations to ASCED narrow fields — scripts/anzsco_asced_crosswalk.csv',
    },
    'fields': fields,
    'unmappedNarrow': sorted(c for c in sup if c not in fields and not c.endswith('00')),
}
with open(a.out, 'w') as fh:
    fh.write('window.EMPDEMAND=' + json.dumps(out, separators=(',', ':'), ensure_ascii=False) + ';\n')

print(f'{len(fields)} fields | occupations mapped {len(wsum)} | missing from projections {missing} | no OSL rating {unrated}')
print(f'{"field":48s} {"emp k":>7s} {"g10%":>6s} {"S%":>5s} {"S+R/M%":>7s} {"HEnet":>6s}')
for f, v in sorted(fields.items(), key=lambda kv: -kv[1]['emp']):
    print(f'{f} {v["name"][:43]:43s} {v["emp"]:7.1f} {v["g10"]:6.1f} {str(v["shortS"]):>5s} {str(v["shortAny"]):>7s} {v["heNet"]:6d}')
