"""ContextIndex — embed segments into a FAISS index and answer questions with citations."""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any, Optional, Protocol

from harness.agent_tools import agent_instructions, agent_toolset, tools
from harness.agent_tools.agent_tools import agent_tool
from harness.agent_tools.tool_call import ToolCall
from harness.installation.files import skill
from harness.markdown.front_matter import FrontMatter
from harness.mcp.mcp_server import mcp

# ── Index entries and results ────────────────────────────────────────────────

@dataclasses.dataclass
class IndexedSegment:
    """One segment file a SegmentIndex holds: where it is, its section label (the file's stem), and the view its front
    matter names (story | domain | architecture | ux | general)."""

    path: str
    section: str
    view: str

    @classmethod
    def of_file(cls, path: Path, text: str) -> IndexedSegment:
        """The entry for the segment file at path whose text is text; a file whose front matter names no view is
        ``general``."""
        return cls(path=str(path), section=path.stem, view=FrontMatter(text).fields.get("view") or "general")

    def ranked(self, score: float) -> RankedChunk:
        """This segment as a search answers it, with its relevance score."""
        return RankedChunk(path=self.path, section=self.section, view=self.view, score=score)

@dataclasses.dataclass
class RankedChunk(IndexedSegment):
    """One retrieved segment with its relevance score in [0, 1]; higher is more relevant."""

    score: float

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

# ── The index on disk ────────────────────────────────────────────────────────

class SegmentIndex:
    """The searchable index of segment files in one folder: ``index.faiss`` holds one vector per segment and
    ``meta.json`` each segment's entry, in the same order. It is the one reader and writer of those two files, so the
    entry a vector answers is always the one saved beside it."""

    _VECTORS = "index.faiss"
    _ENTRIES = "meta.json"

    def __init__(self, folder: Path, vectors: Any, segments: list[IndexedSegment]) -> None:
        self.folder = folder
        self._vectors = vectors
        self.segments = segments

    @classmethod
    def built(cls, folder: Path, segments: list[IndexedSegment], embeddings: list[list[float]]) -> SegmentIndex:
        """The index of segments, one embedding each, saved into folder."""
        import faiss
        import numpy as np

        matrix = np.array(embeddings, dtype=np.float32)
        vectors = faiss.IndexFlatL2(matrix.shape[1])
        vectors.add(matrix)
        made = cls(folder, vectors, segments)
        made._save()
        return made

    @classmethod
    def opened(cls, folder: Path) -> SegmentIndex:
        """The index embed saved into folder."""
        import faiss

        entries = json.loads((folder / cls._ENTRIES).read_text(encoding="utf-8"))
        return cls(folder, faiss.read_index(str(folder / cls._VECTORS)), [IndexedSegment(**entry) for entry in entries])

    @property
    def views(self) -> list[str]:
        """The distinct views its segments cover, sorted."""
        return sorted({segment.view for segment in self.segments})

    def ranked(self, query: list[float], top_k: int) -> list[RankedChunk]:
        """The segments nearest query, at most top_k, most relevant first."""
        import numpy as np

        distances, positions = self._vectors.search(np.array([query], dtype=np.float32), min(top_k, self._vectors.ntotal))
        return [
            self.segments[int(position)].ranked(float(1.0 / (1.0 + distance)))
            for distance, position in zip(distances[0], positions[0])
            if position >= 0
        ]

    def _save(self) -> None:
        import faiss

        self.folder.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._vectors, str(self.folder / self._VECTORS))
        entries = [dataclasses.asdict(segment) for segment in self.segments]
        (self.folder / self._ENTRIES).write_text(json.dumps(entries, indent=2), encoding="utf-8")

