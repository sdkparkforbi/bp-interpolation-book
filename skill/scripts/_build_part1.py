# -*- coding: utf-8 -*-
# PART 1 (개정) — 데이터·정제·스플릿·보간. 새 파이프라인(4169세션·72:24:24·분단위 하이브리드 보간) + 120명 그림. 팀 공유용.
import base64, os, sys
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
A='C:/Temp/HYPT/ADAY_BP_Prediction_Model/'
def b64(p): return 'data:image/png;base64,'+base64.b64encode(open(p,'rb').read()).decode()
IMG={k:b64(A+v) for k,v in {
 'status':'_fig_data_status.png','noise':'_fig_variability.png',
 'interp':'_fig_interp_minute.png','i120s':'_fig_interp_120_SBP.png','i120d':'_fig_interp_120_DBP.png',
}.items()}
def im(k): return IMG[k]

CSS='''
:root{--ink:#16232b;--muted:#5d6b82;--bg:#0b1722;--paper:#fbfdfe;--accent:#2b6cb0;--deep:#13334a}
*{box-sizing:border-box} body{margin:0;font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;color:var(--ink);background:var(--bg);line-height:1.8}
.hero img{width:100%;display:block}
.nav{background:var(--deep);color:#fff;padding:10px 22px;font-size:14px}.nav a{color:#8fd0f0;text-decoration:none;font-weight:700}
.wrap{max-width:980px;margin:0 auto;background:var(--paper);padding:0 22px 90px;box-shadow:0 0 60px rgba(0,0,0,.5)}
h1{font-size:30px}.toc{font-size:13.5px;color:var(--accent);margin:4px 0 0}.toc a{color:var(--accent);text-decoration:none;margin:0 9px 0 0;white-space:nowrap;display:inline-block}
.chap{display:flex;align-items:center;gap:12px;margin:52px 0 6px}.chap .no{flex:none;width:46px;height:46px;border-radius:50%;background:var(--accent);color:#fff;font-weight:800;font-size:19px;display:flex;align-items:center;justify-content:center}.chap h2{font-size:23px;margin:0}
.card{background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.08);padding:22px 26px;margin:16px 0}
.fig{text-align:center;margin:14px 0}.fig img{max-width:100%;border:1px solid #e3e9ee;border-radius:10px}.cap{color:var(--muted);font-size:13px;margin-top:7px;text-align:left;padding:0 4px}
.lead{font-size:18px;color:#1b3447;background:#eef6fc;border:1px dashed var(--accent);border-radius:12px;padding:18px 22px;margin:20px 0}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:12px 0}th,td{border:1px solid #e3e9ee;padding:6px 9px;text-align:center}th{background:#eef4fa}td.l,th.l{text-align:left}.best{background:#fff6cf;font-weight:800}
.note{background:#eef6fc;border-left:5px solid var(--accent);padding:12px 16px;border-radius:8px;margin:12px 0;font-size:14px}
.win{background:#eefaf0;border-left:5px solid #1e7d4f;padding:12px 16px;border-radius:8px;margin:12px 0}
.warn{background:#fff6ec;border-left:5px solid #c08a00;padding:12px 16px;border-radius:8px;margin:12px 0}
.steps{counter-reset:s;list-style:none;padding-left:0}.steps li{counter-increment:s;margin:12px 0;padding-left:46px;position:relative}.steps li::before{content:counter(s);position:absolute;left:0;top:0;width:32px;height:32px;background:var(--accent);color:#fff;border-radius:50%;text-align:center;line-height:32px;font-weight:700}
'''

