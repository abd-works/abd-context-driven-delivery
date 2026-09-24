"""BDD spec for tools/context_setup/context_index.py — ContextIndex toolset.

Covers Increment 1 stories:
  Tool --> Embed Chunks     (embed tool)
  Tool --> Search Memory    (search tool)
  AI Chat --> Answer With Citations  (ask action expansion)

All tests use a FakeEmbeddingProvider so no OpenAI API key is required.
"""
import sys
import tempfile
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

from context_setup.context_index import (
    ContextIndex,
    EmbedResult,
    EmbeddingProvider,
    RankedChunk,
    SearchResult,
)
from harness.agent_tools.agent_tools import AgentInstructions


# ── Fake embedding provider ───────────────────────────────────────────────────

_DIM = 16  # small dimension for fast tests


class FakeEmbeddingProvider:
    """Returns deterministic unit vectors based on the text hash — no API needed."""

    def embed_texts(self, texts: list) -> list:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list:
        return self._vec(text)

    def _vec(self, text: str) -> list:
        import hashlib
        import math as _math

        digest = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        floats = []
        for i in range(_DIM):
            floats.append(float((digest >> (i * 4)) & 0xF) / 15.0)
        # normalise so dot-product distance is meaningful
        norm = _math.sqrt(sum(x * x for x in floats)) or 1.0
        return [x / norm for x in floats]


class SpecFixture:
    def __init__(self) -> None:
        self._root = Path()
        self._name = ""
        self._content = ""

    def _make_index(self) -> ContextIndex:
        return ContextIndex(embedding_provider=FakeEmbeddingProvider())

    def _write_segment(self) -> Path:
        path = self._root / self._name
        path.write_text(self._content, encoding="utf-8")
        return path

    def _expanded_ask(self) -> str:
        ci = self._make_index()
        func = getattr(type(ci), "ask")
        body = AgentInstructions.for_callable(func, ci)
        return "\n".join(body.prompt)


fixture = SpecFixture()


# ── spec ─────────────────────────────────────────────────────────────────────