class SegmentNotFound(FileNotFoundError):
    """Raised when embed is named a segment file that is not there; embedding it as empty text would index nothing
    under its name and leave the search silently wrong."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"no segment file at {path.as_posix()}; name it from the project's root, or absolute")
        self.path = path

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

@agent_toolset
class ContextIndex:
    """Embed partitioned segments into a FAISS index and answer questions with source citations.

    The cdd server makes one for each call, for the session that call works in, so every path a call names is read from
    that session's project rather than the server's own folder."""

    def __init__(self, embedding_provider: Optional[EmbeddingProvider] = None, session: Any = None) -> None:
        self._provider = embedding_provider  # None → lazy-init OpenAIEmbeddingProvider on first use
        self._session = session

    def for_call(self, call: ToolCall) -> ContextIndex:
        """A ContextIndex made for call: it reads the paths call names from the project of the session call works in,
        and embeds with this index's provider."""
        return type(self)(self._provider, call.session)

    def _path_named(self, named: str) -> Path:
        """named as a path in this index's session's project; read as given when it works in no session, as an index
        run in process does."""
        return self._session.path_named(named) if self._session is not None else Path(named)

    def _segment_text(self, file: Path) -> str:
        if not file.is_file():
            raise SegmentNotFound(file)
        return file.read_text(encoding="utf-8")

    def _get_provider(self) -> EmbeddingProvider:
        if self._provider is None:
            self._provider = OpenAIEmbeddingProvider()
        return self._provider

    # ── @tools — deterministic Python ────────────────────────────────────────

    @mcp
    @skill
    @agent_tool
    def embed(self, segments_paths: list[str], out_path: str) -> EmbedResult:
        """Read every segment markdown file listed in segments_paths, embed using the embedding provider,
        and write a FAISS index to out_path/index.faiss with a metadata sidecar at out_path/meta.json.
        segments_paths — the *-segment.md files partition wrote, from the project's root or absolute. A path that is not there is refused.
        out_path — directory where index.faiss and meta.json are written (created if absent), from the project's root or absolute.
        Returns EmbedResult with index_path, segment_count, and views_covered."""
        out_dir = self._path_named(out_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        files = [self._path_named(segment_path) for segment_path in segments_paths]
        texts = [self._segment_text(file) for file in files]
        if not texts:
            return EmbedResult(index_path=str(out_dir), segment_count=0, views_covered=[])
        segments = [IndexedSegment.of_file(file, text) for file, text in zip(files, texts)]
        index = SegmentIndex.built(out_dir, segments, self._get_provider().embed_texts(texts))
        return EmbedResult(index_path=str(out_dir), segment_count=len(index.segments), views_covered=index.views)

    @mcp
    @skill
    @agent_tool
    def search(self, query: str, index_path: str, top_k: int = 5) -> SearchResult:
        """Embed query and search the FAISS index at index_path.
        query — natural-language question or search phrase.
        index_path — directory containing index.faiss and meta.json written by embed(), from the project's root or absolute.
        top_k — maximum number of chunks to return (default 5).
        Returns SearchResult with chunks ordered from most to least relevant."""
        index = SegmentIndex.opened(self._path_named(index_path))
        return SearchResult(chunks=index.ranked(self._get_provider().embed_query(query), top_k))

    # ── @agent_instructions — AI reads recipe; owns judgment ──────────────────────────────

    @mcp
    @skill
    @agent_instructions
    def ask(self, question: str, index_path: str) -> str:
        """Answer question using the FAISS index at index_path, citing sources."""
        "Answer {{question}} from the index at {{index_path}}."
        """Step 1 — Derive a semantic query:
        Read question and formulate a concise search phrase that captures the core intent.
        No tool fires during this step."""
        """Step 2 — call search(query, index_path) to retrieve the top ranked chunks."""
        tools(self.search)
        """Step 3 — Compose answer:
        Read each chunk's view field to weight results — story chunks for user-facing behaviour,
        domain chunks for logic, architecture chunks for structure, ux chunks for screens.
        Write an answer in plain prose, citing source.path and section for every claim made.
        Do not include information that does not appear in the retrieved chunks."""
        return "Answer composed with citations."
