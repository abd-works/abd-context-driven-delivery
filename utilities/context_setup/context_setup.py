# @toolset-manifest python -m tools manifest context_setup.context_setup:ContextSetup
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""ContextSetup — converts a folder of documents to markdown and delegates partitioning to context tools."""
from __future__ import annotations

import dataclasses
import re
from pathlib import Path
from typing import Optional

from primitives.actions.action import action
from tools.tool import tool, toolset

from context_tools.clean_engineering.clean_engineering import CleanEngineering
from context_tools.ddd.ddd import Ddd
from context_tools.stories.stories import Stories
from context_tools.ux.ux import Ux
from context_setup.semantic_indexer import SemanticIndexer
from context_setup.context_index import ContextIndex


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


@toolset
class ContextSetup:
    """Convert a folder of documents to markdown and delegate partitioning to selected context tools."""

    def __init__(self) -> None:
        # Composed context tools — mode="tool" on each instance so the expander
        # treats their @action calls as deferred tool steps (not inlined recipes).
        self.stories: Stories = Stories()
        self.stories.mode = "tool"
        self.clean_engineering: CleanEngineering = CleanEngineering()
        self.clean_engineering.mode = "tool"
        self.ddd: Ddd = Ddd()
        self.ddd.mode = "tool"
        self.ux: Ux = Ux()
        self.ux.mode = "tool"
        self.default_indexer: SemanticIndexer = SemanticIndexer()
        self.default_indexer.mode = "tool"
        # ContextIndex.embed is a @tool — deferred automatically (no mode needed).
        self.context_index: ContextIndex = ContextIndex()

    # ── @tools — deterministic Python ────────────────────────────────────────

    @tool
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

        converter = MarkItDown()
        markdown_files: list[str] = []
        structure_notes: list[StructureNote] = []

        for src in sorted(root.iterdir()):
            if src.is_dir() or src.suffix.lower() not in _SUPPORTED:
                continue

            if src.suffix.lower() == ".md":
                content = src.read_text(encoding="utf-8")
            else:
                result = converter.convert(str(src))
                content = result.text_content or ""

            out_file = out_dir / (src.stem + ".md")
            out_file.write_text(content, encoding="utf-8")
            markdown_files.append(str(out_file))
            structure_notes.append(_analyse(str(out_file), content))

        return ConversionResult(
            markdown_files=markdown_files,
            structure_notes=structure_notes,
        )

    @tool
    def smoke_test(
        self,
        repo_path: str,
        surface: str = "web",
        base_url: str = "",
        entry_paths: Optional[list[str]] = None,
    ) -> SmokeTestResult:
        """Test that the application at repo_path is reachable on its primary screens.
        surface: 'web' | 'desktop' | 'api'.
        base_url: e.g. 'http://localhost:3000' — auto-detected from common ports if blank.
        entry_paths: URL paths to probe, e.g. ['/', '/login', '/dashboard'].
            Defaults to ['/'] when blank.
        Appends smoke-test results to docs/stubs/stub-inventory.md under repo_path.
        Returns SmokeTestResult. passed=True when every probed path returns HTTP 2xx/3xx."""
        import requests as _requests

        root = Path(repo_path)
        out_dir = root / "docs" / "stubs"
        out_dir.mkdir(parents=True, exist_ok=True)
        inventory_path = str(out_dir / "stub-inventory.md")
        paths = entry_paths or ["/"]

        if surface in ("web", "api"):
            resolved_base = base_url or _detect_base_url()
            screen_results = _http_smoke(resolved_base, paths)
        else:
            # desktop surface — check that the process name is running
            screen_results = _desktop_smoke(repo_path)

        passed = bool(screen_results) and all(r.reachable for r in screen_results)
        _append_smoke_results(inventory_path, screen_results)
        return SmokeTestResult(
            passed=passed,
            screen_results=screen_results,
            inventory_path=inventory_path,
        )

    @tool
    def scout_app(
        self,
        repo_path: str,
        surface: str = "web",
        base_url: str = "",
        entry_points: Optional[list[str]] = None,
    ) -> ScoutResult:
        """Phase 0 scout: capture 10-20 representative pages from the application.
        surface: 'web' | 'desktop' | 'api'.
        base_url: e.g. 'http://localhost:3000' — auto-detected if blank.
        entry_points: URL paths to visit, e.g. ['/', '/login', '/dashboard'].
            Defaults to ['/'] when blank.
        Writes per page: screenshot.png and aria.yaml under
            docs/extracted-context/app-extraction/pages/<slug>/.
        Writes extraction-overview.md at
            docs/extracted-context/app-extraction/extraction-overview.md.
        Returns ScoutResult with overview_path, pages_dir, and page_captures."""
        root = Path(repo_path)
        out_root = root / "docs" / "extracted-context" / "app-extraction"
        pages_root = out_root / "pages"
        out_root.mkdir(parents=True, exist_ok=True)
        pages_root.mkdir(parents=True, exist_ok=True)
        overview_path = str(out_root / "extraction-overview.md")

        points = entry_points or ["/"]

        if surface in ("web", "api"):
            resolved_base = base_url or _detect_base_url()
            captures = _web_capture(resolved_base, points, pages_root)
        else:
            captures = _desktop_capture(repo_path, pages_root)

        _write_extraction_overview(overview_path, repo_path, surface, captures)
        return ScoutResult(
            overview_path=overview_path,
            pages_dir=str(pages_root),
            page_captures=captures,
        )

    @tool
    def complete_capture(
        self,
        repo_path: str,
        missing_pages: list[str],
        surface: str = "web",
        base_url: str = "",
    ) -> CaptureResult:
        """Phase N: capture specific missing or failed pages and update extraction-overview.md.
        missing_pages: list of URL paths or slugs to (re-)capture.
        surface: 'web' | 'desktop' | 'api'.
        base_url: e.g. 'http://localhost:3000' — auto-detected if blank.
        Writes screenshot.png and aria.yaml for each page under
            docs/extracted-context/app-extraction/pages/<slug>/.
        Updates extraction-overview.md with the new page sections.
        Returns CaptureResult with added_captures and updated overview path."""
        root = Path(repo_path)
        out_root = root / "docs" / "extracted-context" / "app-extraction"
        pages_root = out_root / "pages"
        pages_root.mkdir(parents=True, exist_ok=True)
        overview_path = str(out_root / "extraction-overview.md")

        if surface in ("web", "api"):
            resolved_base = base_url or _detect_base_url()
            added = _web_capture(resolved_base, missing_pages, pages_root)
        else:
            added = _desktop_capture(repo_path, pages_root)

        existing_slugs = _read_existing_slugs(overview_path)
        total = len(existing_slugs) + len(added)
        _append_extraction_overview(overview_path, added)
        return CaptureResult(
            overview_path=overview_path,
            added_captures=added,
            total_page_count=total,
        )

    # ── @action — AI reads recipe; owns judgment; calls @tools + collaborators ─

    @action
    def capture_from_live_app(
        self,
        repo_path: str,
        surface: str = "web",
    ) -> str:
        """Capture context memory from a live application at repo_path.
        repo_path={repo_path}  surface={surface} (one of web | desktop | api).
        Collaborators (compile-time references): ContextIndex.

        Step 1 — Classify External Dependencies (AI judgment, no tool):
        Scan the repo at repo_path for third-party call sites, SDK initialisations,
        and environment variables holding external URLs. For each candidate, classify
        as 'external' (needs a stub) or 'in-scope' (same-repo or peer-repo service — skip).
        Produce a Classification Table: service name, file path, symbol, classification, reason.

        Complex-stub trigger: if 5 or more distinct external services are found, OR any
        dependency requires a domain-shaped stub return (more than 3 fields), STOP and
        produce three pre-pass documents before writing any stubs:
          1. docs/stubs/story-map.md — stub-focus story map
          2. docs/stubs/acceptance-criteria.md — stub-focus acceptance criteria
          3. docs/stubs/domain-glossary.md — domain term → minimum fields mapping
        Only proceed to Step 2 once all three documents are written.

        Step 2 — Write External Stubs (AI judgment, no tool):
        For each dependency classified as 'external', write a stub at its outermost
        boundary — the HTTP client adapter, SDK factory, or module export. DO NOT stub
        OAuth token flows, deep SDK internals, or protocol-layer methods.
        Record every hardcoded value introduced by each stub.
        Write the Stub Inventory to docs/stubs/stub-inventory.md under repo_path with
        one row per stub: service, boundary point (file + symbol), hardcoded values,
        BDD step phrase references (When / And / Then).

        Step 3 — Smoke Test: call smoke_test(repo_path=repo_path, surface=surface).
        If smoke_test_result.passed is False, identify which screens failed, trace the
        boundary point from the stub inventory, repair the stub (Step 2), and call
        smoke_test again. Do not proceed to Step 4 until passed is True.

        Step 4 — Scout App Pages: call scout_app(repo_path=repo_path, surface=surface).
        This runs a Phase 0 thin capture (10-20 representative pages or endpoints) and
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
        Call complete_capture(repo_path=repo_path, missing_pages=missing_pages,
        surface=surface).
        After capture, call context_index.embed(segments_paths=[capture_result.overview_path])
        to index the updated overview and report all pages captured."""
        self.smoke_test()
        self.scout_app()
        self.complete_capture()
        self.context_index.embed()
        return "Live app captured and indexed."

    @action
    def capture_from_documents(
        self,
        folder_path: str,
        indexers: Optional[list[str]] = None,
        first: str = "",
    ) -> str:
        """Capture documents from folder_path, partition through selected context tools, embed into one FAISS index.
        folder_path={folder_path}, indexers={indexers}, first={first}.
        Collaborators (compile-time references): Stories, CleanEngineering, Ddd, Ux, SemanticIndexer."""
        """Step 1 — call convert(folder_path) to convert every document to markdown.
        Inspect the returned structure_notes.  If any note shows heading_depth=0 and
        word_count > 200, note it for the user — the document may need a semantic re-pass
        before partitioning gives useful results (do not block; continue to Step 2)."""
        self.convert()
        """Step 2 — Choose Indexers:
        If indexers is None or empty, ask the user via AskQuestion (allow_multiple=True):
          Which context tools should index this content?
          Options: stories | clean_engineering | ddd | ux | cdd | default_indexer
        Also ask: which tool runs first? (first)
        No tool fires during this step — just collect the user's selection."""
        """Step 3 — Sequence & Delegate (partition is additive; multi-pass is safe):
        Call ONLY the tools the user selected in Step 2. Start with the tool named by
        `first`; after it completes, read its index output to decide the order for the
        remaining selected tools. Each call writes segments to folder_path/.context/
        (out_root=folder_path) and accumulates views without wiping prior passes.
        'cdd' means call both stories and clean_engineering.
        If the user selected nothing, call self.default_indexer.partition() only."""
        self.stories.partition()
        self.clean_engineering.partition()
        self.ddd.partition()
        self.ux.partition()
        self.default_indexer.partition()
        """Step 4 — Embed:
        segments_paths = glob(folder_path/.context/**/*-segment.md).
        Pass them to context_index.embed with out_path=folder_path/rag.
        Report the resulting index_path to the user."""
        self.context_index.embed()
        return "Documents captured and indexed."


