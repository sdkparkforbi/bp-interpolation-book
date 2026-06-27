# -*- coding: utf-8 -*-
# PART1 2단계: 분할(day1 튜닝/2~6 학습 60:20:20/day7 예측) + 분단위 보간 타깃 생성.
# 보간함수(군집 일주기)는 train 사람 day2~6에서만 적합. 보간된 분단위 BP=모형 타깃. 평가는 실측 세션점에서만.
import pandas as pd, numpy as np, sys, warnings
warnings.filterwarnings('ignore')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
ELL=196.0; KAPPA=5.0; GRIDSTEP=30  # 30분 격자(학습 밀도용); 평가는 실측점
SM=pd.read_pickle('_clean_sessions.pkl')
g=pd.read_csv('train_model_data.csv',encoding='cp949').groupby('ID').first()
age=pd.to_numeric(g['Age'],errors='coerce'); male=(g['Gender']==1); amed=age.median()
ids=sorted(SM.ID.unique()); cl={p:(0 if age.get(p,amed)<=amed else 2)+(0 if male.get(p,True) else 1) for p in ids}
SM['cl']=SM.ID.map(cl)
# 역할
SM['role']=np.where(SM.dord==1,'tune',np.where(SM.dord==7,'forecast',np.where(SM.dord.between(2,6),'train','extra')))
# 사람 분할 60:20:20 (seed 0)
u=np.array(ids); np.random.RandomState(0).shuffle(u); a=int(len(u)*.6); b=int(len(u)*.8)
spl={p:('train' if i<a else 'valid' if i<b else 'test') for i,p in enumerate(u)}
SM['split']=SM.ID.map(spl)
print(f"분할: train {sum(v=='train' for v in spl.values())}명 / valid {sum(v=='valid' for v in spl.values())}명 / test {sum(v=='test' for v in spl.values())}명")
print(f"역할 세션수: {SM.role.value_counts().to_dict()}")
def circ(a,b): d=np.abs(a-b); return np.minimum(d,1440-d)
GRID=np.arange(0,1440,GRIDSTEP)
# 보간함수의 군집 일주기: train 사람 × day2~6 세션에서만
def phase_curve(tg):
    src=SM[(SM.split=='train')&(SM.role=='train')]
    C={}
    for c in range(4):
        s=src[src.cl==c];
        if len(s)<20: s=src
        # 개인평균 제거 후 위상 평활
        pm=s.groupby('ID')[tg].transform('mean'); ph=s.tod.values; dv=(s[tg]-pm).values
        cc=np.array([np.sum(np.exp(-circ(ph,gg)**2/(2*ELL**2))*dv)/max(np.sum(np.exp(-circ(ph,gg)**2/(2*ELL**2))),1e-9) for gg in GRID])
        C[c]=cc
    return C
Sc={'SBP':phase_curve('SBP'),'DBP':phase_curve('DBP')}
def look(C,phi): return C[(np.round(phi/GRIDSTEP).astype(int))%len(GRID)]
# 분단위(30분격자) 보간 타깃: (사람,일) 그 날 세션 앵커 + 군집 일주기
rows=[]
for (p,day),s in SM.groupby(['ID','day']):
    if len(s)==0: continue
    c=cl[p]; dord=int(s.dord.iloc[0]); role=s.role.iloc[0]; split=spl[p]
    tods=s.tod.values
    for tg in['SBP','DBP']:
        bp=s[tg].values; dm=bp.mean(); scg=look(Sc[tg][c],GRID)
        for gi,gg in enumerate(GRID):
            w=np.exp(-circ(tods,gg)**2/(2*ELL**2)); W=w.sum()
            anchor=np.sum(w*bp)/W if W>0 else dm; al=W/(W+KAPPA)
            val=al*anchor+(1-al)*(dm+scg[gi])
            if tg=='SBP': rows.append([p,day,dord,role,split,c,gg,val,np.nan])
            else: rows[-(len(GRID))+gi][-1]=val  # DBP를 같은 행에 채움
T=pd.DataFrame(rows,columns=['ID','day','dord','role','split','cl','tod','SBP_t','DBP_t'])
# 보간 품질 sanity: 실측 세션 tod에서 보간값 vs 실측 (작아야 정상)
def at_grid(tod): return (np.round(tod/GRIDSTEP).astype(int))%len(GRID)*GRIDSTEP
chk=SM.copy(); chk['gtod']=at_grid(chk.tod.values)
m=chk.merge(T,left_on=['ID','day','gtod'],right_on=['ID','day','tod'],suffixes=('','_i'))
print(f"\n보간 분단위 타깃: {len(T)}행 ({T.ID.nunique()}명 × 일 × {len(GRID)}격자/타깃)")
print(f"보간 sanity (실측 tod 격자에서 |보간−실측|): SBP {np.abs(m.SBP_t-m.SBP).mean():.2f}, DBP {np.abs(m.DBP_t-m.DBP).mean():.2f} mmHg (작을수록 앵커 충실)")
T.to_pickle('_interp_target.pkl'); SM.to_pickle('_sessions_roled.pkl')
print("저장: _interp_target.pkl (분단위 보간 타깃), _sessions_roled.pkl (역할·분할 세션)"); print("DONE")
