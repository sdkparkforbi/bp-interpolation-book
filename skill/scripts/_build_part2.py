# -*- coding: utf-8 -*-
# PART 2 (신구조) — 추정(Nowcasting). 수준+위상=E0, 편차=워치+지난BP추정. 20모형 zoo train/valid/test MAE+BHS. 2-1~2-5. days2-6, day7은 PART3.
import pickle, json, os, shutil, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
SITE='C:/Temp/HYPT/book_site/'
for f in ['fig_p2_zoo.png','fig_p2_overfit.png','fig_p2_ablation.png']:
    if os.path.exists('C:/Temp/HYPT/'+f): shutil.copy('C:/Temp/HYPT/'+f,SITE+f)
P=pickle.load(open('C:/Temp/HYPT/ADAY_BP_Prediction_Model/_part2_preds.pkl','rb')); PRED=P['PRED']; ACT=P['ACT']
def bhs(e): e=np.abs(e); return 100*np.mean(e<=5),100*np.mean(e<=10),100*np.mean(e<=15)
def gr(b): return 'A' if b[0]>=60 and b[1]>=85 and b[2]>=95 else 'B' if b[0]>=50 and b[1]>=75 and b[2]>=90 else 'C' if b[0]>=40 and b[1]>=65 and b[2]>=85 else 'D'
def daily(pr,y,ID): a=pd.DataFrame({'ID':ID,'pr':pr,'y':y}).groupby('ID').mean(); return (a.pr-a.y).values
def gspan(g): return f'<span class="g{g}">{g}</span>'
def C(e): e=np.abs(np.asarray(e)); return f'{e.mean():.2f}<span class="g{gr(bhs(e))}">{gr(bhs(e))}</span>'
ORDER=['수준+커널 E0','Ê=E0+워치편차(ET)','회귀 Ridge','회귀 Lasso','회귀 ElasticNet','회귀 MultiTaskElasticNet',
 '스펙트럴 Harmonic+Ridge','스펙트럴 Harmonic+MTEN','웨이블릿 Wavelet+Ridge','웨이블릿 Wavelet+MTEN',
 '트리 RandomForest','트리 ExtraTrees','트리 ExtraTrees(multi)','GBM XGBoost','GBM LightGBM','GBM CatBoost',
 'GBM XGBoost(multi)','GBM CatBoost(multi)','딥러닝 MLP','딥러닝 MLP(multi)']
def zoo_rows():
    rows=''
    for nm in ORDER:
        if nm not in PRED: continue
        cells=''
        for sp in ['valid','test']:
            yS,yD,ID=ACT[sp]; prS,prD=PRED[nm][sp]
            cells+=f'<td>{C(prS-yS)}</td><td>{C(prD-yD)}</td><td>{C(daily(prS,yS,ID))}</td><td>{C(daily(prD,yD,ID))}</td>'
        cls=' class="best"' if nm in ('회귀 Ridge','스펙트럴 Harmonic+Ridge') else ''
        rows+=f'<tr{cls}><td class="l">{nm}</td>{cells}</tr>'
    return rows
