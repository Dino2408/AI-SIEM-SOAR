from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path

DATA_DIR=Path(os.environ.get("SIEM_DATA_DIR","./data"))
EVENT_FILE=DATA_DIR/"events.jsonl"
DATA_DIR.mkdir(parents=True,exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, payload):
        body=json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        if self.path=="/health":
            return self._json(200,{"status":"ok","service":"ai-siem-soar-api"})
        if self.path=="/api/v1/events":
            events=[]
            if EVENT_FILE.exists():
                events=[json.loads(x) for x in EVENT_FILE.read_text(encoding="utf-8").splitlines() if x.strip()]
            return self._json(200,{"count":len(events),"events":events[-100:]})
        return self._json(404,{"error":"not_found"})
    def do_POST(self):
        if self.path!="/api/v1/events":
            return self._json(404,{"error":"not_found"})
        length=int(self.headers.get("Content-Length","0"))
        event=json.loads(self.rfile.read(length))
        with EVENT_FILE.open("a",encoding="utf-8") as f:
            f.write(json.dumps(event,ensure_ascii=False)+"
")
        return self._json(201,{"accepted":True,"event":event})
    def log_message(self,*args): pass

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",8080),Handler).serve_forever()