# ── Helpers ───────────────────────────────────────────────────────────────────

def _analyse(file_path: str, content: str) -> StructureNote:
    """Extract heading and word metrics from markdown content."""
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


# ── Live-app capture helpers ──────────────────────────────────────────────────

_COMMON_PORTS = [3000, 8000, 8080, 5000, 4000, 5173, 4173]


def _detect_base_url() -> str:
    """Return the first localhost port that accepts a TCP connection."""
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


def _http_smoke(base_url: str, paths: list[str]) -> list[ScreenResult]:
    """HTTP GET each path and return reachability results."""
    import requests as _requests

    results: list[ScreenResult] = []
    for path in paths:
        url = base_url.rstrip("/") + path
        slug = (path.strip("/").replace("/", "-") or "root")
        try:
            resp = _requests.get(url, timeout=5, allow_redirects=True)
            status = resp.status_code
            reachable = status < 400
        except Exception:
            status = 0
            reachable = False
        results.append(ScreenResult(slug=slug, url=url, reachable=reachable, status_code=status))
    return results


def _desktop_smoke(repo_path: str) -> list[ScreenResult]:
    """Check that a desktop process matching the repo name is running."""
    import subprocess
    repo_name = Path(repo_path).name
    try:
        out = subprocess.check_output(
            ["tasklist" if re.search(r"[A-Za-z]:\\", repo_path) else "ps", "-e"],
            stderr=subprocess.DEVNULL,
        ).decode(errors="replace")
        running = repo_name.lower() in out.lower()
    except Exception:
        running = False
    return [ScreenResult(slug="desktop-root", url=repo_path, reachable=running, status_code=0 if not running else 200)]


