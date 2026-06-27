// HeyGen LiveAvatar 스트리밍 토큰 발급 (서버 사이드) — Vercel 서버리스 함수.
// 라이브 키는 서버 환경변수(HEYGEN_LIVE_API_KEY)에만 두고 절대 클라이언트에 노출하지 않는다.
// 배포: 이 파일을 Vercel 프로젝트의 api/heygen-token.js 로 두고, 환경변수 HEYGEN_LIVE_API_KEY 설정.
//       qna.html을 같은 도메인에 올리면 /api/heygen-token 으로 자동 연결.
//       다른 도메인이면 qna.html에서 window.HEYGEN_TOKEN_URL = 'https://your-app.vercel.app/api/heygen-token' 지정.
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(200).end();
  try {
    const r = await fetch('https://api.heygen.com/v1/streaming.create_token', {
      method: 'POST',
      headers: { 'x-api-key': process.env.HEYGEN_LIVE_API_KEY, 'content-type': 'application/json' },
    });
    const d = await r.json();
    const token = d && d.data && d.data.token;
    if (!token) return res.status(502).json({ error: 'no token', detail: d });
    return res.status(200).json({ token });
  } catch (e) {
    return res.status(500).json({ error: String(e) });
  }
}
