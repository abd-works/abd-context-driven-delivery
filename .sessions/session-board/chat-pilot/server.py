"""Chat pilot: a local page whose buttons put a fixed command into a registered Claude chat.

Page button -> this server -> chat-pilot mod polling /next -> $.prompt.submit or $.prompt.fill.
The commands are fixed text, and POSTs from any other origin are refused, so another website
open in a browser cannot put words into the chat through this port.
"""
from __future__ import annotations

import json
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PORT = 8777
ORIGIN = f"http://127.0.0.1:{PORT}"
PAGE = Path(__file__).with_name("page.html")
COMMANDS = {
    "submit": "Chat pilot check, sent by the page's Submit button: reply with the single word received.",
    "fill": "Chat pilot check, placed by the page's Fill button for you to review.",
}

chats: dict[str, float] = {}
queue: deque[dict] = deque()
events: list[dict] = []
started = time.monotonic()


def record(what: str, **details) -> None:
    events.append({"seconds": round(time.monotonic() - started, 2), "what": what, **details})


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, value, status: int = 200) -> None:
        self._send(status, json.dumps(value).encode(), "application/json")

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self) -> None:
        url = urlparse(self.path)
        if url.path == "/":
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        elif url.path == "/status":
            self._json({"chats": sorted(chats), "queued": len(queue), "events": events})
        elif url.path == "/next":
            chat = parse_qs(url.query).get("chat", [""])[0]
            chats[chat] = time.monotonic()
            self._json(self._take_for(chat))
        else:
            self._json({"error": "not found"}, 404)

    def _take_for(self, chat: str) -> dict:
        for command in list(queue):
            if command["chat"] == chat:
                queue.remove(command)
                record("delivered", mode=command["mode"], chat=chat)
                return command
        return {}

    def do_POST(self) -> None:
        origin = self.headers.get("Origin")
        if origin and origin != ORIGIN:
            self._json({"error": "origin refused"}, 403)
            return
        url = urlparse(self.path)
        body = self._body()
        if url.path == "/press":
            self._press(body)
        elif url.path == "/result":
            record("result", **{key: body.get(key) for key in ("mode", "chat", "outcome")})
            self._json({"ok": True})
        else:
            self._json({"error": "not found"}, 404)

    def _press(self, body: dict) -> None:
        mode = body.get("mode")
        chat = body.get("chat")
        if mode not in COMMANDS or chat not in chats:
            self._json({"error": "unknown mode or chat"}, 400)
            return
        queue.append({"mode": mode, "chat": chat, "text": COMMANDS[mode]})
        record("pressed", mode=mode, chat=chat)
        self._json({"ok": True})


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
