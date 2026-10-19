"""BDD spec for tools/context_setup/context_setup.py — ContextSetup toolset.

Covers Increment 1 stories:
  Tool --> Convert To Markdown           (convert tool)
  AI Chat --> Review Document Structure  (action expansion — convert is listed)
  User --> Capture From Documents        (action expansion — step order)

Covers Increment 2 stories:
  User --> Capture From Live App         (action expansion — step order)
  Tool --> Smoke Test App                (smoke_test tool — real HTTP server)
  Tool --> Scout App Pages               (scout_app tool — Playwright against real HTTP server)
  Tool --> Complete App Capture          (complete_capture tool — targeted re-capture)
"""
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
for _cat in ("tools", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_empty, be_false, be_true, contain, equal, expect, have_len
from mamba import after, before, context, description, it

from inspect import signature

from context_setup.context_setup import (
    CaptureResult,
    ContextSetup,
    ConversionResult,
    PageCapture,
    ScoutResult,
    ScreenResult,
    SmokeTestResult,
    StructureNote,
)
from harness.agent_tools.agent_tools import AgentInstructions


# ── helpers ───────────────────────────────────────────────────────────────────

_TEST_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head><title>Test App</title></head>
<body>
  <main>
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
  <main>
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
    def __init__(self) -> None:
        self._root = Path()
        self._name = ""
        self._content = ""

    def context_setup(self) -> ContextSetup:
        return ContextSetup.from_defaults()

    def start_test_server(self) -> tuple[HTTPServer, int]:
        server = HTTPServer(("localhost", 0), _AppHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.1)
        return server, port

    def expanded_capture_from_documents(self) -> str:
        cs = self.context_setup()
        func = getattr(type(cs), "capture_from_documents")
        body = AgentInstructions.for_callable(func, cs)
        return "\n".join(body.prompt)

    def expanded_capture_from_live_app(self) -> str:
        cs = self.context_setup()
        func = getattr(type(cs), "capture_from_live_app")
        body = AgentInstructions.for_callable(func, cs)
        return "\n".join(body.prompt)

    def write(self) -> Path:
        path = self._root / self._name
        path.write_text(self._content, encoding="utf-8")
        return path


fixture = SpecFixture()


# ── spec ─────────────────────────────────────────────────────────────────────

with description("a ContextSetup"):
    with context("that is created"):
        with it("should be a ContextSetup instance"):
            expect(ContextSetup.from_defaults()).to(be_a(ContextSetup))

    with context("that chooses where capture artifacts are written"):
        with it("should write under repo_path when capture_repo is blank"):
            app = Path(tempfile.mkdtemp())
            cs = ContextSetup.from_defaults()
            cs.repo_path = str(app)
            cs.capture_repo = ""
            expect(cs._write_root().resolve()).to(equal(app.resolve()))

        with it("should write under capture_repo when it is given"):
            app = Path(tempfile.mkdtemp())
            capture = Path(tempfile.mkdtemp())
            cs = ContextSetup.from_defaults()
            cs.repo_path = str(app)
            cs.capture_repo = str(capture)
            expect(cs._write_root().resolve()).to(equal(capture.resolve()))

    # ── Tool: Convert To Markdown ─────────────────────────────────────────────

    with context("whose convert tool is given a folder with a plain markdown file"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            fixture._root = self._root
            fixture._name = "notes.md"
            fixture._content = "# Title\n\nSome body text with several words.\n"
            fixture.write()
            self._result = ContextSetup.from_defaults().convert(str(self._root))

        with after.each:
            self._tmp.cleanup()

        with it("should return a ConversionResult"):
            expect(self._result).to(be_a(ConversionResult))

        with it("should list exactly one markdown file"):
            expect(self._result.markdown_files).to(have_len(1))

        with it("should write the markdown file under the markdown/ subdirectory"):
            out = Path(self._result.markdown_files[0])
            expect(out.parent.name).to(equal("markdown"))

        with it("should preserve the file stem"):
            out = Path(self._result.markdown_files[0])
            expect(out.stem).to(equal("notes"))

        with it("should produce one StructureNote"):
            expect(self._result.structure_notes).to(have_len(1))

        with it("should detect the heading depth as 1"):
            note = self._result.structure_notes[0]
            expect(note.heading_depth).to(equal(1))

        with it("should count one heading"):
            note = self._result.structure_notes[0]
            expect(note.heading_count).to(equal(1))

        with it("should count words greater than zero"):
            note = self._result.structure_notes[0]
            expect(note.word_count > 0).to(be_true)

    with context("whose convert tool is given a folder with multiple heading levels"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            fixture._root = self._root
            fixture._name = "deep.md"
            fixture._content = "# H1\n\n## H2\n\n### H3\n\nsome content words here\n"
            fixture.write()
            self._result = ContextSetup.from_defaults().convert(str(self._root))

        with after.each:
            self._tmp.cleanup()

        with it("should report heading_depth as 3"):
            note = self._result.structure_notes[0]
            expect(note.heading_depth).to(equal(3))

        with it("should count three headings"):
            note = self._result.structure_notes[0]
            expect(note.heading_count).to(equal(3))

    with context("whose convert tool is given a folder with no headings"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            fixture._root = self._root
            fixture._name = "flat.md"
            fixture._content = "Just plain prose with no headings at all.\n"
            fixture.write()
            self._result = ContextSetup.from_defaults().convert(str(self._root))

        with after.each:
            self._tmp.cleanup()

        with it("should report heading_depth as 0 (flat document)"):
            note = self._result.structure_notes[0]
            expect(note.heading_depth).to(equal(0))

        with it("should report heading_count as 0"):
            note = self._result.structure_notes[0]
            expect(note.heading_count).to(equal(0))

    with context("whose convert tool is given a folder containing an unsupported file type"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            fixture._root = self._root
            fixture._name = "ignored.csv"
            fixture._content = "col1,col2\nval1,val2\n"
            fixture.write()
            fixture._name = "kept.md"
            fixture._content = "# Kept\n\nContent.\n"
            fixture.write()
            self._result = ContextSetup.from_defaults().convert(str(self._root))

        with after.each:
            self._tmp.cleanup()

        with it("should skip the unsupported file"):
            expect(self._result.markdown_files).to(have_len(1))

        with it("should only include the supported file"):
            expect(Path(self._result.markdown_files[0]).stem).to(equal("kept"))

    with context("whose convert tool is given an empty folder"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._result = ContextSetup.from_defaults().convert(self._tmp.name)

        with after.each:
            self._tmp.cleanup()

        with it("should return no markdown files"):
            expect(self._result.markdown_files).to(be_empty)

        with it("should return no structure notes"):
            expect(self._result.structure_notes).to(be_empty)

    with context("whose convert tool is given multiple supported files"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            fixture._root = self._root
            fixture._name = "alpha.md"
            fixture._content = "# Alpha\n\nAlpha content.\n"
            fixture.write()
            fixture._name = "beta.md"
            fixture._content = "# Beta\n\nBeta content.\n"
            fixture.write()
            self._result = ContextSetup.from_defaults().convert(str(self._root))

        with after.each:
            self._tmp.cleanup()

        with it("should produce one entry per file"):
            expect(self._result.markdown_files).to(have_len(2))

        with it("should produce one structure note per file"):
            expect(self._result.structure_notes).to(have_len(2))

    # ── AgentTool: capture_from_documents (expansion tests) ─────────────────────

    with context("whose capture_from_documents action is expanded"):
        with it("should list convert as a tool to call"):
            prose = fixture.expanded_capture_from_documents()
            expect("convert" in prose).to(be_true)

        with it("should instruct the AI to ask the user to choose indexers"):
            prose = fixture.expanded_capture_from_documents()
            expect("AskQuestion" in prose or "indexer" in prose.lower()).to(be_true)

        with it("should mention partition delegation to context tools"):
            prose = fixture.expanded_capture_from_documents()
            expect("partition" in prose).to(be_true)

        with it("should mention embed as the final step"):
            prose = fixture.expanded_capture_from_documents()
            expect("embed" in prose).to(be_true)

    with context("whose capture_from_documents action tool_steps are resolved"):
        with it("should include convert"):
            from harness.agent_tools.agent_tools import AgentInstructions
            cs = ContextSetup.from_defaults()
            func = getattr(type(cs), "capture_from_documents")
            body = AgentInstructions.for_callable(func, cs)
            expect("convert" in body.tool_steps).to(be_true)

        with it("should include partition for each context tool (5 total)"):
            from harness.agent_tools.agent_tools import AgentInstructions
            cs = ContextSetup.from_defaults()
            func = getattr(type(cs), "capture_from_documents")
            body = AgentInstructions.for_callable(func, cs)
            expect(body.tool_steps.count("partition")).to(equal(5))

        with it("should include embed from ContextIndex"):
            from harness.agent_tools.agent_tools import AgentInstructions
            cs = ContextSetup.from_defaults()
            func = getattr(type(cs), "capture_from_documents")
            body = AgentInstructions.for_callable(func, cs)
            expect("embed" in body.tool_steps).to(be_true)

    # ── AgentTool: capture_from_live_app (expansion tests) ──────────────────────

    with context("whose capture_from_live_app action is expanded"):
        with it("should instruct the AI to classify external dependencies"):
            prose = fixture.expanded_capture_from_live_app()
            expect("Classify External Dependencies" in prose or "classify" in prose.lower()).to(be_true)

        with it("should mention the complex-stub trigger threshold"):
            prose = fixture.expanded_capture_from_live_app()
            expect("5" in prose and "external" in prose.lower()).to(be_true)

        with it("should write the complex-stub pre-pass as stub-focus-map.md not Stories story-map.md"):
            prose = fixture.expanded_capture_from_live_app()
            expect("tests/stubs/stub-focus-map.md" in prose).to(be_true)
            expect("tests/stubs/story-map.md" in prose).to(be_false)

        with it("should instruct the AI to write external stubs"):
            prose = fixture.expanded_capture_from_live_app()
            expect("stub" in prose.lower()).to(be_true)

        with it("should tell the AI to write global stubs under tests/stubs/{system}/"):
            prose = fixture.expanded_capture_from_live_app()
            expect("tests/stubs/{system}/" in prose).to(be_true)

        with it("should tell the AI domain-owned stubs go on the aggregate"):
            prose = fixture.expanded_capture_from_live_app()
            expect("domain/{aggregate}/stubs/{system}/" in prose).to(be_true)

        with it("should forbid a domain folder inside tests"):
            prose = fixture.expanded_capture_from_live_app()
            expect("never" in prose.lower() and "domain folder" in prose.lower()).to(be_true)

        with it("should scout under sandbox/extracted-context"):
            prose = fixture.expanded_capture_from_live_app()
            expect("sandbox/extracted-context" in prose).to(be_true)

        with it("should accept capture_repo on capture_from_live_app"):
            expect("capture_repo" in signature(ContextSetup.capture_from_live_app).parameters).to(
                be_true
            )

        with it("should tell the AI to set capture_repo then call smoke_test with repo_path and surface"):
            prose = fixture.expanded_capture_from_live_app()
            expect("capture_repo field" in prose).to(be_true)
            expect("smoke_test(repo_path=repo_path, surface=surface)" in prose).to(be_true)

        with it("should list smoke_test as a tool to call"):
            prose = fixture.expanded_capture_from_live_app()
            expect("smoke_test" in prose).to(be_true)

        with it("should list scout_app as a tool to call"):
            prose = fixture.expanded_capture_from_live_app()
            expect("scout_app" in prose).to(be_true)

        with it("should list complete_capture as a tool to call"):
            prose = fixture.expanded_capture_from_live_app()
            expect("complete_capture" in prose).to(be_true)

        with it("should mention PASS WARN FAIL review verdicts"):
            prose = fixture.expanded_capture_from_live_app()
            expect("PASS" in prose and "FAIL" in prose).to(be_true)

        with it("should list embed as the final indexing step"):
            prose = fixture.expanded_capture_from_live_app()
            expect("embed" in prose).to(be_true)

    with context("whose capture_from_live_app action tool_steps are resolved"):
        with it("should include smoke_test"):
            cs = ContextSetup.from_defaults()
            func = getattr(type(cs), "capture_from_live_app")
            body = AgentInstructions.for_callable(func, cs)
            expect("smoke_test" in body.tool_steps).to(be_true)

        with it("should include scout_app"):
            cs = ContextSetup.from_defaults()
            func = getattr(type(cs), "capture_from_live_app")
            body = AgentInstructions.for_callable(func, cs)
            expect("scout_app" in body.tool_steps).to(be_true)

        with it("should include complete_capture"):
            cs = ContextSetup.from_defaults()
            func = getattr(type(cs), "capture_from_live_app")
            body = AgentInstructions.for_callable(func, cs)
            expect("complete_capture" in body.tool_steps).to(be_true)

        with it("should include embed from ContextIndex"):
            cs = ContextSetup.from_defaults()
            func = getattr(type(cs), "capture_from_live_app")
            body = AgentInstructions.for_callable(func, cs)
            expect("embed" in body.tool_steps).to(be_true)

    # ── Tool: smoke_test ─────────────────────────────────────────────────────

    with context("whose smoke_test tool is given a running web server"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._server, port = fixture.start_test_server()
            self._base_url = f"http://localhost:{port}"
            cs = ContextSetup.from_defaults()
            cs.base_url = self._base_url
            cs.entry_paths = ["/"]
            self._result = cs.smoke_test(
                repo_path=self._tmp.name,
                surface="web",
            )

        with after.each:
            self._server.shutdown()
            self._tmp.cleanup()

        with it("should return a SmokeTestResult"):
            expect(self._result).to(be_a(SmokeTestResult))

        with it("should report passed=True when the root is reachable"):
            expect(self._result.passed).to(be_true)

        with it("should contain one ScreenResult for the probed path"):
            expect(self._result.screen_results).to(have_len(1))

        with it("should record status 200 for the root"):
            expect(self._result.screen_results[0].status_code).to(equal(200))

        with it("should write an inventory file"):
            expect(Path(self._result.inventory_path).exists()).to(be_true)

        with it("should write the inventory under tests/stubs/"):
            expect(Path(self._result.inventory_path).as_posix()).to(
                contain("tests/stubs/stub-inventory.md")
            )

    with context("whose smoke_test tool is probing a non-existent server"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            cs = ContextSetup.from_defaults()
            cs.base_url = "http://localhost:19999"
            cs.entry_paths = ["/"]
            self._result = cs.smoke_test(
                repo_path=self._tmp.name,
                surface="web",
            )

        with after.each:
            self._tmp.cleanup()

        with it("should return passed=False when the server is not reachable"):
            expect(self._result.passed).to(be_false)

        with it("should record status 0 for the unreachable path"):
            expect(self._result.screen_results[0].status_code).to(equal(0))

    with context("whose smoke_test tool probes multiple paths"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._server, port = fixture.start_test_server()
            self._base_url = f"http://localhost:{port}"
            cs = ContextSetup.from_defaults()
            cs.base_url = self._base_url
            cs.entry_paths = ["/", "/login"]
            self._result = cs.smoke_test(
                repo_path=self._tmp.name,
                surface="web",
            )

        with after.each:
            self._server.shutdown()
            self._tmp.cleanup()

        with it("should produce one ScreenResult per path"):
            expect(self._result.screen_results).to(have_len(2))

        with it("should mark all reachable paths as passed"):
            expect(self._result.passed).to(be_true)

    # ── Tool: scout_app ──────────────────────────────────────────────────────

    with context("whose scout_app tool captures pages from a running web server"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._server, port = fixture.start_test_server()
            self._base_url = f"http://localhost:{port}"
            cs = ContextSetup.from_defaults()
            cs.base_url = self._base_url
            cs.entry_paths = ["/", "/login"]
            self._result = cs.scout_app(
                repo_path=self._tmp.name,
                surface="web",
            )

        with after.each:
            self._server.shutdown()
            self._tmp.cleanup()

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
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._server, port = fixture.start_test_server()
            self._base_url = f"http://localhost:{port}"
            cs = ContextSetup.from_defaults()
            cs.base_url = self._base_url
            cs.entry_paths = ["/"]
            self._scout = cs.scout_app(
                repo_path=self._tmp.name,
                surface="web",
            )
            self._result = cs.complete_capture(
                repo_path=self._tmp.name,
                missing_pages=["/login"],
            )

        with after.each:
            self._server.shutdown()
            self._tmp.cleanup()

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
