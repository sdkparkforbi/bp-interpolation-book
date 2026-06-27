# -*- coding: utf-8 -*-
# PART1 보간 마무리: 분당(1분 격자) 보간 타깃. 보간함수(군집 일주기)=train day2~6에서만. 벡터화. sanity + 샘플 그림.
import pandas as pd, numpy as np, sys, warnings
warnings.filterwarnings('ignore')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
for f in ['Malgun Gothic','맑은 고딕']:
    try: plt.rcParams['font.family']=f; break
    except Exception: pass
plt.rcParams['axes.unicode_minus']=False
ELL=90.0; KAPPA=0.5   # 앵커(실측) 충실: 좁은 위상폭 + 작은 KAPPA
SM=pd.read_pickle('_sessions_roled.pkl')
def circ(a,b): d=np.abs(a-b); return np.minimum(d,1440-d)
GRID=np.arange(0,1440,1.0)  # 분당
# 군집 일주기: train 사람 × day2~6
def phase_curve(tg):
    src=SM[(SM.split=='train')&(SM.role=='train')]; C={}
    for c in range(4):
        s=src[src.cl==c]; s=s if len(s)>=20 else src
        pm=s.groupby('ID')[tg].transform('mean'); ph=s.tod.values; dv=(s[tg]-pm).values
        D=circ(GRID[:,None],ph[None,:]); W=np.exp(-D**2/(2*ELL**2))
        C[c]=(W*dv).sum(1)/np.clip(W.sum(1),1e-9,None)
    return C
Sc={'SBP':phase_curve('SBP'),'DBP':phase_curve('DBP')}
# 벡터화 1분 보간
parts=[]; sanity={'SBP':[],'DBP':[]}
for (p,day),s in SM.groupby(['ID','day']):
    c=int(s.cl.iloc[0]); dord=int(s.dord.iloc[0]); role=s.role.iloc[0]; split=s.split.iloc[0]; tods=s.tod.values.astype(float)
    D=circ(GRID[:,None],tods[None,:]); Wm=np.exp(-D**2/(2*ELL**2)); Wsum=Wm.sum(1); al=Wsum/(Wsum+KAPPA)
    idx=np.clip(np.round(tods).astype(int),0,1439); ia=np.zeros(len(GRID),dtype=np.int8); ia[idx]=1
    out={'ID':p,'day':day,'dord':dord,'role':role,'split':split,'tod':GRID.astype(np.int16),'is_actual':ia}
    for tg in['SBP','DBP']:
        bp=s[tg].values.astype(float); dm=bp.mean(); anchor=(Wm*bp).sum(1)/np.clip(Wsum,1e-9,None)
        val=al*anchor+(1-al)*(dm+Sc[tg][c])
        val[idx]=bp   # 실측 있는 분 = 실측값으로 대체 (하이브리드 시계열)
        out[tg]=val.astype(np.float32); sanity[tg]+=list(np.abs(val[idx]-bp))
    parts.append(pd.DataFrame(out))
T=pd.concat(parts,ignore_index=True)
for cc in ['ID','day','role','split']: T[cc]=T[cc].astype('category')
print(f"분당 보간 타깃: {len(T):,}행 (= {T.ID.nunique()}명 × 일 × 1440분)")
print(f"sanity (실측 분에서 |보간−실측|): SBP {np.mean(sanity['SBP']):.2f}, DBP {np.mean(sanity['DBP']):.2f} mmHg  (앵커 충실해질수록 작아짐)")
T.to_pickle('_interp_target_min.pkl')
print(f"저장: _interp_target_min.pkl ({T.memory_usage(deep=True).sum()/1024/1024:.0f} MB)")
# 샘플 그림: test 환자 1명, 7일 보간 곡선 + 실측 세션
tp=SM[(SM.split=='test')&(SM.dord==7)].ID.iloc[0]
fig,ax=plt.subplots(2,1,figsize=(15,7),sharex=True)
for j,tg,col in [(0,'SBP','#c0392b'),(1,'DBP','#2471a3')]:
    a=ax[j]
    for d in range(1,8):
        sub=T[(T.ID==tp)&(T.dord==d)]
        if len(sub)==0: continue
        x=(d-1)*1440+sub.tod.values; a.plot(x,sub[tg].values,'-',color=col,lw=1,alpha=.8)
        ss=SM[(SM.ID==tp)&(SM.dord==d)]; a.scatter((d-1)*1440+ss.tod.values,ss[tg].values,s=22,color='#111',zorder=3)
        role=sub.role.iloc[0]; a.axvspan((d-1)*1440,d*1440,color=('#fff3e0' if role=='tune' else '#fdeaea' if role=='forecast' else '#eefaf0'),alpha=.35,zorder=0)
    a.set_ylabel(f'{tg} (mmHg)',fontsize=12); a.set_xlim(0,7*1440)
ax[0].set_title(f'분당 보간 곡선 + 실측 세션(검정) — 샘플 test 환자 {tp[:8]}  (주황=day1 튜닝, 초록=학습, 빨강=day7 예측)',fontsize=12.5,fontweight='bold')
ax[1].set_xticks([720+1440*i for i in range(7)]); ax[1].set_xticklabels([f'day{i+1}' for i in range(7)]); ax[1].set_xlabel('시간',fontsize=11)
fig.tight_layout(); fig.savefig('_fig_interp_minute.png',dpi=100,bbox_inches='tight'); print('saved _fig_interp_minute.png'); print('DONE')
