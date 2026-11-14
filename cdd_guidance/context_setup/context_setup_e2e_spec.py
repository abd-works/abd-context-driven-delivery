"""E2E spec for ContextSetup's live-app tools that drive a real browser: Playwright scouts and re-captures the
pages of a test app served on localhost. ``context_setup_heavy_spec.py`` covers the rest without a browser."""
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
import mcp.types  # SDK, before harness/mcp is on PYTHONPATH
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_empty, be_false, be_true, contain, equal, expect, have_len
from mamba import after, before, context, description, it

from inspect import signature

from cdd_guidance.context_setup.context_setup import ContextSetup, ConversionResult, StructureNote
from cdd_guidance.context_setup.live_app_capture import CaptureResult, PageCapture, ScoutResult, ScreenResult, SmokeTestResult
from harness.agent_tools.agent_tools import AgentInstructions
from harness.agent_tools.tool_call import ToolCall
from space.session.throwaway_project import ThrowawayProject


# ── helpers ───────────────────────────────────────────────────────────────────

_TEST_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head><title>Test App</title></head>
<body>
  <main id="root">
    <h1>Home</h1>
    <nav aria-label="main">
      <a href="/login">Login</a>
    </nav>
    <button>Get Started</button>
  </main>
</body>
</html>"""

_LOGIN_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head><title>Login</title></head>
<body>
  <main id="root">
    <h1>Login</h1>
    <form>
      <input type="text" aria-label="Username" />
      <input type="password" aria-label="Password" />
      <button type="submit">Sign In</button>
    </form>
  </main>
</body>
</html>"""


class _AppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = _LOGIN_HTML if self.path == "/login" else _TEST_HTML
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_: object) -> None:
        pass  # silence server logs during tests


class SpecFixture:
    """Opens the folders, servers, and projects an example works with, and closes every one of them in ``release``. An
    ``after.each`` that closed the attributes its ``before.each`` set would raise AttributeError whenever that setup
    failed part way, and mamba would report that error in place of the one that broke the setup."""

    def __init__(self) -> None:
        self._root = Path()
        self._name = ""
        self._content = ""
        self._folders: list[tempfile.TemporaryDirectory] = []
        self._servers: list[HTTPServer] = []
        self.session_root = Path()

    def temporary_folder(self) -> Path:
        folder = tempfile.TemporaryDirectory()
        self._folders.append(folder)
        return Path(folder.name)

    def start_test_server(self) -> int:
        """Serve the test app on a free port until ``release``; answer the port."""
        server = HTTPServer(("localhost", 0), _AppHandler)
        self._servers.append(server)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        time.sleep(0.1)
        return server.server_address[1]

    def release(self) -> None:
        while self._servers:
            self._servers.pop().shutdown()
        while self._folders:
            self._folders.pop().cleanup()
        ThrowawayProject.close_all()

    def context_setup_for_a_call(self) -> ContextSetup:
        """A ContextSetup made for a call on a throwaway project, as the cdd server makes one for each call, so it works
        in the session open in that project."""
        call = ToolCall(project=ThrowawayProject().root)
        self.session_root = call.session.work_root
        return ContextSetup().for_call(call)

    def instructions_for(self, cs: ContextSetup, name: str) -> AgentInstructions:
        return AgentInstructions.for_callable(getattr(type(cs), name), cs)

    def expanded_capture_from_live_app(self) -> str:
        cs = ContextSetup()
        return "\n".join(self.instructions_for(cs, "capture_from_live_app").prompt)

    def write(self) -> Path:
        path = self._root / self._name
        path.write_text(self._content, encoding="utf-8")
        return path


fixture = SpecFixture()


# ── spec ─────────────────────────────────────────────────────────────────────

with description("a ContextSetup driving a real browser"):
    # ── Tool: scout_app ──────────────────────────────────────────────────────

    with context("whose scout_app tool captures pages from a running web server"):
        with before.all:
            self._folder = str(fixture.temporary_folder())
            port = fixture.start_test_server()
            self._base_url = f"http://localhost:{port}"
            self._result = fixture.context_setup_for_a_call().scout_app(
                repo_path=self._folder,
                surface="web",
                base_url=self._base_url,
                entry_paths=["/", "/login"],
            )

        with after.all:
            fixture.release()

        with it("should return a ScoutResult"):
            expect(self._result).to(be_a(ScoutResult))

        with it("should capture one PageCapture per entry point"):
            expect(self._result.page_captures).to(have_len(2))

        with it("should write a screenshot for each captured page"):
            for cap in self._result.page_captures:
                expect(Path(cap.screenshot_path).exists()).to(be_true)

        with it("should write an aria.yaml for each captured page"):
            for cap in self._result.page_captures:
                expect(Path(cap.aria_path).exists()).to(be_true)

        with it("should write the extraction-overview.md"):
            expect(Path(self._result.overview_path).exists()).to(be_true)

        with it("should write capture under sandbox/extracted-context/app-extraction"):
            expect(Path(self._result.overview_path).as_posix()).to(
                contain("sandbox/extracted-context/app-extraction")
            )

        with it("should report the correct page count via page_count property"):
            expect(self._result.page_count).to(equal(2))

        with it("should list both page slugs via page_slugs property"):
            expect(self._result.page_slugs).to(have_len(2))

    # ── Tool: complete_capture ───────────────────────────────────────────────

    with context("whose complete_capture tool adds a missing page to an existing capture"):
        with before.all:
            self._folder = str(fixture.temporary_folder())
            port = fixture.start_test_server()
            self._base_url = f"http://localhost:{port}"
            cs = fixture.context_setup_for_a_call()
            self._scout = cs.scout_app(
                repo_path=self._folder,
                surface="web",
                base_url=self._base_url,
                entry_paths=["/"],
            )
            self._result = cs.complete_capture(
                repo_path=self._folder,
                missing_pages=["/login"],
                base_url=self._base_url,
            )

        with after.all:
            fixture.release()

        with it("should return a CaptureResult"):
            expect(self._result).to(be_a(CaptureResult))

        with it("should add one new PageCapture for the missing page"):
            expect(self._result.added_captures).to(have_len(1))

        with it("should write a screenshot for the added page"):
            cap = self._result.added_captures[0]
            expect(Path(cap.screenshot_path).exists()).to(be_true)

        with it("should write an aria.yaml for the added page"):
            cap = self._result.added_captures[0]
            expect(Path(cap.aria_path).exists()).to(be_true)

        with it("should report total_page_count as scout count plus added count"):
            expect(self._result.total_page_count).to(equal(
                self._scout.page_count + len(self._result.added_captures)
            ))

        with it("should update the extraction-overview.md with the new page section"):
            overview = Path(self._result.overview_path).read_text(encoding="utf-8")
            expect(any(cap.slug in overview for cap in self._result.added_captures)).to(be_true)
