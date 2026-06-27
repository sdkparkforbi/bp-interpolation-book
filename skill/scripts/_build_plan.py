# -*- coding: utf-8 -*-
# 연구계획 공유용 self-contained HTML (개정2: 데이터·정제·보간 / 추정 / 예측 + 전 모형계열 + 시스템 + mock-up).
import base64, os, sys
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
A='C:/Temp/HYPT/ADAY_BP_Prediction_Model/'
def b64(p): return 'data:image/png;base64,'+base64.b64encode(open(p,'rb').read()).decode()
IMG={k:b64(A+v) for k,v in {'status':'_fig_data_status.png','varanat':'_fig_variability.png'}.items()}

SVG_FLOW='''<svg viewBox="0 0 880 120" width="100%" font-family="Malgun Gothic,sans-serif" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M2 1L8 5L2 9" fill="none" stroke="#888" stroke-width="1.5"/></marker></defs>
<rect x="8" y="38" width="104" height="46" rx="8" fill="#eef2f1" stroke="#b4b2a9"/><text x="60" y="66" text-anchor="middle" font-size="13" font-weight="700" fill="#444">연구계획</text>
<line x1="116" y1="61" x2="146" y2="61" stroke="#888" stroke-width="1.2" marker-end="url(#ar)"/>
<rect x="150" y="30" width="186" height="62" rx="8" fill="#f1efe8" stroke="#888780"/><text x="243" y="55" text-anchor="middle" font-size="14" font-weight="700" fill="#444441">PART 1</text><text x="243" y="74" text-anchor="middle" font-size="11.5" fill="#5f5e5a">데이터·정제·스플릿·보간</text>
<line x1="340" y1="61" x2="358" y2="61" stroke="#888" stroke-width="1.2" marker-end="url(#ar)"/>
<rect x="362" y="30" width="160" height="62" rx="8" fill="#e1f5ee" stroke="#1d9e75"/><text x="442" y="55" text-anchor="middle" font-size="14" font-weight="700" fill="#0f6e56">PART 2 · 추정</text><text x="442" y="74" text-anchor="middle" font-size="11.5" fill="#0f6e56">Nowcasting</text>
<line x1="526" y1="61" x2="544" y2="61" stroke="#888" stroke-width="1.2" marker-end="url(#ar)"/>
<rect x="548" y="30" width="160" height="62" rx="8" fill="#e6f1fb" stroke="#378add"/><text x="628" y="55" text-anchor="middle" font-size="14" font-weight="700" fill="#185fa5">PART 3 · 예측</text><text x="628" y="74" text-anchor="middle" font-size="11.5" fill="#185fa5">Forecasting</text>
<line x1="712" y1="61" x2="730" y2="61" stroke="#888" stroke-width="1.2" marker-end="url(#ar)"/>
<rect x="734" y="38" width="138" height="46" rx="8" fill="#eef2f1" stroke="#b4b2a9"/><text x="803" y="58" text-anchor="middle" font-size="12.5" font-weight="700" fill="#444">논문 · mock-up</text><text x="803" y="74" text-anchor="middle" font-size="10.5" fill="#777">GitHub 게시</text>
</svg>'''

