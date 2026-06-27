# -*- coding: utf-8 -*-
# PART2 공유 특징행렬 빌더 (누수-free). zoo·LLM·앙상블이 재사용. 저장: _part2_feats.pkl
import pandas as pd, numpy as np, sys, warnings, pickle
warnings.filterwarnings('ignore')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesRegressor
TAU=1440.0; ELL=196.0; KAPPA=5.0
F=pd.read_pickle('_feat_estimation_sess.pkl')
dt=pd.to_datetime(F['t']*60,unit='s',utc=True).dt.tz_convert('Asia/Seoul'); F['day']=dt.dt.strftime('%Y-%m-%d')
lev=pd.read_csv('_stage1_levels_external.csv').set_index('ID')
g=pd.read_csv('train_model_data.csv',encoding='cp949').groupby('ID').first(); age=pd.to_numeric(g['Age'],errors='coerce'); male=(g['Gender']==1); amed=age.median()
ids=[p for p in sorted(F.ID.unique()) if p in lev.index]; cl={p:(0 if age.get(p,amed)<=amed else 2)+(0 if male.get(p,True) else 1) for p in ids}
F=F[F.ID.isin(ids)].sort_values(['ID','t']); F['cl']=F.ID.map(cl)
F['dord']=F.groupby('ID')['day'].transform(lambda s: pd.factorize(s)[0]+1)
F['role']=np.where(F.dord==1,'tune',np.where(F.dord==7,'forecast',np.where(F.dord.between(2,6),'train','extra')))
uu=np.array(ids); np.random.RandomState(0).shuffle(uu); a=int(len(uu)*.6); b=int(len(uu)*.8)
spl={p:('train' if i<a else 'valid' if i<b else 'test') for i,p in enumerate(uu)}; F['split']=F.ID.map(spl)
F['AGE']=F.ID.map(age).astype(float); F['MALE']=F.ID.map(male).astype(float)
F['HR']=pd.to_numeric(F['last_심박수'],errors='coerce'); F['kwHR']=pd.to_numeric(F['kw_심박수'],errors='coerce')
F['HR_rest']=F.groupby('ID')['HR'].transform(lambda x:x.quantile(.1)); F['dHR']=F['HR']-F['HR_rest']
F['METs']=pd.to_numeric(F['last_절대적 운동 강도'],errors='coerce'); F['steps']=pd.to_numeric(F['last_걸음'],errors='coerce')
F['HRV']=pd.to_numeric(F[next(c for c in F if c.startswith('last_') and '심박 변이' in c)],errors='coerce'); F['WT']=pd.to_numeric(F[next(c for c in F if c.startswith('last_') and '손목 온도' in c)],errors='coerce')
night=(F.tod<360)|(F.tod>=1320); F['active']=((F.METs>=3)|(F.steps>=300)).astype(int); F['sleep']=((night)&(F.active==0)).astype(int)
WF=['HR','kwHR','dHR','HRV','WT','active','sleep','METs']
def circ(a,b): d=np.abs(a-b); return np.minimum(d,1440-d)
GRID=np.arange(0,1440,30.0)
def phase_curve(tg):
    src=F[(F.split=='train')&(F.role=='train')]; C={}
    for c in range(4):
        s=src[src.cl==c]; s=s if len(s)>=20 else src; pm=s.groupby('ID')[tg].transform('mean'); ph=s.tod.values; dv=(s[tg]-pm).values
        C[c]=np.array([np.sum(np.exp(-circ(ph,gg)**2/(2*ELL**2))*dv)/max(np.sum(np.exp(-circ(ph,gg)**2/(2*ELL**2))),1e-9) for gg in GRID])
    return C
Sc={'SBP':phase_curve('SBP'),'DBP':phase_curve('DBP')}
def look(C,phi): return C[(np.round(np.asarray(phi,float)/30).astype(int))%len(GRID)]
PED={}
for p in ids:
    s=F[F.ID==p]; c1=s[s.role=='tune']
    PED[p]=dict(cph=c1.tod.values.astype(float),ct=c1['t'].values.astype(float),c1S=c1.SBP.values,c1D=c1.DBP.values,cmS=c1.SBP.mean(),cmD=c1.DBP.mean(),LS=lev.loc[p,'Lext_S'],LD=lev.loc[p,'Lext_D'],cl=cl[p])
def estimate(p,tg,tt,tph):
    d=PED[p]; n=len(d['ct']); cm=d['cmS'] if tg=='S' else d['cmD']; L=d['LS'] if tg=='S' else d['LD']; lvl=(n*cm+2.0*L)/(n+2.0)
    cdev=(d['c1S'] if tg=='S' else d['c1D'])-cm; sc=look(Sc['SBP' if tg=='S' else 'DBP'][d['cl']],tph); o=np.empty(len(tt))
    for k in range(len(tt)):
        w=np.exp(-np.abs(tt[k]-d['ct'])/TAU)*np.exp(-circ(d['cph'],tph[k])**2/(2*ELL**2)); Wc=w.sum(); dc=np.sum(w*cdev)/Wc if Wc>0 else 0; al=Wc/(Wc+KAPPA); o[k]=lvl+al*dc+(1-al)*sc[k]
    return o
