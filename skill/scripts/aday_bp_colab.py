#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ADAY BP pipeline — portable (Google Colab / 서버 단독 실행).
경로 하드코딩 없음. 합성 데모 데이터로 즉시 실행되고, 실데이터(CSV)도 연결 가능.

수준+위상 = E0  ·  편차 r = 실측 − E0 ~ f(워치, 지난추정)  ·  최종 = E0 + r̂
평가: MAE + BHS 등급 (세션·일평균, train/valid/test).  PART3: 정적(1-step)·동적(rollout).

Colab:
    !pip -q install scikit-learn pandas numpy matplotlib
    !python aday_bp_colab.py            # 합성 데모
    !python aday_bp_colab.py --csv my.csv   # 실데이터 (열: ID,day,tod,SBP,DBP,HR,METs,age,cl)
"""
import argparse, numpy as np, pandas as pd, sys
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

def synth(n=120, days=7, seed=0):
    """합성 데모: 사람별 수준(ICC~0.7) + 일주기 + 급성(워치) + 측정잡음."""
    rng = np.random.RandomState(seed); rows = []
    for i in range(n):
        Ls, Ld = rng.normal(118, 13), rng.normal(76, 9); cl = int(rng.randint(4)); age = int(rng.randint(20, 66))
        for d in range(1, days + 1):
            for _ in range(rng.randint(4, 7)):
                tod = int(rng.randint(360, 1380)); circ = np.sin((tod - 540) / 1440 * 2 * np.pi)
                act = rng.rand() < 0.22; hr = 65 + (28 if act else 0) * rng.rand() + rng.normal(0, 4)
                mets = 1.0 + (6 if act else 0) * rng.rand()
                aS = 0.25 * (hr - 65) + (8 if act else 0) * rng.rand(); aD = 0.12 * (hr - 65) + (4 if act else 0) * rng.rand()
                rows.append(dict(ID="P%03d" % i, day=d, tod=tod, cl=cl, age=age,
                                 SBP=Ls + 10 * circ + aS + rng.normal(0, 6),
                                 DBP=Ld + 6 * circ + aD + rng.normal(0, 4),
                                 HR=hr, METs=mets))
    return pd.DataFrame(rows)

def bhs(e):
    e = np.abs(np.asarray(e)); return 100*np.mean(e<=5), 100*np.mean(e<=10), 100*np.mean(e<=15)
def grade(b):
    return 'A' if b[0]>=60 and b[1]>=85 and b[2]>=95 else 'B' if b[0]>=50 and b[1]>=75 and b[2]>=90 else 'C' if b[0]>=40 and b[1]>=65 and b[2]>=85 else 'D'
def cell(e):
    e=np.abs(np.asarray(e)); return "%.2f%s" % (e.mean(), grade(bhs(e)))

def run(F):
    F = F.sort_values(['ID','day','tod']).reset_index(drop=True)
    ids = sorted(F.ID.unique()); rng = np.random.RandomState(0); u = np.array(ids); rng.shuffle(u)
    a, b = int(len(u)*.6), int(len(u)*.8)
    split = {p:('train' if i<a else 'valid' if i<b else 'test') for i,p in enumerate(u)}
    F['split'] = F.ID.map(split); F['role'] = np.where(F.day==1,'tune',np.where(F.day==7,'forecast','est'))
    # 위상(일주기) — train 사람 days2-6에서 군집별 곡선 (단순화: 전역 조화)
    tr = F[(F.split=='train') & (F.role=='est')]
    import numpy.polynomial as _np
    def phase(df, tg):
        ph = 2*np.pi*df.tod.values/1440.0
        X = np.column_stack([np.sin(ph),np.cos(ph),np.sin(2*ph),np.cos(2*ph)])
        pm = df.groupby('ID')[tg].transform('mean'); coef = np.linalg.lstsq(X, df[tg].values-pm.values, rcond=None)[0]
        return coef
    cS, cD = phase(tr,'SBP'), phase(tr,'DBP')
    def phval(tod, coef):
        ph = 2*np.pi*np.asarray(tod,float)/1440.0
        return np.column_stack([np.sin(ph),np.cos(ph),np.sin(2*ph),np.cos(2*ph)]) @ coef
    popS, popD = tr.SBP.mean(), tr.DBP.mean()
    # 수준: day1 보정평균을 모집단으로 shrink (실데이터에선 KNHANES+설문으로 대체)
    d1 = F[F.role=='tune'].groupby('ID').agg(cmS=('SBP','mean'),cmD=('DBP','mean'),n=('SBP','size'))
    def lvl(p, tg):
        if p in d1.index:
            cm = d1.loc[p,'cmS' if tg=='S' else 'cmD']; n = d1.loc[p,'n']; pop = popS if tg=='S' else popD
            return (n*cm + 2*pop)/(n+2)
        return popS if tg=='S' else popD
    F['e0S'] = [lvl(p,'S') for p in F.ID] + phval(F.tod, cS)
    F['e0D'] = [lvl(p,'D') for p in F.ID] + phval(F.tod, cD)
    # 편차 모델 (워치 + 지난추정 lag). 지난추정 = 사람 과거일 평균 e0 (단순화)
    F['rS'], F['rD'] = F.SBP-F.e0S, F.DBP-F.e0D
    F['HRrest'] = F.groupby('ID')['HR'].transform(lambda x:x.quantile(.1)); F['dHR']=F.HR-F.HRrest
    feats = ['HR','dHR','METs']
    TR = F[(F.split=='train')&(F.role=='est')]
    mkr = lambda: make_pipeline(StandardScaler(), Ridge(alpha=10))
    mS, mD = mkr().fit(TR[feats], TR.rS), mkr().fit(TR[feats], TR.rD)
    def daily(D, pr, y):
        t = pd.DataFrame({'ID':D.ID.values,'p':pr,'y':y}).groupby('ID').mean(); return (t.p-t.y).values
    print("== PART2 추정 (편차=E0+워치 Ridge) — MAE+BHS ==")
    print("%-8s %8s %8s %8s %8s" % ("split","세SBP","세DBP","일SBP","일DBP"))
    for sp in ['train','valid','test']:
        D = F[(F.split==sp)&(F.role=='est')]
        pS, pD = D.e0S+mS.predict(D[feats]), D.e0D+mD.predict(D[feats])
        print("%-8s %8s %8s %8s %8s" % (sp, cell(pS-D.SBP), cell(pD-D.DBP), cell(daily(D,pS,D.SBP)), cell(daily(D,pD,D.DBP))))
    # PART3: day7 AR 정적/동적
    print("\n== PART3 예측 (day7) — 정적(1-step) vs 동적(rollout) ==")
    F['sin']=np.sin(2*np.pi*F.tod/1440); F['cos']=np.cos(2*np.pi*F.tod/1440)
    F['prS']=F.groupby('ID')['rS'].shift(1); F['prD']=F.groupby('ID')['rD'].shift(1)
    AR=['prS','prD','sin','cos']+feats; TA=F[(F.split=='train')&(F.role=='est')&F.prS.notna()]
    aS, aD = mkr().fit(TA[AR],TA.rS), mkr().fit(TA[AR],TA.rD)
    print("%-8s %8s %8s %8s %8s" % ("split·모드","세SBP","세DBP","일SBP","일DBP"))
    for sp in ['valid','test']:
        rows=[]
        for p,s in F[F.split==sp].groupby('ID'):
            past=s[s.day<7].sort_values(['day','tod']); d7=s[s.day==7].sort_values(['day','tod'])
            if len(past)==0 or len(d7)==0: continue
            seS,seD=past.rS.values[-1],past.rD.values[-1]; psr,pdr=seS,seD
            for _,r in d7.iterrows():
                base=[r.sin,r.cos]+[r[f] for f in feats]
                stS=r.e0S+aS.predict([[seS,seD]+base])[0]; stD=r.e0D+aD.predict([[seS,seD]+base])[0]
                dyS=r.e0S+aS.predict([[psr,pdr]+base])[0]; dyD=r.e0D+aD.predict([[psr,pdr]+base])[0]
                rows.append((p,r.SBP,r.DBP,stS,stD,dyS,dyD)); seS,seD=r.SBP-r.e0S,r.DBP-r.e0D; psr,pdr=dyS-r.e0S,dyD-r.e0D
        D=pd.DataFrame(rows,columns=['ID','SBP','DBP','stS','stD','dyS','dyD'])
        for mode,a_,b_ in [('정적',D.stS,D.stD),('동적',D.dyS,D.dyD)]:
            print("%-8s %8s %8s %8s %8s" % (sp+'·'+mode, cell(a_-D.SBP), cell(b_-D.DBP), cell(daily(D,a_,D.SBP)), cell(daily(D,b_,D.DBP))))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', help='실데이터 CSV (열: ID,day,tod,SBP,DBP,HR,METs,age,cl). 미지정 시 합성 데모')
    ap.add_argument('--n', type=int, default=120); ap.add_argument('--seed', type=int, default=0)
    A = ap.parse_args()
    if A.csv:
        F = pd.read_csv(A.csv); print("실데이터 %d행 / %d명" % (len(F), F.ID.nunique()))
    else:
        F = synth(A.n, seed=A.seed); print("합성 데모 %d행 / %d명 (실데이터는 --csv)" % (len(F), F.ID.nunique()))
    run(F)
