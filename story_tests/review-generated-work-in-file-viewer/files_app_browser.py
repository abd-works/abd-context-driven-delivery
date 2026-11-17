"""The Files app in a real browser, on its real server, talking to a real cdd server about a real git project: what
the browser tier of Review Generated Work In File Viewer's story tests (`*.story.ui_e2e_spec.py` beside each sub-epic's
scenarios) runs on. The twins of the Files app's unit specs (``harness/files_app/app/files/source-folding.spec.ts``, ``call-expansion.spec.ts``,
``file-bar.spec.ts``), which stub the session's answers and the editor: here the page is built from this checkout's
source, served by the Files server (``harness/files_app/app/spec-files-server.ts``, as ``serve.ts`` serves it), and drives Monaco in
Chromium, while the session's files, graph and members come from a cdd server of the spec's own.

Everything is the spec's own, so it runs beside anything else: the page is built into a temporary folder, never the
app's ``dist``; the Files server and the cdd server answer on free ports, never 8783 or the person's cdd server; the cdd
server runs from a throwaway ``~/.cdd`` (*SpecServer*); and the project is a throwaway git repository. Monaco loads as
the live page loads it."""

import json
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
from urllib.request import urlopen
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from playwright.sync_api import Page, sync_playwright

from harness.mcp.spec_support import SpecServer
from space.session.graph_view_rule_examples import VIOLATING_MAP_TEXT
from space.session.graph_view_examples import BOARD_CODE, BOARD_TEXT, CHECKOUT_FLOW, STEP_STORY, STEP_STORY_TEXT, TICKET_EXAMPLES, TICKET_EXAMPLES_TEXT

_APP = _REPO_ROOT / "harness" / "files_app" / "app"
_NODE_TSX = _APP / "node_modules" / "tsx" / "dist" / "cli.mjs"
_NODE_VITE = _APP / "node_modules" / "vite" / "bin" / "vite.js"
_SERVER_STARTS_WITHIN_SECONDS = 60
# A graph read builds the session's graph of the files listed on the cdd server, which takes seconds on a cold server.
GRAPH_READ_MILLISECONDS = 180_000
SHOWN_MILLISECONDS = 30_000
SETTLE_SECONDS = 10
NBSP = "\u00a0"

# Seed: the ticket code of call-expansion.spec.ts, as the person verified it live: the class Ticket on lines 1 to 9,
# its close on lines 2 to 3 and its delete on lines 5 to 9, which calls self.close(), the module function reread_all,
# and names the class Board; reread_all on lines 12 to 13.
TICKET_CODE = "space/kanban/ticket.py"
TICKET_TEXT = (
    "class Ticket:\n"
    "    def close(self) -> None:\n"
    "        return None\n"
    "\n"
    "    def delete(self, board: Board) -> None:\n"
    "        self.close()\n"
    "        reread_all(board)\n"
    "        Board.reread(board)\n"
    "        return None\n"
    "\n"
    "\n"
    "def reread_all(board) -> None:\n"
    "    board.reread()\n"
)
CLOSE_LINES = "    def close(self) -> None:\n        return None"

# Seed: design-review, a session working in the project's design folder with UX on, its design canvas's version-1
# published at its link (versions.json) and its story map drawn on a whiteboard published to a board (whiteboards.json).
DESIGN_REVIEW = "design-review"
CANVAS = "design/ux/design-canvas/version-1/project/canvas.json"
CANVAS_LINK = "https://claude.ai/artifact/checkout-canvas"
WHITEBOARD = "design/.context/story-map.whiteboard"
BOARD_LINK = "https://claude.ai/artifact/story-board"

# Seed: story-review, a session working in the project's review folder with Stories alone on, whose story map holds two
# stories that open with a generic verb, which verb-noun-format breaks, beside Delete Ticket, which passes it.
STORY_REVIEW = "story-review"
REVIEW_MAP = "review/.context/story-map.md"


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _git(folder: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=folder, capture_output=True, text=True, check=True)


def _write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


def _seed_project(root: Path) -> None:
    """A git project holding checkout-flow's story test and ticket code, design-review's canvas and whiteboard, and
    story-review's story map."""
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "files@example.com")
    _git(root, "config", "user.name", "Files")
    _write(root, "README.md", "project\n")
    _git(root, "add", "README.md")
    _git(root, "commit", "-m", "start")
    # board.py is on main already and checkout-flow's work is on its own branch, so This session lists the files the
    # branch changed without board.py and All session files adds it.
    _write(root, BOARD_CODE, BOARD_TEXT)
    _git(root, "add", BOARD_CODE)
    _git(root, "commit", "-m", "board")
    _git(root, "checkout", "-b", CHECKOUT_FLOW.name)
    for path, text in ((STEP_STORY, STEP_STORY_TEXT), (TICKET_CODE, TICKET_TEXT), (TICKET_EXAMPLES, TICKET_EXAMPLES_TEXT)):
        _write(root, path, text)
    _write(root, ".sessions/checkout-flow/session.json", json.dumps({"name": CHECKOUT_FLOW.name, "title": CHECKOUT_FLOW.title, **CHECKOUT_FLOW.fields}))
    _write(root, ".sessions/checkout-flow/session.log", "")
    _write(root, CANVAS, "{}\n")
    _write(root, "design/ux/design-canvas/versions.json", json.dumps({"version-1": CANVAS_LINK}))
    _write(root, WHITEBOARD, "{}\n")
    _write(root, "design/.context/whiteboards.json", json.dumps({"story-map.whiteboard": BOARD_LINK}))
    _write(root, f".sessions/{DESIGN_REVIEW}/session.json", json.dumps({"name": DESIGN_REVIEW, "title": "Design review", "workpath": str(root / "design")}))
    _write(root, f".sessions/{DESIGN_REVIEW}/session.log", "")
    _write(root, REVIEW_MAP, VIOLATING_MAP_TEXT)
    review = {"practices": {key: {"enabled": False} for key in ("ux", "ddd", "bdd", "clean_engineering")}, "outputs": {"stories": {"root": ".context"}}}
    _write(root, f".sessions/{STORY_REVIEW}/session.json", json.dumps({"name": STORY_REVIEW, "title": "Story review", "workpath": str(root / "review"), **review}))
    _write(root, f".sessions/{STORY_REVIEW}/session.log", "")


