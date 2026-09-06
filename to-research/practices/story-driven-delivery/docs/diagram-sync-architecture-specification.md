# Story Map Diagram Sync — Architecture Specification

> **Status:** Draft — Exploration fidelity
> **Date:** 2026-06-30
> **Mode:** document
> **Domain spec:** [story-ops-domain-specification.md](./story-ops-domain-specification.md)
> **Domain code:** [diagram-sync-domain.ts](./diagram-sync-domain.ts)

---

## Where to Start — What Does This Feature Touch?

Answer each question about the feature or story you are working on. Each "yes" points
to the section with the details you need.

| Question | Read this |
| --- | --- |
| Does it add or change how any story node reads from or writes to any format? | [Multi-Format Story Rendering](#mechanism-multi-format-story-rendering) |
| Does it add or change a document format (Markdown parsing, JSON serialization)? | [Multi-Format Story Rendering](#mechanism-multi-format-story-rendering) — document backends |
| Does it add or change how story nodes are rendered to a diagramming tool? | [Diagram Rendering](#mechanism-diagram-rendering) |
| Does it change where elements are positioned — Y offsets, row heights, column widths? | [Diagram Rendering](#mechanism-diagram-rendering) — layout sub-section |
| Does it change how diagram changes are detected and reported when reading a diagram back? | [Diagram Rendering](#mechanism-diagram-rendering) — sync diffing sub-section |
| Does it add a new diagramming backend (beyond DrawIO and Miro)? | [Diagram Rendering](#mechanism-diagram-rendering) — new concrete classes per node type |
| Does it change how `story-graph.json` is scaffolded into a TypeScript test folder structure? | [Code Rendering](#mechanism-code-rendering) |
| Does it change how existing TypeScript files are preserved during regeneration? | [Code Rendering](#mechanism-code-rendering) — fixture extraction sub-section |
| Does it add a new code generation backend (beyond TypeScript)? | [Code Rendering](#mechanism-code-rendering) — new `LanguageAst` implementation |

---

## Overview

This system takes a canonical story graph (`story-graph.json`) and renders it across multiple output formats — diagramming tools (DrawIO, Miro), TypeScript test folder structures, and source documents (Markdown, JSON) — and reads changed diagrams back to produce a reversible change report. Three layered mechanisms drive the architecture: **Multi-Format Story Rendering**, **Diagram Rendering**, and **Code Rendering**, each building on the one before it.

> **Sources:** [story-ops-domain-specification.md](./story-ops-domain-specification.md), [diagram-sync-domain.ts](./diagram-sync-domain.ts)

---

## Mechanisms

**Multi-Format Story Rendering** (`core/stories/`, `formats/document/`) — `translateFrom` is a fixed template method on `StoryNode`; subclasses extend `updateSelf`, `childCollections`, and one `createChildXxx` factory per child type; document backends (Markdown, JSON) are the simplest case — they use only the domain layer with no extra dependencies. [→ Mechanism section](#mechanism-multi-format-story-rendering)

**Diagram Rendering** (`formats/diagram/`) — adds two mixin layers on top of the base: `DiagramStoryNode` computes positioning from declarative `RowPositions` rules; `DrawIOStoryNode` / `MiroStoryNode` delegate to a held `BackendElement` for XML or Miro API serialization; structural diffing reads diagrams back and compares them against the canonical graph. [→ Mechanism section](#mechanism-diagram-rendering)

**Code Rendering** (`formats/code/`) — adds AST-oriented generation on top of the base: `CodeStoryNode` holds a `LanguageAst` by composition; `TypeScriptStoryNode` provides the concrete implementation including a fixture-extraction parser that preserves hand-written exports during regeneration. [→ Mechanism section](#mechanism-code-rendering)

### Target Package Structure

Every backend folder exposes the same four files. The contracts differ but the slots are identical:

| Slot | Responsibility |
| --- | --- |
| `{fmt}_story_node.py` | StoryNode mixin + concrete node classes |
| `{fmt}_element.py` | The serializable unit the backend writes (XML cell, API payload, dict, heading string, source file) |
| `{fmt}_story_map.py` | Orchestrate a full StoryMap: render out and parse back in |
| `{fmt}_synchronizer.py` | Read the format back, diff against the canonical graph, produce an `UpdateReport` |

```
core/
  stories/
    story_node.py           ← StoryNode (translateFrom, reconcileCollection)
    nodes.py                ← Epic, SubEpic, Story, AcceptanceCriteria
    update_report.py        ← UpdateReport, NodeSnapshot, ChildCollectionPair
    story_map.py            ← StoryMap

formats/
  document/                 ← document backends (no positioning, no AST)
    markdown/
      markdown_story_node.py  ← MarkdownStoryNode mixin + concrete node classes
      markdown_element.py     ← heading/bullet string fragment
      markdown_story_map.py   ← Markdown headings ↔ StoryMap
      markdown_synchronizer.py← parse Markdown back in, diff, UpdateReport
    json/
      json_story_node.py      ← JsonStoryNode mixin + concrete node classes
      json_element.py         ← dict / JSON object
      json_story_map.py       ← JSON ↔ StoryMap (story-graph.json)
      json_synchronizer.py    ← parse JSON back in, diff, UpdateReport

  diagram/                  ← diagram backends (adds positioning layer)
    diagram_story_node.py   ← DiagramStoryNode mixin + DiagramEpic/SubEpic/Story
    row_positions.py        ← RowPositions
    layout.py               ← layout constants, Position, Boundary, style defaults
    drawio/
      drawio_story_node.py    ← DrawIOStoryNode mixin + DrawIOEpic/SubEpic/Story
      drawio_element.py       ← DrawIOElement (XML/mxCell)
      drawio_story_map.py     ← render orchestration
      drawio_synchronizer.py  ← read diagram back, diff, UpdateReport
    miro/
      miro_story_node.py      ← MiroStoryNode mixin + MiroEpic/SubEpic/Story
      miro_element.py         ← MiroElement (Miro v2 API payload)
      miro_story_map.py       ← render orchestration
      miro_synchronizer.py    ← read board back, diff, UpdateReport

  code/                     ← code backends (adds AST layer)
    code_story_node.py      ← CodeStoryNode mixin (holds LanguageAst by composition)
    language_ast.py         ← LanguageAst abstract base (parse, generate, nodeFor)
    typescript/
      typescript_story_node.py  ← TypeScriptStoryNode mixin + concrete node classes
      typescript_element.py     ← TypeScript source file (path + content)
      typescript_story_map.py   ← file tree generation orchestration
      typescript_synchronizer.py← read existing files back, extract fixtures, UpdateReport

cli/
  story_graph_cli.py        ← unified CLI: parse, sync-drawio, sync-miro, generate-ts
```

### Instantiating the Domain

> **The three-layer inheritance chain is the core pattern.** Each format adds exactly one layer on top; no format reaches into another format's layer.

- **DrawIO backend** — `DrawIOEpic(DiagramEpic, DrawIOStoryNode)` — inherits positioning rules from `DiagramEpic` and XML serialization from `DrawIOStoryNode`; holds a `DrawIOElement` by composition. Overrides `createChildSubEpic` to return `DrawIOSubEpic`, ensuring the reconcile loop always produces the correct concrete type.
- **Miro backend** — `MiroEpic(DiagramEpic, MiroStoryNode)` — same pattern; `createChildSubEpic` returns `MiroSubEpic`; holds a `MiroElement` by composition.
- **TypeScript backend** — `TypeScriptSubEpic(SubEpic, TypeScriptStoryNode)` — inherits AC step generation from `TypeScriptStoryNode`; holds a `TypeScriptAst` by composition. `generateTypeScriptFile()` emits the `*-stories.ts` file for the sub-epic.
- **New diagram backend** — create a new `XxxStoryNode` mixin that holds the backend element and delegates `setPosition`/`setSize`/`applyFormatting` to it; override `updateSelf` to serialize after calling super; create concrete node classes overriding each `createChildXxx`. No changes to `translateFrom`, `reconcileCollection`, or any existing class.
- **New code backend** — create a `XxxAst` implementing `LanguageAst`; create a `XxxStoryNode` mixin that holds it; create concrete node classes. No changes to any existing class.

---

## Mechanism: Multi-Format Story Rendering

### The Four-Slot Backend Contract

Every backend — document, diagram, or code — is implemented through exactly four collaborating classes. The slots and the sequence of events between them are the same regardless of format.

**The four slots:**

| Slot | Class | Responsibility |
| --- | --- | --- |
| **node** | `{fmt}StoryNode` mixin + concrete subclasses | Owns `translateFrom`, `updateSelf`, `childCollections`, `createChildXxx`. Holds the element by composition and writes into it during `updateSelf`. |
| **element** | `{fmt}Element` | The serializable unit the backend writes (XML cell, dict, heading string, source file). Knows nothing about the story graph — it only knows its own format. |
| **map** | `{fmt}StoryMap` | Orchestrates a full render or parse of a complete `StoryMap`. Calls `translateFrom` on the root node to kick off the recursive render and assembles the resulting elements into the final artifact. |
| **synchronizer** | `{fmt}Synchronizer` | Reads an existing artifact back in, reconstructs a parallel StoryNode tree, calls `translateFrom` on the canonical tree with the parsed tree as source, and returns the `UpdateReport`. |

**Sequence — render out (canonical graph → format artifact):**

```
StoryMap
  → Map.render(storyMap)
      for each node (root down):
        node.updateSelf(self)          ← writes domain fields into held element
        element.serialize()            ← produces format-specific bytes/payload/dict
  → Map.write(elements)               ← assembles and writes the complete artifact
```

**Sequence — sync back (format artifact → UpdateReport):**

```
Synchronizer.sync(artifact, canonicalMap)
  → parse artifact → parallel {fmt}StoryNode tree
  → canonicalMap.root.translateFrom(parsedRoot)
      for each node pair (matched by name + order):
        node.updateSelf(parsed)        ← copies extracted fields back into canonical node
        reconcileCollection(pair)      ← add / remove / reorder children
  → return UpdateReport (with NodeSnapshot for reversal)
  → on failure: report.reverseOn(canonicalMap.root)
```

The node is the only slot that knows about both the domain (`StoryNode` interface) and the format (its element). The element, map, and synchronizer each know only their own format. `translateFrom` is the seam — it is the single method that makes every format interchangeable.

### Principles & Patterns

**Principle:** Every StoryNode — Epic, SubEpic, Story, AcceptanceCriteria, and all
backend subtypes — participates in a single universal `translateFrom(source): UpdateReport`
algorithm. The algorithm is fixed on `StoryNode` and never overridden. Two abstract
methods and one concrete factory method per child type are the only extension points.

**The fixed `translateFrom` algorithm (four steps, never overridden):**

```
translateFrom(source):
  1. snapshot = NodeSnapshot.capture(self)         ← full recursive before-state
  2. this.updateSelf(source)                        ← abstract; copies type-specific fields
  3. for pair of this.childCollections(source):     ← abstract; returns ChildCollectionPairs
       this.reconcileCollection(pair, report)        ← private; add/match/remove children
  4. return UpdateReport(changes, snapshot)
```

**Pattern — Layered Translator:**

Three abstract layers stack via Python MRO (or TypeScript mixins). Each layer overrides
only `updateSelf`; `translateFrom` and `reconcileCollection` are inherited unchanged.

| Layer | Class | What `updateSelf` adds |
| --- | --- | --- |
| Domain | `StoryNode` subtypes | Type-specific field copies (name, order, domain concepts) |
| Diagram | `DiagramStoryNode` mixin | Calls `super.updateSelf`, then updates `position` + `boundary` via `RowPositions` + `placementRules()` |
| Backend | `DrawIOStoryNode` / `MiroStoryNode` mixins | Calls `super.updateSelf`, then delegates to the held `BackendElement` (XML or Miro API) to serialize |

**`ChildCollectionPair` — how the generic loop knows what to reconcile:**

`childCollections(source)` returns a list of `ChildCollectionPair` value objects. Each pair bundles three things: the self-owned child list, the parallel list from `source`, and a bound reference to the parent's `createChildXxx` factory method. `reconcileCollection` iterates these pairs generically without knowing any node types.

```
ChildCollectionPair {
  selfChildren:   List<StoryNode>          ← children currently owned by this node
  sourceChildren: List<StoryNode>          ← children from the source node
  createChild:    (source) => StoryNode    ← bound to this.createChildXxx(source)
}
```

**`createChildXxx` — polymorphic child factory:**

Every node type implements one `createChildXxx` instance method per child type it can produce. The concrete class (e.g. `DrawIOEpic`) overrides these methods to return the correct backend type. `reconcileCollection` calls `pair.createChild(source)` when a source child has no match — it never names a concrete class.

**Per-node child collections reconciled:**

| Node | `childCollections` returns |
| --- | --- |
| `Epic` | `[{selfChildren: subEpics, createChild: createChildSubEpic}]` |
| `SubEpic` | `[{subEpics, createChildSubEpic}, {stories, createChildStory}]` (two passes) |
| `Story` | `[{acceptanceCriteria, createChildAcceptanceCriteria}]` |
| `AcceptanceCriteria` | `[]` (leaf) |

**Reversibility:** `NodeSnapshot` is captured at step 1 — before any mutation — recording the complete recursive before-state. It is carried by the returned `UpdateReport`. `report.reverseOn(node)` restores all fields and child lists from the snapshot if the downstream write fails.

**Adding a new backend:** Create one concrete class per node type (e.g. `MarkdownEpic`). Override `updateSelf` to add the serialization/extraction step and override each `createChildXxx` to return the matching concrete child type. No changes to `translateFrom`, `reconcileCollection`, `ChildCollectionPair`, or any existing class.

### File Structure

```
core/stories/
    story_node.py              ← StoryNode (translateFrom, reconcileCollection)
    nodes.py                   ← Epic, SubEpic, Story, AcceptanceCriteria
    update_report.py           ← UpdateReport, NodeSnapshot, ChildCollectionPair

formats/document/markdown/
    adapter.py                 ← MarkdownStoryNode (transient adapter)
    story_map_parser.py        ← Markdown → StoryMap
    ac_parser.py               ← AC Markdown → AcceptanceCriteria

formats/diagram/
    diagram_story_node.py      ← DiagramStoryNode mixin + DiagramEpic/SubEpic/Story
    drawio/drawio_story_node.py← DrawIOStoryNode mixin + concrete classes
    drawio/drawio_element.py   ← DrawIOElement — XML/mxCell serialization
    miro/miro_story_node.py    ← MiroStoryNode mixin + concrete classes
    miro/miro_element.py       ← MiroElement — Miro v2 API payload

formats/code/
    code_story_node.py         ← CodeStoryNode mixin (holds LanguageAst)
    language_ast.py            ← LanguageAst abstract base
    typescript/typescript_story_node.py  ← TypeScriptStoryNode mixin + concrete classes
    typescript/typescript_ast.py         ← TypeScriptAst: fixture extraction + emit
```

### Participants

```
StoryNode  (abstract base)
  translateFrom(source: StoryNode): UpdateReport   ← FIXED; never overridden
  updateSelf(source: StoryNode): void              ← ABSTRACT — each layer extends via super
  childCollections(source: StoryNode): ChildCollectionPair[]  ← ABSTRACT — per concrete type
  reconcileCollection(pair, report): void          ← PRIVATE; owns match/create/remove logic
  reverseOn(report: UpdateReport): void

ChildCollectionPair  (value object)
  selfChildren:   StoryNode[]
  sourceChildren: StoryNode[]
  createChild:    (source: StoryNode) => StoryNode  ← bound to parent's createChildXxx

── Layer 1: Domain nodes ────────────────────────────────────────────────────────

  Epic : StoryNode
    updateSelf(source: Epic)
      → copies name, sequentialOrder, domainConcepts
    childCollections(source: Epic): ChildCollectionPair[]
      → [{ selfChildren: subEpics, sourceChildren: source.subEpics,
           createChild: s => this.createChildSubEpic(s) }]
    createChildSubEpic(source: SubEpic): SubEpic
      → new SubEpic(source)                        ← overridden by DrawIOEpic, MiroEpic

  SubEpic : StoryNode
    updateSelf(source: SubEpic)
      → copies name, sequentialOrder, hasSubEpics, testFile, domainConcepts
    childCollections(source: SubEpic): ChildCollectionPair[]
      → [{ subEpics … createChildSubEpic },
         { stories … createChildStory }]           ← two reconcile passes
    createChildSubEpic(source: SubEpic): SubEpic
    createChildStory(source: Story): Story

  Story : StoryNode
    updateSelf(source: Story)
      → copies name, sequentialOrder, storyType, users
    childCollections(source: Story): ChildCollectionPair[]
      → [{ acceptanceCriteria … createChildAcceptanceCriteria }]
    createChildAcceptanceCriteria(source: AC): AC

  AcceptanceCriteria : StoryNode
    updateSelf(source: AC)  → copies criteriaText
    childCollections(source: AC) → []              ← leaf; no children

── Layer 2: Diagram mixin (DiagramMixin<TBase extends StoryNode>) ────────────────

  DiagramStoryNode mixin
    updateSelf(source)
      → super.updateSelf(source)                   ← copies domain fields
      → reads RowPositions(max_depth), placementRules()
      → sets position + boundary

  DiagramEpic   = DiagramMixin(Epic)     — createChildSubEpic → DiagramSubEpic
  DiagramSubEpic = DiagramMixin(SubEpic) — createChildSubEpic → DiagramSubEpic;
                                            createChildStory → DiagramStory
  DiagramStory   = DiagramMixin(Story)   — createChildAcceptanceCriteria → AcceptanceCriteria

── Layer 3: Backend mixins (DrawIOStoryNode, MiroStoryNode) ─────────────────────

  No shared BackendStoryNode class exists — DrawIOStoryNode and MiroStoryNode are
  the real Layer 3 mixins. They follow the same pattern but do not share a superclass.

  DrawIOStoryNode mixin  (abstract)
    element: DrawIOElement                ← held by composition; created in concrete constructor
    setPosition / setSize / applyFormatting → delegate to element
    updateSelf(source)
      → super.updateSelf(source)          ← calls DiagramMixin then domain updateSelf
      → element.setValue(self.name)
      → element.applyStyleForType(…)

  DrawIOEpic : DiagramEpic, DrawIOStoryNode    (concrete)
    createChildSubEpic(source) → new DrawIOSubEpic(source)

  DrawIOSubEpic : DiagramSubEpic, DrawIOStoryNode    (concrete)
    createChildSubEpic(source) → new DrawIOSubEpic(source)
    createChildStory(source)   → new DrawIOStory(source)

  DrawIOStory : DiagramStory, DrawIOStoryNode    (concrete)

  MiroStoryNode mixin  (abstract) — identical pattern; element: MiroElement
  MiroEpic / MiroSubEpic / MiroStory — same structure as DrawIO counterparts

── BackendElement hierarchy (composition boundary) ──────────────────────────────

  BackendElement (abstract)
  DrawIOElement : BackendElement — toXml(): XmlString
  MiroElement   : BackendElement — toApiPayload(): JsonPayload
```

### Flow

```
Caller              DrawIOEpic (translateFrom — fixed algorithm)
  |                     |
  |-- translateFrom(domainEpic) ──────────────────────────────────────────────────
  |                     |
  |                     |─ 1. snapshot = NodeSnapshot.capture(self)
  |                     |      records full recursive before-state for reversal
  |                     |
  |                     |─ 2. this.updateSelf(domainEpic)
  |                     |      ↳ Epic.updateSelf:        copies name, sequentialOrder, domainConcepts
  |                     |      ↳ DiagramStoryNode mixin: super.updateSelf(); then reads RowPositions,
  |                     |                                placementRules(); sets position + boundary
  |                     |      ↳ DrawIOStoryNode mixin:  super.updateSelf(); then calls
  |                     |                                element.setPosition / setSize / applyStyle
  |                     |
  |                     |─ 3. for pair of this.childCollections(domainEpic):
  |                     |       ← DrawIOEpic.childCollections returns:
  |                     |         [{ selfChildren:   this.subEpics,
  |                     |            sourceChildren: domainEpic.subEpics,
  |                     |            createChild:    s => this.createChildSubEpic(s) }]
  |                     |
  |                     |       reconcileCollection(pair, report):
  |                     |         for each source child:
  |                     |           if match found in selfChildren → child.translateFrom(sourceChild)
  |                     |           else → newChild = pair.createChild(sourceChild)
  |                     |                              = this.createChildSubEpic(sourceChild)
  |                     |                              = new DrawIOSubEpic(sourceChild)
  |                     |                  newChild.translateFrom(sourceChild)  ← recurse
  |                     |                  report.recordAdd(newChild)
  |                     |         for each self child with no source match:
  |                     |           pair.selfChildren.remove(selfChild)
  |                     |           report.recordRemove(selfChild)
  |                     |
  |                     |─ 4. return UpdateReport { changes, snapshot }
  |<── UpdateReport ─────|
```

### Walkthrough Example

**Scenario:** Render a single Epic with two SubEpics into a DrawIO diagram.

1. Caller holds a domain `Epic("User Authentication")` from `story-graph.json`.
   Creates an empty `DrawIOEpic("User Authentication")` (holds `DrawIOElement`).

2. Calls `drawioEpic.translateFrom(domainEpic)`.

3. **Step 1 — snapshot.** `NodeSnapshot.capture(drawioEpic)` records the before-state
   recursively — currently empty children.

4. **Step 2 — `updateSelf`.** Calls down the mixin chain:
   - `Epic.updateSelf` copies `name = "User Authentication"`, `sequentialOrder`, `domainConcepts`.
   - `DiagramMixin.updateSelf` reads `RowPositions(max_depth=0)` → `EPIC_Y`. Calls `placementRules()` for height and width strategy. Sets `this.position` and `this.boundary`.
   - `DrawIOStoryNode mixin.updateSelf` calls `element.setPosition(x, EPIC_Y)`, `element.setSize(width, EPIC_HEIGHT)`, `element.applyStyleForType("epic")`. This is the only DrawIO-specific step.

5. **Step 3 — `childCollections` + `reconcileCollection`.**
   `DrawIOEpic.childCollections(domainEpic)` returns one pair:
   `{ selfChildren: [], sourceChildren: [subEpic1, subEpic2], createChild: s => this.createChildSubEpic(s) }`.
   `reconcileCollection` finds no matches; for each source child calls
   `this.createChildSubEpic(subEpic)` → `new DrawIOSubEpic(subEpic)`.
   Then calls `newChild.translateFrom(subEpic)` recursively at `depth=0`.

6. **Step 4 — returns** `UpdateReport` with two `add_new_subEpic` entries and the
   `NodeSnapshot` from step 1.

**Current code gap:** In the existing codebase this sequence is named `render_from_domain`
on `DrawIOEpic`. In the target architecture it becomes `translateFrom`. The logic is
equivalent; the rename and the `createChildXxx` extraction make the universal pattern explicit.

---

## Mechanism: Diagram Rendering

### Principles & Patterns

**Principle:** Positioning is computed once from declarative rules in `lib` — no
backend hard-codes pixel coordinates. All backends consume the same `RowPositions`
values and the same layout constants, so stories in different epics always align
horizontally regardless of which backend is rendering.

**Pattern — Declarative Rule Methods:**

Each `DiagramStoryNode` subclass declares three rule methods:

| Method | Returns | What it defines |
| --- | --- | --- |
| `containmentRules()` | `ContainmentRule` | Allowed parents; what this node can contain |
| `placementRules()` | `PlacementRule` | Y position, height, width strategy, spacing |
| `formattingRules()` | `FormattingRule` | Fill colour, stroke, font, shape key |

`RowPositions` is a standalone geometry calculator — not a node — that computes
absolute Y for every row given a `max_depth` integer. All render variants (outline,
exploration, increments) must call `RowPositions` so stories across epics align.

### File Structure

```
lib/diagram_story_sync/
    diagram_story_node.py   ← DiagramEpic.containmentRules(), placementRules(), formattingRules()
                               DiagramSubEpic, DiagramStory, DiagramIncrement — same
    layout_constants.py     ← EPIC_Y, EPIC_HEIGHT, SUB_EPIC_HEIGHT, CELL_SIZE, ROW_GAP,
                               ACTOR_GAP, CELL_SPACING, BAR_PADDING, SPACING, CONTAINER_PADDING
    node_comparison.py      ← RowPositions (sub_epic_y, actor_y, story_y)
    position.py             ← Position(x, y), Boundary(position, width, height)
    style_defaults.py       ← STYLE_DEFAULTS dict keyed by node type
```

### Participants

```
DiagramEpic
  containmentRules() → { allowed_parents: [], contains_sub_epics: True, contains_stories: False }
  placementRules()   → { y: EPIC_Y, height: EPIC_HEIGHT, span_children: True }
  formattingRules()  → STYLE_DEFAULTS['epic']

DiagramSubEpic
  containmentRules() → { allowed_parents: [DiagramEpic, DiagramSubEpic], … }
  placementRules()   → { y_offset: 75, height: SUB_EPIC_HEIGHT, span_children: True }

DiagramStory
  containmentRules() → { allowed_parents: [DiagramSubEpic], … }
  placementRules()   → { size: CELL_SIZE, spacing: CELL_SPACING, layout: 'left-to-right' }

RowPositions(max_depth)
  sub_epic_y(depth)  = EPIC_Y + EPIC_HEIGHT + ROW_GAP + depth × (SUB_EPIC_HEIGHT + ROW_GAP)
  actor_y            = deepest sub_epic_y + SUB_EPIC_HEIGHT + ACTOR_GAP
  story_y            = actor_y + CELL_SIZE + ROW_GAP
```

### Flow

```
DiagramStoryNode.updateSelf(source)     ← called from step 2 of translateFrom
  |
  |--> RowPositions(max_sub_epic_depth(source))
  |--> self.placementRules()           # which Y offset, height, width strategy
  |--> self.position = Position(x, rows.sub_epic_y(depth))
  |--> self.boundary = Boundary(…, placementRules()['height'])

DrawIOStoryNode.updateSelf(source)      ← called next in MRO chain
  |
  |--> super.updateSelf(source)         # ↑ DiagramStoryNode sets position/boundary
  |--> element.setPosition(x, rows.sub_epic_y(depth))
  |--> element.setSize(width, placementRules()['height'])
  |--> element.applyStyleForType(self.formattingRules())
```

### Walkthrough Example

**Scenario:** Position a `DrawIOSubEpic` at depth 1 (nested sub-epic) in a map with
`max_depth = 2`.

1. `RowPositions(2)` is constructed. `sub_epic_y(1)` =
   `EPIC_Y(20) + EPIC_HEIGHT(30) + ROW_GAP(10) + 1 × (SUB_EPIC_HEIGHT(30) + ROW_GAP(10))` = 100.

2. `DiagramSubEpic.placementRules()` returns `height: SUB_EPIC_HEIGHT`.

3. `DrawIOSubEpic.translateFrom` calls `element.setPosition(x_cursor, 100)` and
   `element.setSize(computed_width, SUB_EPIC_HEIGHT)`.

4. DrawIO renders the sub-epic bar at y=100 — the same value that `MiroSubEpic` would
   use for the same node. Both backends align horizontally because both consult
   `RowPositions`, never their own hardcoded values.

---

### Sync Diffing

### Principles & Patterns

**Principle:** Structural comparison of an extracted diagram tree against the canonical
story graph is format-agnostic — it operates only on `name`, `sequential_order`, and
`isinstance(node, Epic/SubEpic/Story)`; it never touches XML attributes or Miro API
shape.

**Pattern — Structural Comparator with Backend Hook:**

`compare_node_lists` in `lib` accepts an `is_manual_subtree_root` predicate as a
backend hook. The default predicate treats every node as generated. DrawIO passes
`_drawio_is_manual_subtree_root` to veto rename pairing for cells the user drew
manually (numeric `cell_id` without a `/` path). Miro passes the default.

`UpdateReport` is a reversible transaction log — it records both the changes
(exact match, rename, new, removed, reorder) and a `NodeSnapshot` of the before-state.
`reverseOn(StoryNode)` restores prior state.

**`UpdateReport` ownership:** Defined in `story_graph_ops/update_report.py` (domain
result, not a diagram concept). `lib/diagram_story_sync/update_report.py` is a
re-export shim — backends import from it for convenience.

### File Structure

```
lib/diagram_story_sync/
    node_comparison.py      ← compare_node_lists, RowPositions,
                               report_sub_epic_sibling_reorder_if_needed,
                               report_leaf_story_group_reorder_if_needed,
                               collect_all_names, max_sub_epic_depth
    update_report.py        ← re-export shim → story_graph_ops.update_report
    render_summary.py       ← UpdateReport → human-readable Markdown summary

story-graph-ops/scripts/story_graph_ops/
    update_report.py        ← UpdateReport (authoritative), NodeSnapshot,
                               MatchEntry, StoryEntry, SubEpicSiblingReorder, …
```

### Participants

```
compare_node_lists(extracted, original, report, *, is_manual_subtree_root)
  → populates UpdateReport with exact_matches, renames, new_*, removed_*, reorders

UpdateReport
  changes: Change          (add / rename / remove / reorder entries)
  snapshot: NodeSnapshot   (before-state for reversal)
  reverseOn(StoryNode): void

_drawio_is_manual_subtree_root(node) → bool
  → True when node.cell_id has no '/' (manually drawn in DrawIO canvas)
  → only DrawIO backend passes this; Miro uses the default (always False)
```

### Flow

```
Extraction phase (read diagram → node tree):
  DrawIOStoryMap.extract()
    → builds DrawIOEpic / DrawIOSubEpic / DrawIOStory tree from XML

Diff phase:
  compare_node_lists(extracted_epics, original_epics, report, recurse=True,
                     is_manual_subtree_root=_drawio_is_manual_subtree_root)
    → for each extracted node: find exact match in original by name
    → unmatched extracted: check if it's a rename candidate (not in global name set,
      not a manual subtree root)
    → unmatched original: record as removed
    → recurse into children via node._compare_children(original_node, report)

Result:
  UpdateReport { exact_matches, renames, new_epics, new_sub_epics, new_stories,
                 removed_*, sub_epic_sibling_reorders, story_group_reorders }
```

### Walkthrough Example

**Scenario:** User renames "Login Flow" → "Sign-in Flow" in the DrawIO diagram. The
diagram is extracted and diffed against the canonical graph.

1. `compare_node_lists` receives `extracted=[DrawIOEpic("Sign-in Flow")]` and
   `original=[Epic("Login Flow")]`.

2. Exact match fails — names differ.

3. `"Sign-in Flow"` is not in `all_original_names` → rename candidate.
   `"Login Flow"` is not in `all_extracted_names` → rename candidate.
   `_drawio_is_manual_subtree_root(epic)` → False (path-based `cell_id` contains `/`).

4. `report.add_rename("Sign-in Flow", "Login Flow", confidence=1.0)` is recorded.

5. `UpdateReport` returned to `StoryIOSynchronizer`, which writes the rename back to
   `story-graph.json` and the canonical graph is updated.

---

### Document Backends

### Principles & Patterns

**Principle:** Markdown is one more source format. Parsing Markdown into a `StoryMap`
follows the same `translateFrom` pattern as rendering to a diagram backend — the
parser exposes the common `StoryNode` interface and the domain nodes call
`translateFrom` on each source node.

**Pattern — Markdown Source Adapter:**

Markdown parsers (`md_story_map_to_story_graph.py`,
`md_acceptance_criteria_to_story_graph.py`) read Markdown headings as story node
candidates. Each heading line becomes a transient node that exposes `name`,
`sequential_order`, and `children` — the same interface as any `StoryNode`. Domain
nodes then call `translateFrom(markdown_node)` to populate themselves.

The canonical output is `story-graph.json`, written by `story_graph_ops/` scripts.

### File Structure

```
story-graph-ops/scripts/
    md_story_map_to_story_graph.py           ← Markdown story map → StoryMap
    md_acceptance_criteria_to_story_graph.py ← Markdown AC → StoryMap AC fields
    story_graph_ops/
        nodes.py                             ← StoryMap, Epic, SubEpic, Story
        story_graph_paths.py                 ← canonical file path resolution
        story_map_updater.py                 ← writes story-graph.json
```

### Participants

```
MarkdownStoryNode (transient adapter — exposes StoryNode interface)
  name: NodeName
  sequential_order: Integer
  children(): MarkdownStoryNode

StoryMap.translateFrom(MarkdownStoryNode)
  → reads heading hierarchy
  → creates Epic / SubEpic / Story nodes
  → writes to story-graph.json via StoryMapUpdater
```

### Flow

```
Markdown file
  → md_story_map_to_story_graph.py parses headings into MarkdownStoryNode tree
  → StoryMap.translateFrom(markdown_root)
      for each heading-level-1 → create Epic, epic.translateFrom(h1_node)
        for each heading-level-2 → create SubEpic, sub_epic.translateFrom(h2_node)
          for each heading-level-3 → create Story, story.translateFrom(h3_node)
  → StoryMapUpdater.write(story_map) → story-graph.json
```

### Walkthrough Example

**Scenario:** A Markdown file has heading structure `# Login → ## Sign In → ### Enter Password`.

1. Parser reads `# Login` → `MarkdownStoryNode("Login", depth=1)`.

2. `StoryMap.translateFrom` creates `Epic("Login")`.
   `epic.translateFrom(markdown_node)` reads `markdown_node.name = "Login"` and sets
   `self.name = "Login"` — the "update self" step for the domain layer.

3. Parser reads `## Sign In` → child of Login node.
   `epic.translateFrom` reconciles children: `"Sign In"` is new → creates `SubEpic("Sign In")`
   and calls `sub_epic.translateFrom(markdown_node)`.

4. Parser reads `### Enter Password` → child of Sign In.
   `sub_epic.translateFrom` creates `Story("Enter Password")`.

5. `UpdateReport` records three `add_new_*` entries. `StoryMapUpdater.write(story_map)`
   persists the result to `story-graph.json`.

---

## Mechanism: Code Rendering

### Principles & Patterns

**Principle:** `story-graph.json` is the single source of truth for story structure.
TypeScript test files (`*-stories.ts`) are generated from it — one file per sub-epic,
organized into `tests/{epic-slug}/{sub-epic-slug}/` folder paths. Regeneration is safe
because existing files are read before writing: a **fixture-extraction parser** identifies
and preserves hand-written exports (route constants, example arrays, helper functions)
while replacing only the generated story const blocks.

**Pattern — One-directional generation (not `translateFrom`):**

This mechanism is distinct from `translateFrom`. There is no "reverse" — TypeScript
files are not read back into the story graph. The flow is strictly:

```
story-graph.json  →  parse  →  transform per sub-epic  →  merge with existing  →  write *.ts
```

**Pattern — Sub-Epic as generation unit:**

The `SubEpic` is the file boundary. Each sub-epic produces exactly one `*-stories.ts`
file. Stories within the sub-epic become top-level TypeScript `const` blocks inside
that file. AcceptanceCriteria within a story become the `steps` array inside the story
const.

**Pattern — Fixture Extraction (brace-counting parser):**

When a `*-stories.ts` file already exists, the generator reads it and separates its
content into two zones:
- **Generated zone** — `const <SCREAMING_SNAKE> = { … }` blocks that match the story
  slug pattern; will be replaced.
- **Fixture zone** — everything else (imports, route constants, example arrays, helper
  exports); will be preserved verbatim and emitted at the top of the new file.

The current parser uses brace-counting (not a TypeScript AST) to find block boundaries.
This is the key integration gap — see violations V-09.

**Pattern — AC text → Gherkin step dicts:**

`generate-domain-stories.py` includes a mini-parser (`parse_ac_text`) that converts
free-form acceptance criteria text into structured step dicts:
```
"Given the user is logged in\nWhen they view an invoice\nThen they see the total"
  →  [{ "type": "given", "text": "the user is logged in" },
      { "type": "when",  "text": "they view an invoice" },
      { "type": "then",  "text": "they see the total" }]
```
These step dicts populate the `steps` field of each story const.

### File Structure

```
story-graph-ops/scripts/                 ← standalone today; target: integrate into package
    generate-domain-stories.py           ← full generator: story-graph.json + AC markdown
                                           → tests/**/*-stories.ts with fixture preservation
    generate-stories.py                  ← simpler variant: story-graph.json only, no AC merge

story-graph-ops/scripts/story_graph_ops/ ← target location for integrated implementation
    nodes.py                             ← StoryNode, Epic, SubEpic, Story (will grow TypeScript
                                           code-gen methods once CodeStoryNode is introduced)
```

### Participants

```
SubEpicGroup  (internal data class — standalone scripts only)
  epic_slug:    String
  sub_epic_slug: String
  stories:      List<StoryDict>

StoryDict  (internal data class — standalone scripts only)
  name:         String
  slug:         String          ← SCREAMING_SNAKE const name
  steps:        List<StepDict>

StepDict
  type:         "given" | "when" | "then" | "and" | "but"
  text:         String

parse_graph(story_graph_path)       → List<SubEpicGroup>
ts_path_for(epic_slug, sub_epic_slug) → Path (tests/{epic}/{sub-epic}/*-stories.ts)
generate_file(sub_epic_group)       → String (TypeScript file content)
generate_story_const(story_dict)    → String (single const block)
extract_fixture_lines(ts_path)      → List<String> (non-story lines from existing file)
parse_ac_text(raw_text)             → List<StepDict>
```

**Target participants (after re-architecture):**

```
SubEpic : StoryNode
  generateTypeScriptFile() → String    ← owns file-level emit
  typeScriptPath() → Path              ← owns slug → path rule

Story : StoryNode
  generateTypeScriptConst() → String   ← owns const block emit

AcceptanceCriteria : StoryNode
  toStepDicts() → List<StepDict>       ← owns Gherkin step parsing

TypeScriptFixtureExtractor            ← standalone utility (fixture preservation)
  extractFrom(path: Path) → FixtureContent
  mergeWith(generated: String, fixtures: FixtureContent) → String
```

### Flow

```
Caller
  |
  |── parse_graph(story-graph.json)
  |     → yields SubEpicGroup per sub-epic
  |
  |── for each SubEpicGroup:
  |     dest = ts_path_for(epic_slug, sub_epic_slug)
  |     fixtures = extract_fixture_lines(dest)    ← reads existing file (if any)
  |     content = generate_file(sub_epic_group)   ← generates story const blocks
  |     write(dest, fixtures + content)           ← preserves hand-written exports
```

### Walkthrough Example

**Scenario:** Sub-epic "Review Past Invoices" under epic "Manage Billing" with one story
"View Invoice Total" has two AC steps.

1. `parse_graph()` yields:
   ```
   SubEpicGroup(epic_slug="manage-billing", sub_epic_slug="review-past-invoices",
     stories=[{ name: "View Invoice Total", slug: "VIEW_INVOICE_TOTAL",
                steps: [{ type: "given", text: "an invoice exists" },
                        { type: "then",  text: "the total is shown" }] }])
   ```

2. `ts_path_for("manage-billing", "review-past-invoices")` →
   `tests/manage-billing/review-past-invoices/review-past-invoices-stories.ts`

3. File already exists; `extract_fixture_lines(dest)` finds:
   ```typescript
   export const INVOICE_ROUTE = '/billing/invoices'
   export const exampleInvoices = [{ id: 1, total: 99.99 }]
   ```
   These are preserved.

4. `generate_file(group)` emits:
   ```typescript
   export const VIEW_INVOICE_TOTAL = {
     name: 'View Invoice Total',
     steps: [
       { type: 'given', text: 'an invoice exists' },
       { type: 'then',  text: 'the total is shown' },
     ],
   }
   ```

5. Output file = preserved fixture lines + generated story const. Hand-written
   `INVOICE_ROUTE` and `exampleInvoices` survive the regeneration unchanged.

**Current code gap:** The generation scripts are standalone (`generate-domain-stories.py`,
`generate-stories.py`) with no integration into `story_graph_ops`. The target
re-architecture introduces `CodeStoryNode` / `TypeScriptStoryNode` in the domain
hierarchy so each node type owns its own generation method, following the same pattern
as `DrawIOStoryNode.updateSelf`.

---

## Testing Architecture

Tests for diagram sync follow a **unit-by-layer** pattern: domain and lib components
are tested with plain Python pytest (no diagram tool connection); backend node tests
stub `DrawIOElement` / `MiroElement` at the composition boundary and assert on the
element's state; end-to-end sync tests load real `story-graph.json` fixtures and
assert on the rendered XML / Miro payload structure. See
`drawio-story-sync/tests/` and `miro-story-sync/tests/` for test file layout.

---

## Violations (Existing System)

The following gaps between current code and the target architecture are recorded for
tracking. Each should be addressed as a separate refactoring ticket.

| # | Location | Violation | Severity | Resolution |
| --- | --- | --- | --- | --- |
| V-01 | `drawio_story_sync/drawio_story_node.py` | `render_from_domain` is the name used instead of `translateFrom`; the pattern exists but is not named consistently across backends | Medium | Rename to `translateFrom` across DrawIO and Miro backends |
| V-02 | `drawio_story_sync/drawio_story_node.py` | `DrawIOIncrementLane` does not inherit `DiagramIncrement` | Medium | Refactor `DrawIOIncrementLane` to extend `DrawIOStoryNode` as `DrawIOIncrementLane(DiagramIncrement, DrawIOStoryNode)` |
| V-03 | `drawio_story_sync/story_io_position.py` | Local `Position`, `Boundary` duplicate `lib/diagram_story_sync/position.py` | Low | Delete local copy; import from `lib` |
| V-04 | `UpdateReport` | Does not yet carry `NodeSnapshot` for reversal — `reverseOn(StoryNode)` is not implemented | High | Extend `UpdateReport` with `NodeSnapshot` and implement `reverseOn` |
| V-05 | `drawio_story_sync/drawio_story_node.py` | `DrawIOStoryNode.containment_rules()`, `placement_rules()`, `formatting_rules()` return empty dicts, overriding the lib rules rather than inheriting them | Low | Remove the overrides; let MRO resolve to `DiagramEpic` / `DiagramSubEpic` / `DiagramStory` implementations |
| V-06 | `story_graph_ops/nodes.py`, `drawio_story_node.py`, `miro_story_node.py` | `createChildXxx` factory methods do not yet exist; child creation is ad-hoc inside `render_from_domain` rather than via the polymorphic `ChildCollectionPair.createChild` pattern | High | Introduce `createChildSubEpic`, `createChildStory`, `createChildAcceptanceCriteria` on each node type; override in backend classes to return concrete types; make `reconcileCollection` the only caller |
| V-07 | All node classes | `reconcileCollection` is not a private shared method on `StoryNode`; child reconciliation is duplicated per backend | High | Extract into `StoryNode.reconcileCollection(pair, report)` — a private method called by the fixed `translateFrom` algorithm |
| V-08 | `generate-domain-stories.py`, `generate-stories.py` | Code scaffolding scripts are standalone outside `story_graph_ops`; `SubEpic`/`Story`/`AcceptanceCriteria` do not own their own TypeScript generation methods | High | Re-architect: introduce `CodeStoryNode` and `TypeScriptStoryNode` mixins in `story_graph_ops/`; move generation into `SubEpic.generateTypeScriptFile()`, `Story.generateTypeScriptConst()`, `AcceptanceCriteria.toStepDicts()`; wire into `story_graph_cli.py` as a first-class `generate` command |
| V-09 | `generate-domain-stories.py` — `extract_fixture_lines()` | TypeScript fixture extraction uses brace-counting and regex, not a structural parser; brittle against nested braces and template literals | Medium | Replace with a proper TypeScript AST-based extractor (`TypeScriptFixtureExtractor`) using a lightweight parser (e.g. `ts-morph` or `acorn`) to identify and preserve non-generated exports reliably |

---

## References

- **Domain specification:** [story-ops-domain-specification.md](./story-ops-domain-specification.md)
- **Domain TypeScript (1-1 from spec):** [diagram-sync-domain.ts](./diagram-sync-domain.ts)
- **Domain model (conceptual):** [diagram-sync-domain-model.md](./diagram-sync-domain-model.md)
- **Shared library:** `lib/diagram_story_sync/` — platform-agnostic diagram node hierarchy, layout, diffing
- **Story-graph-ops:** `skills/supporting/story-graph-ops/scripts/story_graph_ops/` — domain nodes, UpdateReport
- **DrawIO backend:** `skills/supporting/drawio-story-sync/scripts/drawio_story_sync/`
- **Miro backend:** `skills/supporting/miro-story-sync/scripts/miro_story_sync/`
- **Code scaffolding (standalone):** `skills/supporting/story-graph-ops/scripts/generate-domain-stories.py` — story-graph.json → `*-stories.ts`
- **Planning doc:** `docs/domain-multi-backend-planning.md`
