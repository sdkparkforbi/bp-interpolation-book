# -*- coding: utf-8 -*-
# PART2 classical zoo (RESIDUAL mode): E0(수준+위상) 고정, target=편차 r=실측-E0, 최종=E0+r̂.
# 편차 모델 특징 = 워치(급성) + 과거추정 level lag(pmean/ptyp/lag1). 회귀·스펙트럴·트리·GBM·딥러닝 single+multi. 저장 _part2_preds.pkl.
import pandas as pd, numpy as np, sys, warnings, pickle
warnings.filterwarnings('ignore')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge, Lasso, ElasticNet, MultiTaskElasticNet
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.neural_network import MLPRegressor
import xgboost as xgb, lightgbm as lgb
from catboost import CatBoostRegressor
SP=['train','valid','test']
D=pickle.load(open('_part2_feats.pkl','rb')); cols=D['cols']; Xtr=D['Xtr']; yS=D['ytrS']; yD=D['ytrD']; sets=D['sets']
iS=cols.index('e0S'); iD=cols.index('e0D'); ih=cols.index('ehatS')
# residual target (train)
rS=yS-Xtr[:,iS]; rD=yD-Xtr[:,iD]; rM=np.column_stack([rS,rD])
# 편차 특징: e0·ehat 제외, pmean/ptyp/lag1 + 워치
keep=[i for i,c in enumerate(cols) if c not in ('e0S','e0D','ehatS','ehatD')]
Xr=Xtr[:,keep]; SXr={sp:sets[sp]['X'][:,keep] for sp in SP}
E0={sp:(sets[sp]['X'][:,iS],sets[sp]['X'][:,iD]) for sp in SP}   # 고정 level+phase
def harm(M):
    ph=2*np.pi*np.asarray(M['tod'],float)/1440.0; return np.column_stack([f(k*ph) for k in (1,2,3) for f in (np.sin,np.cos)])
XrH=np.column_stack([Xr,harm(D['Mtr'])]); SXrH={sp:np.column_stack([SXr[sp],harm(sets[sp]['M'])]) for sp in SP}
PRED={}
def single(name,mk,Xt=Xr,SXd=SXr):
    mS=mk().fit(Xt,rS); mD=mk().fit(Xt,rD); PRED[name]={sp:(E0[sp][0]+mS.predict(SXd[sp]),E0[sp][1]+mD.predict(SXd[sp])) for sp in SP}
def multi(name,mk,Xt=Xr,SXd=SXr):
    m=mk().fit(Xt,rM); PRED[name]={sp:(E0[sp][0]+m.predict(SXd[sp])[:,0],E0[sp][1]+m.predict(SXd[sp])[:,1]) for sp in SP}
PRED['수준+커널 E0']={sp:(E0[sp][0],E0[sp][1]) for sp in SP}
PRED['Ê=E0+워치편차(ET)']={sp:(sets[sp]['X'][:,ih],sets[sp]['X'][:,ih+1]) for sp in SP}
single('회귀 Ridge',lambda:make_pipeline(StandardScaler(),Ridge(alpha=10)))
single('회귀 Lasso',lambda:make_pipeline(StandardScaler(),Lasso(alpha=0.05)))
single('회귀 ElasticNet',lambda:make_pipeline(StandardScaler(),ElasticNet(alpha=0.05,l1_ratio=.5)))
multi('회귀 MultiTaskElasticNet',lambda:make_pipeline(StandardScaler(),MultiTaskElasticNet(alpha=0.05,l1_ratio=.5)))
single('스펙트럴 Harmonic+Ridge',lambda:make_pipeline(StandardScaler(),Ridge(alpha=10)),XrH,SXrH)
multi('스펙트럴 Harmonic+MTEN',lambda:make_pipeline(StandardScaler(),MultiTaskElasticNet(alpha=0.05,l1_ratio=.5)),XrH,SXrH)
single('트리 RandomForest',lambda:RandomForestRegressor(n_estimators=400,min_samples_leaf=15,n_jobs=6,random_state=0))
single('트리 ExtraTrees',lambda:ExtraTreesRegressor(n_estimators=400,min_samples_leaf=15,n_jobs=6,random_state=0))
multi('트리 ExtraTrees(multi)',lambda:ExtraTreesRegressor(n_estimators=400,min_samples_leaf=15,n_jobs=6,random_state=0))
xgk=dict(n_estimators=400,max_depth=3,learning_rate=.03,min_child_weight=15,subsample=.8,colsample_bytree=.7,reg_lambda=1,n_jobs=6,random_state=0,verbosity=0)
single('GBM XGBoost',lambda:xgb.XGBRegressor(**xgk))
single('GBM LightGBM',lambda:lgb.LGBMRegressor(n_estimators=400,num_leaves=15,learning_rate=.03,min_child_samples=20,subsample=.8,colsample_bytree=.7,reg_lambda=1,n_jobs=6,random_state=0,verbosity=-1))
single('GBM CatBoost',lambda:CatBoostRegressor(iterations=400,depth=3,learning_rate=.03,l2_leaf_reg=3,random_seed=0,verbose=0))
try: multi('GBM XGBoost(multi)',lambda:xgb.XGBRegressor(multi_strategy='multi_output_tree',**xgk))
except Exception as e: print('xgbmulti skip',e)
try: multi('GBM CatBoost(multi)',lambda:CatBoostRegressor(iterations=400,depth=3,learning_rate=.03,loss_function='MultiRMSE',random_seed=0,verbose=0))
except Exception as e: print('catmulti skip',e)
mlpk=dict(hidden_layer_sizes=(32,),alpha=3e-2,max_iter=800,random_state=0,early_stopping=True)
single('딥러닝 MLP',lambda:make_pipeline(StandardScaler(),MLPRegressor(**mlpk)))
multi('딥러닝 MLP(multi)',lambda:make_pipeline(StandardScaler(),MLPRegressor(**mlpk)))
def bhs(e): e=np.abs(np.asarray(e)); return 100*np.mean(e<=5),100*np.mean(e<=10),100*np.mean(e<=15)
def gr(b): return 'A' if b[0]>=60 and b[1]>=85 and b[2]>=95 else 'B' if b[0]>=50 and b[1]>=75 and b[2]>=90 else 'C' if b[0]>=40 and b[1]>=65 and b[2]>=85 else 'D'
def cell(e): e=np.abs(np.asarray(e)); return f"{e.mean():.2f}{gr(bhs(e))}"
def daily(pr,y,ID): df=pd.DataFrame({'ID':ID,'pr':pr,'y':y}); a=df.groupby('ID').mean(); return (a.pr-a.y).values
ACT={sp:(sets[sp]['yS'],sets[sp]['yD'],sets[sp]['ID']) for sp in SP}
pickle.dump({'PRED':PRED,'ACT':ACT,'mode':'residual'},open('_part2_preds.pkl','wb'))
for sp in SP:
    yS_,yD_,ID_=ACT[sp]
    print(f"\n[{sp}]  N={pd.Series(ID_).nunique()}명 / {len(yS_)}세션")
    print(f"{'모형':26s}{'세션SBP':>8s}{'세션DBP':>8s}{'일SBP':>7s}{'일DBP':>7s}")
    for nm,pr in PRED.items():
        prS,prD=pr[sp]; print(f"{nm:26s}{cell(prS-yS_):>8s}{cell(prD-yD_):>8s}{cell(daily(prS,yS_,ID_)):>7s}{cell(daily(prD,yD_,ID_)):>7s}")
print("\nRESIDUAL mode (E0 고정, 편차만 모델). 저장 _part2_preds.pkl  DONE")
