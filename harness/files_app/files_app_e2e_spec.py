"""E2E spec: the Files app in a real browser, on its real server, talking to a real cdd server about a real git project.
The twins of the Files app's unit specs (``app/files/source-folding.spec.ts``, ``call-expansion.spec.ts``,
``file-bar.spec.ts``), which stub the session's answers and the editor: here the page is built from this checkout's
source, served by the Files server (``app/spec-files-server.ts``, as ``serve.ts`` serves it), and drives Monaco in
Chromium, while the session's files, graph and members come from a cdd server of the spec's own.

Everything is the spec's own, so it runs beside anything else: the page is built into a temporary folder, never the
app's ``dist``; the Files server and the cdd server answer on free ports, never 8783 or the person's cdd server; the cdd
server runs from a throwaway ``~/.cdd`` (*SpecServer*); and the project is a throwaway git repository. Monaco loads as
the live page loads it."""

import json
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

from expects import be_above, be_none, equal, expect
from mamba import after, before, context, description, it
from playwright.sync_api import Page, sync_playwright

from harness.mcp.spec_support import SpecServer
from space.session.graph_view_examples import BOARD_CODE, BOARD_TEXT, CHECKOUT_FLOW, STEP_STORY, STEP_STORY_TEXT, TICKET_EXAMPLES, TICKET_EXAMPLES_TEXT

_APP = _REPO_ROOT / "harness" / "files_app" / "app"
_NODE_TSX = _APP / "node_modules" / "tsx" / "dist" / "cli.mjs"
_NODE_VITE = _APP / "node_modules" / "vite" / "bin" / "vite.js"
_SERVER_STARTS_WITHIN_SECONDS = 60
# A graph read builds the session's graph of the files listed on the cdd server, which takes seconds on a cold server.
_GRAPH_READ_MILLISECONDS = 180_000
_SHOWN_MILLISECONDS = 30_000
_SETTLE_SECONDS = 10
_NBSP = "\u00a0"

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
    """A git project holding checkout-flow's story test and ticket code, and design-review's canvas and whiteboard."""
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "files@example.com")
    _git(root, "config", "user.name", "Files")
    _write(root, "README.md", "project\n")
    _git(root, "add", "README.md")
    _git(root, "commit", "-m", "start")
    for path, text in ((STEP_STORY, STEP_STORY_TEXT), (TICKET_CODE, TICKET_TEXT), (BOARD_CODE, BOARD_TEXT), (TICKET_EXAMPLES, TICKET_EXAMPLES_TEXT)):
        _write(root, path, text)
    _write(root, ".sessions/checkout-flow/session.json", json.dumps({"name": CHECKOUT_FLOW.name, "title": CHECKOUT_FLOW.title, **CHECKOUT_FLOW.fields}))
    _write(root, ".sessions/checkout-flow/session.log", "")
    _write(root, CANVAS, "{}\n")
    _write(root, "design/ux/design-canvas/versions.json", json.dumps({"version-1": CANVAS_LINK}))
    _write(root, WHITEBOARD, "{}\n")
    _write(root, "design/.context/whiteboards.json", json.dumps({"story-map.whiteboard": BOARD_LINK}))
    _write(root, f".sessions/{DESIGN_REVIEW}/session.json", json.dumps({"name": DESIGN_REVIEW, "title": "Design review", "workpath": str(root / "design")}))
    _write(root, f".sessions/{DESIGN_REVIEW}/session.log", "")


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


def _graph_view(page: Page) -> None:
    """Every file under the session's root listed, shown as the session's graph, read for real."""
    page.get_by_role("button", name="All session files").click()
    page.locator(".file-list, .file-tree").first.wait_for(timeout=_SHOWN_MILLISECONDS)
    page.get_by_role("button", name="Graph", exact=True).click()
    page.locator("ul.graph-tree").wait_for(timeout=_GRAPH_READ_MILLISECONDS)