SVG_SYS='''<svg viewBox="0 0 880 140" width="100%" font-family="Malgun Gothic,sans-serif" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ar2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M2 1L8 5L2 9" fill="none" stroke="#888" stroke-width="1.5"/></marker></defs>
<rect x="6" y="40" width="150" height="60" rx="8" fill="#e1f5ee" stroke="#1d9e75"/><text x="81" y="65" text-anchor="middle" font-size="13" font-weight="700" fill="#0f6e56">새 개인 + 설문</text><text x="81" y="84" text-anchor="middle" font-size="11" fill="#0f6e56">군집 판별</text>
<line x1="158" y1="70" x2="176" y2="70" stroke="#888" stroke-width="1.2" marker-end="url(#ar2)"/>
<rect x="180" y="40" width="150" height="60" rx="8" fill="#e1f5ee" stroke="#1d9e75"/><text x="255" y="65" text-anchor="middle" font-size="13" font-weight="700" fill="#0f6e56">군집 프로파일</text><text x="255" y="84" text-anchor="middle" font-size="11" fill="#0f6e56">기본 파라미터</text>
<line x1="332" y1="70" x2="350" y2="70" stroke="#888" stroke-width="1.2" marker-end="url(#ar2)"/>
<rect x="354" y="40" width="150" height="60" rx="8" fill="#faece7" stroke="#d85a30"/><text x="429" y="65" text-anchor="middle" font-size="13" font-weight="700" fill="#993c1d">1분 측정</text><text x="429" y="84" text-anchor="middle" font-size="11" fill="#993c1d">초기 BP 고정</text>
<line x1="506" y1="70" x2="524" y2="70" stroke="#888" stroke-width="1.2" marker-end="url(#ar2)"/>
<rect x="528" y="40" width="160" height="60" rx="8" fill="#e6f1fb" stroke="#378add"/><text x="608" y="65" text-anchor="middle" font-size="13" font-weight="700" fill="#185fa5">와치 분단위</text><text x="608" y="84" text-anchor="middle" font-size="11" fill="#185fa5">실시간 업데이트</text>
<line x1="690" y1="70" x2="708" y2="70" stroke="#888" stroke-width="1.2" marker-end="url(#ar2)"/>
<rect x="712" y="30" width="162" height="80" rx="8" fill="#0e3b35"/><text x="793" y="58" text-anchor="middle" font-size="13" font-weight="700" fill="#ffe08a">Nowcast 현재 BP</text><text x="793" y="80" text-anchor="middle" font-size="13" font-weight="700" fill="#8fe3d2">Forecast 1일 곡선</text>
<text x="440" y="128" text-anchor="middle" font-size="11.5" fill="#5d6b82">시나리오: 심한 운동 · 큰 충격 · 수면 부족 · 보행 부족 → 혈압이 어떻게 변하는지 알려줌</text>
</svg>'''

CSS='''
*{box-sizing:border-box} body{font-family:'Malgun Gothic','맑은 고딕',sans-serif;color:#1a2b28;line-height:1.7;background:#eef2f1;margin:0}
.wrap{max-width:940px;margin:0 auto;background:#fff;box-shadow:0 0 40px rgba(0,0,0,.10)}
header{background:#0e3b35;color:#fff;padding:40px 48px}
header h1{margin:0;font-size:30px} header .sub{color:#8fe3d2;margin-top:10px;font-size:16px} header .meta{color:#bfe8dc;margin-top:6px;font-size:13px}
.content{padding:6px 48px 80px}
h2{font-size:22px;color:#0f6e56;border-bottom:2px solid #d9ece7;padding-bottom:7px;margin-top:44px}
h3{font-size:16.5px;color:#13302b;margin-bottom:6px}
table{border-collapse:collapse;width:100%;font-size:14px;margin:14px 0}
th,td{border:1px solid #dde8e5;padding:8px 11px;text-align:left;vertical-align:top}
th{background:#eef7f3;color:#0f6e56;font-weight:700}
.best{background:#eafaf0;font-weight:700}
.hi{background:#effaf6;border-left:4px solid #16a085;padding:14px 18px;border-radius:6px;margin:16px 0}
.warn{background:#fff6ec;border-left:4px solid #c08a00;padding:14px 18px;border-radius:6px;margin:16px 0}
.fig{margin:18px 0;text-align:center} .fig img{max-width:100%;border:1px solid #e3ece9;border-radius:8px}
.cap{color:#5d6b82;font-size:13px;margin-top:7px;text-align:left}
code{background:#eef7f3;padding:2px 6px;border-radius:4px;font-size:13px;color:#0e3b35}
ol li,ul li{margin:7px 0} .diagram{margin:18px 0;padding:8px 0;border:1px solid #e3ece9;border-radius:10px;background:#fcfdfd}
.tag{display:inline-block;background:#0e3b35;color:#ffe08a;border-radius:6px;padding:2px 9px;font-size:12px;font-weight:700;margin-right:6px}
.topnav{background:#11463e;color:#cfeee3;padding:10px 48px;font-size:13.5px}
.topnav a{color:#8fe3d2;text-decoration:none;font-weight:700}
'''

