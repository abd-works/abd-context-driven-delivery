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

    # ── @action — AI reads recipe; owns judgment; calls @tools + collaborators ─

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
