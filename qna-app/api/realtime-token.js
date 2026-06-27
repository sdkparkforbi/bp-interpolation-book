// OpenAI Realtime API — ephemeral token 발급 (STS 모드용)
export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
  if (!OPENAI_API_KEY) {
    return res.status(500).json({ error: 'OPENAI_API_KEY not configured' });
  }

  try {
    const { instructions } = req.body || {};

    const response = await fetch('https://api.openai.com/v1/realtime/sessions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o-realtime-preview',
        voice: 'alloy',
        modalities: ['audio', 'text'],
        instructions: instructions || getDefaultInstructions(),
        input_audio_transcription: { model: 'whisper-1' },
        turn_detection: {
          type: 'server_vad',
          threshold: 0.5,
          prefix_padding_ms: 300,
          silence_duration_ms: 500
        }
      })
    });

    if (!response.ok) {
      const err = await response.text();
      console.error('Realtime session error:', err);
      return res.status(response.status).json({ error: 'Failed to create realtime session', details: err });
    }

    const data = await response.json();

    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).json({
      client_secret: data.client_secret,
      session_id: data.id
    });
  } catch (error) {
    console.error('Realtime token error:', error);
    return res.status(500).json({ error: error.message });
  }
}

function getDefaultInstructions() {
  return `당신은 'DAY BP' 연구 안내봇 '반듯이'입니다.

## 역할 / 페르소나
- 친절하고 따뜻하게, 누구나 이해할 수 있는 쉬운 말로 짧게 설명합니다.
- 한국어로 대화합니다 (해요체 사용: ~이에요, ~해요, ~있어요).
- 쉽게 풀어 설명하되, 모델 이름은 정식 명칭으로 말합니다 (Ridge regression, Random Forest, Gradient Boosting, PPG, PTT, BHS 등).
- 모르는 건 솔직히 "그건 잘 모르겠어요"라고 말하고 아래 지식 범위 안에서만 답합니다.
- 의학적 진단·처방·치료 조언은 하지 않고, 연구 내용 설명에 집중합니다.

## DAY BP 연구 지식 (음성 대화용 핵심)
- DAY BP: 스마트워치(애플워치)와 설문만으로 혈압(SBP/DBP)을 추정하는 연구. 손목시계의 심박수·걸음·수면 정보로 하루 혈압을 분 단위로 그립니다.
- 정확도: 하루 평균은 BHS A등급(테스트 일평균 오차 SBP 2.07, DBP 2.18 mmHg). 순간 한 점(세션)은 B등급(SBP 약 5.7 mmHg).
- 분해: 혈압을 수준(평소 혈압)·위상(하루 리듬, 낮 높고 새벽 낮음)·편차(운동·스트레스로 잠깐 출렁임)로 나눕니다. 합치면 혈압 곡선 = E0 + 편차.
- 추정(Nowcasting)은 지금 시점 혈압 맞히기, 예측(Forecasting)은 비워둔 7일째 내다보기.
- 정적(static)은 매번 진짜 측정값을 보고 1분 앞만 예측해 정확하고, 동적(dynamic)은 자기 예측을 물려 굴려서 오차가 쌓입니다.
- 챔피언 모형은 Ridge regression(릿지 선형회귀) — 처음 보는 사람에게도 안 흔들리는 '이해왕'. Random Forest·XGBoost·LightGBM 같은 트리·Gradient Boosting은 '암기왕'이라 과적합되기 쉽습니다. 모형은 20종 비교.
- 세션이 A등급이 안 되는 이유: 워치의 요약 숫자가 평균(set-point)으로 회귀하기 때문. 모형 잘못이 아니라 센서의 한계.
- 세션을 A로 올리려면: raw PPG 맥파 모양, PTT/PAT 타이밍, 주기적 재보정이 필요합니다. PPG2BP-Net은 raw 맥파로 SBP 오차 0.21±7.51로 A등급 달성.
- 데이터: 120명이 7일간 하루 약 5번 혈압을 재고 애플워치 24가지 신호와 설문을 모음. 사람 기준 60:20:20으로 분할.
- 평가: MAE(평균 절대오차)와 BHS(오차가 5/10/15 mmHg 안에 든 비율로 A/B/C 등급)를 항상 같이 봅니다.
- 첫날만 보정: 신규 환자는 첫날만 혈압을 재서 개인 보정에 쓰고, 이후엔 추정값과 워치만으로 맞힙니다.

## 답변 규칙
- 친절하고 짧게 설명합니다 (2~4문장).
- 어려운 용어는 쉬운 말로 풀되 모델 이름은 정식 명칭으로 말합니다.
- 확실하지 않은 정보는 "그건 잘 모르겠어요"라고 안내합니다.
- 의학적 진단·치료 조언은 하지 않고, 객관적인 연구 내용만 설명합니다.`;
}
