# @toolset-manifest python -m tools manifest context_setup.context_index:ContextIndex
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""ContextIndex — embed segments into a FAISS index and answer questions with citations."""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Protocol, Sequence

from primitives.actions.action import agent_instructions, agentic_toolset
from harness.harness_tool import prompt
from tools.tool import agent_tool

if TYPE_CHECKING:
    pass


# ── Result types ─────────────────────────────────────────────────────────────


@dataclasses.dataclass
class RankedChunk:
    """One retrieved segment with its relevance score."""

    path: str      # absolute path to the *-segment.md file
    section: str   # stem of the segment file (used as section label)
    view: str      # story | domain | architecture | ux | general
    score: float   # similarity score in [0, 1]; higher is more relevant


@dataclasses.dataclass
class EmbedResult:
    """Summary of a completed embed() call."""

    index_path: str           # directory containing index.faiss + meta.json
    segment_count: int
    views_covered: list[str]  # sorted list of distinct view tags found in segments


@dataclasses.dataclass
class SearchResult:
    """Ordered list of ranked chunks from a search() call."""

    chunks: list[RankedChunk]


# ── Embedding provider protocol (injectable for tests) ───────────────────────


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


class OpenAIEmbeddingProvider:
    """Default provider — calls OpenAI text-embedding-3-small."""

    _MODEL = "text-embedding-3-small"

    def __init__(self) -> None:
        from openai import OpenAI

        self._client = OpenAI()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model=self._MODEL, input=texts)
        return [e.embedding for e in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


# ── Toolset ───────────────────────────────────────────────────────────────────


@agentic_toolset
class ContextIndex:
    """Embed partitioned segments into a FAISS index and answer questions with source citations."""

    def __init__(self, embedding_provider: Optional[EmbeddingProvider] = None) -> None:
        self._provider = embedding_provider  # None → lazy-init OpenAIEmbeddingProvider on first use

    def _get_provider(self) -> EmbeddingProvider:
        if self._provider is None:
            self._provider = OpenAIEmbeddingProvider()
        return self._provider

    # ── @tools — deterministic Python ────────────────────────────────────────

    @prompt(name="embed")
    @agent_tool
    def embed(self, segments_paths: list[str], out_path: str) -> EmbedResult:
        """Read every segment markdown file listed in segments_paths, embed using the embedding provider,
        and write a FAISS index to out_path/index.faiss with a metadata sidecar at out_path/meta.json.
        segments_paths — absolute paths to *-segment.md files produced by context tool partitions.
        out_path — directory where index.faiss and meta.json are written (created if absent).
        Returns EmbedResult with index_path, segment_count, and views_covered."""
        import numpy as np
        import faiss

        out_dir = Path(out_path)
        out_dir.mkdir(parents=True, exist_ok=True)

        texts: list[str] = []
        metas: list[dict] = []
        views_covered: set[str] = set()

        for seg_path in segments_paths:
            p = Path(seg_path)
            content = p.read_text(encoding="utf-8") if p.exists() else ""
            view = _extract_view(content)
            views_covered.add(view)
            texts.append(content)
            metas.append({"path": str(p), "view": view, "section": p.stem})

        if not texts:
            return EmbedResult(index_path=str(out_dir), segment_count=0, views_covered=[])

        vectors = np.array(self._get_provider().embed_texts(texts), dtype=np.float32)
        dim = vectors.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(vectors)

        faiss.write_index(index, str(out_dir / "index.faiss"))
        (out_dir / "meta.json").write_text(json.dumps(metas, indent=2), encoding="utf-8")

        return EmbedResult(
            index_path=str(out_dir),
            segment_count=len(texts),
            views_covered=sorted(views_covered),
        )

    @prompt(name="search")
    @agent_tool
    def search(self, query: str, index_path: str, top_k: int = 5) -> SearchResult:
        """Embed query and search the FAISS index at index_path.
        query — natural-language question or search phrase.
        index_path — directory containing index.faiss and meta.json written by embed().
        top_k — maximum number of chunks to return (default 5).
        Returns SearchResult with chunks ordered from most to least relevant."""
        import numpy as np
        import faiss

        idx_dir = Path(index_path)
        index = faiss.read_index(str(idx_dir / "index.faiss"))
        metas: list[dict] = json.loads((idx_dir / "meta.json").read_text(encoding="utf-8"))

        query_vec = np.array([self._get_provider().embed_query(query)], dtype=np.float32)
        k = min(top_k, index.ntotal)
        distances, indices = index.search(query_vec, k)

        chunks: list[RankedChunk] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0:
                continue
            meta = metas[int(idx)]
            score = float(1.0 / (1.0 + dist))
            chunks.append(
                RankedChunk(
                    path=meta["path"],
                    section=meta.get("section", ""),
                    view=meta.get("view", "general"),
                    score=score,
                )
            )
        return SearchResult(chunks=chunks)

    # ── @agent_instructions — AI reads recipe; owns judgment ──────────────────────────────

    @prompt(name="ask")
    @agent_instructions
    def ask(self, question: str, index_path: str) -> str:
        """Answer question using the FAISS index at index_path, citing sources.
        question={question}, index_path={index_path}."""
        """Step 1 — Derive a semantic query:
        Read question and formulate a concise search phrase that captures the core intent.
        No tool fires during this step."""
        """Step 2 — call search(query, index_path) to retrieve the top ranked chunks."""
        self.search()
        """Step 3 — Compose answer:
        Read each chunk's view field to weight results — story chunks for user-facing behaviour,
        domain chunks for logic, architecture chunks for structure, ux chunks for screens.
        Write an answer in plain prose, citing source.path and section for every claim made.
        Do not include information that does not appear in the retrieved chunks."""
        return "Answer composed with citations."


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_view(content: str) -> str:
    """Read the 'view:' field from YAML front matter; fall back to 'general'."""
    if not content.startswith("---"):
        return "general"
    try:
        end = content.index("---", 3)
        for line in content[3:end].splitlines():
            if line.startswith("view:"):
                return line.split(":", 1)[1].strip()
    except ValueError:
        pass
    return "general"