BODY=f'''
<div class="topnav">📋 ADAY BP 연구 계획 &nbsp;|&nbsp; <a href="index.html">목차</a> &nbsp;|&nbsp; <a href="part1.html">PART 1</a> &nbsp;|&nbsp; <a href="part2.html">PART 2</a> &nbsp;|&nbsp; <a href="part3.html">PART 3</a> &nbsp;|&nbsp; <a href="paper.html">논문</a></div>
<header><h1>ADAY BP 연구 계획</h1>
<div class="sub">설문 + 워치로 혈압을 추정·예측한다 — 새 사람·전 국민으로, 누수 없이, 실측으로 평가.</div>
<div class="meta">개정 2 · 팀 공유용 · N=120 · 저자 이규성·차상현·성봉주·박대근·김효영</div></header>
<div class="content">

<h2>1. 개요와 PART 구조</h2>
<p>연구는 <b>데이터 &#8594; 추정 &#8594; 예측</b> 순서로 흐른다. 문서 흐름은 <b>연구계획 &#8594; PART 1 · 2 · 3 &#8594; 논문 · mock-up</b>.</p>
<div class="diagram">{SVG_FLOW}</div>
<table><tr><th>PART</th><th>일</th><th>내용</th></tr>
<tr><td>PART 1</td><td>데이터 · 정제 · 스플릿 · 보간</td><td>입수 &#8594; 정제(세션평균·이상점) &#8594; 분할(day1 튜닝 / day2~6 학습 60:20:20 / day7 예측) &#8594; <b>분단위 보간 타깃</b> 생성.</td></tr>
<tr class="best"><td>PART 2</td><td>추정 (estimation · Nowcasting)</td><td>군집 프로파일 + day1 보정 + 와치로 <b>현재 시점 BP를 추정</b> (새 사람 = cross-subject).</td></tr>
<tr class="best"><td>PART 3</td><td>예측 (prediction · Forecasting)</td><td>day2~6로 <b>day7(미래) 1일 곡선을 예측</b> (과거&#8594;미래 + cross-subject).</td></tr></table>

<h2>2. PART 1 — 데이터 · 정제 · 스플릿 · 보간</h2>
<div class="fig"><img src="{IMG['status']}"><div class="cap">데이터 현황 + 정제 + 분할 구조. 120명·8,195측정·워치 24종. 이상점 2건 제거 + 1분 2회 세션평균 &#8594; <b>4,169 세션</b>(개인내 SBP SD 7.97&#8594;7.26). day1 튜닝 / day2~6 학습 / day7 예측.</div></div>
<ol>
<li><b>정제</b> — 생리불가 이상점만 제거(SBP=12·DBP=17; 저혈압 가능값 유지), 연속 측정(&#916;t&#8804;3분)을 <b>세션평균</b>(시각=마지막).</li>
<li><b>분할</b> — <b>day1 = 튜닝</b>(초기 BP 보정용), <b>day2~6 = 학습</b>(사람 <b>60:20:20</b> train:valid:test), <b>day7 = 예측 타깃</b>(119명). 성과는 test의 <b>day7 실측점</b>에서만.</li>
<li><b>분단위 보간 타깃</b> — 측정 사이를 분단위로 채운 BP를 모형의 <b>타깃</b>으로 쓴다. <b>보간함수는 train 사람 day2~6에서만</b> 적합(군집 일주기), val·test·예측 구간엔 <b>적용만 하고 학습엔 미사용</b>.</li>
</ol>
<div class="warn"><b>누수 차단 규칙 (핵심).</b> 모형 입력에 <b>실측 과거 BP는 day1 튜닝을 제외하고 쓰지 않는다.</b> 설문·와치, 그리고 설문·와치로 <b>추정한 BP</b>는 입력 가능. <b>타깃 = 분단위 보간 BP</b>, <b>성과 측정 = 실측 BP에서만</b>(보간값으로 성과를 재지 않음).</div>

<h2>3. PART 2 — 추정 (Nowcasting) · 시스템</h2>
<p>새 사람이 와도 <b>설문으로 군집을 판별</b>하면 그 군집의 기본 파라미터 프로파일을 가져온다. <b>1분 실제 측정</b>으로 초기 BP를 고정하고, 와치 정보로 <b>분단위로 현재 BP를 업데이트</b>한다.</p>
<div class="diagram">{SVG_SYS}</div>
<div class="hi"><b>시스템 핵심.</b> 새 개인 &#8594; 설문 군집 &#8594; 기본 프로파일 &#8594; <b>1분 측정 = 초기 BP</b> &#8594; 와치 분단위 업데이트 &#8594; <b>Nowcast(현재) + Forecast(1일 곡선) 실시간</b>. 심한 운동·큰 충격·수면 부족·최근 보행 부족 시 혈압이 어떻게 변할지 알려준다.</div>

<h2>4. PART 3 — 예측 (Forecasting)</h2>
<p>학습된 모형으로 <b>day7의 1일 혈압 곡선을 통째로 예측</b>한다(그날 실측을 보지 않고 day2~6만으로). 현재(Nowcasting)와 미래(Forecasting)를 함께 — <b>현재 혈압과 미래 혈압을 정확히 알아보는 것</b>이 목표다.</p>

<h2>5. 모형 — 전 계열 총동원</h2>
<p>아는 모든 모형 계열을 single-task·multi-task로 비교한다.</p>
<table><tr><th>계열</th><th>모형</th><th>task</th></tr>
<tr><td>전통 시계열</td><td>AR · ARIMA · VAR · <b>VARX</b></td><td>single · multi(VAR/VARX)</td></tr>
<tr><td>회귀</td><td>Ridge · ElasticNet · 선형</td><td>single · multi</td></tr>
<tr><td>위상 스펙트럴</td><td>Harmonic/Fourier · 위상커널 · 합성커널(역시간×위상)</td><td>single · multi</td></tr>
<tr><td>Perceptron</td><td>MLP</td><td>single · multi</td></tr>
<tr><td>Tree</td><td>RandomForest · ExtraTrees · LightGBM · XGBoost · CatBoost · <b>MT-GBM</b></td><td>single · multi(MT-GBM)</td></tr>
<tr><td>Transformer</td><td>FT-Transformer · Sequence Transformer · <b>Multi-task Transformer</b></td><td>single · multi</td></tr></table>
<div class="hi"><b>Multi-task의 이점.</b> SBP·DBP를 <b>하나의 구조로 공유</b>해 동시 학습하면 두 출력이 <b>상호 제약</b>하여, 자연스럽게 <b>오버핏이 방지</b>된다(별도 두 모형보다 test에서 유리할 수 있음).</div>
<p style="font-size:13.5px;color:#5d6b82"><b>입력</b>: 설문 · 와치 · day1 튜닝 BP · (설문·와치로) 추정한 BP. <b>실측 과거 BP는 미사용</b>(day1 제외). <b>타깃</b>: 분단위 보간 BP. <b>평가</b>: day7 실측점.</p>

<h2>6. 평가 원칙</h2>
<div class="hi">
<b>1. 성과는 test의 실측 BP에서만</b> 측정한다(보간값으로 metric을 재지 않음).<br>
<b>2. Interpolation은 도구</b> — 타깃 생성·feature 정렬엔 자유, 평가 set만 실측으로 둔다.<br>
<b>3. Metric</b> = MAE + BHS, train/valid/test 분리.<br>
<b>4. 누수 차단</b> — 보간함수·모형은 train·day2~6에서만, day7은 적합에서 제외.
</div>
<div class="fig"><img src="{IMG['varanat']}"><div class="cap">측정 잡음 — 1분 2회 측정의 per-reading SD&#8776;4.8 mmHg. 세션평균이 이를 줄이고, 분단위 보간은 이 정제된 곡선을 타깃으로 삼는다. 성과는 항상 실측점에서.</div></div>

<h2>7. Mock-up (환자 대시보드)</h2>
<p>마지막에 <b>mock-up</b>을 만든다. <b>환자 ID를 선택하면 그 환자의 모든 내용</b>(프로파일·1일 BP 곡선 Nowcast/Forecast·시나리오 반응·성과)을 확인할 수 있는 대시보드. <b>GitHub에 만들어 게시</b>한다.</p>

<h2>8. 로드맵</h2>
<ol>
<li><b>PART 1</b> &#8212; 정제 ✓ · 분할 ✓ · 분단위 보간(1분 해상도 마무리 중).</li>
<li><b>PART 2 추정</b> &#8212; 군집 프로파일 + day1 보정 + 와치 Nowcasting.</li>
<li><b>PART 3 예측</b> &#8212; 전 모형계열(single·multi) day7 Forecasting.</li>
<li><b>Mock-up</b> &#8212; 환자 대시보드 → GitHub 게시.</li>
<li><b>문서</b> &#8212; PART 1·2·3 그림책 + 논문 갱신·게시.</li>
</ol>

<h2>9. 한계와 산출물</h2>
<ul>
<li>분단위 순간 BP는 <b>measurement error(per-reading SD&#8776;4.8) + 개인 내 생리</b>가 정밀도 한계를 정함. 임상 가치는 <b>일평균·1일 곡선</b>에 무게.</li>
<li>cuffless의 임상 진단 사용은 권고되지 않음(AHA/ACC 2025) &#8594; <b>연구·추세 추정</b>으로 포지셔닝. 통계적 유의성으로 판단.</li>
<li><b>산출물</b>: PART 1·2·3 그림책 · 논문(저자 이규성·차상현·성봉주·박대근·김효영, 저널 TBD) · 환자 대시보드 mock-up · 파이프라인 코드.</li>
</ul>

</div>'''

