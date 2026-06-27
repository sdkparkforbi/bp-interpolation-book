# -*- coding: utf-8 -*-
# PART2 그림: (1) 20모형 valid MAE 비교(계열색), (2) train vs valid 과적합 산점, (3) 편차 ablation(없음/와치/지난추정/둘다).
import pickle, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in ['Malgun Gothic','Apple SD Gothic Neo','NanumGothic']:
    if any(f in x.name for x in fm.fontManager.ttflist): plt.rcParams['font.family']=f; break
plt.rcParams['axes.unicode_minus']=False
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge
OUT='C:/Temp/HYPT/'
P=pickle.load(open('_part2_preds.pkl','rb')); PRED=P['PRED']; ACT=P['ACT']
def mae(e): return float(np.mean(np.abs(e)))
def daily(pr,y,ID): a=pd.DataFrame({'ID':ID,'pr':pr,'y':y}).groupby('ID').mean(); return np.abs(a.pr-a.y).values
FAM={'수준+커널 E0':'기준','Ê=E0+워치편차(ET)':'기준','회귀 Ridge':'회귀','회귀 Lasso':'회귀','회귀 ElasticNet':'회귀','회귀 MultiTaskElasticNet':'회귀',
 '스펙트럴 Harmonic+Ridge':'스펙트럴','스펙트럴 Harmonic+MTEN':'스펙트럴','웨이블릿 Wavelet+Ridge':'웨이블릿','웨이블릿 Wavelet+MTEN':'웨이블릿',
 '트리 RandomForest':'트리','트리 ExtraTrees':'트리','트리 ExtraTrees(multi)':'트리','GBM XGBoost':'GBM','GBM LightGBM':'GBM','GBM CatBoost':'GBM',
 'GBM XGBoost(multi)':'GBM','GBM CatBoost(multi)':'GBM','딥러닝 MLP':'딥러닝','딥러닝 MLP(multi)':'딥러닝'}
COL={'기준':'#7f8c9b','회귀':'#1e7d4f','스펙트럴':'#16a085','웨이블릿':'#2471a3','트리':'#e08e0b','GBM':'#c0392b','딥러닝':'#6c5ce7'}
def perf(sp):
    yS,yD,ID=ACT[sp]; R={}
    for nm,pr in PRED.items():
        prS,prD=pr[sp]; R[nm]=dict(sS=mae(prS-yS),sD=mae(prD-yD),dS=mae(daily(prS,yS,ID)),dD=mae(daily(prD,yD,ID)))
    return R
Rv=perf('valid'); Rt=perf('test'); Rtr=perf('train')
# ---- (1) 20모형 valid 세션 SBP + 일DBP ----
names=list(PRED.keys()); names_sorted=sorted(names,key=lambda n:Rv[n]['sS'])
fig,axes=plt.subplots(1,2,figsize=(13.5,7.6));
for ax,key,ttl in [(axes[0],'sS','검증 세션 SBP MAE'),(axes[1],'dD','검증 일평균 DBP MAE')]:
    od=sorted(names,key=lambda n:Rv[n][key]); y=np.arange(len(od))
    ax.barh(y,[Rv[n][key] for n in od],color=[COL[FAM[n]] for n in od],edgecolor='white')
    ax.set_yticks(y); ax.set_yticklabels(od,fontsize=8.5); ax.invert_yaxis()
    for i,n in enumerate(od): ax.text(Rv[n][key]+.02,i,f"{Rv[n][key]:.2f}",va='center',fontsize=7.5)
    ax.set_xlabel('MAE (mmHg, 낮을수록 우수)'); ax.set_title(ttl,fontweight='bold')
    ax.axvline(Rv['수준+커널 E0'][key],color='#555',ls='--',lw=1)
from matplotlib.patches import Patch
axes[1].legend(handles=[Patch(color=c,label=k) for k,c in COL.items()],fontsize=8,loc='lower right')
fig.suptitle('PART2 추정 — 20모형 비교 (검증 24명·596세션, days2-6)  · 선형·스펙트럴이 일반화 챔피언',fontweight='bold',fontsize=13)
fig.tight_layout(rect=[0,0,1,.97]); fig.savefig(OUT+'fig_p2_zoo.png',dpi=125); plt.close(fig)
# ---- (2) train vs valid 과적합 산점 (세션 SBP) ----
fig,ax=plt.subplots(figsize=(7.8,7.2))
for n in names:
    ax.scatter(Rtr[n]['sS'],Rv[n]['sS'],s=70,color=COL[FAM[n]],edgecolor='white',zorder=3)
