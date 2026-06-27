# -*- coding: utf-8 -*-
# PART3 그림: (1) static vs dynamic MAE 비교, (2) 한 환자 day7 SBP 궤적(정적=1-step 밀착 / 동적=rollout 누적).
import pickle, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in ['Malgun Gothic','Apple SD Gothic Neo','NanumGothic']:
    if any(f in x.name for x in fm.fontManager.ttflist): plt.rcParams['font.family']=f; break
plt.rcParams['axes.unicode_minus']=False
OUT='C:/Temp/HYPT/'
RES=pickle.load(open('_part3_res.pkl','rb'))
def mae(e): return float(np.mean(np.abs(e)))
def dly(D,pr,y): a=D.assign(p=pr,a=y).groupby('ID').agg(p=('p','mean'),a=('a','mean')); return np.abs(a.p-a.a).values
# ---- (1) static vs dynamic ----
fig,axes=plt.subplots(1,2,figsize=(12.5,5.4))
mets=['세션 SBP','세션 DBP','일평균 SBP','일평균 DBP']
for ax,sp in zip(axes,['valid','test']):
    D=RES['Ridge'][sp]
    st=[mae(D.sS-D.SBP),mae(D.sD-D.DBP),mae(dly(D,D.sS,D.SBP)),mae(dly(D,D.sD,D.DBP))]
    dy=[mae(D.dS-D.SBP),mae(D.dD-D.DBP),mae(dly(D,D.dS,D.SBP)),mae(dly(D,D.dD,D.DBP))]
    x=np.arange(4); w=.38
    ax.bar(x-w/2,st,w,color='#1d9e75',label='정적 static (1-step 재앵커)',edgecolor='white')
    ax.bar(x+w/2,dy,w,color='#d85a30',label='동적 dynamic (rollout)',edgecolor='white')
    for i in range(4):
        ax.text(i-w/2,st[i]+.04,f"{st[i]:.2f}",ha='center',fontsize=9,fontweight='bold')
        ax.text(i+w/2,dy[i]+.04,f"{dy[i]:.2f}",ha='center',fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(mets,fontsize=9.5); ax.set_ylabel('MAE (mmHg)')
    ax.set_title(f'[{sp}] day7 예측 (Ridge)',fontweight='bold'); ax.set_ylim(0,max(dy)*1.2); ax.legend(fontsize=9,loc='upper right')
fig.suptitle('PART3 예측 — 정적(1-step) vs 동적(rollout). 매 스텝 실측 재앵커가 오차 누적을 막는다',fontweight='bold',fontsize=12.5)
fig.tight_layout(rect=[0,0,1,.95]); fig.savefig(OUT+'fig_p3_staticdyn.png',dpi=125); plt.close(fig)
# ---- (2) 한 환자 day7 궤적 ----
D=RES['Ridge']['test'].copy().sort_values(['ID','tod'])
cnt=D.groupby('ID').size(); cand=cnt[cnt>=5].index
# 동적 드리프트가 보이는 환자 선택
def drift(p): d=D[D.ID==p]; return mae(d.dS-d.SBP)-mae(d.sS-d.SBP)
pid=max(cand,key=drift) if len(cand) else cnt.idxmax()
d=D[D.ID==pid].sort_values('tod'); h=d.tod/60.0
fig,ax=plt.subplots(figsize=(9.2,5.4))
ax.plot(h,d.e0S,'--',color='#888',lw=1.5,label='E0 (수준+위상)',zorder=1)
ax.plot(h,d.SBP,'o-',color='#1a1a1a',lw=1.5,ms=9,label='실측 SBP',zorder=4)
ax.plot(h,d.sS,'^-',color='#1d9e75',lw=1.8,ms=8,label='정적 static (1-step)',zorder=3)
ax.plot(h,d.dS,'x--',color='#d85a30',lw=1.8,ms=9,mew=2.5,label='동적 dynamic (rollout)',zorder=2)
ax.set_xlabel('하루 중 시각 (시)'); ax.set_ylabel('수축기 혈압 SBP (mmHg)')
ax.set_title(f'한 환자(test)의 day7 SBP 예측 — 정적은 실측에 밀착, 동적은 굴러가며 누적',fontweight='bold',fontsize=12)
ax.legend(fontsize=10,loc='best'); ax.grid(alpha=.25)
fig.tight_layout(); fig.savefig(OUT+'fig_p3_rollout.png',dpi=125); plt.close(fig)
print('SAVED fig_p3_staticdyn / fig_p3_rollout  (patient',pid,')')
