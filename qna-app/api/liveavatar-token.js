// api/liveavatar-token.js
// LiveAvatar 세션 토큰 생성 + 세션 시작 (2단계 통합)

function corsHeaders(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
}

export default async function handler(req, res) {
  corsHeaders(res);

  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const LIVEAVATAR_API_KEY = process.env.LIVEAVATAR_API_KEY;
  if (!LIVEAVATAR_API_KEY) {
    return res.status(500).json({ error: "LIVEAVATAR_API_KEY not configured" });
  }

  try {
    const body = req.body || {};
    const avatarId = body.avatar_id;
    // 선택: 지식(RAG) 컨텍스트를 묶으려면 body.context_id 로 전달(없으면 null).
    const contextId = body.context_id || null;
    const interactivityType = body.interactivity_type || "CONVERSATIONAL";
    // voice_id 고정(요청): env에 의존하지 않고 dkpark 음성으로 박음. LiveAvatar는 voice_id를 avatar_persona 바로 아래에서 받음.
    // (body.voice_id로만 예외 override 가능. 잘못된 LIVEAVATAR_VOICE_ID env는 무시.)
    let voiceId = body.voice_id || "33868819-2331-4d2f-8b7d-dd589c82cead";
    if (!voiceId || voiceId === avatarId) voiceId = "33868819-2331-4d2f-8b7d-dd589c82cead";

    if (!avatarId) return res.status(400).json({ error: "avatar_id required" });

    const tokenRes = await fetch("https://api.liveavatar.com/v1/sessions/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": LIVEAVATAR_API_KEY,
      },
      body: JSON.stringify({
        mode: "FULL",
        avatar_id: avatarId,
        is_sandbox: false,
        video_settings: { quality: "medium", encoding: "H264" },
        avatar_persona: {
          context_id: contextId,
          language: "ko",
          ...(voiceId ? { voice_id: voiceId } : {}),
          voice_settings: { model: "eleven_flash_v2_5", speed: 1.0 },
          stt_config: { provider: "deepgram" },
        },
        interactivity_type: interactivityType,
      }),
    });

    const tokenData = await tokenRes.json();
    if (!tokenRes.ok || tokenData.code !== 1000) {
      return res.status(tokenRes.status).json({ error: "Token creation failed", detail: tokenData });
    }

    const sessionToken = tokenData.data.session_token;
    const sessionId = tokenData.data.session_id;

    const startRes = await fetch("https://api.liveavatar.com/v1/sessions/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + sessionToken,
      },
    });

    const startData = await startRes.json();
    if (!startRes.ok || startData.code !== 1000) {
      return res.status(startRes.status).json({ error: "Session start failed", detail: startData });
    }

    return res.status(200).json({
      session_id: sessionId,
      session_token: sessionToken,
      livekit_url: startData.data.livekit_url,
      livekit_client_token: startData.data.livekit_client_token,
    });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
