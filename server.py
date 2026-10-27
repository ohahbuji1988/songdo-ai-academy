import os
import sys
import json
import time
from datetime import datetime
import urllib.request
import urllib.error
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


def load_env():
    """Load key-value environment variables from local .env file."""
    env_path = os.path.join(DIRECTORY, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

def send_telegram_notification(record):
    """Send real-time Telegram push notification when a new application is submitted."""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not bot_token or not chat_id:
        return
    try:
        import urllib.request
        import json
        msg = (
            f"🔔 <b>[송도 AI 아카데미] 무료 수강 신청 접수!</b>\n\n"
            f"👤 <b>신청자 성함:</b> {record.get('name')}\n"
            f"📞 <b>연락처:</b> {record.get('phone')}\n"
            f"🎯 <b>신청 트랙:</b> {record.get('track')}\n"
            f"📝 <b>희망 내용/질문:</b> {record.get('note') or '(없음)'}\n"
            f"⏰ <b>신청 일시:</b> {record.get('created_at')}\n\n"
            f"👉 확인 후 수강생에게 안내 연락을 진행해 주세요!"
        )
        data = json.dumps({
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML"
        }).encode('utf-8')
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=5)
        print(f"[Telegram Notification Sent] To chat_id: {chat_id}")
    except Exception as te:
        print(f"[Telegram Notification Error] {te}")


# ============================================================================
# Deep Module 1: ContentStore
# Encapsulates file persistence, path traversal protection, and atomic writes.
# ============================================================================
class ContentStore:
    ALLOWED_PAGES = {
        'landing.html',
        'presentation.html',
        'curriculum.html',
        'creator.html',
        'process.html',
        'diagnostic.html',
        'courseware/lessons.html',
        'courseware/index.html',
        'curriculum_data.json'
    }

    def __init__(self, base_dir: str):
        self.base_dir = os.path.abspath(base_dir)

    def get_curriculum_data(self) -> dict:
        json_path = os.path.join(self.base_dir, 'curriculum_data.json')
        if not os.path.exists(json_path):
            raise FileNotFoundError("curriculum_data.json not found")
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_curriculum_data(self, data: dict) -> None:
        self.save_file('curriculum_data.json', json.dumps(data, ensure_ascii=False, indent=2))

    def save_application(self, record: dict) -> None:
        app_file = os.path.join(self.base_dir, 'applications.json')
        applications = []
        if os.path.exists(app_file):
            try:
                with open(app_file, 'r', encoding='utf-8') as f:
                    applications = json.load(f)
                    if not isinstance(applications, list):
                        applications = []
            except Exception:
                applications = []
        applications.append(record)
        tmp_path = app_file + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(applications, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, app_file)

    def save_file(self, rel_path: str, content: str) -> str:
        clean_path = rel_path.replace('\\', '/').strip('/')
        if clean_path not in self.ALLOWED_PAGES:
            raise PermissionError(f"저장 권한이 없는 대상입니다: {rel_path}")

        target_path = os.path.abspath(os.path.join(self.base_dir, clean_path))
        if not target_path.startswith(self.base_dir):
            raise PermissionError("Path traversal guard: 상위 디렉터리 접근 차단")

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        # Atomic write pattern: write to tmp file first, then atomic replace
        tmp_path = target_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        os.replace(tmp_path, target_path)
        return clean_path


# ============================================================================
# Deep Adapter 2: RangeStreamer
# Encapsulates HTTP byte-range parsing (RFC 7233) and chunked socket streaming.
# ============================================================================
class RangeStreamer:
    @staticmethod
    def stream(handler: SimpleHTTPRequestHandler, file_path: str, range_header: str | None) -> None:
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            handler.send_error(404, "File not found")
            return

        file_size = os.path.getsize(file_path)
        content_type = 'video/mp4' if file_path.endswith('.mp4') else 'application/octet-stream'

        if not range_header:
            handler.send_response(200)
            handler.send_header('Content-Type', content_type)
            handler.send_header('Content-Length', str(file_size))
            handler.send_header('Accept-Ranges', 'bytes')
            handler.end_headers()
            with open(file_path, 'rb') as f:
                handler.copyfile(f, handler.wfile)
            return

        try:
            range_val = range_header.strip().split('=')[1]
            start_str, end_str = range_val.split('-')
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
            if end >= file_size:
                end = file_size - 1
            content_length = end - start + 1

            handler.send_response(206, "Partial Content")
            handler.send_header('Content-Type', content_type)
            handler.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
            handler.send_header('Content-Length', str(content_length))
            handler.send_header('Accept-Ranges', 'bytes')
            handler.end_headers()

            with open(file_path, 'rb') as f:
                f.seek(start)
                bytes_left = content_length
                while bytes_left > 0:
                    chunk_size = min(64 * 1024, bytes_left)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    handler.wfile.write(chunk)
                    bytes_left -= len(chunk)
        except Exception:
            pass


