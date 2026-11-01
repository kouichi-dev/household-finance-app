"""index.html を配り、/api/* を API (localhost:8000) に中継する。
同じオリジンになるので、API 側に CORS 設定を足さなくて済む。標準ライブラリのみ。

    python serve.py   →  http://localhost:5173
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import urllib.request
import urllib.error
import os

# Docker で動かすときは compose.share.yml が API=http://app:8000 / HOST=0.0.0.0 を渡す
API = os.environ.get("API", "http://localhost:8000")
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = 5173
HERE = Path(__file__).parent


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def _proxy(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        headers = {k: v for k, v in self.headers.items() if k.lower() in ("authorization", "content-type")}
        req = urllib.request.Request(API + self.path[len("/api"):], data=body, headers=headers, method=self.command)
        try:
            res = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:   # 4xx / 5xx もそのまま返す
            res = e
        except urllib.error.URLError:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write('{"detail": "API に接続できません。docker compose up しましたか？"}'.encode())
            return
        data = res.read()
        self.send_response(res.status)
        if res.headers.get("Content-Type"):
            self.send_header("Content-Type", res.headers["Content-Type"])
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _route(self, fallback):
        if self.path.startswith("/api/"):
            self._proxy()
        elif fallback:
            fallback()
        else:
            self.send_error(405)

    def _index(self):
        # index.html 以外（.env / .git など）は配らない
        if self.path.split("?")[0] in ("/", "/index.html"):
            super().do_GET()
        else:
            self.send_error(404)

    def do_GET(self):    self._route(self._index)
    def do_POST(self):   self._route(None)
    def do_PATCH(self):  self._route(None)
    def do_DELETE(self): self._route(None)


if __name__ == "__main__":
    print(f"http://localhost:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
