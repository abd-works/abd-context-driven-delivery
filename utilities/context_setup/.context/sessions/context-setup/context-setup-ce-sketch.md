---
fidelity: [model]
artifact: [modules-model]
format: md
example-of: none
---

# Clean Engineering Sketch — Context Setup (model)

**Sources / context:**
`context_tools/base/base_context_tool.py` (`self.partitioner = Partition()` composition at line 70; `partition()` action lines 219–230 passing `slug`/`scaffold`);
`utilities/partition/partition.py` (`Partition.partition` → `index` → `segment` → `verify_segment_completeness`; `mode` = one_go | pause | index_only);
`context_tools/stories/stories.py`, `context_tools/ddd/ddd.py`, `context_tools/clean_engineering/clean_engineering.py` (concrete context tools, each a `BaseContextTool` with `.partition()`);
`utilities/echo/echo.py`, `utilities/agent_skills/agent_skills.py` (precedent — plain `@toolset`);
`abd-skills/.../abd-context-{to-markdown,semantic-index,chunk,db-embed,db-ask}/SKILL.md` (default indexer + embed/ask capabilities);
`utilities/context_setup/.context/sessions/context-setup/context-setup-sketch.md` (stories);
`utilities/context_setup/.context/cdr/0001-plain-toolset-not-context-domain.md`.

---

## Core design decision — context_setup is an orchestrator, not a re-implementation

The previous sketch invented a parallel tag/chunk/embed pipeline. That was wrong.
Every context tool already partitions source material through its own lens
(`self.partitioner.partition(context, slug=domain_slug, scaffold=scaffold)`).

So `context_setup` does not tag content itself. It **delegates partitioning to the
context tools the user chooses** — each tool's partition output IS the view-tagged
content for that lens (Stories → story view, CleanEngineering → module/arch view,
Ddd → domain view, Ux → ux view). It then embeds all resulting segments into one
retrievable index.

```
// ── Plain @toolset — NOT a context_tools @context domain (CDR 0001) ──────────
@toolset  ← tools.tool                 publishes manifest; dispatch via python -m tools run
@action   ← primitives.actions.action  AI reads recipe + owns judgment; NOT executed as Python
@tool     ← tools.tool                 real executable Python method

No BaseContextTool.   No generate/validate/satisfy lifecycle.   No scripts/ folder.
```

---

## Module layout

```
utilities/context_setup/
  context_setup.py     ← ContextSetup @toolset (orchestrator)
```

`ContextSetup` holds compile-time references to the concrete context tools and to the
default semantic indexer. It composes them — it does not inherit from any of them.

---

## ContextSetup — class sketch

```
ContextSetup                                        // @toolset

  // ── composed collaborators (compile-time references) ─────────────────────────
  //   Each is a BaseContextTool with a .partition(context, mode) action.
  //   ContextSetup calls .partition() on the ones the user selects.

  stories:           Stories             // story view
  clean_engineering: CleanEngineering    // module / architecture view
  ddd:               Ddd                 // domain view
  ux:                Ux                  // ux view
  cdd:               Cdd                 // full CDD view
  default_indexer:   SemanticIndexer     // existing abd-context-semantic-index skill —
                                         //   broad four-view tagging, no domain scaffold


  // ── @actions : AI reads recipe; owns judgment; calls @tools + collaborators ──

  @action
  capture_from_documents(folder_path: str, indexers: list[str] = [], first: str = "")
    @tool convert(folder_path) -> ConversionResult
    //
    // judgment: Choose Indexers — if `indexers` is empty:
    //   AI presents all options via AskQuestion (allow_multiple):
    //     stories | clean_engineering | ddd | ux | cdd | default_indexer
    //   User selects one or more, and names `first`. No tool fires.
    //
    // judgment: Sequence & Delegate —
    //   AI calls selected_indexer.partition(markdown_path, mode="index_only") on `first`;
    //   reads that partition's index/segments; then decides order for the remaining
    //   indexers and calls each one's .partition() in turn.
    //   (default_indexer.partition falls back to broad four-view tagging.)
    //
    @tool embed(segments_paths) -> EmbedResult
    //   builds one FAISS index over the union of every selected indexer's segments

  @action
  ask(question: str, index_path: str)
    // judgment: derive semantic query from question — no tool
    @tool search(query, index_path) -> SearchResult
    // judgment: weight results by view/chunk metadata; compose answer with citations — no tool


  // ── @tools : deterministic Python ─────────────────────────────────────────

  @tool
  convert(folder_path: str) -> ConversionResult
    // converts every .docx / .pdf / .pptx in folder_path to markdown
    // (wraps the abd-context-to-markdown capability)
    // writes markdown to folder_path/markdown/

  @tool
  embed(segments_paths: list[str]) -> EmbedResult
    // reads every *-segment.md produced by the selected indexers
    // embeds each segment; builds one FAISS index over all of them
    // writes index to folder_path/rag/

  @tool
  search(query: str, index_path: str) -> SearchResult
    // embeds query; loads FAISS index; returns top-k nearest segments


  // ── result types ────────────────────────────────────────────────────────────

  ConversionResult
    markdown_files: list[str]
    structure_notes: list[StructureNote]

  StructureNote
    file: str
    heading_depth: int
    heading_count: int
    word_count: int

  EmbedResult
    index_path: str                     // folder_path/rag/
    segment_count: int
    views_covered: list[str]            // which lenses contributed segments

  SearchResult
    chunks: list[RankedChunk]

  RankedChunk
    path: str                           // path to the *-segment.md chunk
    section: str
    view: str                           // story | domain | architecture | ux (from the indexer that produced it)
    score: float
```

---

## Delegation flow (the "intelligent delegation")

```
User: capture_from_documents("./docs", indexers=[], first="")
  │
  ├─ @tool convert("./docs")                 → ./docs/markdown/*.md
  │
  ├─ judgment: Choose Indexers
  │     indexers empty → AskQuestion:
  │       [ ] stories   [ ] clean_engineering   [ ] ddd   [ ] ux   [ ] cdd   [ ] default_indexer
  │     User: {stories, clean_engineering}, first = stories
  │
  ├─ judgment: Sequence & Delegate
  │     self.stories.partition("./docs/markdown", mode="index_only")     ← user's `first`
  │       → reads story-index + story segments
  │     AI reads that output, decides CE goes next
  │     self.clean_engineering.partition("./docs/markdown", mode="index_only")
  │       → adds module/arch columns to the SAME index (Partition is additive)
  │
  └─ @tool embed([story segments, CE segments])   → ./docs/rag/  (one FAISS index)
```

Partition is additive across passes (see `partition.md` Multi-pass rules), so each
delegated tool adds its view to the shared `{subject}-index.md` without wiping prior
passes — exactly the behavior context_setup needs for multi-lens indexing.

---

## Judgment checkpoints — where they live

- Choose Indexers — inside `capture_from_documents`; AI asks via AskQuestion when `indexers` empty
- Sequence & Delegate — inside `capture_from_documents`; AI runs `first`, then orders the rest
- Derive semantic query — inside `ask`, before `search`
- Compose answer — inside `ask`, after `search`

---

## Unresolved

- `?` `SemanticIndexer` (default_indexer) shape — is it a thin Python `@toolset` wrapping the
  existing abd-context-semantic-index skill, or does it expose a `.partition()`-compatible
  method so it drops into the same delegation loop as the context tools? Needs one more pass.
- `?` Session plumbing — `.partition()` is a `BaseContextTool` action needing a workspace session.
  How does ContextSetup construct/pass sessions to each delegated tool so they write segments
  under a shared root? Flagged for the next (model → specification) pass.
