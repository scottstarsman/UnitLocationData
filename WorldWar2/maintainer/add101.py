import csv,glob,io,os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
URL='https://www.fold3.com/image/158876338/'
NOM='https://nominatim.openstreetmap.org/'
REF='R834'; DAY='4 November 2026'
places={r['place_id']:r for r in csv.DictReader(open('data/places.csv'))}
def L(g):
    return f'{REF}: English p.{g} (Fold3 page {g+67})'
REV="Review: confidence {c} from the rubric (one postwar manuscript by the corps commander, index of 19 September 1950, English translation only with no German original, a low-contrast scan; 0.5 for a dated place clearly read, 0.3 where the place or date carries a [?] reading); added in the FMS Fold3 reading of "+DAY+" (FMS B-101, branch fms-fold3-german-2): old value none, new value this claim; parent_unit_id old value none, new value blank, reason: parents are left blank on this pass."
C=[]
def add(u,date,pl,rep,prec,op,ev,act,conf,loc,dtxt,defn,lsup,basis='documented_on_date',ctx='',cmd='unknown',grp=''):
    C.append(dict(u=u,date=date,pl=pl,rep=rep,prec=prec,op=op,ev=ev,act=act,conf=conf,loc=loc,dtxt=dtxt,defn=defn,lsup=lsup,basis=basis,ctx=ctx,cmd=cmd,grp=grp))
add('GER-COR-067C','1945-01-26','PL3713','headquarters',3,'OP-CAMP-RHINELAND','hq_observation','LXVII Corps under the Fifteenth Army with its command post at Kronenburg [?] at the start of the West Wall fighting','0.3',L(5),'26 January 1945, the opening date of the report (the command post is stated for the period after the Ardennes offensive)','the corps is subordinated to the Fifteenth Army and its command post is at Kronenburg [?]; divisions 277, 89, 3rd Parachute and 246 are under it.','the text names Kronenburg, read with uncertainty in a low-contrast scan','documented_on_date','Context: the place reading carries a [?], so confidence 0.3; date old value none, new value 1945-01-26, reason: the command post is given for the situation at the opening date of the report (26 January).',cmd='General der Infanterie Otto Hitzfeld')
add('GER-COR-067C','1945-03-07','PL3714','headquarters',3,'OP-REMAGEN','hq_move','LXVII Corps command post moves from Falkenberg [?] to Brück on the Ahr early on 7 March for the attack toward Gelsdorf','0.5',L(25),'7 March 1945 (order of the evening of 6 March: move by early 7 March; the corps staff leaves at about 0900 and sets up at Brück)','on the Fifteenth Army order of the evening of 6 March the corps is to attack across the Ahr toward Gelsdorf; its command post moves to Brück, where the operations staff meets the 277th Division staff on 7 March.','the text names Brück on the Ahr repeatedly; the earlier post Falkenberg is uncertain and not entered','documented_on_date','',cmd='General der Infanterie Otto Hitzfeld')
add('GER-COR-067C','1945-03-10','PL3716','headquarters',3,'OP-REMAGEN','relocation','LXVII Corps staff crosses the Rhine by the emergency ferry from Brohl to Rheinbrohl early on 10 March','0.5',L(50),'early 10 March 1945','the corps staff crosses by the 272nd Division emergency ferry from Brohl to Rheinbrohl; the small bridgehead west of the Rhine is held to 11 March and the last elements cross in the night of 12 March.','the text names Brohl and Rheinbrohl','documented_on_date','',cmd='General der Infanterie Otto Hitzfeld')
add('GER-COR-067C','1945-03-12','PL3715','headquarters',3,'OP-CAMP-RHINELAND','defense','LXVII Corps holds the Rhine front from Leubsdorf to Vallendar with its command post at Altwied','0.5',L(52),'12 March 1945','the corps holds the east bank of the Rhine from Leubsdorf to Vallendar, adjoining the Bayerlein corps on the right and the replacement division of von Berg on the left; its command post is at Altwied (Model visits it about 10 March), later moved to Muscheid [?].','the text names Altwied as corps command post (pages 40 and 52)','documented_on_date','',cmd='General der Infanterie Otto Hitzfeld')
add('GER-COR-067C','1945-03-19','PL3717','sector_center',3,'OP-CAMP-RHINELAND','withdrawal','LXVII Corps loses Neuwied and the Wied sector on its left wing about 19 March','0.3',L(54),'about 19 March 1945 (day read with uncertainty, 19 or 16)','the Wied sector and Neuwied, a declared strongpoint held by 150-200 men, are lost to an attack by at least one regiment with tanks; Hitzfeld orders the last 20 men out and four get through.','the text names Neuwied','documented_on_date','Context: inferred date, old value none, new value 1945-03-19; reason: the day is read as 19 [?] (possibly 16).',cmd='General der Infanterie Otto Hitzfeld')
byfile={}
cid=8222
for c in C:
    c['id']='C%04d'%cid; cid+=1
    f=glob.glob(f"data/claims/*/{c['u']}.csv")[0]; byfile.setdefault(f,[]).append(c)
