# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for utilities/context_setup/context_setup.py — ContextSetup toolset.

Covers Increment 1 stories:
  Tool --> Convert To Markdown           (convert tool)
  AI Chat --> Review Document Structure  (action expansion — convert is listed)
  User --> Capture From Documents        (action expansion — step order)
"""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_empty, be_false, be_true, contain, equal, expect, have_len
from mamba import after, before, context, description, it

from context_setup.context_setup import ContextSetup, ConversionResult, StructureNote
from primitives.actions.action import _ActionExpander


# ── helpers ───────────────────────────────────────────────────────────────────

def _expanded_capture_from_documents() -> str:
    cs = ContextSetup()
    func = getattr(type(cs), "capture_from_documents")
    body = _ActionExpander.instance().parse_body(func, cs)
    return "\n".join(body.prose_parts)


def _write(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


# ── spec ─────────────────────────────────────────────────────────────────────

with description("a ContextSetup"):
    with context("that is created"):
        with it("should be a ContextSetup instance"):
            expect(ContextSetup()).to(be_a(ContextSetup))

    # ── Tool: Convert To Markdown ─────────────────────────────────────────────

    with context("whose convert tool is given a folder with a plain markdown file"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            _write(self._root, "notes.md", "# Title\n\nSome body text with several words.\n")
            self._result = ContextSetup().convert(str(self._root))

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
            _write(
                self._root,
                "deep.md",
                "# H1\n\n## H2\n\n### H3\n\nsome content words here\n",
            )
            self._result = ContextSetup().convert(str(self._root))

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
            _write(self._root, "flat.md", "Just plain prose with no headings at all.\n")
            self._result = ContextSetup().convert(str(self._root))

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
            _write(self._root, "ignored.csv", "col1,col2\nval1,val2\n")
            _write(self._root, "kept.md", "# Kept\n\nContent.\n")
            self._result = ContextSetup().convert(str(self._root))

        with after.each:
            self._tmp.cleanup()

        with it("should skip the unsupported file"):
            expect(self._result.markdown_files).to(have_len(1))

        with it("should only include the supported file"):
            expect(Path(self._result.markdown_files[0]).stem).to(equal("kept"))

    with context("whose convert tool is given an empty folder"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._result = ContextSetup().convert(self._tmp.name)

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
            _write(self._root, "alpha.md", "# Alpha\n\nAlpha content.\n")
            _write(self._root, "beta.md", "# Beta\n\nBeta content.\n")
            self._result = ContextSetup().convert(str(self._root))

        with after.each:
            self._tmp.cleanup()

        with it("should produce one entry per file"):
            expect(self._result.markdown_files).to(have_len(2))

        with it("should produce one structure note per file"):
            expect(self._result.structure_notes).to(have_len(2))

    # ── Action: capture_from_documents (expansion tests) ─────────────────────

    with context("whose capture_from_documents action is expanded"):
        with it("should list convert as a tool to call"):
            prose = _expanded_capture_from_documents()
            expect("convert" in prose).to(be_true)

        with it("should instruct the AI to ask the user to choose indexers"):
            prose = _expanded_capture_from_documents()
            expect("AskQuestion" in prose or "indexer" in prose.lower()).to(be_true)

        with it("should mention partition delegation to context tools"):
            prose = _expanded_capture_from_documents()
            expect("partition" in prose).to(be_true)

        with it("should mention embed as the final step"):
            prose = _expanded_capture_from_documents()
            expect("embed" in prose).to(be_true)

    with context("whose capture_from_documents action tool_steps are resolved"):
        with it("should include convert"):
            from primitives.actions.action import _ActionExpander
            cs = ContextSetup()
            func = getattr(type(cs), "capture_from_documents")
            body = _ActionExpander.instance().parse_body(func, cs)
            expect("convert" in body.tool_steps).to(be_true)

        with it("should include partition for each context tool (5 total)"):
            from primitives.actions.action import _ActionExpander
            cs = ContextSetup()
            func = getattr(type(cs), "capture_from_documents")
            body = _ActionExpander.instance().parse_body(func, cs)
            expect(body.tool_steps.count("partition")).to(equal(5))

        with it("should include embed from ContextIndex"):
            from primitives.actions.action import _ActionExpander
            cs = ContextSetup()
            func = getattr(type(cs), "capture_from_documents")
            body = _ActionExpander.instance().parse_body(func, cs)
            expect("embed" in body.tool_steps).to(be_true)
