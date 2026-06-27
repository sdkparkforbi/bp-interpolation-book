# -*- coding: utf-8 -*-
# PART3 예측(day7). AR residual 모형: r(t)=BP(t)-E0(t) ~ f(prev_resid, dt, 워치(t), tod).
#  static(정적)= 1-step ahead, prev_resid=실측(매 스텝 재앵커).  dynamic(동적)= recursive rollout, prev_resid=예측값(굴림).
#  학습=days2-6, 평가=day7 실측. valid·test 각 24명. session·일평균 MAE+BHS.
import pandas as pd, numpy as np, sys, warnings, pickle
warnings.filterwarnings('ignore')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge
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
def estimate(p,tg,tt,tph):  # E0
    d=PED[p]; n=len(d['ct']); cm=d['cmS'] if tg=='S' else d['cmD']; L=d['LS'] if tg=='S' else d['LD']; lvl=(n*cm+2.0*L)/(n+2.0)
    cdev=(d['c1S'] if tg=='S' else d['c1D'])-cm; sc=look(Sc['SBP' if tg=='S' else 'DBP'][d['cl']],tph); o=np.empty(len(tt))
    for k in range(len(tt)):
        w=np.exp(-np.abs(tt[k]-d['ct'])/TAU)*np.exp(-circ(d['cph'],tph[k])**2/(2*ELL**2)); Wc=w.sum(); dc=np.sum(w*cdev)/Wc if Wc>0 else 0; al=Wc/(Wc+KAPPA); o[k]=lvl+al*dc+(1-al)*sc[k]
    return o
F=F.sort_values(['ID','t']).reset_index(drop=True)
e0S=np.empty(len(F)); e0D=np.empty(len(F)); i=0
for p,s in F.groupby('ID',sort=False):
    e0S[i:i+len(s)]=estimate(p,'S',s['t'].values.astype(float),s.tod.values.astype(float)); e0D[i:i+len(s)]=estimate(p,'D',s['t'].values.astype(float),s.tod.values.astype(float)); i+=len(s)
F['e0S']=e0S; F['e0D']=e0D
from sklearn.impute import SimpleImputer
imp=SimpleImputer(strategy='median').fit(F.loc[(F.split=='train')&(F.role=='train'),WF].values); F[WF]=imp.transform(F[WF].values)
F['rS']=F.SBP-F.e0S; F['rD']=F.DBP-F.e0D
F['sin']=np.sin(2*np.pi*F.tod/1440); F['cos']=np.cos(2*np.pi*F.tod/1440)
# 직전 세션(같은 사람) 실측 편차 + 시간차
F['prS']=F.groupby('ID')['rS'].shift(1); F['prD']=F.groupby('ID')['rD'].shift(1); F['pt']=F.groupby('ID')['t'].shift(1)
F['dtm']=(F['t']-F['pt']); F['decay']=np.exp(-F['dtm'].clip(lower=0)/720.0)
ARF=['prS','prD','dtm','decay','sin','cos']+WF
def fitter(kind):
    if kind=='Ridge': return make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),Ridge(alpha=10))
    return make_pipeline(SimpleImputer(strategy='median'),ExtraTreesRegressor(n_estimators=300,min_samples_leaf=20,n_jobs=6,random_state=0))
TR=F[(F.split=='train')&(F.role=='train')&F.prS.notna()]
def day7_eval(kind):
    mS=fitter(kind).fit(TR[ARF].values,TR.rS.values); mD=fitter(kind).fit(TR[ARF].values,TR.rD.values)
    out={}
    for sp in ['valid','test']:
        rows=[]
        for p,s in F[(F.split==sp)].groupby('ID',sort=False):
            past=s[s.dord<7].sort_values('t'); d7=s[s.dord==7].sort_values('t')
            if len(d7)==0 or len(past)==0: continue
            seedS=past.rS.values[-1]; seedD=past.rD.values[-1]; lastt=past['t'].values[-1]
            prS_s=seedS; prD_s=seedD; lt_s=lastt   # static 시드
            prS_d=seedS; prD_d=seedD; lt_d=lastt   # dynamic 시드
            for _,r in d7.iterrows():
                e0s=r.e0S; e0d=r.e0D; base=[r.sin,r.cos]+[r[w] for w in WF]
                # static: prev=실측 직전, dynamic: prev=예측 직전
                dt_s=r['t']-lt_s; dc_s=np.exp(-max(dt_s,0)/720.0)
                xs=np.array([[prS_s,prD_s,dt_s,dc_s]+base]); psS=e0s+mS.predict(xs)[0]; psD=e0d+mD.predict(xs)[0]
                dt_d=r['t']-lt_d; dc_d=np.exp(-max(dt_d,0)/720.0)
                xd=np.array([[prS_d,prD_d,dt_d,dc_d]+base]); pdS=e0s+mS.predict(xd)[0]; pdD=e0d+mD.predict(xd)[0]
                rows.append((p,r.tod,r['t'],e0s,e0d,r.SBP,r.DBP,psS,psD,pdS,pdD))
                # update: static=실측 편차, dynamic=예측 편차
                prS_s=r.SBP-e0s; prD_s=r.DBP-e0d; lt_s=r['t']
                prS_d=pdS-e0s; prD_d=pdD-e0d; lt_d=r['t']
        out[sp]=pd.DataFrame(rows,columns=['ID','tod','t','e0S','e0D','SBP','DBP','sS','sD','dS','dD'])
    return out
def bhs(e): e=np.abs(np.asarray(e)); return 100*np.mean(e<=5),100*np.mean(e<=10),100*np.mean(e<=15)
def gr(b): return 'A' if b[0]>=60 and b[1]>=85 and b[2]>=95 else 'B' if b[0]>=50 and b[1]>=75 and b[2]>=90 else 'C' if b[0]>=40 and b[1]>=65 and b[2]>=85 else 'D'
def cell(e): e=np.abs(np.asarray(e)); return f'{e.mean():.2f}{gr(bhs(e))}'
def dly(D,pr,y): a=D.assign(p=pr,a=y).groupby('ID').agg(p=('p','mean'),a=('a','mean')); return (a.p-a.a).values
RES={}
for kind in ['Ridge','ExtraTrees']: RES[kind]=day7_eval(kind)
print("PART3 예측(day7) — AR residual. static=1-step(실측 재앵커) / dynamic=rollout(예측 굴림)\n")
for sp in ['valid','test']:
    print(f"[{sp}] 24명 day7")
    print(f"{'모형·모드':22s}{'세션SBP':>8s}{'세션DBP':>8s}{'일SBP':>7s}{'일DBP':>7s}")
    for kind in ['Ridge','ExtraTrees']:
        D=RES[kind][sp]
        print(f"{kind+' static':22s}{cell(D.sS-D.SBP):>8s}{cell(D.sD-D.DBP):>8s}{cell(dly(D,D.sS,D.SBP)):>7s}{cell(dly(D,D.sD,D.DBP)):>7s}")
        print(f"{kind+' dynamic':22s}{cell(D.dS-D.SBP):>8s}{cell(D.dD-D.DBP):>8s}{cell(dly(D,D.dS,D.SBP)):>7s}{cell(dly(D,D.dD,D.DBP)):>7s}")
    print()
pickle.dump(RES,open('_part3_res.pkl','wb')); print("저장 _part3_res.pkl  DONE")