def _open_branches(page: Page, *names: str) -> None:
    for name in names:
        page.get_by_role("button", name=f"Open {name}", exact=True).first.click()
        page.get_by_role("button", name=f"Close {name}", exact=True).first.wait_for(timeout=_GRAPH_READ_MILLISECONDS)


def _select(page: Page, title: str) -> None:
    page.locator(f'button.graph-node[title="{title}"]').first.click()


def _line(page: Page, text: str):
    return page.locator(".view-lines .view-line", has_text=text).first


def _shown_lines(page: Page) -> list[str]:
    return [line.replace(_NBSP, " ") for line in page.locator(".view-lines .view-line").all_inner_texts()]


def _mark_on(page: Page, text: str):
    """The callout mark beside the line reading text, none when the line opens nothing in place."""
    row = _line(page, text).bounding_box()
    for mark in page.locator(".callout-mark").all():
        box = mark.bounding_box()
        if box and row and abs((box["y"] + box["height"] / 2) - (row["y"] + row["height"] / 2)) < row["height"] / 2:
            return mark
    return None


def _open_callout_on(page: Page, text: str) -> None:
    mark = _mark_on(page, text)
    if mark is None:
        raise AssertionError(f"no callout mark beside the line {text!r}: the line opens nothing in place")
    mark.click()
    page.locator(".callout-block").first.wait_for(state="attached", timeout=_SHOWN_MILLISECONDS)


def _callout_texts(page: Page) -> list[str]:
    """Each open callout's lines, one line to each of its rows."""
    return ["\n".join(row.replace(_NBSP, " ") for row in block.locator(".callout-text").all_inner_texts()) for block in page.locator(".callout-block").all()]


def _settled(read, is_settled, seconds: float = _SETTLE_SECONDS):
    """What read answers once is_settled holds of it, or what it answers when seconds have passed: the editor folds,
    unfolds and lays out view zones over a few frames after the page asks it to."""
    deadline = time.monotonic() + seconds
    answer = read()
    while not is_settled(answer) and time.monotonic() < deadline:
        time.sleep(0.1)
        answer = read()
    return answer


def _callout_heights(page: Page) -> list[float]:
    return [(block.bounding_box() or {"height": 0.0})["height"] for block in page.locator(".callout-block").all()]