HEAD='''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ADAY BP 연구 계획 — 데이터·추정·예측</title>
<meta property="og:type" content="article">
<meta property="og:title" content="ADAY BP 연구 계획 — 데이터·정제·보간 / 추정 / 예측">
<meta property="og:description" content="PART1 데이터·정제·스플릿·보간 / PART2 추정(Nowcasting) / PART3 예측(Forecasting). 전 모형계열(시계열·회귀·스펙트럴·perceptron·tree·transformer × single·multi). 설문 군집 프로파일+1분 초기BP+와치 분단위 업데이트로 1일 곡선 실시간. 평가는 실측에서만. 환자 대시보드 mock-up. N=120.">
<meta property="og:image" content="https://sdkparkforbi.github.io/bp-interpolation-book/thumbnail_plan.png">
<style>__CSS__</style></head><body><div class="wrap">__BODY__</div></body></html>'''
HTML=HEAD.replace('__CSS__',CSS).replace('__BODY__',BODY)
for out in ['C:/Temp/HYPT/book_site/plan.html','C:/Temp/HYPT/ADAY_BP_Prediction_Model/연구계획.html']:
    open(out,'w',encoding='utf-8').write(HTML)
print('SAVED book_site/plan.html', round(os.path.getsize('C:/Temp/HYPT/book_site/plan.html')/1024/1024,2),'MB')
