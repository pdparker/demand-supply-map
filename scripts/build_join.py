import json, re, csv, os
SIS_DIR='/Users/philipparker/Dropbox/Claude_Cowork/inbox/student-interest-signals'
CRICOS='/Users/philipparker/Dropbox/claude_projects/cricos-dashboard-2025-2026/index.html'

# ---- Student Signals demand ----
s=open(f'{SIS_DIR}/assets/js/data.js').read()
sis=json.loads(s[s.index('{'):s.rindex('}')+1])
doe=sis['doe']; yrs=doe['years']
FIELDS=doe['fields']  # 10 ASCED broad fields (university-relevant)
i16,i19,i24=yrs.index(2016),yrs.index(2019),yrs.index(2024)

# ---- CRICOS supply ----
html=open(CRICOS).read(); idx=html.find('const D='); start=html.find('{',idx)
depth=0;i=start;instr=False;esc=False;ch=''
while i<len(html):
    c=html[i]
    if instr:
        if esc:esc=False
        elif c=='\\':esc=True
        elif c==ch:instr=False
    else:
        if c in '"\'':instr=True;ch=c
        elif c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:break
    i+=1
D=json.loads(html[start:i+1])
HE={'Bachelor Degree','Bachelor Honours Degree','Associate Degree','Graduate Certificate','Graduate Diploma','Masters Degree (Coursework)','Masters Degree (Research)','Masters Degree (Extended)','Doctoral Degree'}
sup={f:{'allNew':0,'allRem':0,'heNew':0,'heRem':0} for f in FIELDS}
for c in D['courses']:
    bf=re.sub(r'^\d+\s*-\s*','',c['bf'])
    if bf not in sup: continue
    isnew=c['st']=='new'
    sup[bf]['allNew' if isnew else 'allRem']+=1
    if c['cl'] in HE: sup[bf]['heNew' if isnew else 'heRem']+=1

# ---- ACU commencements by field ----
acu={}
for r in csv.DictReader(open(f'{SIS_DIR}/data/processed/commencements_acu_long.csv')):
    f=r['field']
    if f in FIELDS:
        acu.setdefault(f,{})[int(r['year'])]=int(r['commencing'])

out={'generated':'2026-07-21','fields':FIELDS,'years_demand':yrs,'supply_period':'2025 → 2026',
     'demand':{}, 'supply':{}, 'acu':{}}
for f in FIELDS:
    a=doe['app_share'][f]; ap=doe['applications'][f]
    out['demand'][f]={'app_share':a,'applications':ap,
        'share_latest':a[i24],'d5yr':round(a[i24]-a[i19],2),'d8yr':round(a[i24]-a[i16],2),
        'vol_latest':ap[i24],'vol_d5yr':ap[i24]-ap[i19]}
    s2=sup[f]
    out['supply'][f]={'allNet':s2['allNew']-s2['allRem'],'allNew':s2['allNew'],'allRem':s2['allRem'],
        'heNet':s2['heNew']-s2['heRem'],'heNew':s2['heNew'],'heRem':s2['heRem']}
    if f in acu:
        yr=sorted(acu[f]); out['acu'][f]={'series':{str(y):acu[f][y] for y in yr},
            'latest':acu[f][yr[-1]],'latest_year':yr[-1],'first':acu[f][yr[0]],'first_year':yr[0]}

out['meta']={
 'demand_source':'Domestic university application share by ASCED broad field of education — Dept of Education, via the Student Interest Signals dashboard. National, 2010-2024.',
 'supply_source':'Net change in CRICOS-registered courses by broad field, 2025 vs 2026 (new minus removed) — from the CRICOS dashboard. The CRICOS register is the international-student market.',
 'acu_source':'ACU commencing domestic enrolments by field, 2017-2024 (Student Signals).',
 'caveat_market':'DEMAND is domestic student appetite; SUPPLY is provider behaviour in the international-student register. Related proxies for a field’s momentum, but NOT the same market — read directionally, not as a like-for-like ratio.',
 'caveat_level':'CRICOS all-levels supply is dominated by VET/private-provider churn. The higher-education-only cut (Bachelor and above) is the relevant lens for a university degree portfolio, and often tells a different story (e.g. Architecture: all-levels +246 but degree-level -14).',
 'caveat_horizon':'Supply is one-year momentum (2025->2026 snapshot pair); demand is a multi-year share trend. Demand is a SHARE of applications (relative), which can rise even as total applications fall.'
}
os.makedirs('.',exist_ok=True)
with open('data.js','w') as f:
    f.write('window.DEMANDSUPPLY = '); json.dump(out,f,separators=(',',':')); f.write(';\n')
print('data.js', os.path.getsize('data.js'),'bytes | fields:',len(FIELDS),'| acu fields:',len(out['acu']))
print()
print(f'{"Field":34s} {"demΔ5y":>7s} {"HEsup":>6s} {"ALLsup":>7s} {"ACU24":>6s}  quadrant(HE lens)')
for f in FIELDS:
    d=out['demand'][f]; sp=out['supply'][f]; ac=out['acu'].get(f,{}).get('latest','-')
    dm=d['d5yr']; sm=sp['heNet']
    q=('OPEN' if dm>0 and sm<=0 else 'HOT' if dm>0 and sm>0 else 'CROWDED' if dm<=0 and sm>0 else 'FADING')
    print(f'{f[:34]:34s} {dm:+7.2f} {sm:+6d} {sp["allNet"]:+7d} {str(ac):>6s}  {q}')
