# FTF (Face-to-Face) 라이브 아바타 — 토큰 서버

QnA의 **FTF 모드**(반듯이 라이브 영상 대화)는 HeyGen 스트리밍 토큰이 필요합니다. 라이브 키(`HEYGEN_LIVE_API_KEY`)는 **서버에서만** 쓰고 클라이언트에 노출하지 않습니다. 그래서 토큰 발급 엔드포인트가 필요합니다(참고 사이트가 Vercel 앱인 이유).

## 동작 구조

```
브라우저(qna.html FTF)  --POST-->  /api/heygen-token  --x-api-key-->  HeyGen streaming.create_token
        |  <-- {token} --                 (서버, 키 보유)
        └─ @heygen/streaming-avatar SDK 로 LiveAvatar(dkpark) 영상·음성 대화
```

- TTT(텍스트)·STS(음성)는 토큰 없이 정적 페이지에서 바로 작동
- FTF만 토큰 서버 필요

## 1) Vercel 배포 (권장)

1. 새 Vercel 프로젝트에 `api/heygen-token.js`를 두고, `qna.html`을 같은 프로젝트로 올린다.
2. 환경변수 `HEYGEN_LIVE_API_KEY` 설정.
3. 같은 도메인이면 `/api/heygen-token`로 자동 연결. 끝.

## 2) 로컬/온프레미스 테스트

```
HEYGEN_LIVE_API_KEY=라이브키 python server_local.py     # http://localhost:8788/api/heygen-token
```
`qna.html`을 열기 전(또는 콘솔에서):
```js
window.HEYGEN_TOKEN_URL = 'http://localhost:8788/api/heygen-token';
```

## 설정값

- 라이브 아바타: `window.HEYGEN_LIVE_AVATAR_ID` (기본 dkpark = `3303593d-4571-486f-a82d-35056b0d2e2c`)
- 지식: qna.html 안 `KB_TEXT`(knowledgeBase). 더 풍부하게는 `../heygen_knowledge.md`를 labs.heygen.com Knowledge Base로 등록해 `knowledgeId` 사용
- SDK: `@heygen/streaming-avatar` (CDN esm.sh)

> 주의: 라이브 키를 **절대** 정적 페이지·저장소에 커밋하지 마세요. 서버 환경변수로만.
