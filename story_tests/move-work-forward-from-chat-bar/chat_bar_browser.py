"""The CDD chat bar in a real browser: what the browser tier of Move Work Forward From Chat Bar's story tests
(`*.story.ui_e2e_spec.py` beside each sub-epic's scenarios) runs on.

The Claude app refuses computer control of its own window, so the chat bar cannot be driven where it lives. Here the
cdd-board mod's own code (`harness/chat-ui/pane/hooks`, from `register.ts` down, unchanged) is bundled with a stand-in
for the part of the Claude app it runs in (`harness/chat-ui/pane/test-page/claude-code-stand-in.ts`) into a plain page,
which Chromium opens and Playwright drives. The stand-in is the only fake: every cdd tool the bar calls is answered by
a cdd server of the spec's own, about a throwaway git project, so the bar shows real health, a real session card and
real fidelities; what the bar sends to the chat is kept on the page (`window.chatBarPage.sent`) for a spec to read.

Everything is the spec's own, so it runs beside anything else: the page is bundled into a temporary folder, the page's
server and the cdd server answer on free ports, and the cdd server runs from a throwaway ``~/.cdd`` (*SpecServer*)."""

import asyncio
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from playwright.sync_api import Page, sync_playwright

from harness.mcp.mcp_address import CHAT_HEADER, PROJECT_HEADER
from harness.mcp.spec_support import SpecServer
from space.kanban.graph_view_examples import CHECKOUT_FLOW, STORY_MAP, STORY_MAP_TEXT

_PANE = _REPO_ROOT / "harness" / "chat-ui" / "pane"
# Names another copy of the mod's folder to bundle, such as one holding a fix under trial; unset, this checkout's mod.
PANE_VARIABLE = "CDD_CHAT_BAR_PANE"
# The chat the specs open the bar in.
CHECKOUT_CHAT = "checkout-chat"
SESSION_FILE = f".sessions/{CHECKOUT_FLOW.name}/session.json"
# The colour the bar draws a running part and the connected mark in (BRAND.ok), as Chromium reports it.
GREEN = "rgb(34, 197, 94)"
PRACTICES = ("stories", "ddd", "ux", "clean_engineering", "bdd")
_ESBUILD = _REPO_ROOT / "space" / "kanban" / "app" / "node_modules" / "esbuild" / "bin" / "esbuild"
_CALL_SECONDS = 180
# The bar reads the board and the server's health after the chat starts, on a cdd server that may be cold.
SHOWN_MILLISECONDS = 60_000
PAGE_FILES = {"/": ("index.html", "text/html"), "/page.js": ("page.js", "text/javascript")}


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _git(folder: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=folder, capture_output=True, text=True, check=True)


def _write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


def seed_checkout_flow(root: Path) -> None:
    """A git project on the branch checkout-flow, holding that session with Stories and Clean Engineering on and its
    story map under .context."""
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "chat-bar@example.com")
    _git(root, "config", "user.name", "Chat Bar")
    _write(root, "README.md", "project\n")
    _git(root, "add", "README.md")
    _git(root, "commit", "-m", "start")
    _git(root, "checkout", "-b", CHECKOUT_FLOW.name)
    _write(root, STORY_MAP, STORY_MAP_TEXT)
    _write(root, f".sessions/{CHECKOUT_FLOW.name}/session.json", json.dumps({"name": CHECKOUT_FLOW.name, "title": CHECKOUT_FLOW.title, **CHECKOUT_FLOW.fields}))
    _write(root, f".sessions/{CHECKOUT_FLOW.name}/session.log", "")


def seed_checkout_flow_under_harness(root: Path) -> None:
    """checkout-flow as above with its five practices on, every one writing under the folder harness."""
    seed_checkout_flow(root)
    fields = {"practices": {key: {"enabled": True} for key in PRACTICES}, "outputs": {key: {"root": "harness"} for key in PRACTICES}}
    _write(root, SESSION_FILE, json.dumps({"name": CHECKOUT_FLOW.name, "title": CHECKOUT_FLOW.title, **fields}))
    (root / "harness").mkdir()


