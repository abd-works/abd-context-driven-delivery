# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for utilities/context_setup/context_index.py — ContextIndex toolset.

Covers Increment 1 stories:
  Tool --> Embed Chunks     (embed tool)
  Tool --> Search Memory    (search tool)
  AI Chat --> Answer With Citations  (ask action expansion)

All tests use a FakeEmbeddingProvider so no OpenAI API key is required.
"""
import math
import sys
import tempfile
from pathlib import Path
from typing import List

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
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
from primitives.actions.action import _ActionExpander


# ── Fake embedding provider ───────────────────────────────────────────────────

_DIM = 16  # small dimension for fast tests


class FakeEmbeddingProvider:
    """Returns deterministic unit vectors based on the text hash — no API needed."""

    def embed_texts(self, texts: list) -> list:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list:
        return self._vec(text)

    @staticmethod
    def _vec(text: str) -> list:
        import hashlib
        import math as _math

        digest = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        floats = []
        for i in range(_DIM):
            floats.append(float((digest >> (i * 4)) & 0xF) / 15.0)
        # normalise so dot-product distance is meaningful
        norm = _math.sqrt(sum(x * x for x in floats)) or 1.0
        return [x / norm for x in floats]


def _make_index() -> ContextIndex:
    return ContextIndex(embedding_provider=FakeEmbeddingProvider())


# ── helpers ───────────────────────────────────────────────────────────────────

def _write_segment(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


def _expanded_ask() -> str:
    ci = _make_index()
    func = getattr(type(ci), "ask")
    body = _ActionExpander.instance().parse_body(func, ci)
    return "\n".join(body.prose_parts)


# ── spec ─────────────────────────────────────────────────────────────────────

with description("a ContextIndex"):
    with context("that is created with a fake embedding provider"):
        with it("should be a ContextIndex instance"):
            expect(_make_index()).to(be_a(ContextIndex))

    # ── Tool: Embed Chunks ────────────────────────────────────────────────────

    with context("whose embed tool is called with one segment file"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            seg = _write_segment(
                self._root,
                "intro-segment.md",
                "---\nview: story\n---\n# Introduction\nThis is the intro segment.\n",
            )
            out = str(self._root / "rag")
            self._result = _make_index().embed([str(seg)], out_path=out)

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
            _write_segment(
                self._root,
                "story-seg.md",
                "---\nview: story\n---\nUser story content.\n",
            )
            _write_segment(
                self._root,
                "domain-seg.md",
                "---\nview: domain\n---\nDomain logic content.\n",
            )
            segs = [str(self._root / "story-seg.md"), str(self._root / "domain-seg.md")]
            out = str(self._root / "rag")
            self._result = _make_index().embed(segs, out_path=out)

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
            self._result = _make_index().embed([], out_path=out)

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
            seg = _write_segment(self._root, "plain.md", "Plain content with no front matter.\n")
            out = str(self._root / "rag")
            self._result = _make_index().embed([str(seg)], out_path=out)

        with after.each:
            self._tmp.cleanup()

        with it("should fall back to view 'general'"):
            expect("general" in self._result.views_covered).to(be_true)

    # ── Tool: Search Memory ───────────────────────────────────────────────────

    with context("whose search tool is called on a populated index"):
        with before.each:
            self._tmp = tempfile.TemporaryDirectory()
            self._root = Path(self._tmp.name)
            ci = _make_index()
            # Build an index with three segments
            segs = []
            for i, (name, text) in enumerate([
                ("alpha-segment.md", "---\nview: story\n---\n# Alpha\nAlpha content about users.\n"),
                ("beta-segment.md",  "---\nview: domain\n---\n# Beta\nBeta content about rules.\n"),
                ("gamma-segment.md", "---\nview: ux\n---\n# Gamma\nGamma content about screens.\n"),
            ]):
                p = _write_segment(self._root, name, text)
                segs.append(str(p))
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
            ci = _make_index()
            seg = _write_segment(self._root, "only.md", "Just one segment.\n")
            out = str(self._root / "rag")
            ci.embed([str(seg)], out_path=out)
            self._ci = ci
            self._out = out

        with after.each:
            self._tmp.cleanup()

        with it("should return only as many chunks as exist (not crash)"):
            result = self._ci.search("anything", self._out, top_k=100)
            expect(len(result.chunks)).to(equal(1))

    # ── Action: ask (expansion tests) ────────────────────────────────────────

    with context("whose ask action is expanded"):
        with it("should list search as a tool to call"):
            prose = _expanded_ask()
            expect("search" in prose).to(be_true)

        with it("should instruct the AI to derive a semantic query"):
            prose = _expanded_ask()
            expect("query" in prose.lower() or "semantic" in prose.lower()).to(be_true)

        with it("should instruct the AI to cite source paths"):
            prose = _expanded_ask()
            expect("cit" in prose.lower()).to(be_true)

        with it("should mention weighting by view"):
            prose = _expanded_ask()
            expect("view" in prose.lower()).to(be_true)