BODY=f'''
<div class="hero"><img src="thumbnail_part1.png" alt="표지"></div>
<div class="nav">🧱 PART 1 · 데이터 · 정제 · 스플릿 · 보간 &nbsp;|&nbsp; <a href="plan.html">📋 연구계획</a> &nbsp;|&nbsp; <a href="part2.html">PART 2</a> &nbsp;|&nbsp; <a href="part3.html">PART 3</a> &nbsp;|&nbsp; <a href="paper.html">논문</a></div>
<div class="wrap">
<h1>🧱 데이터에서 분단위 혈압 곡선까지</h1>
<p class="toc">📑 <a href="#c1">1. 데이터 현황</a><a href="#c2">2. 정제</a><a href="#c3">3. 분할</a><a href="#c4">4. 분단위 보간</a><a href="#c5">5. 120명 전부</a><a href="#c6">6. 다음 — 추정·예측의 타깃</a></p>

<div class="lead"><b>PART 1.</b> 모든 분석의 토대. 띄엄띄엄 측정된 혈압을 <b>입수 &#8594; 정제 &#8594; 분할 &#8594; 분단위 보간</b>해, 모형이 학습할 <b>깨끗한 분단위 혈압 곡선</b>을 만든다. 핵심은 <b>누수 차단</b> — 보간함수와 모형은 학습 구간에서만 만들고, <b>성과는 끝까지 실측에서만</b> 잰다.</div>

<div class="chap" id="c1"><div class="no">1</div><h2>데이터 현황 — 무엇을 가지고 있나</h2></div>
<div class="card">
<p>120명에게서 <b>7일간 하루 약 5세션(2회씩)</b>, 총 <b>8,195 측정</b>. 각 측정엔 참조 SBP·DBP·맥박과 <b>워치 24종</b>(심박·심박변이·혈중산소·호흡·활동·걸음·수면·손목온도 등)이 함께 기록된다.</p>
<div class="fig"><img src="{im('status')}"><div class="cap">데이터 현황 + 정제 + 분할 구조. 사람당 중앙 7일·70측정, 워치 대부분 100% 커버리지(손목온도 50%·보행안정성 76% 등 일부 낮음). BP 분포 SBP 113&#177;14 / DBP 75&#177;9.</div></div>
</div>

<div class="chap" id="c2"><div class="no">2</div><h2>정제 — 이상점과 측정 잡음</h2></div>
<div class="card">
<p>두 가지를 정리한다. <b>① 명백한 이상점</b>(생존 불가값 SBP=12·DBP=17) 2건만 제거 — 저혈압 가능값(SBP=68 등)은 유지한다. <b>② 1분 간격 2회 측정을 세션평균</b>(시각=마지막)으로 묶는다.</p>
<div class="win"><b>왜 세션평균인가.</b> 같은 사람을 1분 간격으로 두 번 재도 값이 다르다 &#8212; 혈압계도 체중계처럼 잴 때마다 흔들린다(<b>per-reading SD &#8776; 4.8 mmHg</b>). 2회 평균이 이 측정 잡음을 줄인다: <b>8,193 측정 &#8594; 4,169 세션</b>, 개인 내 SBP SD <b>7.97 &#8594; 7.26</b>.</div>
<div class="fig"><img src="{im('noise')}"><div class="cap">측정 잡음의 해부. 1분 쌍의 차이로 per-reading SD&#8776;4.8(SBP)을 추정. 세션평균이 이를 줄이고, 이후 보간은 이 정제된 세션값을 앵커로 삼는다.</div></div>
</div>

<div class="chap" id="c3"><div class="no">3</div><h2>분할 — 누가 학습이고 무엇이 평가인가</h2></div>
<div class="card">
<p>두 축으로 나눈다. <b>날짜</b>: day1=튜닝(초기 BP 보정), day2~6=학습, day7=예측 타깃. <b>사람</b>: <b>60:20:20</b> train:valid:test(72:24:24명).</p>
<table>
<tr><th class="l">역할</th><th>구간</th><th>쓰임</th></tr>
<tr><td class="l">튜닝</td><td>day 1</td><td>새 사람의 초기 BP 보정(개인 앵커)</td></tr>
<tr><td class="l">학습</td><td>day 2&#8211;6</td><td>보간함수·모형 적합 (사람 60:20:20)</td></tr>
<tr class="best"><td class="l">예측 타깃</td><td>day 7</td><td>성과 측정 (test 24명, <b>실측점에서만</b>)</td></tr>
</table>
<div class="warn"><b>누수 차단 규칙(핵심).</b> 보간함수와 모형은 <b>train 사람의 day2~6에서만</b> 적합한다. val·test·예측(day7) 구간엔 <b>보간함수를 적용만</b> 하고 학습엔 쓰지 않는다. 모형 입력에 <b>실측 과거 BP는 day1 튜닝을 빼고 쓰지 않으며</b>(설문·워치·추정 BP는 가능), <b>성과는 끝까지 실측 BP에서만</b> 잰다.</div>
</div>

<div class="chap" id="c4"><div class="no">4</div><h2>분단위 보간 — 띄엄띄엄을 곡선으로</h2></div>
<div class="card">
<p>하루 5세션을 <b>분단위(1,440분) 곡선</b>으로 채운다. 방식은 <b>하이브리드 시계열</b>:</p>
<ol class="steps">
<li><b>실측이 있는 분</b>은 그대로 <b>실측값</b>을 쓴다(곡선이 측정점을 정확히 통과).</li>
<li><b>사이의 분</b>은 그 날의 세션 앵커 + <b>군집(연령&#215;성별) 일주기</b>로 채운다(앵커 가까이엔 앵커, 멀어지면 일주기).</li>
<li><b>군집 일주기(보간함수)</b>는 <b>train 사람 day2~6에서만</b> 추정 &#8212; 누수 없음.</li>
</ol>
<div class="fig"><img src="{im('interp')}"><div class="cap">샘플 test 환자의 7일 분단위 보간 곡선 + 실측 세션(검정). 곡선이 모든 실측점을 통과하고 사이를 일주기 모양으로 채운다. 주황=day1 튜닝, 초록=학습, 빨강=day7 예측. 실측 분에서 \|보간&#8722;실측\|=0.</div></div>
<div class="win"><b>✅ 결과.</b> 1,236,960행(120명 &#215; 7일 &#215; 1,440분)의 분단위 하이브리드 타깃. 실측은 보존, 사이는 매끄럽게. 이것이 PART 2·3 모형의 <b>학습 타깃</b>이 된다(평가는 실측점에서만).</div>
</div>

<div class="chap" id="c5"><div class="no">5</div><h2>120명 전부</h2></div>
<div class="card">
<p>전 대상자의 분단위 보간 곡선. 곡선(보간)이 점(실측)을 지나며, 각 사람의 하루 리듬을 복원한다.</p>
<div class="fig"><img src="{im('i120s')}"><div class="cap">120명 분당 하이브리드 보간 — <b>SBP</b>. 패널 제목=ID·split(tr/va/te). 주황 day1 / 초록 학습 / 빨강 day7.</div></div>
<div class="fig"><img src="{im('i120d')}"><div class="cap">120명 분당 하이브리드 보간 — <b>DBP</b>.</div></div>
</div>

<div class="chap" id="c6"><div class="no">∎</div><h2>다음 — 이 곡선이 추정·예측의 타깃</h2></div>
<div class="card">
<div class="note"><b>PART 1이 만든 것</b> &#8212; 정제된 <b>4,169 세션</b>, 누수 없는 <b>분할</b>, 그리고 <b>분단위 하이브리드 보간 타깃</b>. 이 토대 위에서:</div>
<ul>
<li><b>PART 2 · 추정 (Nowcasting)</b> &#8212; 설문 군집 프로파일 + day1 보정 + 와치로 <b>현재 시점 BP</b>를 추정. <a href="part2.html">보러 가기 →</a></li>
<li><b>PART 3 · 예측 (Forecasting)</b> &#8212; day2~6로 <b>day7 1일 곡선</b>을 예측. <a href="part3.html">보러 가기 →</a></li>
</ul>
<p style="color:var(--muted);font-size:13px;margin-top:14px">120명 &#215; 7일 · 정제(이상점 2건·세션평균) · 분할(day1 튜닝/day2~6 학습 60:20:20/day7 예측) · 분단위 하이브리드 보간(실측 보존+군집 일주기, 보간함수 train만) · 평가는 day7 실측점에서만 · 전체 설계는 <a href="plan.html" style="color:var(--accent)">연구 계획</a>.</p>
</div>
</div>'''

HEAD='''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PART 1 · 데이터·정제·스플릿·보간 — 분단위 혈압 곡선</title>
<meta property="og:type" content="article">
<meta property="og:title" content="🧱 PART 1 · 데이터에서 분단위 혈압 곡선까지">
<meta property="og:description" content="입수→정제(이상점·세션평균 4,169세션)→분할(day1 튜닝/day2~6 학습 60:20:20/day7 예측)→분단위 하이브리드 보간(실측 보존+군집 일주기, 보간함수 train만). 누수차단·평가는 실측에서만. 120명.">
<meta property="og:image" content="https://sdkparkforbi.github.io/bp-interpolation-book/thumbnail_part1.png">
<style>__CSS__</style></head><body>__BODY__</body></html>'''
html=HEAD.replace('__CSS__',CSS).replace('__BODY__',BODY)
open('C:/Temp/HYPT/book_site/part1.html','w',encoding='utf-8').write(html)
print('SAVED part1.html', round(os.path.getsize('C:/Temp/HYPT/book_site/part1.html')/1024/1024,2),'MB')
