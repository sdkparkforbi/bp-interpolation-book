# -*- coding: utf-8 -*-
# 편차(residual) 모델 ablation: 와치 / 지난BP추정 / 둘다 / 없음(E0). Ridge로 각 그룹의 편차축소 기여 검증. valid·test, MAE+BHS.
import pickle, numpy as np, pandas as pd, warnings, sys
warnings.filterwarnings('ignore')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge
SP=['valid','test']
D=pickle.load(open('_part2_feats.pkl','rb')); cols=D['cols']; Xtr=D['Xtr']; yS=D['ytrS']; yD=D['ytrD']; sets=D['sets']
iS=cols.index('e0S'); iD=cols.index('e0D')
PAST=[cols.index(c) for c in ['pmeanS','pmeanD','ptypS','ptypD','lag1S','lag1D']]
WCH=[cols.index(c) for c in ['HR','kwHR','dHR','HRV','WT','active','sleep','METs']]
rS=yS-Xtr[:,iS]; rD=yD-Xtr[:,iD]
E0={sp:(sets[sp]['X'][:,iS],sets[sp]['X'][:,iD]) for sp in SP}
ACT={sp:(sets[sp]['yS'],sets[sp]['yD'],sets[sp]['ID']) for sp in SP}
def bhs(e): e=np.abs(e); return 100*np.mean(e<=5),100*np.mean(e<=10),100*np.mean(e<=15)
def gr(b): return 'A' if b[0]>=60 and b[1]>=85 and b[2]>=95 else 'B' if b[0]>=50 and b[1]>=75 and b[2]>=90 else 'C' if b[0]>=40 and b[1]>=65 and b[2]>=85 else 'D'
def cell(e): e=np.abs(np.asarray(e)); return f'{e.mean():.2f}{gr(bhs(e))}'
def daily(pr,y,ID): a=pd.DataFrame({'ID':ID,'pr':pr,'y':y}).groupby('ID').mean(); return (a.pr-a.y).values
def fitpred(idx):
    if idx is None: return {sp:(E0[sp][0],E0[sp][1]) for sp in SP}
    mk=lambda:make_pipeline(StandardScaler(),Ridge(alpha=10)); mS=mk().fit(Xtr[:,idx],rS); mD=mk().fit(Xtr[:,idx],rD)
    return {sp:(E0[sp][0]+mS.predict(sets[sp]['X'][:,idx]),E0[sp][1]+mD.predict(sets[sp]['X'][:,idx])) for sp in SP}
CASES=[('없음 (E0만, 편차모델 X)',None),('와치만',WCH),('지난BP추정만',PAST),('둘다 (와치+지난추정)',PAST+WCH)]
for sp in SP:
    yS_,yD_,ID_=ACT[sp]
    print(f'\n[{sp}] {pd.Series(ID_).nunique()}명/{len(yS_)}세션   세SBP   세DBP   일SBP   일DBP')
    for nm,idx in CASES:
        pr=fitpred(idx); prS,prD=pr[sp]
        print(f'  {nm:22s}{cell(prS-yS_):>7s}{cell(prD-yD_):>7s}{cell(daily(prS,yS_,ID_)):>7s}{cell(daily(prD,yD_,ID_)):>7s}')
print('\n* E0=수준+위상 고정. 편차=실측-E0. 각 그룹 Ridge로 편차 적합 후 E0+r̂. DONE')
