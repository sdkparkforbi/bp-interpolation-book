# -*- coding: utf-8 -*-
# 웨이블릿 모형 추가 (residual). 연속 웨이블릿(Ricker) 다해상도 기저를 원형 tod에 + 워치/lag → 편차 회귀. _part2_preds.pkl에 append, 전체 표 출력.
import pickle, numpy as np, pandas as pd, warnings, sys
warnings.filterwarnings('ignore')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge, MultiTaskElasticNet
SP=['train','valid','test']
D=pickle.load(open('_part2_feats.pkl','rb')); cols=D['cols']; Xtr=D['Xtr']; yS=D['ytrS']; yD=D['ytrD']; sets=D['sets']
P=pickle.load(open('_part2_preds.pkl','rb')); PRED=P['PRED']; ACT=P['ACT']
iS=cols.index('e0S'); iD=cols.index('e0D')
rS=yS-Xtr[:,iS]; rD=yD-Xtr[:,iD]; rM=np.column_stack([rS,rD])
keep=[i for i,c in enumerate(cols) if c not in ('e0S','e0D','ehatS','ehatD')]
Xr=Xtr[:,keep]; SXr={sp:sets[sp]['X'][:,keep] for sp in SP}
E0={sp:(sets[sp]['X'][:,iS],sets[sp]['X'][:,iD]) for sp in SP}
def wav(M,scales=(45,90,180,360),ntrans=16):  # 원형 tod 위 Ricker 웨이블릿 frame
    tod=np.asarray(M['tod'],float); trans=np.linspace(0,1440,ntrans,endpoint=False); Fc=[]
    for s in scales:
        for tau in trans:
            d=np.abs(tod-tau); d=np.minimum(d,1440-d); x=d/float(s); Fc.append((1-x**2)*np.exp(-x**2/2))
    return np.column_stack(Fc)
Wtr=np.column_stack([Xr,wav(D['Mtr'])]); SWr={sp:np.column_stack([SXr[sp],wav(sets[sp]['M'])]) for sp in SP}
def single(name,mk):
    mS=mk().fit(Wtr,rS); mD=mk().fit(Wtr,rD); PRED[name]={sp:(E0[sp][0]+mS.predict(SWr[sp]),E0[sp][1]+mD.predict(SWr[sp])) for sp in SP}
def multi(name,mk):
    m=mk().fit(Wtr,rM); PRED[name]={sp:(E0[sp][0]+m.predict(SWr[sp])[:,0],E0[sp][1]+m.predict(SWr[sp])[:,1]) for sp in SP}
single('웨이블릿 Wavelet+Ridge',lambda:make_pipeline(StandardScaler(),Ridge(alpha=20)))
multi('웨이블릿 Wavelet+MTEN',lambda:make_pipeline(StandardScaler(),MultiTaskElasticNet(alpha=0.05,l1_ratio=.5)))
pickle.dump({'PRED':PRED,'ACT':ACT,'mode':'residual'},open('_part2_preds.pkl','wb'))
ORDER=['수준+커널 E0','Ê=E0+워치편차(ET)','회귀 Ridge','회귀 Lasso','회귀 ElasticNet','회귀 MultiTaskElasticNet',
 '스펙트럴 Harmonic+Ridge','스펙트럴 Harmonic+MTEN','웨이블릿 Wavelet+Ridge','웨이블릿 Wavelet+MTEN',
 '트리 RandomForest','트리 ExtraTrees','트리 ExtraTrees(multi)','GBM XGBoost','GBM LightGBM','GBM CatBoost',
 'GBM XGBoost(multi)','GBM CatBoost(multi)','딥러닝 MLP','딥러닝 MLP(multi)']
def bhs(e): e=np.abs(e); return 100*np.mean(e<=5),100*np.mean(e<=10),100*np.mean(e<=15)
def gr(b): return 'A' if b[0]>=60 and b[1]>=85 and b[2]>=95 else 'B' if b[0]>=50 and b[1]>=75 and b[2]>=90 else 'C' if b[0]>=40 and b[1]>=65 and b[2]>=85 else 'D'
def cell(e): e=np.abs(np.asarray(e)); return f'{e.mean():.2f}{gr(bhs(e))}'
def daily(pr,y,ID): a=pd.DataFrame({'ID':ID,'pr':pr,'y':y}).groupby('ID').mean(); return (a.pr-a.y).values
for sp in SP:
    yS_,yD_,ID_=ACT[sp]; tag='in-sample' if sp=='train' else 'held-out'
    print(f'\n===== [{sp}] {pd.Series(ID_).nunique()}명 / {len(yS_)}세션 ({tag}) =====')
    print(f"{'모형':26s}{'세SBP':>7s}{'세DBP':>7s}{'일SBP':>7s}{'일DBP':>7s}")
    for nm in ORDER:
        if nm not in PRED: continue
        prS,prD=PRED[nm][sp]; print(f'{nm:26s}{cell(prS-yS_):>7s}{cell(prD-yD_):>7s}{cell(daily(prS,yS_,ID_)):>7s}{cell(daily(prD,yD_,ID_)):>7s}')
print('\n웨이블릿 2종 추가·저장 완료  DONE')