# 워치 기초통계 (120명 집계)
WSTAT=[('심박수 HR','BPM',4462,100,'75.2±13.5','43–141'),('활동 에너지','kcal',3753,100,'3.9±3.5','0–32'),
('휴식 에너지','kcal',3720,100,'17.4±8.2','0.1–86.6'),('절대적 운동강도 METs','MET',3361,100,'1.8±1.0','1–12'),
('걷기+달리기 거리','km',2242,100,'0.1±0.1','0–0.7'),('걸음','steps',1175,100,'96.6±124.2','1–1056'),
('일어서기 시간(분)','분',357,100,'1.7±1.0','1–5'),('호흡수','/min',273,99,'15.5±2.8','7.5–32.5'),
('운동하기 시간','분',239,97,'1.0±0.0','1'),('보행 보폭 / 속도','cm·m/s',213,98,'63.4 / 1.1','25–132'),
('수면','단계',205,99,'3.2±1.2','0–5'),('이중 지지 시간','s',190,98,'0.3±0.0','0.2–0.4'),
('보행 비대칭성','%',102,98,'0.04±0.1','0–1'),('혈중 산소 SpO2','%',113,100,'1.0(=100%)','0.8–1.0'),
('심박 변이 HRV','ms',80,100,'45.2±24.8','0–221'),('오른 층수','층',34,94,'1.9±1.5','1–17'),
('계단 올라가기 속도','m/s',21,87,'0.3±0.1','0.2–1.1'),('일광 시간','시간',20,78,'2.9±1.5','1–5'),
('휴식기 / 걷기 심박수','BPM',7,100,'63.1 / 98.5','44–146'),('손목 온도','°C',3,50,'35.6±0.5','34.3–38.2'),
('보행 안정성','-',0,76,'0.9±0.1','0.7–1.0')]
def dens(f): return ('고밀도','#1e7d4f') if f>=1000 else ('중밀도','#d4a017') if f>=100 else ('저밀도','#c0392b')
def wstat_rows():
    r=''
    for nm,u,f,cov,ms,rg in WSTAT:
        lab,col=dens(f); r+=f'<tr><td class="l">{nm}</td><td>{u}</td><td>{f:,}</td><td>{cov}</td><td>{ms}</td><td>{rg}</td><td style="color:{col};font-weight:700">{lab}</td></tr>'
    return r
# 선행연구 레퍼런스 (워크플로 결과)
try: REFS=json.load(open('C:/Temp/HYPT/_watch_refs.json',encoding='utf-8'))
except Exception: REFS=[]
def ref_blocks():
    h=''
    for v in REFS:
        var=v.get('variable',''); rel=v.get('bp_relationship',''); refs=v.get('references',[])[:2]
        rl=''.join(f'<li>{x}</li>' for x in refs)
        h+=f'<div class="refitem"><b>{var}</b><div class="rel">{rel}</div><ul>{rl}</ul></div>'
    return h

CSS="""
:root{--ink:#1d2433;--muted:#5d6b82;--bg:#0f1830;--paper:#fbfbfd;--card:#fff;--red:#c0392b;--blue:#2471a3;--green:#1e7d4f;--gold:#d4a017;--teal:#16a085;--purple:#2e7d6b}
*{box-sizing:border-box}
body{margin:0;font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;color:var(--ink);background:var(--bg);line-height:1.8}
.wrap{max-width:1000px;margin:0 auto;background:var(--paper);padding:0 24px 90px;box-shadow:0 0 60px rgba(0,0,0,.5)}
.nav{background:#10463b;color:#fff;padding:11px 22px;font-size:14px}.nav a{color:#9fe0cf;text-decoration:none;font-weight:700}
.hero{background:linear-gradient(135deg,#10463b,#16a085);color:#fff;padding:40px 30px 30px}
.hero h1{font-size:32px;margin:0 0 6px}.hero p{font-size:16px;color:#d3f3ea;margin:6px 0 0}
.toc{font-size:13px;color:var(--purple);margin:14px 0 0;line-height:2}.toc a{color:var(--purple);text-decoration:none;margin:0 8px 0 0;white-space:nowrap;display:inline-block}
.chap{display:flex;align-items:center;gap:12px;margin:48px 0 6px}
.chap .no{flex:none;min-width:54px;height:40px;padding:0 10px;border-radius:20px;background:var(--teal);color:#fff;font-weight:800;font-size:15px;display:flex;align-items:center;justify-content:center}
.chap h2{font-size:22px;margin:0}
.card{background:var(--card);border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.07);padding:20px 24px;margin:16px 0}
.fig{text-align:center;margin:16px 0}.fig img{max-width:100%;border:1px solid #e8e8ee;border-radius:10px}
.cap{color:var(--muted);font-size:13px;margin-top:7px;text-align:left;padding:0 4px}
.lead{font-size:17px;color:#22303a;background:#eafaf4;border:1px dashed var(--teal);border-radius:12px;padding:18px 22px;margin:18px 0}
table{border-collapse:collapse;width:100%;font-size:12.5px;margin:12px 0}
th,td{border:1px solid #e6e6ee;padding:5px 7px;text-align:center}th{background:#eef6f3}
.best{background:#fff6cf}.best td{font-weight:700}td.l,th.l{text-align:left}
.note{background:#eef6f3;border-left:5px solid var(--teal);padding:12px 16px;border-radius:8px;margin:12px 0;font-size:14px}
.win{background:#eefaf0;border-left:5px solid var(--green);padding:12px 16px;border-radius:8px;margin:12px 0}
.twist{background:#fff1ec;border-left:5px solid var(--red);padding:12px 16px;border-radius:8px;margin:12px 0}
.formula{background:#0f1830;color:#d3f3ea;border-radius:10px;padding:12px 16px;font-family:Consolas,monospace;font-size:14px;margin:10px 0;overflow-x:auto}
.gA{color:#1e7d4f;font-weight:800}.gB{color:#d4a017;font-weight:800}.gC{color:#c0392b;font-weight:800}.gD{color:#7f1d1d;font-weight:800}
.refitem{border-left:3px solid #16a085;padding:8px 12px;margin:9px 0;background:#f6fbf9;border-radius:0 8px 8px 0}
.refitem .rel{font-size:13px;color:#34495e;margin:3px 0 5px}.refitem ul{margin:0;padding-left:18px;font-size:12px;color:#5d6b82}
.steps{counter-reset:s;list-style:none;padding-left:0}.steps li{counter-increment:s;margin:11px 0;padding-left:44px;position:relative}
.steps li::before{content:counter(s);position:absolute;left:0;top:0;width:30px;height:30px;background:var(--teal);color:#fff;border-radius:50%;text-align:center;line-height:30px;font-weight:700}
.kpi{display:inline-block;background:#10463b;color:#9fe0cf;border-radius:7px;padding:2px 9px;font-weight:700}
"""

