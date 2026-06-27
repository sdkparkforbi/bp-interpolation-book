# DAY BP · AI 안내소 (qna-app)

스마트워치로 하루 혈압을 추정하는 **DAY BP** 연구를 안내하는 3-모드 AI 챗봇입니다.
안내봇 **반듯이**가 친절하고 쉬운 말로(단, 모델 이름은 정식 명칭으로) DAY BP 연구를 설명합니다.

- **TTT (글로 묻기)** — 텍스트 채팅. OpenAI `gpt-4o-mini`.
- **STS (음성 대화)** — OpenAI Realtime API, 브라우저에서 WebRTC로 실시간 음성 대화.
- **FTF (아바타와)** — LiveAvatar + LiveKit 인터랙티브 아바타와 얼굴 보며 대화.

> 이 앱은 의학적 진단·처방이 아니라 **연구 설명용**입니다.

---

## 구조

```
qna-app/
├── api/                       # Vercel Serverless Functions (ESM, export default handler)
│   ├── openai-chat.js         # TTT/FTF 공용 — gpt-4o-mini, DAY BP 지식. JSON {reply, ttsReply, action:"none"}
│   ├── realtime-token.js      # STS — OpenAI Realtime ephemeral 토큰 발급 (반듯이 persona)
│   ├── liveavatar-token.js    # FTF — LiveAvatar 세션 토큰 발급 + 세션 시작 (livekit_url/client_token 반환)
│   └── liveavatar-session.js  # FTF — 세션 keep-alive / stop
├── public/
│   └── index.html             # 프론트엔드 (HTML+CSS+JS 통합, 인트로 영상 + 3 모드 탭 + 채팅)
├── vercel.json                # 라우팅 (/api/* → 함수, /* → public)
└── README.md
```

소개 영상은 `public/index.html`에서 `heygen_intro.mp4`(같은 `public/` 폴더)로 임베드됩니다. 원본은 `book_site/heygen_intro.mp4`이며 배포 시 정적 서빙되도록 `public/heygen_intro.mp4`로 복사해 두었습니다. 영상을 갱신하면 `public/`의 사본도 함께 갱신하세요.

---

## 환경변수 (Vercel)

Vercel 프로젝트 → **Settings → Environment Variables** 에 등록하세요. 키는 절대 코드/깃에 커밋하지 마세요.

| 변수 | 필요한 모드 | 용도 |
|------|-------------|------|
| `OPENAI_API_KEY` | **TTT + STS** | `gpt-4o-mini`(텍스트 채팅) + Realtime API(음성 대화) ephemeral 토큰 발급 |
| `LIVEAVATAR_API_KEY` | **FTF** | LiveAvatar 세션 토큰 발급 / keep-alive / stop |
| `LIVEAVATAR_VOICE_ID` | **FTF** | ElevenLabs 음성 ID(voice_id). LiveAvatar `context_id`를 쓰면 생략 가능 |
| `AVATAR_ID` | **FTF** | LiveAvatar 아바타 UUID (프론트 상수, 기본 dkpark) |

- **TTT만 쓰려면** `OPENAI_API_KEY` 하나면 됩니다.
- **STS(음성)** 도 `OPENAI_API_KEY` 만 있으면 됩니다 (Realtime 세션이 같은 키로 발급).
- **FTF(아바타)** 는 `LIVEAVATAR_API_KEY` + `AVATAR_ID` (+ `LIVEAVATAR_VOICE_ID` 또는 context) 가 있어야 동작합니다.

> **이 프로젝트 .env 매핑:** `LIVEAVATAR_API_KEY` = `HEYGEN_LIVE_API_KEY`(값 동일), `AVATAR_ID` = `HEYGEN_LIVE_AVATAR_ID` = `3303593d-4571-486f-a82d-35056b0d2e2c`(dkpark — **이미 index.html 기본값으로 설정됨**). FTF 발화 음성은 `LIVEAVATAR_VOICE_ID`(ElevenLabs)를 넣거나 LiveAvatar 워크스페이스 `context_id`를 사용. (이 키로 LiveAvatar 인증 통과 검증 완료 — 세션 생성 시 voice_id/context_id만 지정하면 작동.)

모든 키는 `api/*.js` 안에서 `process.env`로만 읽습니다. 프론트엔드(`index.html`)에는 어떤 비밀키도 들어가지 않습니다.

---

## AVATAR_ID 설정 (FTF)

아바타 UUID는 프론트엔드에서 JS 상수로 주입합니다. `public/index.html`에 다음과 같이 되어 있습니다:

```js
const AVATAR_ID = window.AVATAR_ID || '3303593d-4571-486f-a82d-35056b0d2e2c'; // dkpark 기본
```

기본값은 **dkpark**(`HEYGEN_LIVE_AVATAR_ID`)로 이미 설정돼 있습니다. 다른 아바타를 쓰려면:

1. **직접 수정** — `index.html`의 위 UUID를 다른 LiveAvatar 아바타 UUID로 교체.
2. **런타임 주입** — `index.html`의 `<head>` 또는 `<body>` 위쪽에 다음 한 줄을 추가:
   ```html
   <script>window.AVATAR_ID = '여기에-아바타-UUID';</script>
   ```
   (Vercel 환경변수 `AVATAR_ID`를 빌드 단계에서 이 줄에 주입하도록 구성할 수도 있습니다.)

`AVATAR_ID`가 placeholder 그대로면 FTF 시작 시 "AVATAR_ID가 설정되지 않았어요" 안내가 뜨고 세션을 시작하지 않습니다. (TTT/STS는 영향 없음.)

---

## 배포 (Vercel)

1. 이 `qna-app/` 폴더(또는 `heygen_intro.mp4`를 포함한 상위 폴더)를 Vercel 프로젝트로 연결합니다.
   - 영상 임베드 경로가 `../heygen_intro.mp4`이므로, `heygen_intro.mp4`가 정적으로 서빙되는 위치를 확인하세요.
2. 위 표의 환경변수를 등록합니다 (`OPENAI_API_KEY` 필수, FTF 쓰면 `LIVEAVATAR_API_KEY` + `AVATAR_ID`).
3. 배포하면 `vercel.json`의 rewrites에 따라:
   - `/api/*` → 서버리스 함수
   - 그 외 모든 경로 → `public/*`
4. 빌드 설정은 별도 프레임워크 없이 정적 + 서버리스 함수만으로 동작합니다.

---

## 로컬 개발

Vercel CLI를 쓰면 서버리스 함수까지 로컬에서 그대로 실행됩니다:

```bash
npm i -g vercel
cd qna-app
# .env.local 또는 셸 환경에 키 설정 (커밋 금지!)
#   OPENAI_API_KEY=sk-...
#   LIVEAVATAR_API_KEY=...
#   AVATAR_ID=...
vercel dev
```

- **STS / FTF는 HTTPS 또는 localhost가 필요**합니다 — 마이크 권한(getUserMedia)과 WebRTC가 secure context에서만 동작합니다. `vercel dev`의 `localhost`는 secure context로 취급되어 정상 동작합니다.
- 정적 파일만 빠르게 보려면 아무 정적 서버(`npx serve public` 등)로 `index.html`을 열 수 있지만, 이 경우 `/api/*` 함수가 없어 채팅/음성/아바타는 동작하지 않습니다.

---

## 요청/응답 계약 (참고)

- `POST /api/openai-chat`
  - 요청: `{ "message": "...", "history": [{role, content}, ...] }`
  - 응답: `{ "reply": "...", "ttsReply": "...", "action": "none" }`
    - `ttsReply`는 영어 약어를 한글 발음으로 변환 (BHS→비에이치에스, PPG→피피지, PTT→피티티, Ridge→릿지 등). TTS/아바타 발화에 사용.
    - DAY BP에는 상품/카테고리 페이지가 없으므로 `action`은 항상 `"none"`.
- `POST /api/realtime-token`
  - 요청: `{}` (선택적으로 `{ "instructions": "..." }`)
  - 응답: `{ "client_secret": { "value": "ek_..." }, "session_id": "sess_..." }`
  - 프론트엔드는 `client_secret.value`로 `https://api.openai.com/v1/realtime` 에 SDP offer를 보내 WebRTC 연결을 맺습니다.
- `POST /api/liveavatar-token`
  - 요청: `{ "avatar_id": "...", "interactivity_type": "CONVERSATIONAL" }`
  - 응답: `{ "session_id", "session_token", "livekit_url", "livekit_client_token" }`
  - 프론트엔드는 `livekit_url` + `livekit_client_token`으로 `Room.connect`.
- `POST /api/liveavatar-session`
  - 요청: `{ "action": "keep-alive" | "stop", "session_id": "...", "reason"?: "..." }`

---

## 보안

- **API 키를 코드/깃에 절대 커밋하지 마세요.** 모든 키는 Vercel 환경변수 → `process.env`로만 사용합니다.
- 프론트엔드에는 비밀키가 없습니다. STS는 서버가 발급한 **ephemeral** 토큰(`ek_...`)만 브라우저로 전달합니다.