for path,lst in byfile.items():
    rd=list(csv.DictReader(open(path,newline=''))); hdr=list(rd[0].keys()); tmpl=rd[0]
    for c in lst:
        p=places[c['pl']]; n=dict(tmpl)
        for k in n:
            if k not in('unit_id','theater','nationality','unit_name','echelon','branch'): n[k]=''
        notes=(f"Event date: {c['dtxt']} (FMS B-101 (Hitzfeld), English translation only, {c['loc'][6:]}). Event definition: {c['defn']} Event support: one source family (FMS, German postwar manuscripts; English translation only, no German original). "
               f"Location: {p['name']} (place {c['pl']}) with a precision of {c['prec']} km. Location support: {c['lsup']}. "+REV.format(c=c['conf'])+(' '+c['ctx'] if c['ctx'] else ''))
        n.update(claim_id=c['id'],conflict_group_id=c['grp'],claim_status='preferred',date=c['date'],commander=c['cmd'],latitude=p['latitude'],longitude=p['longitude'],place_id=c['pl'],location_represents=c['rep'],precision_km=str(c['prec']),operation_id=c['op'],composing_units='unknown',established='false',disestablished='false',destroyed='false',confidence=c['conf'],source=f"{URL} | {NOM}",reference_ids=f'{REF};R002',source_locator=c['loc'],event_type=c['ev'],current_activity=c['act'],notes=notes,location_date=c['date'],location_basis=c['basis'])
        rd.append(n)
    rd.sort(key=lambda r:r['date'])
    out=io.StringIO(); w=csv.DictWriter(out,fieldnames=hdr,lineterminator='\n'); w.writeheader(); w.writerows(rd); open(path,'w',newline='').write(out.getvalue())
print('last id',cid-1, 'count',len(C))
corr={
'C1160':(L(29),'at about 0100 on 7 March the Fifteenth Army subordinates the Remagen bridgehead to LXVII Corps while the corps attack order stays in force'),
'C1169':('R834: English pp.52-53 (Fold3 pages 119-120)','from 12 March the 272nd Division holds the right wing of the corps Rhine front near Leubsdorf and fights the extension of the Remagen bridgehead from 13 March'),
'C1167':('R834: English pp.52-53 (Fold3 pages 119-120)','the 26th Volksgrenadier Division returns from the Bonn area and is committed on the east bank to the left of the 272nd Division against the Remagen bridgehead'),
}
for f in glob.glob('data/claims/*/*.csv'):
    rd=list(csv.DictReader(open(f,newline=''))); ch=False
    for r in rd:
        if r['claim_id'] in corr:
            lc,why=corr[r['claim_id']]; oldr,olds=r['reference_ids'],r['source_locator']
            refs=oldr.split(';'); i=refs.index('R002') if 'R002' in refs else (refs.index('R001') if 'R001' in refs else len(refs)); refs.insert(i,REF); r['reference_ids']=';'.join(refs)
            r['source_locator']=(olds+'; ' if olds else '')+lc
            s=r['source'].split(' | ')
            if URL not in s: s.append(URL)
            r['source']=' | '.join(s)
            r['notes']+=f" [FMS B-101 corroboration (branch fms-fold3-german-2, {DAY}): reference_ids old value {oldr}, new value {r['reference_ids']}; source_locator old value {olds}, new value {r['source_locator']}; reason: {lc[6:]}, agrees: {why}. Confidence is unchanged at {r["confidence"]}; reason: FMS is one source family.]"
            ch=True
    if ch:
        hdr=list(rd[0].keys()); out=io.StringIO(); w=csv.DictWriter(out,fieldnames=hdr,lineterminator='\n'); w.writeheader(); w.writerows(rd); open(f,'w',newline='').write(out.getvalue())
