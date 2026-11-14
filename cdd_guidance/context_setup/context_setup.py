"""ContextSetup — converts a folder of documents to markdown and captures a live application into indexed context."""
from __future__ import annotations

import dataclasses
import functools
import re
from pathlib import Path
from typing import Any, Optional

from harness.agent_tools import agent_instructions, agent_toolset
from harness.agent_tools.agent_tools import agent_tool, tools
from harness.agent_tools.tool_call import ToolCall
from harness.installation.files import skill
from harness.guidance_actions import ActionWorksInNoSession
from harness.mcp.mcp_annotations import mcp
from cdd_guidance.context_setup.context_index import ContextIndex
from cdd_guidance.context_setup.live_app_capture import (
    CaptureResult,
    LiveAppCapture,
    ScoutResult,
    SmokeTestResult,
)

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

# ── Toolset ───────────────────────────────────────────────────────────────────

_SUPPORTED = frozenset({".docx", ".doc", ".pdf", ".pptx", ".ppt", ".txt", ".md", ".html", ".htm"})


@functools.cache
def _document_converter() -> Any:
    """The one MarkItDown of the process: making one registers every converter it has, which takes longer than most
    conversions."""
    from markitdown import MarkItDown

    return MarkItDown()


@agent_toolset
class ContextSetup:
    """Convert a folder of documents to markdown, and capture a live application into indexed context. Partition runs
    the documents pipeline: it calls convert, partitions the markdown through the practices, then embeds the segments.

    The cdd server makes one for each call, for the session that call works in, so the folders a call names are read
    from that session's project."""

    def __init__(self, context_index: Optional[ContextIndex] = None, session: Any = None) -> None:
        """A ContextIndex left out is made here, so the toolset the cdd server builds with no arguments can run every
        step of its recipes."""
        self.context_index = context_index if context_index is not None else ContextIndex()
        self._session = session

    def for_call(self, call: ToolCall) -> ContextSetup:
        """A ContextSetup made for call, working in the session call works in, holding a ContextIndex made for it."""
        return self.in_session(call.session)

    def in_session(self, session: Any) -> ContextSetup:
        """A ContextSetup working in session, as an action that holds one, such as Partition, makes it for its own
        session, holding a ContextIndex made for that session with this one's embedding provider."""
        return type(self)(self.context_index.in_session(session), session)

    @property
    def session(self) -> Any:
        """The session this toolset works in, whose project the folders a call names are read from. Raises
        ActionWorksInNoSession for a toolset made for no session."""
        if self._session is None:
            raise ActionWorksInNoSession(type(self).__name__)
        return self._session

    def _capture(self, repo_path: str, capture_repo: str, surface: str, base_url: str, entry_paths: Optional[list[str]]) -> LiveAppCapture:
        """The application this call captures, with its folders read from the session's project."""
        repository = str(self.session.path_named(repo_path))
        written_to = str(self.session.path_named(capture_repo)) if capture_repo else ""
        return LiveAppCapture(repository, written_to, surface, base_url, entry_paths)

    # ── @tools — deterministic Python ────────────────────────────────────────

    @mcp
    @skill
    @agent_tool
    def convert(self, folder_path: str) -> ConversionResult:
        """Convert every supported document in folder_path, a folder from the project's root or absolute, to a Markdown file.
        Supported formats: .docx, .doc, .pdf, .pptx, .ppt, .txt, .md, .html, .htm.
        Writes each markdown document to folder_path/markdown/<stem>.md.
        Returns a ConversionResult containing markdown_files (absolute paths) and
        structure_notes (one StructureNote per file with heading_depth, heading_count,
        word_count)."""
        root = self.session.path_named(folder_path)
        out_dir = root / "markdown"
        out_dir.mkdir(parents=True, exist_ok=True)
        converter = _document_converter()
        notes = [self._convert_source(converter, src, out_dir) for src in sorted(root.iterdir()) if self._is_convertible(src)]
        return ConversionResult(markdown_files=[note.file for note in notes], structure_notes=notes)

    def _is_convertible(self, src: Path) -> bool:
        return src.is_file() and src.suffix.lower() in _SUPPORTED

    def _convert_source(self, converter, src: Path, out_dir: Path) -> StructureNote:
        content = src.read_text(encoding="utf-8") if src.suffix.lower() == ".md" else (
            converter.convert(str(src)).text_content or ""
        )
        out_file = out_dir / (src.stem + ".md")
        out_file.write_text(content, encoding="utf-8")
        return self._analyse(str(out_file), content)

    @mcp
    @skill
    @agent_tool
    def smoke_test(
        self,
        repo_path: str,
        surface: str = "web",
        capture_repo: str = "",
        base_url: str = "",
        entry_paths: Optional[list[str]] = None,
    ) -> SmokeTestResult:
        """Test that the application at repo_path is reachable on its primary screens. repo_path and capture_repo are
        folders from the project's root, or absolute.
        surface: 'web' | 'desktop' | 'api'. Blank capture_repo means repo_path; blank base_url auto-detects common
        local ports; blank entry_paths probes ['/'].
        Appends smoke-test results to tests/stubs/stub-inventory.md under capture_repo.
        Returns SmokeTestResult. passed=True when every probed path returns HTTP 2xx/3xx."""
        return self._capture(repo_path, capture_repo, surface, base_url, entry_paths).smoke_test()

    @mcp
    @skill
    @agent_tool
    def scout_app(
        self,
        repo_path: str,
        surface: str = "web",
        capture_repo: str = "",
        base_url: str = "",
        entry_paths: Optional[list[str]] = None,
    ) -> ScoutResult:
        """Phase 0 scout: capture 10-20 representative pages from the application.
        surface: 'web' | 'desktop' | 'api'. Blank capture_repo means repo_path; blank base_url auto-detects; blank
        entry_paths captures ['/'].
        Writes per page: screenshot.png and aria.yaml under
            sandbox/extracted-context/app-extraction/pages/<slug>/.
        Writes extraction-overview.md at
            sandbox/extracted-context/app-extraction/extraction-overview.md.
        Returns ScoutResult with overview_path, pages_dir, page_captures, and failed_pages (each page the browser
        could not load, with its reason)."""
        return self._capture(repo_path, capture_repo, surface, base_url, entry_paths).scout()

    @mcp
    @skill
    @agent_tool
    def complete_capture(
        self,
        repo_path: str,
        missing_pages: list[str],
        surface: str = "web",
        capture_repo: str = "",
        base_url: str = "",
    ) -> CaptureResult:
        """Phase N: capture specific missing or failed pages and update extraction-overview.md.
        missing_pages: list of URL paths to (re-)capture. Blank capture_repo means repo_path; blank base_url
        auto-detects.
        Writes screenshot.png and aria.yaml for each page under
            sandbox/extracted-context/app-extraction/pages/<slug>/.
        Updates extraction-overview.md with the new page sections.
        Returns CaptureResult with added_captures, failed_pages, and the updated overview path."""
        return self._capture(repo_path, capture_repo, surface, base_url, missing_pages).complete()

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
        surface is one of web | desktop | api.
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

        Step 3 — Smoke Test: call smoke_test(repo_path=repo_path, surface=surface, capture_repo=capture_repo).
        If smoke_test_result.passed is False, identify which screens failed, trace the
        boundary point from the stub inventory, repair the stub (Step 2), and call
        smoke_test again. Do not proceed to Step 4 until passed is True.

        Step 4 — Scout App Pages: call scout_app(repo_path=repo_path, surface=surface, capture_repo=capture_repo).
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
        FAIL and WARN pages need re-capture; note the reason for each. Every entry in scout_result.failed_pages
        is a FAIL: the browser could not load that page, and its reason says why.
        If all pages PASS: call context_index.embed(segments_paths=[scout_result.overview_path], out_path=<the folder
        holding scout_result.overview_path>/rag) to index the extraction overview, which holds a section per captured
        page, beside it, and report capture complete with the index_path embed returns. Stop.
        If any pages FAIL or WARN: proceed to Step 6.

        Step 6 — Complete App Capture (only when Step 5 found FAIL or WARN pages):
        Collect the URLs or slugs of FAIL and WARN pages into missing_pages.
        Call complete_capture(repo_path=repo_path, missing_pages=missing_pages, surface=surface,
        capture_repo=capture_repo).
        After capture, call context_index.embed(segments_paths=[capture_result.overview_path], out_path=<the folder
        holding capture_result.overview_path>/rag) to index the updated overview in the same place, and report all pages
        captured with the index_path embed returns."""
        "The application is at repo_path={{repo_path}}."
        tools(self.smoke_test)
        tools(self.scout_app)
        tools(self.complete_capture)
        tools(self.context_index.embed())
        return "Live app captured and indexed."

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