with description("the Files app served for real") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with description("Folds a selected node opens"):
        with context("with a step of a Python story test selected, its decorator first"):
            with before.all:
                self.page = self.stack.open(CHECKOUT_FLOW.name, "stories-acceptance-tests,clean-engineering-code")
                _graph_view(self.page)
                _open_branches(self.page, "stories", "Manage Tickets", "Remove Tickets", "Delete Ticket", "Delete Ticket", "a ticket on the board is deleted")
                _select(self.page, "Given given a ticket on the board")
                _line(self.page, "world.ticket = ticket_on_board(world)").wait_for(timeout=_SHOWN_MILLISECONDS)

            with after.all:
                self.page.close()

            with it("should unfold the step's function under its decorator, as well as the folds around it"):
                expect([line for line in _shown_lines(self.page) if line.strip() in ('@s.given("a ticket on the board")', "def _(world):", "world.ticket = ticket_on_board(world)")][:3]).to(
                    equal(['    @s.given("a ticket on the board")', "    def _(world):", "        world.ticket = ticket_on_board(world)"])
                )

            with it("should keep the other steps' functions folded"):
                others = lambda: [line for line in _shown_lines(self.page) if "world.ticket.delete(world.board)" in line or "assert ticket_left(world)" in line]
                expect(_settled(others, lambda shown: shown == [])).to(equal([]))

    with description("Calls and classes a line opens in place"):
        with context("with ticket.py opened at its operation delete, the graph's members read"):
            with before.all:
                self.page = self.stack.open(CHECKOUT_FLOW.name, "stories-acceptance-tests,clean-engineering-code")
                _graph_view(self.page)
                _open_branches(self.page, "clean_engineering", "kanban", "Ticket")
                _select(self.page, "Operation delete")
                _line(self.page, "self.close()").wait_for(timeout=_SHOWN_MILLISECONDS)
                self.page.locator(".callout-mark").first.wait_for(timeout=_SHOWN_MILLISECONDS)

            with after.all:
                self.page.close()

            with context("with a line inside the class it names"):
                with it("should never open the class it sits in"):
                    expect(_mark_on(self.page, "class Ticket:")).to(be_none)

            with context("with a method's call on self"):
                with it("should open the method of the class around it"):
                    _open_callout_on(self.page, "self.close()")
                    expect(_callout_texts(self.page)).to(equal([CLOSE_LINES]))

            with context("with a call to a module function by its bare name"):
                with it("should open that function"):
                    _open_callout_on(self.page, "reread_all(board)")
                    expect([text for text in _callout_texts(self.page) if text.startswith("def reread_all")]).to(equal(["def reread_all(board) -> None:\n    board.reread()"]))

        with context("with ticket.py opened from the file list, its methods folded on open, and delete unfolded"):
            with before.all:
                self.page = self.stack.open(CHECKOUT_FLOW.name, "stories-acceptance-tests,clean-engineering-code")
                _graph_view(self.page)
                self.page.get_by_role("button", name="List", exact=True).click()
                self.page.locator(f'button.file-entry[title="{TICKET_CODE}"]').click()
                self.page.locator(".callout-mark").first.wait_for(timeout=_SHOWN_MILLISECONDS)
                _line(self.page, "def delete(self, board: Board) -> None:").click()
                self.page.keyboard.press("Control+Shift+BracketRight")
                _line(self.page, "self.close()").wait_for(timeout=_SHOWN_MILLISECONDS)
                _open_callout_on(self.page, "self.close()")

            with after.all:
                self.page.close()

            with context("with a method's call on self"):
                with it("should show the method it opens, its lines taking room under the line"):
                    heights = _settled(lambda: _callout_heights(self.page), lambda shown: bool(shown) and min(shown) > 0)
                    expect(min(heights or [0.0])).to(be_above(0))

    with description("a design canvas in the file bar"):
        with context("with UX on and version-1 published at its link in versions.json"):
            with before.all:
                self.page = self.stack.open(DESIGN_REVIEW, "ux-mockup,stories-story-map")
                self.entry = self.page.locator(f'a.file-entry.is-published[title^="{CANVAS}"]')
                self.entry.wait_for(timeout=_SHOWN_MILLISECONDS)

            with after.all:
                self.page.close()

            with it("should open the design canvas at its link"):
                expect(self.entry.get_attribute("href")).to(equal(CANVAS_LINK))

            with it("should be named by its version, marked as a design canvas"):
                expect(self.entry.inner_text().replace(_NBSP, " ").strip()).to(equal("version-1 ↗ design canvas"))

    with description("a whiteboard file in the file bar"):
        with context("with its board in Claude kept in whiteboards.json, and the diagram filter on"):
            with before.all:
                self.page = self.stack.open(DESIGN_REVIEW, "ux-mockup,stories-story-map")
                diagram = self.page.locator('.format-toggle[title^="diagram:"]')
                diagram.wait_for(timeout=_SHOWN_MILLISECONDS)
                if diagram.get_attribute("aria-pressed") != "true":
                    diagram.click()
                self.page.locator('.format-toggle[title^="diagram:"][aria-pressed="true"]').wait_for(timeout=_SHOWN_MILLISECONDS)
                self.entry = self.page.locator(f'a.file-entry.is-published[title^="{WHITEBOARD}"]')
                self.entry.wait_for(timeout=_SHOWN_MILLISECONDS)

            with after.all:
                self.page.close()

            with it("should open its board"):
                expect(self.entry.get_attribute("href")).to(equal(BOARD_LINK))

            with it("should be named story-map, marked as a whiteboard"):
                expect(self.entry.inner_text().replace(_NBSP, " ").strip()).to(equal("story-map ↗ whiteboard"))