def _append_smoke_results(inventory_path: str, results: list[ScreenResult]) -> None:
    """Append a smoke-test results table to the stub inventory file."""
    lines = [
        "\n\n## Smoke Test Results\n",
        "| Slug | URL | Reachable | Status |\n",
        "|------|-----|-----------|--------|\n",
    ]
    for r in results:
        lines.append(f"| {r.slug} | {r.url} | {'yes' if r.reachable else 'no'} | {r.status_code} |\n")
    p = Path(inventory_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.writelines(lines)


def _slug_from_path(path: str, index: int) -> str:
    """Convert a URL path to a numbered slug like '01-login'."""
    label = path.strip("/").replace("/", "-") or "home"
    return f"{index + 1:02d}-{label}"


def _web_capture(base_url: str, paths: list[str], pages_root: Path) -> list[PageCapture]:
    """Use Playwright to capture screenshot + aria.yaml for each path."""
    from playwright.sync_api import sync_playwright

    captures: list[PageCapture] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for i, path in enumerate(paths):
            url = base_url.rstrip("/") + path
            slug = _slug_from_path(path, i)
            page_dir = pages_root / slug
            page_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = str(page_dir / "screenshot.png")
            aria_path = str(page_dir / "aria.yaml")
            try:
                page.goto(url, timeout=10_000, wait_until="load")
                page.screenshot(path=screenshot_path, full_page=True)
                # page.aria_snapshot() returns an ARIA-roles text representation (Playwright ≥1.44)
                aria_text = page.aria_snapshot()
                Path(aria_path).write_text(
                    f"user_intent: visit {path}\naria_snapshot: |\n"
                    + "\n".join(f"  {line}" for line in aria_text.splitlines()),
                    encoding="utf-8",
                )
                captures.append(PageCapture(
                    slug=slug,
                    url=url,
                    screenshot_path=screenshot_path,
                    aria_path=aria_path,
                ))
            except Exception:
                pass  # unreachable pages are left out; AI Chat flags them in review
        browser.close()
    return captures


def _desktop_capture(repo_path: str, pages_root: Path) -> list[PageCapture]:
    """Placeholder for desktop UIA capture via pywinauto (not yet wired)."""
    return []


def _write_extraction_overview(
    overview_path: str,
    repo_path: str,
    surface: str,
    captures: list[PageCapture],
) -> None:
    """Write a fresh extraction-overview.md from the given page captures."""
    app_name = Path(repo_path).name
    lines = [
        "---\n",
        f"app: {app_name}\n",
        f"surface: {surface}\n",
        "tool: playwright\n",
        "---\n\n",
        f"# Extraction Overview — {app_name}\n\n",
    ]
    for cap in captures:
        lines += [
            f"## {cap.slug}\n\n",
            f"- **url:** {cap.url}\n",
            f"- **screenshot:** {cap.screenshot_path}\n",
            f"- **aria:** {cap.aria_path}\n\n",
        ]
    Path(overview_path).write_text("".join(lines), encoding="utf-8")


def _read_existing_slugs(overview_path: str) -> list[str]:
    """Return the list of ## slugs already in the extraction-overview."""
    p = Path(overview_path)
    if not p.exists():
        return []
    return re.findall(r"^## (\S+)", p.read_text(encoding="utf-8"), re.MULTILINE)


def _append_extraction_overview(overview_path: str, captures: list[PageCapture]) -> None:
    """Append new page sections to an existing extraction-overview.md."""
    lines: list[str] = []
    for cap in captures:
        lines += [
            f"\n## {cap.slug}\n\n",
            f"- **url:** {cap.url}\n",
            f"- **screenshot:** {cap.screenshot_path}\n",
            f"- **aria:** {cap.aria_path}\n",
        ]
    p = Path(overview_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.writelines(lines)