BODY=f"""
<div class="nav">🩺 PART 2 · 혈압 추정(Nowcasting) &nbsp;|&nbsp; <a href="plan.html">📋 연구계획</a> &nbsp;|&nbsp; <a href="part1.html">← PART 1 보간</a> &nbsp;|&nbsp; <a href="part3.html">PART 3 예측 →</a> &nbsp;|&nbsp; <a href="paper.html">논문</a></div>
<div class="hero"><h1>🩺 PART 2 · 혈압 추정 (Nowcasting)</h1>
<p>설문·외부데이터로 <b>수준</b>, 일주기로 <b>위상</b>, 워치·지난 추정으로 <b>편차</b> — 신규 환자의 <b>분단위 혈압</b>을 추정한다. days2-6, 검증 24명. (day7은 PART3 예측 전용)</p></div>
<div class="wrap">
<p class="toc">📑 <a href="#c0">0. 추정의 구조</a><a href="#c1">2-1 외부(KNHANES)</a><a href="#c2">2-2 내부데이터</a><a href="#c3">2-3 1-day calibration</a><a href="#c4">2-4 위상 커널</a><a href="#c5">2-5 와치(핵심)</a><a href="#c6">편차 모델</a><a href="#c7">20모형 zoo</a><a href="#c8">과적합</a><a href="#c9">결론</a></p>

<div class="lead"><b>PART 2는 "추정(estimation·Nowcasting)"이다.</b> 새 사람이 와도 — 설문과 외부 코호트(KNHANES)로 <b>평균 수준 L</b>을 잡고, 하루의 <b>위상(일주기)</b>을 더해 구조적 추정치 <b>E0 = 수준 + 위상</b>을 만든다. 그 뒤 남는 <b>편차 r = 실측 − E0</b>를 워치(급성 생리)와 지난 BP 추정으로 줄인다. 최종은 <b>분단위 혈압 곡선</b>이며, 성과는 실측 시점에서만 잰다(MAE + BHS, 세션·일평균).</div>

<div class="chap" id="c0"><div class="no">구조</div><h2>추정의 계층 구조 — 수준 · 위상 · 편차</h2></div>
<div class="card">
<ol class="steps">
<li><b>수준 L(p).</b> 외부(KNHANES 가중회귀)+설문+day1 보정을 shrinkage로 합친 사람별 평균 혈압 — <b>2-1·2-2·2-3</b></li>
<li><b>위상.</b> 일주기 phase 커널. 수준과 합쳐 <b>E0 = 수준 + 위상</b> (구조적 추정치) — <b>2-4</b></li>
<li><b>편차 r = 실측 − E0.</b> 워치(급성)와 지난 BP 추정으로 남은 편차를 모델 — <b>2-5 · 편차모델</b></li>
<li><b>최종 = E0 + r̂.</b> 분단위로 출력, 세션·일평균으로 집계, 실측에서 평가</li>
</ol>
<div class="formula">E0(t) = L(p) + 위상(tod)　|　r(t) = 실측(t) − E0(t) ≈ f(워치(t), 지난BP추정)　|　최종(t) = E0(t) + r̂(t)</div>
<div class="note"><b>평가 원칙.</b> 학습·집계엔 보간값을 모두 쓰되, <b>성과는 실측 시점에서만</b> MAE + BHS로. PART2는 <b>days2-6</b>만 — day7은 절대 건드리지 않고 PART3 예측(정적·동적)에서 쓴다.</div>
</div>

<div class="chap" id="c1"><div class="no">2-1</div><h2>외부데이터 — KNHANES 앵커</h2></div>
<div class="card"><p>신규 환자는 과거 혈압이 없다. 그래서 <b>국민건강영양조사(KNHANES)</b>를 외부 앵커로 — 나이·성별·BMI·설문 변수로 가중회귀해 그 사람의 <b>모집단 기대 수준 Lext</b>를 만든다. 내부 코호트가 작아도(120명) 외부 분포로 수준을 안정화하는 shrinkage의 바깥쪽 닻이다.</p>
<div class="formula">수준 L = (n·cm + 2·Lext) / (n + 2)　— day1 보정평균 cm을 Lext로 shrink (n=day1 측정수)</div></div>

<div class="chap" id="c2"><div class="no">2-2</div><h2>내부데이터 — 장비 offset 정렬</h2></div>
<div class="card"><p>KNHANES는 표준 cuff, 우리는 다른 장비·프로토콜이다. 둘의 측정 scale 차이를 <b>내부 train 코호트로 offset α를 적합</b>해 정렬한다 — Lext를 우리 장비 단위로 옮기는 보정. 내부데이터는 또한 위상 커널·편차 모델의 학습원이다(train 사람 days2-6).</p></div>

<div class="chap" id="c3"><div class="no">2-3</div><h2>1-day calibration — 개인 닻</h2></div>
<div class="card"><p>day1(첫날) 측정만 보정에 쓴다(이후 실측 과거 BP는 금지). day1 평균 cm을 외부 수준 Lext로 <b>shrink</b>해 사람별 level을 잡는다. day1이 많을수록(n↑) 개인값을, 적을수록 외부 앵커를 더 믿는 <b>경험적 베이즈</b> 구조.</p>
<div class="note">수준 분해(검증 24명, days2-6): 모집단 평균에서 출발해 <b>외부+내부offset → +1day → +위상</b>으로 갈수록 일평균 MAE가 단계적으로 낮아진다(2-4 표).</div></div>

<div class="chap" id="c4"><div class="no">2-4</div><h2>위상 커널 — 일주기 추정</h2></div>
<div class="card"><p>혈압은 하루 주기로 오르내린다(낮 높고 새벽 낮음). 같은 <b>시간대(time-of-day)</b>일수록 큰 가중치를 주는 phase 커널로 군집 일주기를 복원해 수준에 더한다. 하루는 1440분 <b>원</b>이라 circular 거리를 쓴다.</p>
<div class="formula">위상(tod) = Σ exp(−circ(φ,φ')²/2ℓ²)·dev(φ') / Σ exp(...)　,　circ(a,b)=min(|a−b|,1440−|a−b|)</div>
<div class="note"><b>E0 = 수준 + 위상.</b> 이 구조적 추정치가 days2-6 held-out에서 이미 일평균 BHS A에 근접(test 일 SBP 2.35 A·DBP 2.19 A). 이후 편차 모델은 이 위에서 <b>세션 DBP·일평균</b>을 더 깎는다.</div></div>

<div class="chap" id="c5"><div class="no">2-5</div><h2>와치 — 변수 하나하나 (핵심)</h2></div>
<div class="card">
<p>편차의 급성 동인은 <b>워치</b>다. 엑셀 26시트(Info·BP + 24개 신호)를 한 장씩 점검했다. 신호마다 <b>측정 빈도·해상도가 천차만별</b> — 분단위급(HR·에너지·METs·걸음)부터 sparse(HRV·SpO2·손목온도)까지. 아래는 120명 집계 기초통계.</p>
<table><tr><th class="l">워치 변수</th><th>단위</th><th>측정/주·명</th><th>커버%</th><th>평균±SD</th><th>범위</th><th>밀도</th></tr>
{wstat_rows()}</table>
<div class="note"><b>점검 포인트.</b> 손목온도는 커버리지 50%·주 3회로 가장 sparse하나 말초저항(TPR)의 대리로 이론적 중요도가 높다. SpO2는 decimal(1.0=100%) 코딩. 걸음은 평균보다 SD가 커(우편향) log 후보. 고밀도 신호는 분단위 feature로, sparse는 imputation으로 다룬다.</div>
<h3 style="margin-top:22px;color:#10463b">변수별 BP 관계 · 선행연구 레퍼런스</h3>
<p style="font-size:13px;color:#5d6b82">각 워치 변수가 혈압과 어떻게·왜 연결되는지(방향·기전)와 핵심 인용. (다중 에이전트 문헌조사 기반)</p>
{ref_blocks()}
</div>

<div class="chap" id="c6"><div class="no">편차</div><h2>편차 모델 — 와치 + 지난 BP 추정</h2></div>
<div class="card">
<p>E0를 고정하고 <b>편차 r = 실측 − E0</b>만 모델한다(잘 보정된 수준·위상을 다시 흔들지 않기 위해 residual mode). 입력은 <b>두 그룹</b> — 와치(급성 생리)와 지난 BP 추정(전날 동시각·과거일 동시각평균·과거일 평균, 실측 day2-6은 미사용).</p>
<div class="fig"><img src="fig_p2_ablation.png"><div class="cap">편차 ablation(검증 24명). <b>와치는 세션 DBP</b>(급성 생리)를, <b>지난 BP 추정은 일평균 SBP level</b>(사람 drift)을 줄인다. 둘은 상보적이라 <b>합쳐야</b> 모든 지표 최저. 어느 하나만으론 일부를 놓친다.</div></div>
<div class="win"><b>✅ 둘 다 기여 + 상보적.</b> 와치만 → 세션 DBP B→A. 지난추정만 → 일 SBP 2.35→2.09. 둘다 → 세션 SBP B·DBP A·일평균 최저를 동시에. 설계대로다.</div>
</div>

<div class="chap" id="c7"><div class="no">zoo</div><h2>전 모형 zoo — 20개, train/valid/test</h2></div>
<div class="card">
<p>같은 편차 과제에 <b>회귀·스펙트럴·웨이블릿·트리·GBM·딥러닝</b>을 single·multi로 올렸다(최종=E0+r̂). 셀 = <b>MAE + BHS등급</b>. days2-6, 검증·테스트 각 24명.</p>
<table>
<tr><th class="l" rowspan="2">모형</th><th colspan="4">검증 valid (596세션)</th><th colspan="4">테스트 test (580세션)</th></tr>
<tr><th>세SBP</th><th>세DBP</th><th>일SBP</th><th>일DBP</th><th>세SBP</th><th>세DBP</th><th>일SBP</th><th>일DBP</th></tr>
{zoo_rows()}
</table>
<div class="fig"><img src="fig_p2_zoo.png"><div class="cap">20모형 검증 MAE(계열색). <b>선형(회귀)·스펙트럴·웨이블릿</b>이 낮은 쪽에, <b>트리·GBM</b>이 높은 쪽에 모인다. 점선=E0 기준.</div></div>
<div class="win"><b>🏆 챔피언 = 회귀 Ridge</b> (≈ ElasticNet·Harmonic+Ridge, 선형 shrinkage). 검증 세션 SBP <span class="kpi">6.06 B</span>, 일평균 SBP <span class="kpi">3.59 A</span>·DBP <span class="kpi">2.33 A</span> — 전 계열 최저. 웨이블릿은 일평균에 강점, 세션엔 약점.</div>
</div>

<div class="chap" id="c8"><div class="no">진단</div><h2>과적합 — 단순 모형이 일반화한다</h2></div>
<div class="card">
<div class="fig"><img src="fig_p2_overfit.png"><div class="cap">학습 vs 검증 세션 SBP MAE. 대각선 아래로 멀수록 overfit. <b>트리·GBM</b>(LightGBM 학습 4.06→검증 7.05)은 학습을 외우고 held-out에서 붕괴. <b>회귀·스펙트럴</b>은 대각선 근처(학습 6.70→검증 6.06)로 안정.</div></div>
<div class="twist"><b>🌀 트리·GBM은 사람 패턴을 memorize.</b> 학습(in-sample)에선 최고(LightGBM 일DBP 0.76)지만 신규 사람(valid·test)에선 등급이 C/D로 추락. <b>딥러닝(MLP)</b>은 데이터가 1,792세션으로 늘어 선형에 근접 — 딥러닝은 데이터량 의존. 선택은 <b>valid 기준</b>으로, 트리·GBM 제외.</div>
</div>

<div class="chap" id="c9"><div class="no">∎</div><h2>결론 — 그리고 분단위 곡선</h2></div>
<div class="card">
<div class="win"><b>🏁 추정 최종.</b> E0(수준+위상)가 일평균을 BHS A로 잡고, 편차(와치+지난추정)가 세션 DBP·일평균을 더 깎는다. 챔피언 <b>회귀 Ridge</b> — 검증 세션 SBP 6.06 B / DBP 4.92 B, 일평균 SBP 3.59 A / DBP 2.33 A. 테스트 일평균 SBP 2.07 A·DBP 2.18 A.</div>
<div class="note"><b>분단위 예측모형.</b> 모형은 임의 분에서 E0와 r̂을 산출해 <b>분단위 혈압 곡선</b>을 그린다. 세션·일평균은 그 집계다. 다음 그림으로 한 환자의 분당 추정 곡선(수면·운동 구간 포함)을 보일 예정.</div>
<div class="twist"><b>→ PART 3 예측.</b> 비워둔 <b>day7</b>을 이 추정 모형으로 예측한다 — <b>정적(static)</b>: 하루 전체를 미리, <b>동적(dynamic)</b>: 분단위 nowcast. 추정(PART2)과 예측(PART3)은 t와 t−k의 관계로 이어진다.</div>
<p style="color:var(--muted);font-size:13px;margin-top:16px">120명 · 세션평균 하이브리드 보간 · 사람 60:20:20 · days2-6 추정 / day7 보류 · 수준(KNHANES+설문+day1)+위상+편차(와치+지난추정) · 20모형 single·multi · MAE+BHS · 세션·일평균</p>
<p><a href="part1.html" style="color:var(--teal);font-weight:700">← PART 1 보간</a> &nbsp;·&nbsp; <a href="part3.html" style="color:var(--teal);font-weight:700">PART 3 예측 →</a> &nbsp;·&nbsp; <a href="paper.html" style="color:var(--teal);font-weight:700">논문</a></p>
</div>
</div>
"""
HEAD="""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PART 2 · 혈압 추정(Nowcasting) — 수준·위상·편차, 20모형 zoo</title>
<meta property="og:title" content="🩺 PART 2 · 혈압 추정 — 수준+위상=E0, 편차=워치+지난추정, 20모형 MAE+BHS">
<meta property="og:description" content="신규환자 분단위 혈압 추정. 회귀 Ridge 챔피언(검증 일평균 SBP 3.59A/DBP 2.33A). 트리·GBM 과적합. 2-1~2-5, 와치 변수별 선행연구.">
<style>__CSS__</style></head><body>__BODY__</body></html>"""
html=HEAD.replace('__CSS__',CSS).replace('__BODY__',BODY)
open(SITE+'part2.html','w',encoding='utf-8').write(html)
print('SAVED part2.html', round(os.path.getsize(SITE+'part2.html')/1024,1),'KB · refs',len(REFS),'· models',len([n for n in ORDER if n in PRED]))
