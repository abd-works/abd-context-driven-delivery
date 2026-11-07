"""Serve any .drawio file into the real draw.io editor, in a browser tab, with Save writing back to disk.

    python tools/drawio_viewer/drawio_viewer.py [root] [port]

Open http://127.0.0.1:8791/ for every .drawio file under root, or
http://127.0.0.1:8791/edit?f=<path> for one file (relative to root, or absolute).
"""

import html
import json
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

EXTENSIONS = (".drawio", ".drawio.xml")
SKIPPED_FOLDERS = {".git", ".venv", "node_modules", "__pycache__", ".pycache", ".retired"}
EMBED_URL = "https://embed.diagrams.net/?embed=1&proto=json&spin=1&noExitBtn=1&saveAndExit=0&libraries=1"

INDEX_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>draw.io files</title>
<style>body{{font-family:sans-serif;margin:16px}}li{{margin:3px 0}}a{{text-decoration:none}}</style>
</head><body><h3>draw.io files under {root}</h3><ul>{items}</ul></body></html>"""

EDITOR_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<style>html,body{{margin:0;height:100%;overflow:hidden}}iframe{{border:0;width:100%;height:100%}}</style>
</head><body><iframe id="drawio" src="{embed}"></iframe>
<script>
const file = {file};
const xml = {xml};
const frame = document.getElementById('drawio');
const send = message => frame.contentWindow.postMessage(JSON.stringify(message), '*');
window.addEventListener('message', async event => {{
  if (event.source !== frame.contentWindow || typeof event.data !== 'string') return;
  const message = JSON.parse(event.data);
  if (message.event === 'init') send({{action: 'load', xml, title: file}});
  if (message.event === 'save') {{
    const response = await fetch('/save', {{method: 'POST', headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{f: file, xml: message.xml}})}});
    send(response.ok
      ? {{action: 'status', message: 'Saved to ' + file, modified: false}}
      : {{action: 'status', message: 'Save failed: ' + await response.text(), modified: true}});
  }}
}});
</script></body></html>"""


class DrawioFiles:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def all(self):
        return sorted(
            path for path in self.root.rglob("*")
            if path.name.endswith(EXTENSIONS) and not SKIPPED_FOLDERS.intersection(path.relative_to(self.root).parts)
        )

    def resolve(self, name):
        path = Path(name)
        path = (path if path.is_absolute() else self.root / path).resolve()
        if not path.name.endswith(EXTENSIONS):
            raise ValueError(f"not a draw.io file: {name}")
        return path

    def label(self, path):
        return path.relative_to(self.root).as_posix() if path.is_relative_to(self.root) else str(path)


def handler_for(files, port):
    own_origin = f"http://127.0.0.1:{port}"

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urllib.parse.urlparse(self.path)
            if url.path == "/":
                items = "".join(
                    f'<li><a href="/edit?f={urllib.parse.quote(files.label(path))}">{html.escape(files.label(path))}</a></li>'
                    for path in files.all()
                )
                return self.reply(200, INDEX_PAGE.format(root=html.escape(str(files.root)), items=items))
            if url.path == "/edit":
                name = urllib.parse.parse_qs(url.query).get("f", [""])[0]
                try:
                    path = files.resolve(name)
                    xml = path.read_text(encoding="utf-8") if path.exists() else ""
                except (ValueError, OSError) as error:
                    return self.reply(404, str(error), "text/plain")
                return self.reply(200, EDITOR_PAGE.format(
                    title=html.escape(path.name), embed=EMBED_URL,
                    file=json.dumps(files.label(path)).replace("</", "<\\/"),
                    xml=json.dumps(xml).replace("</", "<\\/"),
                ))
            self.reply(404, "not found", "text/plain")

        def do_POST(self):
            if self.path != "/save" or self.headers.get("Origin") != own_origin:
                return self.reply(403, "refused", "text/plain")
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            try:
                path = files.resolve(body["f"])
                path.write_text(body["xml"], encoding="utf-8")
            except (ValueError, OSError) as error:
                return self.reply(400, str(error), "text/plain")
            self.reply(200, "saved", "text/plain")

        def reply(self, status, text, content_type="text/html"):
            data = text.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    return Handler


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8791
    print(f"draw.io viewer on http://127.0.0.1:{port}/", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), handler_for(DrawioFiles(root), port)).serve_forever()
