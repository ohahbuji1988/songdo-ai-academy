import os
import sys
import time
import urllib.request
import subprocess
import webview

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = "http://127.0.0.1:3000/creator.html"

def is_server_running():
    try:
        with urllib.request.urlopen("http://127.0.0.1:3000/api/curriculum-data", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

def ensure_server():
    if not is_server_running():
        server_script = os.path.join(DIRECTORY, "server.py")
        subprocess.Popen([sys.executable, server_script], cwd=DIRECTORY)
        for _ in range(10):
            time.sleep(0.5)
            if is_server_running():
                break

def main():
    ensure_server()
    window = webview.create_window(
        title="Songdo AI Academy — Curriculum Creator",
        url=SERVER_URL,
        width=1320,
        height=880,
        min_size=(1024, 700),
        text_select=True,
        confirm_close=False
    )
    webview.start()

if __name__ == "__main__":
    main()