F=F.sort_values(['ID','dord','t']).reset_index(drop=True)
e0S=np.empty(len(F)); e0D=np.empty(len(F)); i=0
for p,s in F.groupby('ID',sort=False):
    e0S[i:i+len(s)]=estimate(p,'S',s['t'].values.astype(float),s.tod.values.astype(float)); e0D[i:i+len(s)]=estimate(p,'D',s['t'].values.astype(float),s.tod.values.astype(float)); i+=len(s)
F['e0S']=e0S; F['e0D']=e0D
imp0=SimpleImputer(strategy='median').fit(F.loc[(F.split=='train')&(F.role=='train'),WF].values); WFv=imp0.transform(F[WF].values); F[WF]=WFv
mtr=((F.split=='train')&(F.role=='train')).values
dS=ExtraTreesRegressor(n_estimators=300,min_samples_leaf=20,n_jobs=6,random_state=0).fit(WFv[mtr],(F.SBP-F.e0S).values[mtr])
dD=ExtraTreesRegressor(n_estimators=300,min_samples_leaf=20,n_jobs=6,random_state=0).fit(WFv[mtr],(F.DBP-F.e0D).values[mtr])
F['ehatS']=F.e0S.values+dS.predict(WFv); F['ehatD']=F.e0D.values+dD.predict(WFv)
EXTRA=['AGE','MALE','tod','cmS','cmD','LS','LD']  # LLM 프롬프트용 가독 컨텍스트
for c,src in [('cmS','cmS'),('cmD','cmD'),('LS','LS'),('LD','LD')]:
    F[c]=F.ID.map({p:PED[p][src] for p in ids})
def build(mask):
    rows=[];meta=[]
    for p,s in F.groupby('ID',sort=False):
        do=s.dord.values; td=s.tod.values.astype(float); ehS=s.ehatS.values; ehD=s.ehatD.values; e0s=s.e0S.values; e0d=s.e0D.values
        wv=s[WF].values; sb=s.SBP.values; db=s.DBP.values; tm=mask.loc[s.index].values; ex=s[EXTRA].values
        for k in range(len(s)):
            if not tm[k]: continue
            d=do[k]; phi=td[k]; past=np.where(do<d)[0]
            if len(past)==0: continue
            pmS=ehS[past].mean(); pmD=ehD[past].mean(); cm=circ(td[past],phi); near=past[cm<=120]
            ptS=ehS[near].mean() if len(near) else pmS; ptD=ehD[near].mean() if len(near) else pmD
            rd=do[past].max(); ld=past[do[past]==rd]; j=ld[np.argmin(circ(td[ld],phi))]
            rows.append([e0s[k],e0d[k],ehS[k],ehD[k],pmS,pmD,ptS,ptD,ehS[j],ehD[j],*wv[k]])
            meta.append([p,int(d),float(phi),sb[k],db[k],*ex[k]])
    cols=['e0S','e0D','ehatS','ehatD','pmeanS','pmeanD','ptypS','ptypD','lag1S','lag1D']+WF
    mcols=['ID','dord','tod','SBP','DBP']+EXTRA
    return pd.DataFrame(rows,columns=cols),pd.DataFrame(meta,columns=mcols)
# PART2 = 추정, days2-6만 (role=='train'). day7(forecast)은 PART3 예측 전용 — 절대 미사용.
Xtr,Mtr=build(((F.split=='train')&(F.role=='train')))   # 학습 = train 사람 days2-6
out={'cols':list(Xtr.columns),'WF':WF,'Xtr':Xtr.values,'ytrS':Mtr.SBP.values,'ytrD':Mtr.DBP.values,'Mtr':Mtr,'sets':{}}
for sp in ['train','valid','test']:
    X,M=build(((F.split==sp)&(F.role=='train')))   # 평가도 days2-6 (held-out 사람), day7 제외
    out['sets'][sp]={'X':X.values,'Xdf':X,'M':M,'yS':M.SBP.values,'yD':M.DBP.values,'ID':M.ID.values}
    print(f"{sp}: N={M.ID.nunique()}명 {len(M)}세션 (days2-6)")
out['day7']={}   # PART3 예측 전용 (role=='forecast'). PART2는 이걸 쓰지 않음.
for sp in ['train','valid','test']:
    X,M=build(((F.split==sp)&(F.role=='forecast')))
    out['day7'][sp]={'X':X.values,'M':M,'yS':M.SBP.values,'yD':M.DBP.values,'ID':M.ID.values}
    print(f"{sp} day7: N={M.ID.nunique()}명 {len(M)}세션")
pickle.dump(out,open('_part2_feats.pkl','wb'))
print("cols:",out['cols']); print("saved _part2_feats.pkl"); print("DONE")
