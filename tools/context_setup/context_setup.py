"""ContextSetup — converts a folder of documents to markdown and delegates partitioning to context tools."""
from __future__ import annotations

import dataclasses
import logging
import re
from pathlib import Path
from typing import Optional

from harness.agent_tools import agent_instructions, agent_toolset
from harness.agent_tools.agent_tools import agent_tool
from installation.files import skill
from harness.mcp.mcp_server import mcp
from partition.partition import Partition

from practices.clean_engineering.clean_engineering import CleanEngineering
from practices.ddd.ddd import Ddd
from practices.stories.stories import Stories
from practices.ux.ux import Ux
from context_setup.context_index import ContextIndex

_log = logging.getLogger(__name__)

# ── Result types ─────────────────────────────────────────────────────────────

@dataclasses.dataclass
class StructureNote:
    """Structural metrics for one converted markdown file."""

    file: str
    heading_depth: int     # maximum heading level found (1–6); 0 if no headings
    heading_count: int     # total number of heading lines
    word_count: int        # approximate word count of the full document

@dataclasses.dataclass
class ConversionResult:
    """All markdown files produced by a single convert() call."""

    markdown_files: list[str]
    structure_notes: list[StructureNote]

@dataclasses.dataclass
class ScreenResult:
    """Reachability verdict for one screen during a smoke test."""

    slug: str
    url: str
    reachable: bool
    status_code: int

@dataclasses.dataclass
class SmokeTestResult:
    """Results of a smoke test run against the stubbed application."""

    passed: bool
    screen_results: list[ScreenResult]
    inventory_path: str

@dataclasses.dataclass
class PageCapture:
    """One captured page from a scout or complete-capture run."""

    slug: str
    url: str
    screenshot_path: str
    aria_path: str

@dataclasses.dataclass
class ScoutResult:
    """Results of the Phase 0 app scout."""

    overview_path: str
    pages_dir: str
    page_captures: list[PageCapture]

    @property
    def page_count(self) -> int:
        return len(self.page_captures)

    @property
    def page_slugs(self) -> list[str]:
        return [p.slug for p in self.page_captures]

@dataclasses.dataclass
class CaptureResult:
    """Results of a Phase N complete-capture run."""

    overview_path: str
    added_captures: list[PageCapture]
    total_page_count: int

# ── Toolset ───────────────────────────────────────────────────────────────────

_SUPPORTED = frozenset({".docx", ".doc", ".pdf", ".pptx", ".ppt", ".txt", ".md", ".html", ".htm"})
_STUBS_DIR = ("tests", "stubs")
_SCOUT_DIR = ("sandbox", "extracted-context", "app-extraction")
_COMMON_PORTS = [3000, 8000, 8080, 5000, 4000, 5173, 4173]


