"""The Files app in a real browser, on its real server, talking to a real cdd server about a real git project: what
the browser tier of Review Generated Work In File Viewer's story tests (`*.story.ui_e2e_spec.py` beside each sub-epic's
scenarios) runs on. The twins of the Files app's unit specs (``harness/files_app/app/files/source-folding.spec.ts``, ``call-expansion.spec.ts``,
``file-bar.spec.ts``), which stub the session's answers and the editor: here the page is built from this checkout's
source, served by the Files server (``harness/files_app/app/spec-files-server.ts``, as ``serve.ts`` serves it), and drives Monaco in
Chromium, while the session's files, graph and members come from a cdd server of the spec's own.

Everything is the spec's own, so it runs beside anything else: the page is built into a temporary folder, never the
app's ``dist``; the Files server, the cdd server and the draw.io viewer answer on free ports, never 8783, 8791 or the
person's cdd server; the cdd server runs from a throwaway ``~/.cdd`` (*SpecServer*); the draw.io viewer is already
running, from a throwaway folder of its own, as the person's shared viewer runs from whichever project started it; and
the project is a throwaway git repository. Monaco loads as the live page loads it, and draw.io from embed.diagrams.net
as the viewer loads it.

``FilesStack.on_another_project`` starts the Files server for this CDD checkout, as ``serve.ts`` starts it for
FILES_PROJECT, and opens the page on the throwaway project, as a chat working in another project opens it: every file,
graph and diagram the page shows must then come from the project its link names."""

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
from harness.whiteboard import Whiteboard
from space.kanban.graph_view_rule_examples import VIOLATING_MAP_TEXT
from space.kanban.graph_view_examples import BOARD_CODE, BOARD_TEXT, CHECKOUT_FLOW, STEP_STORY, STEP_STORY_TEXT, TICKET_EXAMPLES, TICKET_EXAMPLES_TEXT

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
# published at its link (versions.json) and its story map drawn on a whiteboard published to a board, whose address the file keeps.
DESIGN_REVIEW = "design-review"
CANVAS = "design/ux/design-canvas/version-1/project/canvas.json"
CANVAS_LINK = "https://claude.ai/artifact/checkout-canvas"
WHITEBOARD = "design/.context/story-map.whiteboard"
BOARD_LINK = "https://claude.ai/artifact/story-board"
# The story map's board as Render saves it: one epic bar over one story card.
BOARD_STORY = "Browse Product Catalog"
WHITEBOARD_TEXT = json.dumps({
    "v": 1,
    "title": "Story Map",
    "order": ["epic", "story"],
    "elements": {
        "epic": {"type": "shape", "color": "purple", "text": "Manage Customer Orders", "x": 20, "y": 120, "w": 168, "h": 60},
        "story": {"type": "shape", "color": "yellow", "text": f"*Customer*\n{BOARD_STORY}", "x": 32, "y": 280, "w": 152, "h": 152},
    },
})

# Seed: story-review, a session working in the project's review folder with Stories alone on, whose story map holds two
# stories whose names describe a system mechanic, which story-name-captures-system-mechanic lists as candidates, beside
# Delete Ticket, which it does not.
STORY_REVIEW = "story-review"
REVIEW_MAP = "review/.context/story-map.md"

# Seed, on another project only: design-review's story map drawn in draw.io, one page named Checkout Story Map holding
# one cell labelled Place Order. The draw.io viewer's own folder holds no such file, so a viewer sent the path from the
# project's root opens a blank Page-1 instead.
DIAGRAM = "design/.context/story-map.drawio"
DIAGRAM_PAGE = "Checkout Story Map"
DIAGRAM_CELL = "Place Order"
DIAGRAM_TEXT = (
    '<mxfile><diagram id="checkout-map" name="Checkout Story Map"><mxGraphModel><root>'
    '<mxCell id="0"/><mxCell id="1" parent="0"/>'
    '<mxCell id="place-order" value="Place Order" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">'
    '<mxGeometry x="40" y="40" width="160" height="60" as="geometry"/></mxCell>'
    "</root></mxGraphModel></diagram></mxfile>\n"
)
# draw.io loads from embed.diagrams.net before it draws the diagram it is sent.
DRAWIO_LOADS_MILLISECONDS = 60_000
_DRAWIO_VIEWER = _REPO_ROOT / "tools" / "drawio_viewer" / "drawio_viewer.py"


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _git(folder: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=folder, capture_output=True, text=True, check=True)