lo,hi=3.8,7.4; ax.plot([lo,hi],[lo,hi],'--',color='#888',lw=1.2,label='y=x (격차 없음)')
for n in ['GBM LightGBM','GBM XGBoost','트리 RandomForest','회귀 Ridge','스펙트럴 Harmonic+Ridge','딥러닝 MLP','수준+커널 E0']:
    ax.annotate(n.replace('GBM ','').replace('회귀 ','').replace('스펙트럴 ','').replace('트리 ','').replace('딥러닝 ',''),
                (Rtr[n]['sS'],Rv[n]['sS']),fontsize=8,xytext=(5,4),textcoords='offset points')
ax.set_xlabel('학습(train·in-sample) 세션 SBP MAE'); ax.set_ylabel('검증(valid·held-out) 세션 SBP MAE')
ax.set_title('과적합 진단 — 학습 vs 검증\n대각선 아래로 멀수록 overfit(학습만 외움)',fontweight='bold')
ax.legend(handles=[Patch(color=c,label=k) for k,c in COL.items()]+[plt.Line2D([0],[0],ls='--',color='#888',label='y=x')],fontsize=8.5,loc='upper left')
ax.set_xlim(lo,hi); ax.set_ylim(5.8,7.3); fig.tight_layout(); fig.savefig(OUT+'fig_p2_overfit.png',dpi=125); plt.close(fig)
# ---- (3) 편차 ablation ----
D=pickle.load(open('_part2_feats.pkl','rb')); cols=D['cols']; Xtr=D['Xtr']; yS=D['ytrS']; yD=D['ytrD']; sets=D['sets']
iS=cols.index('e0S'); iD=cols.index('e0D')
PAST=[cols.index(c) for c in ['pmeanS','pmeanD','ptypS','ptypD','lag1S','lag1D']]; WCH=[cols.index(c) for c in ['HR','kwHR','dHR','HRV','WT','active','sleep','METs']]
rS=yS-Xtr[:,iS]; rD=yD-Xtr[:,iD]
def fp(idx,sp):
    e0S,e0D=sets[sp]['X'][:,iS],sets[sp]['X'][:,iD]
    if idx is None: return e0S,e0D
    mk=lambda:make_pipeline(StandardScaler(),Ridge(alpha=10)); mS=mk().fit(Xtr[:,idx],rS); mD=mk().fit(Xtr[:,idx],rD)
    return e0S+mS.predict(sets[sp]['X'][:,idx]), e0D+mD.predict(sets[sp]['X'][:,idx])
CASES=[('없음\n(E0=수준+위상)',None),('+와치만',WCH),('+지난BP추정만',PAST),('+둘다',PAST+WCH)]
yv,_,IDv=ACT['valid']; _,ydv,_=ACT['valid']
fig,axes=plt.subplots(1,2,figsize=(12.5,5.6))
mets=[('세션 DBP','sD'),('일평균 SBP','dS')]
for ax,(mt,kk) in zip(axes,mets):
    vals=[]
    for nm,idx in CASES:
        pS,pD=fp(idx,'valid'); ys,yd,ID=ACT['valid']
        if kk=='sD': vals.append(mae(pD-yd))
        else: vals.append(mae(daily(pS,ys,ID)))
    bars=ax.bar(range(4),vals,color=['#7f8c9b','#c0392b','#2471a3','#1e7d4f'],edgecolor='white')
    ax.set_xticks(range(4)); ax.set_xticklabels([c[0] for c in CASES],fontsize=9)
    for i,v in enumerate(vals): ax.text(i,v+.01,f"{v:.2f}",ha='center',fontsize=10,fontweight='bold')
    ax.set_ylabel('MAE (mmHg)'); ax.set_title(f'검증 {mt} — 편차 입력별',fontweight='bold'); ax.set_ylim(0,max(vals)*1.18)
fig.suptitle('편차(r=실측−E0) 축소 기여 — 와치·지난BP추정 둘 다, 상보적',fontweight='bold',fontsize=12.5)
fig.tight_layout(rect=[0,0,1,.95]); fig.savefig(OUT+'fig_p2_ablation.png',dpi=125); plt.close(fig)
print('SAVED fig_p2_zoo / fig_p2_overfit / fig_p2_ablation')