with description("a ContextIndex"):
    with context("that is created with a fake embedding provider"):
        with it("should be a ContextIndex instance"):
            expect(fixture._make_index()).to(be_a(ContextIndex))

    # ── Tool: Embed Chunks ────────────────────────────────────────────────────

    with context("whose embed tool is called with one segment file"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            fixture._root = self._root
            fixture._name = "intro-segment.md"
            fixture._content = "---\nview: story\n---\n# Introduction\nThis is the intro segment.\n"
            seg = fixture._write_segment()
            out = str(self._root / "rag")
            self._result = fixture._make_index().embed([str(seg)], out_path=out)

        with after.each:
            self._tmp.cleanup()

        with it("should return an EmbedResult"):
            expect(self._result).to(be_a(EmbedResult))

        with it("should report segment_count as 1"):
            expect(self._result.segment_count).to(equal(1))

        with it("should write index.faiss to the out_path"):
            expect(Path(self._result.index_path, "index.faiss").exists()).to(be_true)

        with it("should write meta.json to the out_path"):
            expect(Path(self._result.index_path, "meta.json").exists()).to(be_true)

        with it("should include 'story' in views_covered"):
            expect("story" in self._result.views_covered).to(be_true)

    with context("whose embed tool is called with segments from multiple views"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            fixture._root = self._root
            fixture._name = "story-seg.md"
            fixture._content = "---\nview: story\n---\nUser story content.\n"
            fixture._write_segment()
            fixture._name = "domain-seg.md"
            fixture._content = "---\nview: domain\n---\nDomain logic content.\n"
            fixture._write_segment()
            segs = [str(self._root / "story-seg.md"), str(self._root / "domain-seg.md")]
            out = str(self._root / "rag")
            self._result = fixture._make_index().embed(segs, out_path=out)

        with after.each:
            self._tmp.cleanup()

        with it("should report segment_count as 2"):
            expect(self._result.segment_count).to(equal(2))

        with it("should list both views in views_covered"):
            expect("story" in self._result.views_covered).to(be_true)
            expect("domain" in self._result.views_covered).to(be_true)

    with context("whose embed tool is called with an empty segments list"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            out = str(Path(self._tmp.name) / "rag")
            self._result = fixture._make_index().embed([], out_path=out)

        with after.each:
            self._tmp.cleanup()

        with it("should return segment_count of 0"):
            expect(self._result.segment_count).to(equal(0))

        with it("should return empty views_covered"):
            expect(self._result.views_covered).to(be_empty)

    with context("whose embed tool is called with a segment lacking front matter"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            fixture._root = self._root
            fixture._name = "plain.md"
            fixture._content = "Plain content with no front matter.\n"
            seg = fixture._write_segment()
            out = str(self._root / "rag")
            self._result = fixture._make_index().embed([str(seg)], out_path=out)

        with after.each:
            self._tmp.cleanup()

        with it("should fall back to view 'general'"):
            expect("general" in self._result.views_covered).to(be_true)

    # ── Tool: Search Memory ───────────────────────────────────────────────────

    with context("whose search tool is called on a populated index"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            fixture._root = self._root
            ci = fixture._make_index()
            segs = []
            for name, text in [
                ("alpha-segment.md", "---\nview: story\n---\n# Alpha\nAlpha content about users.\n"),
                ("beta-segment.md",  "---\nview: domain\n---\n# Beta\nBeta content about rules.\n"),
                ("gamma-segment.md", "---\nview: ux\n---\n# Gamma\nGamma content about screens.\n"),
            ]:
                fixture._name = name
                fixture._content = text
                segs.append(str(fixture._write_segment()))
            out = str(self._root / "rag")
            ci.embed(segs, out_path=out)
            self._ci = ci
            self._out = out

        with after.each:
            self._tmp.cleanup()

        with it("should return a SearchResult"):
            result = self._ci.search("users and screens", self._out)
            expect(result).to(be_a(SearchResult))

        with it("should return at most top_k chunks"):
            result = self._ci.search("anything", self._out, top_k=2)
            expect(len(result.chunks) <= 2).to(be_true)

        with it("should return RankedChunk instances"):
            result = self._ci.search("content", self._out)
            expect(all(isinstance(c, RankedChunk) for c in result.chunks)).to(be_true)

        with it("should include a non-negative score for each chunk"):
            result = self._ci.search("content", self._out)
            expect(all(c.score >= 0 for c in result.chunks)).to(be_true)

        with it("should include the path for each chunk"):
            result = self._ci.search("content", self._out)
            expect(all(c.path for c in result.chunks)).to(be_true)

        with it("should include the view tag for each chunk"):
            result = self._ci.search("content", self._out)
            known_views = {"story", "domain", "ux"}
            expect(all(c.view in known_views for c in result.chunks)).to(be_true)

    with context("whose search is called with top_k larger than the index"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            fixture._root = self._root
            fixture._name = "only.md"
            fixture._content = "Just one segment.\n"
            ci = fixture._make_index()
            seg = fixture._write_segment()
            out = str(self._root / "rag")
            ci.embed([str(seg)], out_path=out)
            self._ci = ci
            self._out = out

        with after.each:
            self._tmp.cleanup()

        with it("should return only as many chunks as exist (not crash)"):
            result = self._ci.search("anything", self._out, top_k=100)
            expect(len(result.chunks)).to(equal(1))

    # ── AgentTool: ask (expansion tests) ────────────────────────────────────────

    with context("whose ask action is expanded"):
        with it("should list search as a tool to call"):
            prose = fixture._expanded_ask()
            expect("search" in prose).to(be_true)

        with it("should instruct the AI to derive a semantic query"):
            prose = fixture._expanded_ask()
            expect("query" in prose.lower() or "semantic" in prose.lower()).to(be_true)

        with it("should instruct the AI to cite source paths"):
            prose = fixture._expanded_ask()
            expect("cit" in prose.lower()).to(be_true)

        with it("should mention weighting by view"):
            prose = fixture._expanded_ask()
            expect("view" in prose.lower()).to(be_true)