def _write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


# Seed: the person turned every stage filter off, so a session's files show from every stage and in every format. Until
# someone chooses, a session's guidance selection shows only the stage its ticket stands in, whose format chips can leave
# out the files these scenarios list.
EVERY_STAGE = {"guidance": {"stages": []}}


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
    _write(root, ".sessions/checkout-flow/session.json", json.dumps({"name": CHECKOUT_FLOW.name, "title": CHECKOUT_FLOW.title, **CHECKOUT_FLOW.fields, **EVERY_STAGE}))
    _write(root, ".sessions/checkout-flow/session.log", "")
    _write(root, CANVAS, "{}\n")
    _write(root, "design/ux/design-canvas/versions.json", json.dumps({"version-1": CANVAS_LINK}))
    _write(root, WHITEBOARD, Whiteboard.published_to(WHITEBOARD_TEXT, BOARD_LINK))
    _write(root, f".sessions/{DESIGN_REVIEW}/session.json", json.dumps({"name": DESIGN_REVIEW, "title": "Design review", "workpath": str(root / "design"), **EVERY_STAGE}))
    _write(root, f".sessions/{DESIGN_REVIEW}/session.log", "")
    _write(root, REVIEW_MAP, VIOLATING_MAP_TEXT)
    review = {"practices": {key: {"enabled": False} for key in ("ux", "ddd", "bdd", "clean_engineering")}, "outputs": {"stories": {"root": ".context"}}}
    _write(root, f".sessions/{STORY_REVIEW}/session.json", json.dumps({"name": STORY_REVIEW, "title": "Story review", "workpath": str(root / "review"), **review, **EVERY_STAGE}))
    _write(root, f".sessions/{STORY_REVIEW}/session.log", "")


def _seed_measured_project(root: Path) -> None:
    """The seeded project, whose config chooses to measure its code with the shipped tools and limits."""
    _seed_project(root)
    _write(root, ".context/config.json", json.dumps({"code_measures": {}}))


# Seed: in story-review's folder, what its file menu acts on: a note to delete, a note no fidelity declares, which only All
# files lists, and a folder of scenarios to add to Stories.
REVIEW_NOTE = "review/.context/notes.md"
UNDECLARED_NOTE = "review/notes.txt"
REVIEW_SCENARIOS = "review/checkout"
REVIEW_SCENARIO_FILE = "review/checkout/checkout_story.test.md"


def _seed_files_to_act_on(root: Path) -> None:
    """The seeded project, with story-review's note, its undeclared note and its folder of scenarios."""
    _seed_project(root)
    for path, text in ((REVIEW_NOTE, "# notes\n"), (UNDECLARED_NOTE, "a note\n"), (REVIEW_SCENARIO_FILE, "# Checkout\n")):
        _write(root, path, text)


# Seed: plain-work, a session in a project that is a plain folder, no git repository, with Discovery and Stories alone
# on and its story map in markdown, as the Nov 18 demo's session had them: its story map and its sketch written under
# .context, and a note of no fidelity beside it.
PLAIN_WORK = "plain-work"
PLAIN_MAP = ".context/story-map.md"
PLAIN_NOTE = "notes/plain.txt"
PLAIN_SKETCH = f".context/{PLAIN_WORK}-sketch.md"