class CddBridge:
    """The page's way to the cdd server: one tool call, or the list of its tools, each as the chat the page names."""

    def __init__(self, url: str) -> None:
        self._url = url

    def call(self, tool: str, arguments: dict, project: str, chat: str) -> dict:
        """The tool's own text and whether the server flagged it an error; `unreachable` when no server answered."""
        try:
            return self._answered(project, chat, lambda session: session.call_tool(tool, arguments), self._as_answer)
        except Exception as not_reached:  # whatever stopped the call is the page's to show, as the app hands it to the mod
            return {"unreachable": f"{type(not_reached).__name__}: {not_reached}"}

    def tools(self) -> list[str]:
        return self._answered("", "", lambda session: session.list_tools(), lambda listed: [tool.name for tool in listed.tools])

    def _answered(self, project: str, chat: str, ask, read):
        """One call on a thread of its own, which ends with the process: a spec's own thread runs Playwright's event
        loop, which no second loop can start inside, and the bar's waiting read is still in flight when a spec ends."""
        outcome: dict = {}

        def answer() -> None:
            try:
                outcome["answer"] = asyncio.run(self._asked(project, chat, ask, read))
            except Exception as failed:  # handed to the caller's thread, which raises it there
                outcome["failed"] = failed

        worker = threading.Thread(target=answer, daemon=True)
        worker.start()
        worker.join()
        if "failed" in outcome:
            raise outcome["failed"]
        return outcome["answer"]

    async def _asked(self, project: str, chat: str, ask, read):
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        headers = {name: value for name, value in ((PROJECT_HEADER, project), (CHAT_HEADER, chat)) if value}
        async with streamablehttp_client(self._url, headers=headers, timeout=_CALL_SECONDS, sse_read_timeout=_CALL_SECONDS) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                return read(await ask(session))

    def _as_answer(self, result) -> dict:
        return {"text": result.content[0].text if result.content else "", "isError": bool(result.isError)}


class PageServer:
    """Serves the bundled test page and bridges its cdd calls, on a port of its own, until stopped."""

    def __init__(self, folder: Path, bridge: CddBridge) -> None:
        self.port = _free_port()
        self._server = ThreadingHTTPServer(("127.0.0.1", self.port), self._handler(folder, bridge))
        # The bar follows the session's guidance selection with a read that waits for a change, so one of its calls is
        # always in flight; the spec's process ends without waiting for it.
        self._server.daemon_threads = True
        self._server.block_on_close = False
        threading.Thread(target=self._server.serve_forever, daemon=True).start()

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()

    def _handler(self, folder: Path, bridge: CddBridge) -> type:
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args) -> None:
                return None

            def do_GET(self) -> None:
                path = urllib.parse.urlparse(self.path).path
                if path == "/cdd/tools":
                    return self._send(json.dumps(bridge.tools()).encode("utf-8"), "application/json")
                if path not in PAGE_FILES:
                    return self._send(b"", "text/plain", 404)
                name, kind = PAGE_FILES[path]
                self._send((folder / name).read_bytes(), f"{kind}; charset=utf-8")

            def do_POST(self) -> None:
                asked = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
                answer = bridge.call(asked["tool"], asked["args"], asked["project"], asked["chat"])
                self._send(json.dumps(answer).encode("utf-8"), "application/json")

            def _send(self, body: bytes, kind: str, status: int = 200) -> None:
                self.send_response(status)
                self.send_header("Content-Type", kind)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                try:
                    self.wfile.write(body)
                except ConnectionError:
                    # The page closed while its call was being answered, as a chat closes with a read in flight.
                    return

        return Handler