class FilesStack:
    """The Files app as a person meets it, every part of it the spec's own: the page built from this checkout, the Files
    server serving it, the cdd server it asks, a git project, and Chromium. ``close`` stops and removes all of them."""

    def __init__(self) -> None:
        self.top = Path(tempfile.mkdtemp(prefix="cdd-files-e2e-")).resolve()
        self.project = self.top / "project"
        self.project.mkdir()
        _seed_project(self.project)
        self._build_page()
        self.cdd = SpecServer()
        self.cdd.start()
        self.port = _free_port()
        self._files = subprocess.Popen(["node", str(_NODE_TSX), "spec-files-server.ts", str(self.top / "dist"), str(self.port), str(self.project)], cwd=_APP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self._wait_for_files_server()
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch()

    def _build_page(self) -> None:
        subprocess.run(["node", str(_NODE_VITE), "build", "--outDir", str(self.top / "dist"), "--emptyOutDir"], cwd=_APP, capture_output=True, text=True, check=True)

    def _wait_for_files_server(self) -> None:
        deadline = time.monotonic() + _SERVER_STARTS_WITHIN_SECONDS
        while time.monotonic() < deadline:
            try:
                with urlopen(f"http://127.0.0.1:{self.port}/", timeout=2):
                    return
            except (urllib.error.URLError, OSError):
                time.sleep(0.25)
        raise TimeoutError(f"the Files server did not answer on port {self.port} within {_SERVER_STARTS_WITHIN_SECONDS} s")

    def open(self, ticket: str, fidelities: str) -> Page:
        """A new page on the files of ticket's fidelities, as the chat bar's files button opens it."""
        page = self.browser.new_page(viewport={"width": 1600, "height": 900})
        query = urllib.parse.urlencode({"files": ticket, "fidelity": fidelities, "project": str(self.project)})
        page.goto(f"http://127.0.0.1:{self.port}/?{query}")
        return page

    def close(self) -> None:
        self.browser.close()
        self._playwright.stop()
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(self._files.pid)], capture_output=True) if sys.platform == "win32" else self._files.kill()
        self._files.wait()
        self.cdd.stop()
        shutil.rmtree(self.top, ignore_errors=True)


def graph_view(page: Page) -> None:
    """Every file under the session's root listed, shown as the session's graph, read for real."""
    page.get_by_role("button", name="All session files").click()
    page.locator(".file-list, .file-tree").first.wait_for(timeout=SHOWN_MILLISECONDS)
    page.get_by_role("button", name="Graph", exact=True).click()
    page.locator("ul.graph-tree").wait_for(timeout=GRAPH_READ_MILLISECONDS)


def open_branches(page: Page, *names: str) -> None:
    for name in names:
        page.get_by_role("button", name=f"Open {name}", exact=True).first.click()
        page.get_by_role("button", name=f"Close {name}", exact=True).first.wait_for(timeout=GRAPH_READ_MILLISECONDS)


def select(page: Page, title: str) -> None:
    page.locator(f'button.graph-node[title="{title}"]').first.click()


def line(page: Page, text: str):
    """The editor's line reading text and nothing else, its indent aside: Monaco keeps its lines' elements in no order,
    so a line that only holds text, such as reread_all's definition holding reread_all(board), must never answer. Its
    spaces are no-break spaces, which the page's whitespace class matches."""
    return page.locator(".view-lines .view-line", has_text=re.compile(r"^\s*" + r"\s".join(re.escape(word) for word in text.split(" ")) + r"\s*$")).first


def shown_lines(page: Page) -> list[str]:
    return [line.replace(NBSP, " ") for line in page.locator(".view-lines .view-line").all_inner_texts()]


def mark_on(page: Page, text: str):
    """The callout mark beside the line reading text, none when the line opens nothing in place."""
    row = line(page, text).bounding_box()
    for mark in page.locator(".callout-mark").all():
        box = mark.bounding_box()
        if box and row and abs((box["y"] + box["height"] / 2) - (row["y"] + row["height"] / 2)) < row["height"] / 2:
            return mark
    return None


def open_callout_on(page: Page, text: str) -> None:
    mark = mark_on(page, text)
    if mark is None:
        raise AssertionError(f"no callout mark beside the line {text!r}: the line opens nothing in place")
    mark.click()
    page.locator(".callout-block").first.wait_for(state="attached", timeout=SHOWN_MILLISECONDS)


def callout_texts(page: Page) -> list[str]:
    """Each open callout's lines, one line to each of its rows."""
    return ["\n".join(row.replace(NBSP, " ") for row in block.locator(".callout-text").all_inner_texts()) for block in page.locator(".callout-block").all()]


def settled(read, is_settled, seconds: float = SETTLE_SECONDS):
    """What read answers once is_settled holds of it, or what it answers when seconds have passed: the editor folds,
    unfolds and lays out view zones over a few frames after the page asks it to."""
    deadline = time.monotonic() + seconds
    answer = read()
    while not is_settled(answer) and time.monotonic() < deadline:
        time.sleep(0.1)
        answer = read()
    return answer


def callout_heights(page: Page) -> list[float]:
    return [(block.bounding_box() or {"height": 0.0})["height"] for block in page.locator(".callout-block").all()]


