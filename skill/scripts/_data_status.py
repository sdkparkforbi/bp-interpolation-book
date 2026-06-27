# -*- coding: utf-8 -*-
# PART1 1단계: 데이터 현황 파악 + 정제(이상점 제거 + 세션평균). day1=튜닝/2~6=학습/7=예측 분할 구조 점검.
import pandas as pd, numpy as np, sys, warnings
warnings.filterwarnings('ignore')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
R=pd.read_pickle('_raw_bp.pkl')  # ID,t,SBP,DBP,PR
loc=R['t'].dt.tz_convert('Asia/Seoul'); R['day']=loc.dt.strftime('%Y-%m-%d'); R['tod']=loc.dt.hour*60+loc.dt.minute
R['tmin']=(R['t']-pd.Timestamp('2025-01-01',tz='UTC')).dt.total_seconds()/60.0
print("="*60); print("1) 데이터 현황"); print("="*60)
print(f"대상자: {R.ID.nunique()}명 · 총 측정: {len(R)}개")
dpp=R.groupby('ID')['day'].nunique()
print(f"사람당 측정일수: 중앙 {dpp.median():.0f}일 (범위 {dpp.min()}~{dpp.max()}); 7일={int((dpp==7).sum())}명, 6일={int((dpp==6).sum())}명, ≤5일={int((dpp<=5).sum())}명")
mpp=R.groupby('ID').size(); mpd=R.groupby(['ID','day']).size()
print(f"사람당 측정수: 중앙 {mpp.median():.0f}개 (범위 {mpp.min()}~{mpp.max()})")
print(f"하루당 측정수: 중앙 {mpd.median():.0f}개 (대개 5세션×2회)")
print(f"BP 분포: SBP 평균 {R.SBP.mean():.0f} (범위 {R.SBP.min():.0f}~{R.SBP.max():.0f}, p1~p99 {R.SBP.quantile(.01):.0f}~{R.SBP.quantile(.99):.0f})")
print(f"          DBP 평균 {R.DBP.mean():.0f} (범위 {R.DBP.min():.0f}~{R.DBP.max():.0f})")
# 워치 변수 커버리지
F=pd.read_pickle('_feat_estimation_full.pkl'); sigs=[c[3:] for c in F.columns if c.startswith('kw_')]
cov=[(s,100*pd.to_numeric(F['last_'+s],errors='coerce').notna().mean()) for s in sigs if 'last_'+s in F.columns]
print(f"\n워치 신호 {len(sigs)}종. 관측 커버리지(last_, 비결측%):")
for s,c in sorted(cov,key=lambda x:-x[1])[:8]: print(f"   {s:14s} {c:4.0f}%")
print(f"   ... 하위: "+", ".join(f"{s}({c:.0f}%)" for s,c in sorted(cov,key=lambda x:x[1])[:4]))
print("\n"+"="*60); print("2) 정제 (이상점 제거 + 세션평균)"); print("="*60)
# 이상점: 명백한 아티팩트 2건
a1=(R.ID=='ba8fb9cdf016')&(R.SBP<=20); a2=(R.ID=='d3444063aed7')&(R.DBP<=20); bad=a1|a2
print(f"이상점 제거: {int(bad.sum())}건 (ba8fb9 SBP={R[a1].SBP.values}, d34440 DBP={R[a2].DBP.values}); SBP=68 등 저혈압 가능값 유지")
R2=R[~bad].copy()
# 세션평균: Δt<=3분 = 한 세션, BP 평균, 시각=마지막
R2=R2.sort_values(['ID','tmin']).reset_index(drop=True)
newsess=(R2.ID!=R2.ID.shift())|((R2.tmin-R2.tmin.shift())>3); R2['sess']=newsess.cumsum()
SM=R2.groupby('sess').agg(ID=('ID','first'),SBP=('SBP','mean'),DBP=('DBP','mean'),tod=('tod','last'),tmin=('tmin','last'),day=('day','last'),nrep=('SBP','size')).reset_index(drop=True)
print(f"세션평균: {len(R2)}측정 → {len(SM)}세션 (1회 {int((SM.nrep==1).sum())}, 2회 {int((SM.nrep==2).sum())}, 3회+ {int((SM.nrep>=3).sum())})")
o=R2.groupby('ID')['SBP'].std().mean(); n=SM.groupby('ID')['SBP'].std().mean()
print(f"개인내 SBP SD: 측정단위 {o:.2f} → 세션평균 {n:.2f} (1분 측정잡음 제거)")
print("\n"+"="*60); print("3) 분할 구조 (day1 튜닝 / 2~6 학습 / 7 예측)"); print("="*60)
# 사람별 날짜 순서 부여
SM['dord']=SM.groupby('ID')['day'].transform(lambda s: pd.factorize(s)[0]+1)  # 1,2,3...
roles=SM.groupby('dord').agg(세션수=('ID','size'),사람수=('ID','nunique'))
print("일차별 세션/사람 수:")
for d,row in roles.iterrows():
    role='튜닝(보정)' if d==1 else ('예측 타깃' if d==7 else '학습' if d<=6 else '추가일')
    print(f"   day{d}: 세션 {int(row.세션수):4d} · 사람 {int(row.사람수):3d}  [{role}]")
nd=SM.groupby('ID')['dord'].max()
print(f"\n7일째(예측 타깃) 보유자: {int((nd>=7).sum())}명 / 6일째까지 보유: {int((nd>=6).sum())}명")
SM.to_pickle('_clean_sessions.pkl')
print(f"\n저장: _clean_sessions.pkl ({len(SM)}세션, dord 포함)"); print("DONE")
