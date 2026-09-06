---
generating-skill: abd-architecture-specification
type: architecture-context
fidelity: specification
---

# Story Map Diagram Sync — Architecture Specification

> **Status:** Draft — Specification fidelity
> **Date:** 2026-06-30
> **Domain spec:** story-ops-domain-specification.md)
> **Domain code:** [diagram-sync-domain.ts](/practices/story-driven-delivery/docs/diagram-sync-domain.ts)

---

## Where to Start — What Does This Feature Touch?

Answer each question about the feature or story you are working on. Each "yes"
points to a context file with the details you need. Read only those files —
you don't need the rest of this document.

| Question | Read this |
| --- | --- |
| Does it add or change the `translateFrom` algorithm, four-slot contract, or `StoryNode` abstract spec? | [Multi-Format Story Rendering](#multi-format-story-rendering) — this file |
| Does it add or change a document format (Markdown parsing, JSON serialization)? | [formats/document/](formats/document/architecture-context.md) |
| Does it add or change how story nodes are rendered to a diagramming tool? | [formats/diagram/](formats/diagram/architecture-context.md) |
| Does it change where elements are positioned — Y offsets, row heights, column widths? | [formats/diagram/](formats/diagram/architecture-context.md) |
| Does it change how diagram changes are detected and reported when reading a diagram back? | [formats/diagram/](formats/diagram/architecture-context.md) |
| Does it add a new diagramming backend (beyond DrawIO and Miro)? | [formats/diagram/](formats/diagram/architecture-context.md) |
| Does it change how story-graph.json is scaffolded into a TypeScript test folder structure? | [formats/code/](formats/code/architecture-context.md) |
| Does it change how existing TypeScript files are preserved during regeneration? | [formats/code/](formats/code/architecture-context.md) |
| Does it add a new code generation backend (beyond TypeScript)? | [formats/code/](formats/code/architecture-context.md) |
| Does it touch core story node types (StoryNode, Epic, SubEpic, Story, AC)? | [core/stories/](core/stories/architecture-context.md) |
| Does it change the CLI entry points or add a new command? | [cli/](cli/architecture-context.md) |

---

## Overview

This system takes a canonical story graph (`story-graph.json`) and renders it across
multiple output formats — diagramming tools (DrawIO, Miro), TypeScript test folder
structures, and source documents (Markdown, JSON) — and reads changed diagrams back
to produce a reversible change report. The rendering protocol (`translateFrom`) is
defined once on `StoryNode` and extended per backend through three pluggable layers.

The architecture has three concerns: a universal rendering contract shared by every
format, a positioning and diffing layer added only by diagram backends, and an
AST-oriented generation layer added only by code backends.

> **Sources:** story-ops-domain-specification.md)

---

## Mechanisms

