---
name: aday-bp-pipeline
description: Estimate (nowcast) and forecast blood pressure (SBP/DBP) from survey + smartwatch data using a level–phase–deviation decomposition, a 20-model zoo, and AR static/dynamic forecasting, evaluated with MAE and BHS grade. Use when building cuffless/wearable BP estimation or prediction pipelines, decomposing BP into person-level + circadian + deviation, comparing model families on tabular physiological data, or evaluating BP models against BHS/AAMI/IEEE standards.
---

# ADAY BP pipeline — 보간·추정·예측

설문 + 스마트워치(애플워치 24신호)로 신규 환자의 **분단위 혈압**을 추정·예측하는 파이프라인. 핵심은 **수준·위상·편차 분해**와 **실측에서만 평가(MAE + BHS)**.

## 핵심 설계

- **수준 L(p)** = 외부(KNHANES 가중회귀) + 설문 + day1 보정평균을 shrinkage로 합친 사람별 평균 BP. `L = (n·cm + 2·Lext)/(n+2)`
- **위상** = 군집 일주기 phase 커널. `w = exp(−circ(φ,φ')²/2ℓ²)`, ℓ≈196분, circ은 1440분 원 거리
- **E0 = 수준 + 위상** (구조적 추정치). 임의 분에서 계산
- **편차 r = 실측 − E0** ← 모형이 잡는 대상. 입력 = 워치(급성 생리) + 지난 BP **추정** lag(전날 동시각·과거일 평균). 실측 과거 BP는 day1만 허용
- **최종 = E0 + r̂** (분단위 곡선). 세션평균·일평균은 집계, **성과는 실측 시점에서만**

## 데이터 분할 (누수 차단)

- day1 = calibration(튜닝), days2-6 = 추정 학습/평가, **day7 = 예측 전용(절대 학습 제외)**
- 사람 기준 60:20:20 (train/valid/test). 보간 함수는 train 사람 days2-6에서만 적합

## 평가 — MAE + BHS (항상 둘 다)

- **MAE**: 평균 절대오차(mmHg), 낮을수록 우수
- **BHS 등급**: |오차| ≤5/≤10/≤15 mmHg 누적 비율로 A(60/85/95) / B(50/75/90) / C(40/65/85). 세 조건 동시 충족
- 세션평균과 일평균 둘 다 보고

## 파일 맵 (scripts/)

PART1 — 데이터·정제·보간
- `_data_status.py` 데이터 현황 + 정제(세션평균, SBP&lt;70/&gt;220 제거)
- `_split_interp.py` 분할 + 30분 보간(군집 일주기)
- `_interp_minute.py` 분단위 하이브리드 보간(실측 시각엔 실측 고정)

PART2 — 추정(Nowcasting)
- `_part2_feats.py` 공유 특징행렬 빌더(E0·편차 lag·워치). days2-6 + day7 세트 저장 → `_part2_feats.pkl`
- `_part2_zoo.py` 20모형 residual zoo(회귀·스펙트럴·트리·GBM·딥러닝 single/multi). 예측 저장 → `_part2_preds.pkl`
- `_part2_wavelet.py` 웨이블릿(연속 Ricker 다해상도) 모형 추가
- `_part2_ablation.py` 편차 입력 ablation(와치 / 지난추정 / 둘다)
- `_part2_predict.py` 예측형 추정(과거 BP 추정 lag 사용)

PART3 — 예측(Forecasting)
- `_part3_forecast.py` AR residual. **정적**(1-step 실측 재앵커) vs **동적**(rollout, 예측 굴림). day7

그림·책·논문 빌더
- `_fig_part2_zoo.py` `_fig_part3.py` 그림
- `_build_part1/2/3.py` `_build_paper.py` `_build_plan.py` HTML 책·논문 빌더

선행연구 레퍼런스(JSON)
- `_watch_refs.json` 워치 변수별 BP 관계·인용 / `_activity_refs.json` 활동 변수 / `_sessionA_refs.json` 세션 Grade A 요건

## 실행 순서

```
python _data_status.py        # 정제
python _split_interp.py        # 분할 + 보간
python _interp_minute.py       # 분단위 보간
python _part2_feats.py         # 특징행렬 (→ _part2_feats.pkl)
python _part2_zoo.py           # 20모형 추정 (→ _part2_preds.pkl)
python _part2_wavelet.py       # 웨이블릿 추가
python _part2_ablation.py      # 편차 ablation
python _part3_forecast.py      # day7 예측 (정적/동적)
```

## 핵심 결과 (N=120)

- 추정 챔피언 = **회귀 Ridge**(선형 shrinkage). 검증 일평균 SBP 3.59(A)·DBP 2.33(A), 테스트 일평균 2.07(A)·2.18(A)
- 트리·GBM은 **과적합**(학습 최저, held-out 붕괴) — valid 기준 선택, 트리계열 제외
- 워치(세션 DBP)와 지난 BP 추정(일평균 level)은 **상보적**
- 예측: **정적(1-step) ≫ 동적(rollout)** — 측정 빈도가 예측 지평을 좌우
- **세션 SBP는 약 5.7(Grade B)이 한계** — 집계 변수의 mean-regression. 세션 Grade A엔 raw PPG 파형·PTT·주기 재보정 필요(`_sessionA_refs.json`)

## 주의

- 환자 데이터(`_feat_estimation_sess.pkl`, `train_model_data.csv` 등)는 **민감정보라 미포함**. 스크립트는 방법론 템플릿 — 자신의 데이터·경로에 맞게 조정해서 사용
- 금지 feature: cuff 맥박수(누수). 과거 실측 BP는 day1만 허용
- 글꼴: Malgun Gothic(한글 그림)

라이브 책·논문: https://sdkparkforbi.github.io/bp-interpolation-book/