def _seed_plain_folder(root: Path) -> None:
    """A plain folder, never made a git repository, holding plain-work's session, its story map, its sketch and a note."""
    _write(root, PLAIN_MAP, VIOLATING_MAP_TEXT)
    _write(root, PLAIN_SKETCH, "# Stories\n")
    _write(root, PLAIN_NOTE, "a note\n")
    practices = {key: {"enabled": False} for key in ("ux", "ddd", "bdd", "clean_engineering")}
    practices["stories"] = {"enabled": True, "formats": {"story_map": ["markdown"]}}
    plain = {"guidance": {"stages": ["discovery"]}, "practices": practices, "outputs": {"stories": {"root": ".context"}}}
    _write(root, f".sessions/{PLAIN_WORK}/session.json", json.dumps({"name": PLAIN_WORK, "title": "Plain work", **plain}))
    _write(root, f".sessions/{PLAIN_WORK}/session.log", "")


class FilesStack:
    """The Files app as a person meets it, every part of it the spec's own: the page built from this checkout, the Files
    server serving it, the cdd server it asks, a project, a git repository unless seeded otherwise, and Chromium.
    ``close`` stops and removes all of them."""

    def __init__(self, started_for: Path | None = None, seed=_seed_project) -> None:
        """started_for is the project the Files server is started for, the one a call naming no project is about; the
        seeded project when none is given. seed writes the project."""
        self.top = Path(tempfile.mkdtemp(prefix="cdd-files-e2e-")).resolve()
        self.project = self.top / "project"
        self.project.mkdir()
        seed(self.project)
        self._build_page()
        self.cdd = SpecServer()
        self.cdd.start()
        self.drawio_root = self.top / "drawio-viewer"
        self.drawio_root.mkdir()
        self.drawio_port = _free_port()
        self._drawio = subprocess.Popen([sys.executable, str(_DRAWIO_VIEWER), str(self.drawio_root), str(self.drawio_port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self._wait_for(self.drawio_port, "the draw.io viewer")
        self.port = _free_port()
        started = str(started_for or self.project)
        self._files = subprocess.Popen(["node", str(_NODE_TSX), "spec-files-server.ts", str(self.top / "dist"), str(self.port), started, str(self.drawio_port)], cwd=_APP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self._wait_for(self.port, "the Files server")
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch()
        self._user_agent = self._browser_user_agent()

    @classmethod
    def on_another_project(cls) -> "FilesStack":
        """The Files app opened on a project other than the CDD checkout: its server started for this checkout, the
        draw.io viewer running from a folder of its own, and the page on the seeded project, which also holds
        design-review's story map diagram."""
        stack = cls(started_for=_REPO_ROOT)
        _write(stack.project, DIAGRAM, DIAGRAM_TEXT)
        return stack

    @classmethod
    def on_a_project_that_measures_its_code(cls) -> "FilesStack":
        """The Files app opened on the seeded project once its config holds a code measures section, so its code is
        held to Clean Engineering's shipped limits and a node's metrics group shows."""
        return cls(seed=_seed_measured_project)

    @classmethod
    def with_files_to_act_on(cls) -> "FilesStack":
        """The Files app opened on the seeded project once story-review's folder holds what its file menu acts on: a
        note to delete, a note no fidelity declares and a folder of scenarios."""
        return cls(seed=_seed_files_to_act_on)

    @classmethod
    def in_a_plain_folder(cls) -> "FilesStack":
        """The Files app opened on a project that is a plain folder, no git repository: plain-work's story map and a
        note."""
        return cls(seed=_seed_plain_folder)

    def _build_page(self) -> None:
        subprocess.run(["node", str(_NODE_VITE), "build", "--outDir", str(self.top / "dist"), "--emptyOutDir"], cwd=_APP, capture_output=True, text=True, check=True)

    def _wait_for(self, port: int, server: str) -> None:
        deadline = time.monotonic() + _SERVER_STARTS_WITHIN_SECONDS
        while time.monotonic() < deadline:
            try:
                with urlopen(f"http://127.0.0.1:{port}/", timeout=2):
                    return
            except (urllib.error.URLError, OSError):
                time.sleep(0.25)
        raise TimeoutError(f"{server} did not answer on port {port} within {_SERVER_STARTS_WITHIN_SECONDS} s")

    def _browser_user_agent(self) -> str:
        """Chromium's own user agent, named as the browser a person runs: embed.diagrams.net refuses a headless one, so
        draw.io would never load in the viewer's page."""
        page = self.browser.new_page()
        try:
            return page.evaluate("navigator.userAgent").replace("HeadlessChrome", "Chrome")
        finally:
            page.close()

    def open(self, ticket: str, fidelities: str) -> Page:
        """A new page on the files of ticket's fidelities, as the chat bar's files button opens it."""
        page = self.browser.new_page(viewport={"width": 1600, "height": 900}, user_agent=self._user_agent)
        query = urllib.parse.urlencode({"files": ticket, "fidelity": fidelities, "project": str(self.project)})
        page.goto(f"http://127.0.0.1:{self.port}/?{query}")
        return page

    def close(self) -> None:
        self.browser.close()
        self._playwright.stop()
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(self._files.pid)], capture_output=True) if sys.platform == "win32" else self._files.kill()
        self._files.wait()
        self._drawio.kill()
        self._drawio.wait()
        self.cdd.stop()
        shutil.rmtree(self.top, ignore_errors=True)


def drawio_editor(page: Page):
    """The draw.io editor the file view shows: the viewer's page in the Files app's frame, and draw.io in the viewer's."""
    return page.frame_locator("iframe.drawio-frame").frame_locator("iframe#drawio")


def all_session_files(page: Page) -> None:
    """Every file under the session's root listed, not only the files the session's branch changed."""
    page.get_by_role("button", name="All session files").click()
    page.locator(".file-list, .file-tree").first.wait_for(timeout=SHOWN_MILLISECONDS)


def tab_opened_by(page: Page, entry) -> str:
    """The address of the browser tab a press on entry opens, as a page no chat opened opens a board in Claude; the tab
    is closed once read."""
    with page.expect_popup(timeout=SHOWN_MILLISECONDS) as opened:
        entry.click()
    tab = opened.value
    tab.wait_for_load_state(timeout=SHOWN_MILLISECONDS)
    address = tab.url
    tab.close()
    return address


def graph_view(page: Page) -> None:
    """Every file under the session's root listed, shown as the session's graph, read for real."""
    all_session_files(page)
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


def lines_in_order(page: Page, path: str) -> list[str]:
    """The lines the open file path shows, top to bottom: Monaco keeps their elements in no order, so they are read by
    where each sits."""
    tops = page.locator(f'section.open-file[aria-label="{path}"] .view-lines .view-line').evaluate_all("lines => lines.map(line => [line.offsetTop, line.innerText])")
    return [text.replace(NBSP, " ") for _, text in sorted(tops)]


def open_files(page: Page) -> list[str]:
    """The files open in the file view, top to bottom."""
    return page.locator("section.open-file").evaluate_all("files => files.map(file => file.getAttribute('aria-label'))")


def marked_lines(page: Page, path: str) -> list[str]:
    """The lines the open file path shows marked as selected, top to bottom: the mark sits in the editor's margin, level
    with the line it marks."""
    read = """file => {
        const marked = new Set([...file.querySelectorAll('.file-selected-range')].map(mark => mark.parentElement.style.top))
        return [...file.querySelectorAll('.view-lines .view-line')].filter(line => marked.has(line.style.top)).map(line => [line.offsetTop, line.innerText])
    }"""
    tops = page.locator(f'section.open-file[aria-label="{path}"]').evaluate(read)
    return [text.replace(NBSP, " ") for _, text in sorted(tops)]


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