class ChatBarStack:
    """The chat bar as a person meets it above a chat's prompt, every part the spec's own: the mod bundled with the
    stand-in for the Claude app, the page's server, the cdd server the bar asks, a git project, and Chromium.
    ``close`` stops and removes all of them."""

    def __init__(self, seed=seed_checkout_flow) -> None:
        self.top = Path(tempfile.mkdtemp(prefix="cdd-chat-bar-e2e-")).resolve()
        self.project = self.top / "project"
        self.project.mkdir()
        seed(self.project)
        self._bundle_page()
        self.cdd = SpecServer()
        self.cdd.start()
        self._bridge = CddBridge(self.cdd.url)
        self._pages = PageServer(self.top / "page", self._bridge)
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self._pages.port}/"

    def _bundle_page(self) -> None:
        """The mod's hooks module and everything it imports, with the stand-in in the place of 'claude-code'."""
        page = self.top / "page"
        page.mkdir()
        test_page = Path(os.environ.get(PANE_VARIABLE) or _PANE) / "test-page"
        shutil.copy(test_page / "index.html", page / "index.html")
        subprocess.run(["node", str(_ESBUILD), str(test_page / "page.ts"), "--bundle", "--format=iife", "--jsx-factory=h", "--jsx-fragment=Fragment",
                        f"--alias:claude-code={test_page / 'claude-code-stand-in.ts'}", f"--outfile={page / 'page.js'}"],
                       cwd=_REPO_ROOT, capture_output=True, text=True, check=True)

    def open(self, chat: str = "") -> Page:
        """A new chat on the project, the chat bar above its prompt, once the bar shows the session's line."""
        page = self.browser.new_page(viewport={"width": 1500, "height": 800})
        query = urllib.parse.urlencode({"project": str(self.project), "chat": chat or str(uuid.uuid4())})
        page.goto(f"{self.url}?{query}")
        return page

    def open_on_checkout_flow(self) -> Page:
        """checkout-chat with the session checkout-flow open, its chat bar drawn and its health mark read."""
        self.as_chat(CHECKOUT_CHAT, "sessions.switch", name=CHECKOUT_FLOW.name)
        page = self.open(CHECKOUT_CHAT)
        box(page, "session-name").get_by_text(CHECKOUT_FLOW.name).wait_for(timeout=SHOWN_MILLISECONDS)
        box(page, "health-icon-mark").get_by_text("✓").wait_for(timeout=SHOWN_MILLISECONDS)
        return page

    def as_chat(self, chat: str, tool: str, **arguments) -> object:
        """What the cdd server answers the chat called chat for tool, as the agent of that chat calls it: how a spec
        seeds the state a scenario's Given names, at the server that owns it."""
        answer = self._bridge.call(tool, arguments, str(self.project), chat)
        if answer.get("unreachable") or answer.get("isError"):
            raise AssertionError(f"{tool} failed: {answer.get('unreachable') or answer.get('text')}")
        try:
            return json.loads(answer["text"])
        except ValueError:
            return answer["text"]

    def close(self) -> None:
        self.browser.close()
        self._playwright.stop()
        self._pages.stop()
        self.cdd.stop()
        shutil.rmtree(self.top, ignore_errors=True)


def sent(page: Page, kind: str = "") -> list[str]:
    """What the bar sent the chat or the app so far, each of kind (prompt, command, filled, app-call, toast, pane,
    process); every kind when none is named."""
    return [each["text"] for each in page.evaluate("() => window.chatBarPage.sent") if not kind or each["kind"] == kind]


def press(page: Page, key: str) -> None:
    """Press the bar's button keyed key, as the mod names it."""
    page.locator(f'#above-prompt button[data-key="{key}"]').first.click()


def bar_text(page: Page) -> str:
    """Every word the band above the prompt shows now."""
    return page.locator("#above-prompt").inner_text()


def box(page: Page, key: str):
    """The bar's Box keyed key, as the mod names it."""
    return page.locator(f'#above-prompt [data-box-key="{key}"]').first


def colour_of(page: Page, key: str) -> str:
    """The colour of the first words in the bar's Box keyed key."""
    return box(page, key).locator(".text").first.evaluate("words => getComputedStyle(words).color")


def open_card(page: Page) -> None:
    """Press the health mark, which opens the session card with the server health panel on top and keeps it open. The
    press reads the board and the server's health before it opens the card, and until then the card shows only under
    the pointer, so the pointer moves off the bar and the card is waited for there."""
    press(page, "health-icon")
    page.locator("#prompt-box").hover()
    box(page, "card-header").wait_for(timeout=SHOWN_MILLISECONDS)


def health_parts(page: Page) -> list[str]:
    """The parts the server health panel shows, in its order."""
    return page.locator('#above-prompt [data-box-key="health-icons"] > [data-box-key]').evaluate_all("parts => parts.map(part => part.dataset.boxKey)")


def shown_tips(page: Page, key: str) -> list[str]:
    """The hover tips showing now inside the bar's Box keyed key."""
    tips = box(page, key).locator("[data-hover]").evaluate_all("tips => tips.filter(tip => getComputedStyle(tip).display !== 'none').map(tip => tip.innerText.trim())")
    return [tip for tip in tips if tip]