# ============================================================================
# Deep Adapter 3: GroqGateway
# Encapsulates external LLM API communications, payload structure, and fallback.
# ============================================================================
class GroqGateway:
    ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

    @classmethod
    def call_roast(cls, api_key: str, user_text: str) -> dict:
        system_prompt = """
너는 인터넷에서 제일 뻔뻔하고 얄미운 한국형 밈(Meme) & 팩폭 장인이야.
진지하게 설명충(칼로리 수치, 영양학, 통계, 과학, 도덕 훈계) 짓 절대 금지!
오직 '피식 터지는 비유'와 '허를 찌르는 반말(ㅋㅋㅋ 포함)'로 상대를 유쾌하게 멕여야 해.
반드시 아래 JSON 형식만 반환해:
{
  "headline": "15자 이내 찰진 펀치라인",
  "subtext": "1~2문장의 얄밉고 웃긴 팩폭"
}
"""
        payload = {
            "model": "qwen/qwen3.8-27b",
            "messages": [
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_text}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.95,
            "max_tokens": 250
        }

        req = urllib.request.Request(
            cls.ENDPOINT,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "SongdoAI/1.0"
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


# ============================================================================
# Server Dispatcher: DevilServerHandler
# Thin translation seam that decodes requests and delegates to deep modules.
# ============================================================================
class DevilServerHandler(SimpleHTTPRequestHandler):
    content_store = ContentStore(DIRECTORY)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

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

    def do_GET(self):
        clean_path = self.path.split('?')[0]

        # Security Guard: Block dotfiles (.env, .git, .DS_Store, etc.)
        path_parts = [p for p in clean_path.split('/') if p]
        if any(p.startswith('.') for p in path_parts):
            self.send_error_json(403, "비공개 시스템 파일 접근이 제한되었습니다.")
            return

        if clean_path == '/api/curriculum-data':
            try:
                data = self.content_store.get_curriculum_data()
                self.send_json_response(200, data)
            except FileNotFoundError:
                self.send_error_json(404, "curriculum_data.json 파일을 찾을 수 없습니다.")
        elif clean_path.endswith('.mp4') or 'Range' in self.headers:
            target_path = self.translate_path(self.path)
            RangeStreamer.stream(self, target_path, self.headers.get('Range'))
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore')

        try:
            body = json.loads(raw_body) if raw_body else {}
        except Exception:
            self.send_error_json(400, "잘못된 JSON 요청입니다.")
            return

        clean_path = self.path.split('?')[0]

        # 1. Unified Content Persistence (Primary Seam)
        if clean_path in ('/api/save-page', '/api/save-curriculum', '/api/save-presentation'):
            # Backward-compatibility routing: map legacy endpoints to canonical target
            target_page = body.get('page', '')
            if clean_path == '/api/save-curriculum':
                target_page = 'curriculum.html'
            elif clean_path == '/api/save-presentation':
                target_page = 'presentation.html'

            html_content = body.get('html', '')
            if not html_content:
                self.send_error_json(400, "저장할 내용(html)이 비어 있습니다.")
                return

            try:
                saved_name = self.content_store.save_file(target_page, html_content)
                self.send_json_response(200, {
                    "success": True,
                    "page": saved_name,
                    "message": f"{saved_name} 파일에 안전하게 영구 저장되었습니다!"
                })
            except (PermissionError, FileNotFoundError) as e:
                self.send_error_json(400, str(e))
            except Exception as e:
                self.send_error_json(500, f"저장 실패: {str(e)}")

        elif clean_path == '/api/apply':
            name = str(body.get('name', '')).strip()
            phone = str(body.get('phone', '')).strip()
            track = str(body.get('track', 'regular')).strip()
            note = str(body.get('note', '')).strip()

            if not name or not phone:
                self.send_error_json(400, "성함과 연락처는 필수 입력 항목입니다.")
                return

            try:
                record = {
                    "id": f"APP-{int(time.time()*1000)}",
                    "name": name,
                    "phone": phone,
                    "track": track,
                    "note": note,
                    "created_at": datetime.now().isoformat()
                }
                self.content_store.save_application(record)
                self.send_json_response(200, {
                    "success": True,
                    "message": f"{name}님의 송도 1기 수강 신청이 정상 접수되었습니다.",
                    "record": record
                })
            except Exception as e:
                self.send_error_json(500, f"수강 신청 저장 실패: {str(e)}")

        elif clean_path == '/api/save-curriculum-data':
            try:
                self.content_store.save_curriculum_data(body)
                self.send_json_response(200, {
                    "success": True,
                    "message": "curriculum_data.json 저장 성공!"
                })
            except Exception as e:
                self.send_error_json(500, f"데이터 저장 실패: {str(e)}")

        elif clean_path == '/api/roast':
            load_env()
            groq_key = os.environ.get('GROQ_API_KEY', '').strip()
            if not groq_key or 'your_groq_key_here' in groq_key:
                self.send_error_json(400, ".env 파일에 유효한 GROQ_API_KEY를 등록해주세요.")
                return

            try:
                user_text = body.get('text', '').strip()
                result = GroqGateway.call_roast(groq_key, user_text)
                self.send_json_response(200, result)
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode('utf-8', errors='ignore')
                self.send_error_json(e.code, f"Groq 에러: {err_msg}")
            except Exception as e:
                self.send_error_json(500, f"Groq 호출 실패: {str(e)}")

        elif clean_path == '/api/open-browser':
            url = body.get('url', 'http://127.0.0.1:3000/landing.html')
            webbrowser.open(url)
            self.send_json_response(200, {"success": True, "opened": url})

        else:
            self.send_error(404, "Not Found")

    def send_json_response(self, status_code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status_code: int, message: str):
        self.send_json_response(status_code, {"error": message, "success": False})


if __name__ == '__main__':
    load_env()
    print(f"[Songdo AI Suite Server] running at http://127.0.0.1:{PORT}")
    server = HTTPServer(('127.0.0.1', PORT), DevilServerHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
