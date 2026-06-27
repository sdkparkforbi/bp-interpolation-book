# -*- coding: utf-8 -*-
# FTF 토큰 서버 (로컬/온프레미스 테스트용). HeyGen 스트리밍 토큰을 서버에서 발급, 라이브 키 미노출.
# 실행: HEYGEN_LIVE_API_KEY=... python server_local.py   (포트 8788)
#       qna.html에서 window.HEYGEN_TOKEN_URL='http://localhost:8788/api/heygen-token' 지정(또는 같은 포트로 qna.html 서빙).
import os, json, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
KEY = os.environ.get('HEYGEN_LIVE_API_KEY', '')
class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()
    def do_POST(self):
        if self.path.rstrip('/') != '/api/heygen-token':
            self.send_response(404); self._cors(); self.end_headers(); return
        try:
            req = urllib.request.Request('https://api.heygen.com/v1/streaming.create_token',
                  data=b'', headers={'x-api-key': KEY, 'content-type': 'application/json'}, method='POST')
            d = json.load(urllib.request.urlopen(req, timeout=30))
            token = (d.get('data') or {}).get('token')
            body = json.dumps({'token': token} if token else {'error': 'no token'}).encode()
            self.send_response(200 if token else 502)
        except Exception as e:
            body = json.dumps({'error': str(e)}).encode(); self.send_response(500)
        self._cors(); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
if __name__ == '__main__':
    if not KEY: print('환경변수 HEYGEN_LIVE_API_KEY 가 필요합니다.')
    print('FTF token server on http://localhost:8788/api/heygen-token')
    HTTPServer(('0.0.0.0', 8788), H).serve_forever()
