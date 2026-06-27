# -*- coding: utf-8 -*-
# PART2 예측 모형 (누수제거): 설명변수(워치) + 과거 BP '추정' lag. 과거 BP는 실측이 아니라 추정치 Ê(=수준커널+워치모델, day1+워치만 사용).
# 보간데이터=학습 타깃·일주기. 평가=day7 실측. 신규환자 시나리오(day1만 실측). session·일평균 MAE+BHS.
import pandas as pd, numpy as np, sys, warnings
warnings.filterwarnings('ignore')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor
import xgboost as xgb
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
def estimate(p,tg,tt,tph):  # E0 = 수준커널 (day1 + Lext + 일주기). 실측 day2-6 미사용
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
# 워치로 day1대비 편차 모델 → Ê = E0 + 편차̂ (train day2-6에서 적합, 모든 사람·일에 적용; 실측 day2-6 미사용)
imp0=SimpleImputer(strategy='median').fit(F.loc[(F.split=='train')&(F.role=='train'),WF].values); WFv=imp0.transform(F[WF].values)
F[WF]=WFv; mtr=((F.split=='train')&(F.role=='train')).values
dS=ExtraTreesRegressor(n_estimators=300,min_samples_leaf=20,n_jobs=6,random_state=0).fit(WFv[mtr],(F.SBP-F.e0S).values[mtr])
dD=ExtraTreesRegressor(n_estimators=300,min_samples_leaf=20,n_jobs=6,random_state=0).fit(WFv[mtr],(F.DBP-F.e0D).values[mtr])
F['ehatS']=F.e0S.values+dS.predict(WFv); F['ehatD']=F.e0D.values+dD.predict(WFv)
def build(mask):
    rows=[];yS=[];yD=[];idx=[]
    for p,s in F.groupby('ID',sort=False):
        do=s.dord.values; td=s.tod.values.astype(float); ehS=s.ehatS.values; ehD=s.ehatD.values; e0s=s.e0S.values; e0d=s.e0D.values
        wv=s[WF].values; sb=s.SBP.values; db=s.DBP.values; tm=mask.loc[s.index].values; si=s.index.values
        for k in range(len(s)):
            if not tm[k]: continue
            d=do[k]; phi=td[k]; past=np.where(do<d)[0]
            if len(past)==0: continue
            pmS=ehS[past].mean(); pmD=ehD[past].mean(); cm=circ(td[past],phi); near=past[cm<=120]
            ptS=ehS[near].mean() if len(near) else pmS; ptD=ehD[near].mean() if len(near) else pmD
            rd=do[past].max(); ld=past[do[past]==rd]; j=ld[np.argmin(circ(td[ld],phi))]
            rows.append([e0s[k],e0d[k],ehS[k],ehD[k],pmS,pmD,ptS,ptD,ehS[j],ehD[j],*wv[k]]); yS.append(sb[k]); yD.append(db[k]); idx.append(si[k])
    cols=['e0S','e0D','ehatS','ehatD','pmeanS','pmeanD','ptypS','ptypD','lag1S','lag1D']+WF
    return pd.DataFrame(rows,columns=cols),np.array(yS),np.array(yD),np.array(idx)
Xtr,ytrS,ytrD,_=build(((F.split=='train')&(F.role=='train')))   # 학습 = train 사람, day2-6
SETS={}
for sp in ['train','valid','test']:
    X,yS,yD,idx=build(((F.split==sp)&(F.role=='forecast'))); SETS[sp]=(X,yS,yD,F.loc[idx])