**Multi-Format Story Rendering** — `translateFrom` is a fixed four-step template method on `StoryNode`; subclasses extend `updateSelf`, `childCollections`, and one `createChildXxx` factory per child type; every backend in the system implements this contract. [Multi-Format Story Rendering](#multi-format-story-rendering) — this file

**Document Rendering** (`formats/document/`) — reference implementation of the base contract; Markdown and JSON backends with no positioning or AST dependencies. [formats/document/](formats/document/architecture-context.md)

**Diagram Rendering** (`formats/diagram/`) — extends the base contract with a positioning layer (`RowPositions`, declarative rules) and structural sync diffing; DrawIO and Miro are the concrete backends. [formats/diagram/](formats/diagram/architecture-context.md)

**Code Rendering** (`formats/code/`) — extends the base contract with AST-oriented generation via a held `LanguageAst`; includes fixture-extraction to preserve hand-written exports during regeneration. [formats/code/](formats/code/architecture-context.md)

---

## Multi-Format Story Rendering

> **This contract governs every backend in the system — document, diagram, and code.**
> Every format backend implements it. Every extension layer builds on top of it.
> Nothing bypasses it.

### Why this shape

**The problem.** Every backend does the same tree operation — walk the source, update matching children, create missing ones, remove extras — but each writes to a different medium: markdown text, diagram cells, source files. If each backend implements the walk itself, you get N copies of reconciliation logic that drift, and every new backend re-derives matching, snapshotting, and reporting from scratch.

**The inversion — three layers, each seeing only what it needs.**

*Algorithm.* `translateFrom` is defined once on `StoryNode` and is **never overridden**. The tree walk, matching, snapshotting, and report generation all live in the base. Every backend, every node type, every extension routes through this same algorithm — there is exactly one place where "how to reconcile a tree" is decided, so reconciliation cannot drift because there is nowhere else for it to live.

*Structure — template method per node type.* Each concrete node type (`Epic`, `SubEpic`, `Story`, `AcceptanceCriteria`) knows what child collections it holds and what its own properties are, but nothing about orchestration. It contributes `childCollections` (which lists to reconcile), `updateSelf` (which properties to copy), and `createChildXxx` (how to construct a child of the right type). This layer is entirely **agnostic of format** — a domain `Epic` does not know whether it is being rendered to Markdown, DrawIO, or TypeScript. It only knows what an Epic is.

*Serialization — the format knows only itself.* The `{fmt}StoryNode` mixin and its `{fmt}Element` contribute nothing to orchestration and nothing to node-shape knowledge. They know only how to write themselves to their medium and how to read themselves back. A DrawIO element knows about mxCells. It does not know that a Story has children, that an Epic has SubEpics, or that reconciliation is happening — those decisions are made in the layers above.

Adding a new node type touches only the middle layer (a new concrete `StoryNode` subclass with its own children and properties). Adding a new backend touches only the third layer (a new mixin + element). The algorithm never changes. That is why the pattern scales additively.

**Document backends are the reference implementation** because they exercise the contract minimally — a heading, a paragraph, an update report. Diagrams add positioning and layout as a middle abstraction layer (`DiagramStoryNode` above the concrete DrawIO / Miro nodes); code backends add AST manipulation the same way. The pattern doesn't change — the middle layer is where format families extend it.

**One more inversion — a uniform callable surface at the seam.** The three layers above tell you *how* a backend is built internally. The seam a caller sees is even flatter: every `{fmt}StoryMap` exposes the same three methods (`parse`, `render`, `sync`) with the same signatures, regardless of family. Middle-layer wrappers (`DiagramStoryMap` for positioning math, `CodeStoryMap` base for AST scaffolding) exist inside the backend but never leak through the seam. That uniformity is what lets the CLI be a two-line router: look up the backend by name, call the method. Without it, coordination logic leaks into every caller, and each caller re-derives which backends need `Backend(x).render()` versus `Backend().render(x)` versus `Backend().render(x, previous)`. The seam is specified explicitly in *The Uniform Callable Surface* below.

### `translateFrom` — The Fixed Four-Step Algorithm

`translateFrom(source: StoryNode): UpdateReport` is defined once on `StoryNode` and
**never overridden**. It is the only entry point for rendering any node into any format.

```
translateFrom(source: StoryNode): UpdateReport
  1. snapshot = NodeSnapshot(self)            ← capture full recursive before-state
  2. self.updateSelf(source)                  ← copy properties; write to element
  3. pairs = self.childCollections(source)    ← declare which child lists to reconcile
  4. for pair in pairs:
       reconcileCollection(pair, report)      ← match, create, remove children
  return UpdateReport(changes, snapshot)
```

`reconcileCollection` matches self-children to source-children by sequential order and
name. Unmatched source children → `createChildXxx(source)` → appended to self.
Unmatched self-children → removed and recorded in the report.

### The Four-Slot Backend Contract

Every backend registers itself through exactly four collaborating classes:

| Slot | Class | Responsibility |
| --- | --- | --- |
| **node** | `{fmt}StoryNode` mixin + concrete subclasses | Owns `updateSelf`, `childCollections`, one `createChildXxx` per child type. Holds the element by composition. |
| **element** | `{fmt}Element` | The serializable unit written by the backend (XML cell, dict, heading string, source file). Knows only its own format. |
| **map** | `{fmt}StoryMap` | Orchestrates a full render (out) and parse (back in) of a complete `StoryMap`. |
| **synchronizer** | `{fmt}Synchronizer` | Reads an existing artifact, reconstructs a `{fmt}StoryNode` tree, calls `translateFrom` on the canonical tree with the parsed tree as source, returns the `UpdateReport`. |

### The Uniform Callable Surface

The four-slot contract is not just a shape — it is also a **callable surface**. Every backend's `{fmt}StoryMap` exposes exactly these three public methods, with these signatures, regardless of whether its external representation is text, XML, or a file tree:

```
class {fmt}StoryMap:
    def parse(external: External) -> StoryMap
    def render(canonical: StoryMap, previous: Optional[External] = None) -> External
    def sync(external: External, canonical: StoryMap) -> UpdateReport
```

Where `External` is the backend's chosen serialization type:

| Backend family | `External` type |
| --- | --- |
| Document (`json`, `markdown`) | `str` |
| Diagram (`drawio`, `miro`) | `str` (XML) |
| Code (`typescript`, `python`, `java`) | `Dict[str, str]` (file-path → content) |

The `External` type varies by domain; **the signature shapes do not**. This is what lets the CLI dispatch to any backend with a two-line lookup instead of per-backend branching.

**Locked disciplines:**

- **No stateful constructors.** `{fmt}StoryMap()` takes no arguments beyond optional configuration that is truly per-instance (e.g., `tests_root` for code backends). It never accepts a canonical `StoryMap` or an external artifact — those go through `render` / `parse` / `sync`.
- **No wrapper return types on the public seam.** `parse` returns the canonical `StoryMap`. Internal wrappers (`DiagramStoryMap` for positioning, `CodeStoryMap` base for AST scaffolding) are constructed inside `render`/`parse` and never leak out.
- **`previous` is accepted and (usually) ignored.** Only backends that need it — currently only the code family, for hand-written preservation — read it. Every other backend accepts the parameter and does nothing with it, so the caller does not need to know which backends care.
- **No public methods beyond `parse`, `render`, `sync`.** Convenience methods (`append_epic`, `remove_epic`, etc.) belong on `StoryMap`, not on the backend. If a spec needs them for fixture setup, it builds the fixture directly on `StoryMap` and passes it in.

### Abstract Class Specification

```
## StoryNode  << abstract >>
+ translateFrom(source: StoryNode): UpdateReport   ← FINAL — never overridden
# abstract — every {fmt}StoryNode mixin must implement all of these:
+ updateSelf(source: StoryNode): void
+ childCollections(source: StoryNode): List[ChildCollectionPair]
+ createChildSubEpic(source: SubEpic): SubEpic
+ createChildStory(source: Story): Story
+ createChildAC(source: AC): AC
- reconcileCollection(pair: ChildCollectionPair, report: UpdateReport): void

## {fmt}StoryNode  << mixin — override these three >>
+ updateSelf(source: StoryNode): void
    self.name = source.name
    self.sequential_order = source.sequential_order
    self.element.write(self)            ← must call element.write — not optional
+ childCollections(source: StoryNode): List[ChildCollectionPair]
    return pairs matching self's child types
+ createChild{Type}(source: {Type}): {Type}
    return {fmt}{Type}(source)          ← must return the concrete backend type

## {fmt}Element  << value object >>
+ write(node: StoryNode): void          ← called from updateSelf
+ serialize(): str | dict | bytes | payload

## {fmt}StoryMap  << orchestrator — uniform callable surface >>
+ parse(external: External): StoryMap
+ render(canonical: StoryMap, previous: Optional[External] = None): External
+ sync(external: External, canonical: StoryMap): UpdateReport
    parsed = self.parse(external)
    return canonical.translateFrom(parsed)

## {fmt}Synchronizer  << optional path/IO adapter >>
+ sync(path: Path, canonical: StoryMap): UpdateReport
    external = read(path)
    report = {fmt}StoryMap().sync(external, canonical)
    write(path, {fmt}StoryMap().render(canonical, previous=external))
    return report
```

### Rules — Must Apply to Every Backend

- **`translateFrom` is never overridden** — backends extend `updateSelf` and `childCollections` only.
- **`updateSelf` must call `self.element.write(self)`** — writing to `self` alone does not persist to the output format.
- **`createChildXxx` must return the concrete backend type** — returning a base `StoryNode` breaks `updateSelf` in child nodes.
- **`updateSelf` reads source only via the `StoryNode` interface** — never cast to a concrete backend type.
- **All four slots must be implemented** — a backend missing any slot cannot complete the sync round-trip.
- **`{fmt}StoryMap` exposes exactly `parse`, `render`, `sync`** — signatures per the Uniform Callable Surface. No stateful constructor arguments. No wrapper return types. No convenience methods (`append_epic`, `remove_epic`, etc.) — those belong on the canonical `StoryMap` the caller passes in.

---

### Package Context

Every folder with significant logic has an `architecture-context.md` alongside its code.

**Mechanisms**

- **Multi-Format Story Rendering** — `translateFrom`, four-slot pattern, abstract `StoryNode` spec — defined in this file [Multi-Format Story Rendering](#multi-format-story-rendering)
- **Document Rendering** — Markdown and JSON backends; reference implementation of the base contract [formats/document/](formats/document/architecture-context.md)
- **Diagram Rendering** — positioning, layout, sync diffing; DrawIO and Miro backends [formats/diagram/](formats/diagram/architecture-context.md)
- **Code Rendering** — AST generation, fixture preservation; TypeScript backend [formats/code/](formats/code/architecture-context.md)

**Core Domain**

- **Core Stories** — `StoryNode`, `Epic`, `SubEpic`, `Story`, `AcceptanceCriteria`, `UpdateReport`, `StoryMap` [core/stories/](core/stories/architecture-context.md)

**CLI**

- **CLI** — unified entry point: `parse`, `sync-drawio`, `sync-miro`, `generate-ts` commands [cli/](cli/architecture-context.md)

### Source Layout

```
story-graph-ops/
+-- scripts/                          <- legacy implementation
+-- src/
    +-- architecture-context.md       <- this file                    [architecture context]
+-- core/
|   +-- stories/                      <- pure domain node hierarchy   [Core Stories]
|       +-- story_node.py             <- StoryNode base
|       +-- nodes.py                  <- Epic, SubEpic, Story, AC
|       +-- update_report.py          <- UpdateReport, NodeSnapshot, ChildCollectionPair
|       +-- story_map.py              <- StoryMap
|       +-- architecture-context.md
+-- formats/
|   +-- document/                     <- document backends            [Document Rendering]
|   |   +-- architecture-context.md
|   |   +-- markdown/
|   |   |   +-- markdown_story_node.py
|   |   |   +-- markdown_element.py
|   |   |   +-- markdown_story_map.py
|   |   |   +-- markdown_synchronizer.py
|   |   +-- json/
|   |       +-- json_story_node.py
|   |       +-- json_element.py
|   |       +-- json_story_map.py     <- story-graph.json I/O
|   |       +-- json_synchronizer.py
|   +-- diagram/                      <- diagram backends             [Diagram Rendering]
|   |   +-- diagram_story_node.py
|   |   +-- row_positions.py
|   |   +-- layout.py
|   |   +-- architecture-context.md
|   |   +-- drawio/
|   |   |   +-- drawio_story_node.py
|   |   |   +-- drawio_element.py
|   |   |   +-- drawio_story_map.py
|   |   |   +-- drawio_synchronizer.py
|   |   +-- miro/
|   |       +-- miro_story_node.py
|   |       +-- miro_element.py
|   |       +-- miro_story_map.py
|   |       +-- miro_synchronizer.py
|   +-- code/                         <- code backends                [Code Rendering]
|       +-- code_story_node.py
|       +-- language_ast.py
|       +-- architecture-context.md
|       +-- typescript/
|           +-- typescript_story_node.py
|           +-- typescript_element.py
|           +-- typescript_story_map.py
|           +-- typescript_synchronizer.py
+-- cli/
    +-- story_graph_cli.py            <- unified CLI                  [CLI]
    +-- architecture-context.md
```

### Instantiating the Domain

> **The three-layer inheritance chain is the core pattern.** Each format adds exactly one layer on top; no format reaches into another format's layer.

- **DrawIO backend** — `DrawIOEpic(DiagramEpic, DrawIOStoryNode)` — inherits positioning from `DiagramEpic`; XML serialization from `DrawIOStoryNode`; holds `DrawIOElement` by composition.
- **Miro backend** — `MiroEpic(DiagramEpic, MiroStoryNode)` — same pattern; holds `MiroElement` by composition.
- **TypeScript backend** — `TypeScriptSubEpic(SubEpic, TypeScriptStoryNode)` — holds `TypeScriptAst`; `generateTypeScriptFile()` emits `*-stories.ts`.
- **New diagram backend** — create `XxxStoryNode` mixin + concrete node classes; no changes to `translateFrom`, `reconcileCollection`, or any existing class.
- **New code backend** — create `XxxAst` implementing `LanguageAst` + `XxxStoryNode` mixin; no changes to any existing class.

---

## Testing Architecture

Tests follow a **unit-by-layer** pattern: `core/` and format mixin classes are tested
with plain pytest; backend node tests stub `DrawIOElement` / `MiroElement` at the
composition boundary; end-to-end sync tests load real `story-graph.json` fixtures and
assert on rendered XML / Miro payload structure. See `tests/architecture-context.md`
for file layout, layer-to-tech mapping, and epic/sub-epic test map.

---

## References

- **Domain specification:** story-ops-domain-specification.md)
- **Domain TypeScript (1-1 from spec):** [diagram-sync-domain.ts](/practices/story-driven-delivery/docs/diagram-sync-domain.ts)
- **Architecture violations log:** [diagram-sync-architecture-context.md § Violations](/practices/story-driven-delivery/docs/diagram-sync-architecture-context.md)
- **Legacy DrawIO backend:** `skills/supporting/drawio-story-sync/scripts/drawio_story_sync/`
- **Legacy Miro backend:** `skills/supporting/miro-story-sync/scripts/miro_story_sync/`
- **Legacy story-graph-ops:** `skills/supporting/story-graph-ops/scripts/story_graph_ops/`