@agent_toolset
class ContextSetup:
    """Convert a folder of documents to markdown and delegate partitioning to selected context tools."""

    def __init__(
        self,
        stories: Optional[Stories] = None,
        clean_engineering: Optional[CleanEngineering] = None,
        ddd: Optional[Ddd] = None,
        ux: Optional[Ux] = None,
        partition: Optional[Partition] = None,
        context_index: Optional[ContextIndex] = None,
    ) -> None:
        self.stories = stories
        self.clean_engineering = clean_engineering
        self.ddd = ddd
        self.ux = ux
        self.partition = partition
        self.context_index = context_index
        self._apply_tool_modes()
        self._reset_capture_fields()

    @classmethod
    def from_defaults(cls) -> ContextSetup:
        return cls(
            stories=Stories(),
            clean_engineering=CleanEngineering(),
            ddd=Ddd(),
            ux=Ux(),
            partition=Partition(),
            context_index=ContextIndex(),
        )

    def _apply_tool_modes(self) -> None:
        for kit in (self.stories, self.clean_engineering, self.ddd, self.ux):
            if kit is not None:
                kit.mode = "tool"

    def _reset_capture_fields(self) -> None:
        self.repo_path = ""
        self.surface = "web"
        self.base_url = ""
        self.capture_repo = ""
        self.entry_paths: Optional[list[str]] = None
        self._pages_root = Path()
        self._overview_path = ""
        self._inventory_path = ""
        self._current_path = ""
        self._current_index = 0
        self._page_url = ""
        self._page_slug = ""
        self._screenshot_path = ""
        self._aria_path = ""

    # ── @tools — deterministic Python ────────────────────────────────────────

    @mcp
    @skill
    @agent_tool
    def convert(self, folder_path: str) -> ConversionResult:
        """Convert every supported document in folder_path to a Markdown file.
        Supported formats: .docx, .doc, .pdf, .pptx, .ppt, .txt, .md, .html, .htm.
        Writes each markdown document to folder_path/markdown/<stem>.md.
        Returns a ConversionResult containing markdown_files (absolute paths) and
        structure_notes (one StructureNote per file with heading_depth, heading_count,
        word_count)."""
        from markitdown import MarkItDown

        root = Path(folder_path)
        out_dir = root / "markdown"
        out_dir.mkdir(parents=True, exist_ok=True)

        self._converter = MarkItDown()
        self._out_dir = out_dir
        markdown_files: list[str] = []
        structure_notes: list[StructureNote] = []

        for src in sorted(root.iterdir()):
            note = self._convert_source(src)
            if note is None:
                continue
            markdown_files.append(note.file)
            structure_notes.append(note)

        return ConversionResult(
            markdown_files=markdown_files,
            structure_notes=structure_notes,
        )

    def _convert_source(self, src: Path) -> Optional[StructureNote]:
        if src.is_dir() or src.suffix.lower() not in _SUPPORTED:
            return None
        content = src.read_text(encoding="utf-8") if src.suffix.lower() == ".md" else (
            self._converter.convert(str(src)).text_content or ""
        )
        out_file = self._out_dir / (src.stem + ".md")
        out_file.write_text(content, encoding="utf-8")
        return self._analyse(str(out_file), content)

    @mcp
    @skill
    @agent_tool
    def smoke_test(self, repo_path: str, surface: str = "web") -> SmokeTestResult:
        """Test that the application at repo_path is reachable on its primary screens.
        surface: 'web' | 'desktop' | 'api'.
        capture_repo, base_url, and entry_paths are instance fields (blank capture_repo = repo_path;
        blank base_url auto-detects common ports; blank entry_paths defaults to ['/']).
        Appends smoke-test results to tests/stubs/stub-inventory.md under capture_repo.
        Returns SmokeTestResult. passed=True when every probed path returns HTTP 2xx/3xx."""
        self.repo_path = repo_path
        self.surface = surface
        return self._run_smoke()

    def _run_smoke(self) -> SmokeTestResult:
        out_dir = self._stubs_root()
        out_dir.mkdir(parents=True, exist_ok=True)
        self._inventory_path = str(out_dir / "stub-inventory.md")
        screen_results = self._probe_screens()
        passed = bool(screen_results) and all(r.reachable for r in screen_results)
        self._append_smoke_results(screen_results)
        return SmokeTestResult(
            passed=passed,
            screen_results=screen_results,
            inventory_path=self._inventory_path,
        )

    @mcp
    @skill
    @agent_tool
    def scout_app(self, repo_path: str, surface: str = "web") -> ScoutResult:
        """Phase 0 scout: capture 10-20 representative pages from the application.
        surface: 'web' | 'desktop' | 'api'.
        capture_repo, base_url, and entry_paths are instance fields (blank capture_repo = repo_path;
        blank base_url auto-detects; blank entry_paths defaults to ['/']).
        Writes per page: screenshot.png and aria.yaml under
            sandbox/extracted-context/app-extraction/pages/<slug>/.
        Writes extraction-overview.md at
            sandbox/extracted-context/app-extraction/extraction-overview.md.
        Returns ScoutResult with overview_path, pages_dir, and page_captures."""
        self.repo_path = repo_path
        self.surface = surface
        return self._run_scout()

    def _run_scout(self) -> ScoutResult:
        out_root = self._scout_root()
        self._pages_root = out_root / "pages"
        out_root.mkdir(parents=True, exist_ok=True)
        self._pages_root.mkdir(parents=True, exist_ok=True)
        self._overview_path = str(out_root / "extraction-overview.md")
        captures = self._capture_for_surface()
        self._write_extraction_overview(captures)
        return ScoutResult(
            overview_path=self._overview_path,
            pages_dir=str(self._pages_root),
            page_captures=captures,
        )

    @mcp
    @skill
    @agent_tool
    def complete_capture(self, repo_path: str, missing_pages: list[str]) -> CaptureResult:
        """Phase N: capture specific missing or failed pages and update extraction-overview.md.
        missing_pages: list of URL paths or slugs to (re-)capture.
        surface, capture_repo, and base_url are instance fields (surface default 'web';
        blank capture_repo = repo_path; blank base_url auto-detects).
        Writes screenshot.png and aria.yaml for each page under
            sandbox/extracted-context/app-extraction/pages/<slug>/.
        Updates extraction-overview.md with the new page sections.
        Returns CaptureResult with added_captures and updated overview path."""
        self.repo_path = repo_path
        self.entry_paths = missing_pages
        return self._run_complete_capture()

    def _run_complete_capture(self) -> CaptureResult:
        out_root = self._scout_root()
        self._pages_root = out_root / "pages"
        self._pages_root.mkdir(parents=True, exist_ok=True)
        self._overview_path = str(out_root / "extraction-overview.md")
        added = self._capture_for_surface()
        existing_slugs = self._read_existing_slugs()
        total = len(existing_slugs) + len(added)
        self._append_extraction_overview(added)
        return CaptureResult(
            overview_path=self._overview_path,
            added_captures=added,
            total_page_count=total,
        )

    # ── @agent_instructions — AI reads recipe; owns judgment; calls @tools + collaborators ─

    @mcp
    @skill
    @agent_instructions
    def capture_from_live_app(self,
        repo_path: str,
        capture_repo: str = "",
        surface: str = "web",
    ) -> str:
        """Capture context memory from a live application at repo_path.
        repo_path={repo_path}  capture_repo={capture_repo}  surface={surface} (one of web | desktop | api).
        capture_repo is where stubs and scout land (tests/stubs/{system}/, domain/{aggregate}/stubs/{system}/, sandbox/extracted-context).
        Blank capture_repo means the same folder as repo_path.
        Collaborators (compile-time references): ContextIndex.

        Step 1 — Classify External Dependencies (AI judgment, no tool):
        Scan the repo at repo_path for third-party call sites, SDK initialisations,
        and environment variables holding external URLs. For each candidate, classify
        as 'external' (needs a stub) or 'in-scope' (same-repo or peer-repo service — skip).
        Produce a Classification Table: service name, file path, symbol, classification, reason.

        Complex-stub trigger: if 5 or more distinct external services are found, OR any
        dependency requires a domain-shaped stub return (more than 3 fields), STOP and
        produce three pre-pass documents before writing any stubs:
          1. tests/stubs/stub-focus-map.md — stub-focus map (not Stories story-map.md)
          2. tests/stubs/acceptance-criteria.md — stub-focus acceptance criteria
          3. tests/stubs/domain-glossary.md — domain term → minimum fields mapping
        Write those files under capture_repo (or repo_path if capture_repo is blank).
        Only proceed to Step 2 once all three documents are written.

        Step 2 — Write External Stubs (AI judgment, no tool):
        For each dependency classified as 'external', write a canned neighbor stub under capture_repo.
        Global systems (no owning domain): tests/stubs/{system}/.
        Domain-owned neighbors: domain/{aggregate}/stubs/{system}/.
        Never a domain folder inside tests/.
        Write at the outermost boundary — the HTTP client adapter, SDK factory, or module export.
        DO NOT stub OAuth token flows, deep SDK internals, or protocol-layer methods.
        Record every hardcoded value introduced by each stub.
        Write the Stub Inventory to tests/stubs/stub-inventory.md under capture_repo with
        one row per stub: service, boundary point (file + symbol), hardcoded values,
        BDD step phrase references (When / And / Then).

        Step 3 — Smoke Test: set this toolset's capture_repo field to capture_repo, then
        call smoke_test(repo_path=repo_path, surface=surface).
        If smoke_test_result.passed is False, identify which screens failed, trace the
        boundary point from the stub inventory, repair the stub (Step 2), and call
        smoke_test again. Do not proceed to Step 4 until passed is True.

        Step 4 — Scout App Pages: keep capture_repo set, then call
        scout_app(repo_path=repo_path, surface=surface).
        This runs a Phase 0 thin capture (10-20 representative pages or endpoints) under
        capture_repo/sandbox/extracted-context/app-extraction/ and
        returns a ScoutResult with overview_path, pages_dir, and page_slugs.

        Step 5 — Review Capture Coverage (AI judgment):
        Read the extraction-overview.md at scout_result.overview_path.
        For each captured page, read its aria.yaml under scout_result.pages_dir/<slug>/:
        - Does the ARIA represent a real rendered screen for the page's user_intent?
        - Are interactive elements (buttons, inputs, links, headings) present and consistent?
        - Is the content suspiciously sparse — single heading, one button, loading skeleton?
        Emit a verdict per page: PASS | WARN | FAIL.
        FAIL and WARN pages need re-capture; note the reason for each.
        If all pages PASS: call context_index.embed(segments_paths=[scout_result.pages_dir])
        to index the captured content and report capture complete. Stop.
        If any pages FAIL or WARN: proceed to Step 6.

        Step 6 — Complete App Capture (only when Step 5 found FAIL or WARN pages):
        Collect the URLs or slugs of FAIL and WARN pages into missing_pages.
        Keep capture_repo set, then call complete_capture(repo_path=repo_path, missing_pages=missing_pages).
        After capture, call context_index.embed(segments_paths=[capture_result.overview_path])
        to index the updated overview and report all pages captured."""
        self.smoke_test()
        self.scout_app()
        self.complete_capture()
        self.context_index.embed()
        return "Live app captured and indexed."

    @mcp
    @skill
    @agent_instructions
    def capture_from_documents(self,
        folder_path: str,
        indexers: Optional[list[str]] = None,
        first: str = "",
    ) -> str:
        """Capture documents from folder_path, partition through selected context tools, embed into one FAISS index.
        folder_path={folder_path}, indexers={indexers}, first={first}.
        Collaborators (compile-time references): Stories, CleanEngineering, Ddd, Ux, Partition."""
        """Step 1 — call convert(folder_path) to convert every document to markdown.
        Inspect the returned structure_notes.  If any note shows heading_depth=0 and
        word_count > 200, note it for the user — the document may need a semantic re-pass
        before partitioning gives useful results (do not block; continue to Step 2)."""
        self.convert()
        """Step 2 — Choose Indexers:
        If indexers is None or empty, ask the user via AskQuestion (allow_multiple=True):
          Which context tools should index this content?
          Options: stories | clean_engineering | ddd | ux | cdd
        Also ask: which tool runs first? (first)
        No tool fires during this step — just collect the user's selection."""
        """Step 3 — Sequence & Delegate (partition is additive; multi-pass is safe):
        Call ONLY the tools the user selected in Step 2. Start with the tool named by
        `first`; after it completes, read its index output to decide the order for the
        remaining selected tools. Each call writes segments to folder_path/.context/
        (out_root=folder_path) and accumulates views without wiping prior passes.
        'cdd' means call both stories and clean_engineering.
        If the user selected nothing, call partition.partition() only."""
        self.stories.partition()
        self.clean_engineering.partition()
        self.ddd.partition()
        self.ux.partition()
        self.partition.partition()
        """Step 4 — Embed:
        segments_paths = glob(folder_path/.context/**/*-segment.md).
        Pass them to context_index.embed with out_path=folder_path/rag.
        Report the resulting index_path to the user."""
        self.context_index.embed()
        return "Documents captured and indexed."

    def _analyse(self, file_path: str, content: str) -> StructureNote:
        headings = re.findall(r"^(#{1,6})\s", content, re.MULTILINE)
        heading_count = len(headings)
        heading_depth = max((len(h) for h in headings), default=0)
        word_count = len(content.split())
        return StructureNote(
            file=file_path,
            heading_depth=heading_depth,
            heading_count=heading_count,
            word_count=word_count,
        )

    def _write_root(self) -> Path:
        chosen = (self.capture_repo or "").strip() or self.repo_path
        return Path(chosen)

    def _stubs_root(self) -> Path:
        return self._write_root().joinpath(*_STUBS_DIR)

    def _scout_root(self) -> Path:
        return self._write_root().joinpath(*_SCOUT_DIR)

    def _detect_base_url(self) -> str:
        import socket
        for port in _COMMON_PORTS:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                try:
                    s.connect(("localhost", port))
                    return f"http://localhost:{port}"
                except OSError:
                    continue
        return "http://localhost:3000"

    def _probe_screens(self) -> list[ScreenResult]:
        if self.surface not in ("web", "api"):
            return self._desktop_smoke()
        if not self.base_url:
            self.base_url = self._detect_base_url()
        return self._http_smoke()

    def _http_smoke(self) -> list[ScreenResult]:
        import requests as _requests

        results: list[ScreenResult] = []
        for path in self.entry_paths or ["/"]:
            results.append(self._http_smoke_path(_requests, path))
        return results

    def _http_smoke_path(self, requests, path: str) -> ScreenResult:
        url = self.base_url.rstrip("/") + path
        slug = (path.strip("/").replace("/", "-") or "root")
        try:
            resp = requests.get(url, timeout=5, allow_redirects=True)
            status = resp.status_code
            reachable = status < 400
        except Exception:
            _log.exception("Smoke request failed for %s", url)
            status = 0
            reachable = False
        return ScreenResult(slug=slug, url=url, reachable=reachable, status_code=status)

    def _desktop_smoke(self) -> list[ScreenResult]:
        import subprocess
        repo_name = Path(self.repo_path).name
        try:
            out = subprocess.check_output(
                ["tasklist" if re.search(r"[A-Za-z]:\\", self.repo_path) else "ps", "-e"],
                stderr=subprocess.DEVNULL,
            ).decode(errors="replace")
            running = repo_name.lower() in out.lower()
        except Exception:
            _log.exception("Desktop smoke failed for %s", self.repo_path)
            running = False
        return [ScreenResult(slug="desktop-root", url=self.repo_path, reachable=running, status_code=0 if not running else 200)]

    def _append_smoke_results(self, results: list[ScreenResult]) -> None:
        lines = [
            "\n\n## Smoke Test Results\n",
            "| Slug | URL | Reachable | Status |\n",
            "|------|-----|-----------|--------|\n",
        ]
        for r in results:
            lines.append(f"| {r.slug} | {r.url} | {'yes' if r.reachable else 'no'} | {r.status_code} |\n")
        p = Path(self._inventory_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.writelines(lines)

    def _slug_from_path(self) -> str:
        label = self._current_path.strip("/").replace("/", "-") or "home"
        return f"{self._current_index + 1:02d}-{label}"

    def _capture_for_surface(self) -> list[PageCapture]:
        if self.surface not in ("web", "api"):
            return self._desktop_capture()
        if not self.base_url:
            self.base_url = self._detect_base_url()
        return self._web_capture()

    def _web_capture(self) -> list[PageCapture]:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            return self._capture_with_browser(playwright)

    def _capture_with_browser(self, playwright) -> list[PageCapture]:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        captures = self._capture_pages(page)
        browser.close()
        return captures

    def _capture_pages(self, page) -> list[PageCapture]:
        captures: list[PageCapture] = []
        for i, path in enumerate(self.entry_paths or ["/"]):
            self._current_path = path
            self._current_index = i
            capture = self._capture_current_path(page)
            if capture is not None:
                captures.append(capture)
        return captures

    def _capture_current_path(self, page) -> Optional[PageCapture]:
        self._page_url = self.base_url.rstrip("/") + self._current_path
        self._page_slug = self._slug_from_path()
        page_dir = self._pages_root / self._page_slug
        page_dir.mkdir(parents=True, exist_ok=True)
        self._screenshot_path = str(page_dir / "screenshot.png")
        self._aria_path = str(page_dir / "aria.yaml")
        try:
            return self._snapshot_page(page)
        except Exception:
            _log.exception("Failed to capture %s", self._page_url)
            return None

    def _snapshot_page(self, page) -> PageCapture:
        page.goto(self._page_url, timeout=30_000, wait_until="networkidle")
        self._wait_for_root(page)
        page.screenshot(path=self._screenshot_path, full_page=True)
        self._write_aria(page)
        return PageCapture(
            slug=self._page_slug,
            url=self._page_url,
            screenshot_path=self._screenshot_path,
            aria_path=self._aria_path,
        )

    def _wait_for_root(self, page) -> None:
        try:
            page.wait_for_function(
                "() => { const r = document.querySelector('#root'); return !!(r && r.childElementCount > 0); }",
                timeout=10_000,
            )
        except Exception:
            _log.exception("Root content did not appear at %s", self._page_url)
            page.wait_for_timeout(1500)

    def _write_aria(self, page) -> None:
        aria_text = page.aria_snapshot()
        Path(self._aria_path).write_text(
            f"user_intent: visit {self._current_path}\naria_snapshot: |\n"
            + "\n".join(f"  {line}" for line in aria_text.splitlines()),
            encoding="utf-8",
        )

    def _desktop_capture(self) -> list[PageCapture]:
        return []

    def _write_extraction_overview(self, captures: list[PageCapture]) -> None:
        app_name = Path(self.repo_path).name
        lines = [
            "---\n",
            f"app: {app_name}\n",
            f"surface: {self.surface}\n",
            "tool: playwright\n",
            "---\n\n",
            f"# Extraction Overview — {app_name}\n\n",
        ]
        for cap in captures:
            lines += self._overview_lines(cap)
        Path(self._overview_path).write_text("".join(lines), encoding="utf-8")

    def _overview_lines(self, cap: PageCapture) -> list[str]:
        return [
            f"## {cap.slug}\n\n",
            f"- **url:** {cap.url}\n",
            f"- **screenshot:** {cap.screenshot_path}\n",
            f"- **aria:** {cap.aria_path}\n\n",
        ]

    def _read_existing_slugs(self) -> list[str]:
        p = Path(self._overview_path)
        if not p.exists():
            return []
        return re.findall(r"^## (\S+)", p.read_text(encoding="utf-8"), re.MULTILINE)

    def _append_extraction_overview(self, captures: list[PageCapture]) -> None:
        lines: list[str] = []
        for cap in captures:
            lines += [
                f"\n## {cap.slug}\n\n",
                f"- **url:** {cap.url}\n",
                f"- **screenshot:** {cap.screenshot_path}\n",
                f"- **aria:** {cap.aria_path}\n",
            ]
        p = Path(self._overview_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.writelines(lines)