def bhs(e): e=np.abs(np.asarray(e)); return 100*np.mean(e<=5),100*np.mean(e<=10),100*np.mean(e<=15)
def gr(b): return 'A' if b[0]>=60 and b[1]>=85 and b[2]>=95 else 'B' if b[0]>=50 and b[1]>=75 and b[2]>=90 else 'C' if b[0]>=40 and b[1]>=65 and b[2]>=85 else 'D'
def daily(Fsub,pr,tg): a=Fsub.assign(pr=pr).groupby('ID').agg(ac=(('SBP' if tg=='S' else 'DBP'),'mean'),pd=('pr','mean')); return np.abs(a.ac-a.pd).values
def cell(e): e=np.abs(np.asarray(e)); return f"{e.mean():.2f}{gr(bhs(e))}"
Xtr2=Xtr.values
mS=make_pipeline(StandardScaler(),Ridge(alpha=10)).fit(Xtr2,ytrS); mD=make_pipeline(StandardScaler(),Ridge(alpha=10)).fit(Xtr2,ytrD)
eS=ExtraTreesRegressor(n_estimators=400,min_samples_leaf=15,n_jobs=6,random_state=0).fit(Xtr2,ytrS); eD=ExtraTreesRegressor(n_estimators=400,min_samples_leaf=15,n_jobs=6,random_state=0).fit(Xtr2,ytrD)
xS=xgb.XGBRegressor(n_estimators=400,max_depth=3,learning_rate=.03,min_child_weight=15,subsample=.8,colsample_bytree=.7,reg_lambda=1,n_jobs=6,random_state=0,verbosity=0).fit(Xtr2,ytrS); xD=xgb.XGBRegressor(n_estimators=400,max_depth=3,learning_rate=.03,min_child_weight=15,subsample=.8,colsample_bytree=.7,reg_lambda=1,n_jobs=6,random_state=0,verbosity=0).fit(Xtr2,ytrD)
MODELS=[('구조 추정치 E0',lambda X:(X.e0S.values,X.e0D.values)),
        ('Ê=E0+워치편차',lambda X:(X.ehatS.values,X.ehatD.values)),
        ('회귀 Ridge(전특징)',lambda X:(mS.predict(X.values),mD.predict(X.values))),
        ('트리 ExtraTrees',lambda X:(eS.predict(X.values),eD.predict(X.values))),
        ('GBM XGBoost',lambda X:(xS.predict(X.values),xD.predict(X.values)))]
print("PART2 예측 모형 (누수제거: 과거 BP=추정치 Ê). MAE+BHS. 평가=각 split day7 실측\n")
for sp in ['train','valid','test']:
    X,yS,yD,Fsub=SETS[sp]
    print(f"[{sp}]  N={Fsub.ID.nunique()}명 / {len(yS)}세션 (day7)")
    print(f"{'모형':22s}{'세션SBP':>9s}{'세션DBP':>9s}{'일SBP':>8s}{'일DBP':>8s}")
    for name,fn in MODELS:
        prS,prD=fn(X)
        print(f"{name:22s}{cell(prS-yS):>9s}{cell(prD-yD):>9s}{cell(daily(Fsub,prS,'S')):>8s}{cell(daily(Fsub,prD,'D')):>8s}")
    print()
print("* 과거 BP=추정치 Ê(전날 동시각·과거일 동시각평균·과거일 평균), 실측 day2-6 미사용. 학습=train 사람 day2-6. 셀=MAE+BHS등급")
def trip(e): e=np.abs(np.asarray(e)); return f"{100*np.mean(e<=5):3.0f} /{100*np.mean(e<=10):4.0f} /{100*np.mean(e<=15):4.0f}"
print("\n[test] BHS 누적% (≤5 / ≤10 / ≤15)  등급기준 A:60/85/95  B:50/75/90  C:40/65/85")
X,yS,yD,Fsub=SETS['test']; md=dict(MODELS)
for name in ['구조 추정치 E0','Ê=E0+워치편차','회귀 Ridge(전특징)']:
    prS,prD=md[name](X)
    print(f"{name}")
    print(f"   세션 SBP  {trip(prS-yS)}  {gr(bhs(prS-yS))}   |  세션 DBP  {trip(prD-yD)}  {gr(bhs(prD-yD))}")
    print(f"   일  SBP  {trip(daily(Fsub,prS,'S'))}  {gr(bhs(daily(Fsub,prS,'S')))}   |  일  DBP  {trip(daily(Fsub,prD,'D'))}  {gr(bhs(daily(Fsub,prD,'D')))}")
print("DONE")
