import os
import sys
import json
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def load_env():
    env_path = os.path.join(DIRECTORY, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

class DevilServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == '/api/curriculum-data':
            json_path = os.path.join(DIRECTORY, 'curriculum_data.json')
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json_response(200, data)
            else:
                self.send_error_json(404, "curriculum_data.json not found")
        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_POST(self):
        if self.path == '/api/roast':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                user_text = data.get('text', '').strip()
            except Exception:
                self.send_error_json(400, "잘못된 JSON 요청입니다.")
                return

            load_env()
            groq_key = os.environ.get('GROQ_API_KEY', '').strip()

            if not groq_key or 'your_groq_key_here' in groq_key:
                self.send_error_json(400, ".env 파일에 GROQ_API_KEY를 넣어주세요!")
                return

            try:
                result = self.call_groq_api(groq_key, user_text)
                self.send_json_response(200, result)
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode('utf-8', errors='ignore')
                self.send_error_json(e.code, f"Groq 에러: {err_msg}")
            except Exception as e:
                self.send_error_json(500, f"Groq 호출 실패: {str(e)}")
        elif self.path == '/api/save-curriculum':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                html_content = data.get('html', '')
                if html_content:
                    file_path = os.path.join(DIRECTORY, 'curriculum.html')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    self.send_json_response(200, {"success": True, "message": "curriculum.html 파일에 즉시 저장되었습니다!"})
                else:
                    self.send_error_json(400, "내용이 비어 있습니다.")
            except Exception as e:
                self.send_error_json(500, f"저장 실패: {str(e)}")
        elif self.path == '/api/save-curriculum-data':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                json_path = os.path.join(DIRECTORY, 'curriculum_data.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.send_json_response(200, {"success": True, "message": "curriculum_data.json 저장 성공!"})
            except Exception as e:
                self.send_error_json(500, f"저장 실패: {str(e)}")
        elif self.path == '/api/open-browser':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                url = data.get('url', 'http://127.0.0.1:3000/curriculum.html')
                import webbrowser
                webbrowser.open(url)
                self.send_json_response(200, {"success": True, "opened": url})
            except Exception as e:
                self.send_error_json(500, f"브라우저 실행 실패: {str(e)}")
        else:
            self.send_error(404, "Not Found")

    def call_groq_api(self, api_key, user_text):
        url = "https://api.groq.com/openai/v1/chat/completions"
        system_prompt = """
너는 인터넷에서 제일 뻔뻔하고 얄미운 한국형 밈(Meme) & 팩폭 장인이야.
진지하게 설명충(칼로리 수치, 영양학, 통계, 과학, 도덕 훈계) 짓 절대 금지!
오직 '피식 터지는 비유'와 '허를 찌르는 반말(ㅋㅋㅋ 포함)'로 상대를 유쾌하게 멕여야 해.

[모범 예시]
유저: "라면은 야채 들어가니까 살 안 찜"
{"headline": "그 논리면 피자는 토마토 샐러드냐?", "subtext": "응 건더기 스프 파 조각 보고 야채 타령~ 국물에 밥까지 말아먹을 거 다 알아 ㅋㅋㅋ"}

유저: "오늘 칼퇴함"
{"headline": "내일의 너: '어제 칼퇴한 놈 나와라'", "subtext": "2시간 일찍 눕는다고 인생 안 바뀐다. 내일의 너한테 대출 땡겨 쓴 거야 ㅋㅋㅋ"}

유저: "공부하려고 아이패드 샀어"
{"headline": "100만원짜리 유튜브 머신 구매 축하", "subtext": "애플펜슬 필기감 타령하다가 3일 뒤에 넷플릭스 거치대행 확정 ㅋㅋㅋ"}

유저: "나 오늘부터 갓생 산다"
{"headline": "인스타 스토리 박제용 1일 천하", "subtext": "작심삼일도 과분함. 오늘 밤 11시에 침대에서 릴스 2시간 보면서 침 질질 흘릴 미래가 훤하다 ㅋㅋㅋ"}

유저: "방향을 잃었어"
{"headline": "그냥 눕고 싶다고 솔직하게 빌어라", "subtext": "방향을 잃은 게 아니라, 가야 할 길이 너무 귀찮아서 방황하는 청춘 소설 쓰는 중 ㅋㅋㅋ"}

반드시 위 예시처럼 설명 없이 웃긴 비유와 찰진 반말로 JSON만 출력해:
{
  "headline": "15자 이내 빵 터지는 찰진 펀치라인",
  "subtext": "1~2문장의 얄밉고 웃긴 팩폭"
}
"""

        payload = {
            "model": "qwen/qwen3.8-27b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.95,
            "max_tokens": 250
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_body = resp.read().decode('utf-8')
            resp_json = json.loads(resp_body)
            raw_content = resp_json['choices'][0]['message']['content'].strip()
            
            if raw_content.startswith("```"):
                lines = raw_content.splitlines()
                raw_content = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
            
            return json.loads(raw_content)

    def send_json_response(self, status_code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status_code, message):
        self.send_json_response(status_code, {"error": message})

if __name__ == '__main__':
    load_env()
    print(f"[Devil's Advocate Server] running at http://localhost:{PORT}")
    server = HTTPServer(('', PORT), DevilServerHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
