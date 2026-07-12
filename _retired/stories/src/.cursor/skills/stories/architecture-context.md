---
generating-skill: abd-architecture-specification
type: architecture-context
fidelity: specification
---

# Story Model & Multi-Channel I/O — Architecture Specification

> **Status:** Draft — Specification fidelity
> **Date:** 2026-07-04

---

## Where to Start — What Does This Feature Touch?

Answer each question about the feature or story you are working on. Each "yes"
points to a context file with the details you need. Read only those files —
you don't need the rest of this document.

| Question | Read this |
| --- | --- |
| Does it change the base `StoryNode` contract (properties, `translate_from`, `update_self`, `child_collections`)? | [The Base Pattern](#the-base-pattern) — this file |
| Does it add a new node type (Epic, SubEpic, Story, Scenario, Increment, StoryMap …)? | [Node Types](#node-types) — this file |
| Does it add a new **channel** — a serialization or discovery target for the model? | [Channels](#channels) — this file |
| Does it change an operation that lives on nodes (`parse`, `render`, `sync`, `from_workspace`, `attach_*`)? | [Operations](#operations-on-nodes) — this file |
| Does it change how a Markdown / JSON document is parsed or rendered? | [document/](document/architecture-context.md) |
| Does it change diagram positioning, layout, or sync diffing (DrawIO, Miro)? | [diagram/](diagram/architecture-context.md) |
| Does it change code scaffolding (TypeScript, Python, Java, JavaScript test folders)? | [code/](code/architecture-context.md) |
| Does it change how a `Workspace` is assembled from a folder? | [Workspace Assembly](#workspace-assembly) — this file |
| Does it change the CLI entry points or add a new command? | [../skill/CLI/](../skill/CLI/) |

---

## Overview

This package holds the **canonical story model** and the **channels** through
which that model is read from and written to the world. The model is a tree of
`StoryNode` value objects. A channel is anything that can turn a chunk of the
world (a markdown file, a JSON document, a DrawIO XML, a folder of `.test.ts`
files) into that tree, or the tree back into that chunk.

There is exactly one canonical form: an in-memory `StoryMap` tree of typed
`StoryNode`s. Every channel — markdown, JSON, DrawIO, Miro, TypeScript, Python,
Java, JavaScript — is peer-equal. JSON is not more canonical than markdown; it
is simply one of the serialization channels.

The architecture is a **two-axis extension pattern**:

- **Axis 1 — node type.** The domain has ~seven node types (`StoryMap`,
  `Epic`, `SubEpic`, `Story`, `Scenario`, `Increment`, plus value-object
  descendants). Every node type is defined once in `model/` with its
  properties, its `update_self`, its `child_collections`, and its
  `create_child_*` factories.
- **Axis 2 — channel.** Every channel provides its own subclass of every node
  type it touches. `MarkdownEpic extends Epic`, `JsonSubEpic extends SubEpic`,
  `DrawIOStory extends Story`, and so on. The channel-specific subclass adds
  channel-specific behaviour (regex, XML shape, folder discovery, positioning)
  while inheriting everything else.

Operations that vary by channel — parsing, rendering, syncing, file discovery,
source-location stamping, cross-linking — all follow this same pattern.
`translate_from` is one operation among several, not the whole story.

> **Sources:** [domain-context.md](domain-context.md), [bdd-context.md](bdd-context.md)

---

## The Base Pattern

Every operation that varies across channels follows the same three-layer shape.

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Layer 1 — model/                                                          │
│    Defines what a node is: name, sequential_order, child collections,      │
│    factory methods with sensible defaults. Zero knowledge of any channel.  │
├────────────────────────────────────────────────────────────────────────────┤
│  Layer 2 — {channel}/nodes.py                                              │
│    A subclass per node type per channel. Adds channel-specific behaviour   │
│    by overriding operations. Nothing else changes.                         │
├────────────────────────────────────────────────────────────────────────────┤
│  Layer 3 — the operation itself                                            │
│    Some operations (translate_from) are FINAL on the base. Others (parse,  │
│    render, from_workspace) are declared abstract on the base and provided  │
│    by the channel's root node (e.g. MarkdownStoryMap.parse).               │
└────────────────────────────────────────────────────────────────────────────┘
```

### Why this shape

**The problem.** Every channel does the same tree work — walk the source, update
matching children, create missing ones, remove extras, discover files, stamp
source locations, cross-link scenarios to stories. If each channel implements
each of these itself, you get N × M copies of the same logic that drift, and
every new channel or new operation re-derives them from scratch.

**The inversion — the logic lives on the node.** Whichever layer is best
positioned to know how to do a thing owns that thing:

- Tree reconciliation is universal, so it lives on `StoryNode` and is FINAL.
- What child collections a node has is per-node-type, so it lives on the
  concrete node type in `model/`.
- How a markdown story map is parsed is per-channel-per-node-type, so it
  lives on `MarkdownStoryMap` in `document/markdown/nodes.py`.

Nothing bypasses this. There is no "adapter" file that owns markdown parsing
separately from `MarkdownStoryMap`, no "loader" file that iterates the tree
separately from the tree itself. If it is about markdown, it lives on the
Markdown node. If it is about the tree shape, it lives on the base node.

---

## Node Types

Defined in `model/`. Every channel inherits from these.

| Type | Role | Children |
| --- | --- | --- |
| `StoryMap` | Root container | `epics`, `increments` |
| `Epic` | Top-level goal grouping | `sub_epics` |
| `SubEpic` | Journey / capability grouping | `sub_epics` (nested), `stories`, `test_suites` |
| `Story` | Verb–noun user story | `scenarios`, `test_cases` |
| `Scenario` | Given / When / Then walk-through (leaf) | *(none — value fields only)* |
| `Increment` | One step in a thin-slicing plan (leaf) | *(none — value fields only)* |

Supporting value objects (never subclassed per channel): `SourceLocation`,
`Clause`, `Interaction`, `Phase`, `TestSuite`, `TestCase`, `Test`, `Tier`,
`Language`, `StoryContext`, `UpdateReport`, `NodeSnapshot`,
`ChildCollectionPair`.

### `StoryNode` base

```
class StoryNode  << abstract >>
  Properties:
    name:             str
    sequential_order: int

  Methods — FINAL (never overridden):
    + translate_from(source: StoryNode) -> UpdateReport
    - _reconcile_collection(pair, report) -> None

  Methods — abstract (every concrete node type implements):
    + update_self(source: StoryNode) -> None
    + child_collections(source: StoryNode) -> List[ChildCollectionPair]
    + create_child_*(source) -> StoryNode          # one per child type
```

`translate_from` is fixed:

```
translate_from(source):
  1. snapshot = NodeSnapshot(self)          # capture full recursive before-state
  2. self.update_self(source)               # copy properties
  3. pairs = self.child_collections(source) # declare which lists to reconcile
  4. for pair in pairs:
       _reconcile_collection(pair, report) # match, create, remove children
  return UpdateReport(changes, snapshot)
```

`_reconcile_collection` matches self-children to source-children by
`sequential_order` and `name`. Unmatched source children are created via
`create_child_*(source)`. Unmatched self-children are removed. Both are
recorded in the `UpdateReport`.

---

## Channels

A **channel** is a serialization or discovery target. It provides:

- A subclass of every node type it needs (typically all of them).
- Overrides of `create_child_*` on those subclasses so `translate_from`
  produces channel-typed children throughout the tree.
- Concrete implementations of channel-specific operations (`parse`, `render`,
  `sync`, `from_workspace`, `attach_source_locations`, …) on the appropriate
  node type — usually the channel's `StoryMap` root, sometimes a leaf.

The channels currently in the repo:

| Channel | Folder | External representation |
| --- | --- | --- |
| Markdown | `document/markdown/` | `str` (markdown text) |
| JSON | `document/json/` | `str` (`story-graph.json` schema) |
| DrawIO | `diagram/drawio/` | `str` (mxGraph XML) |
| Miro | `diagram/miro/` | `str` (Miro payload) |
| TypeScript | `code/typescript/` | `Dict[str, str]` (file-path → content) |
| Python | `code/python/` | `Dict[str, str]` |
| Java | `code/java/` | `Dict[str, str]` |
| JavaScript | `code/javascript/` | `Dict[str, str]` |

**No channel is more canonical than another.** The canonical form is the
in-memory `StoryMap` tree. JSON is a serialization channel like any other; it
just happens to be structurally close to the domain because it was designed
alongside it.

### Instantiating a channel's node tree

The three-layer inheritance is entirely additive. Adding a new channel does
not touch any existing class.

- **Markdown backend** — `MarkdownEpic(Epic)` overrides `create_child_sub_epic`
  to return `MarkdownSubEpic`; `MarkdownStoryMap(StoryMap)` owns
  `parse` / `render` / `sync` / `attach_source_locations` / `from_workspace`.
- **DrawIO backend** — `DrawIOEpic(Epic)` similarly overrides its factories;
  `DrawIOStoryMap(StoryMap)` owns rendering / diffing / sync.
- **TypeScript backend** — `TypeScriptStoryMap(StoryMap)` owns `from_workspace`
  (glob `*.test.ts`) and produces `TestSuite` value objects that get attached
  to `SubEpic.test_suites`.

---

## Operations on Nodes

The pattern from *The Base Pattern* applies to **every** operation that varies
across channels — not only to `translate_from`. This is a partial catalogue.

| Operation | Where declared | Where implemented |
| --- | --- | --- |
| `translate_from(source) -> UpdateReport` | `StoryNode` (FINAL) | — algorithm never overridden — |
| `update_self(source)` | `StoryNode` (abstract) | concrete node types in `model/`, refined by channels if needed |
| `child_collections(source)` | `StoryNode` (abstract) | concrete node types in `model/` |
| `create_child_*(source)` | concrete node types in `model/` | channel subclasses override to return channel-typed children |
| `parse(external) -> {ch}StoryMap` | channel `StoryMap` | `MarkdownStoryMap.parse`, `JsonStoryMap.parse`, `DrawIOStoryMap.parse`, … |
| `render(canonical, previous=None) -> external` | channel `StoryMap` | `MarkdownStoryMap.render`, `DrawIOStoryMap.render`, … |
| `sync(external, canonical) -> UpdateReport` | channel `StoryMap` | one-liner — `canonical.translate_from(self.parse(external))` |
| `from_workspace(root)` | channel root or leaf | `JsonStoryMap.from_workspace`, `MarkdownStoryMap.from_workspace`, `MarkdownScenario.from_workspace`, `MarkdownIncrement.from_workspace`, `TypeScriptStoryMap.from_workspace`, `PythonStoryMap.from_workspace`, `JavaStoryMap.from_workspace`, `JavaScriptStoryMap.from_workspace`, `StoryContext.from_workspace` |
| `attach_source_locations(text, rel)` | channel `StoryMap` | `MarkdownStoryMap`, `JsonStoryMap` |
| `attach_scenarios(scenarios)` | base `StoryMap` | `model/story_map.py` (walks `all_stories()`, calls `story.create_child_scenario()`) |
| `attach_test_suites(suites)` | base `StoryMap` | `model/story_map.py` (walks `all_sub_epics()`, matches by slug) |
| `all_stories()` / `all_sub_epics()` | base `StoryMap` | `model/story_map.py` |

Each row obeys the same rule: the operation lives on the layer that has the
knowledge. `all_stories` is universal → on `StoryMap`. Markdown source
stamping needs regex → on `MarkdownStoryMap`. TypeScript test discovery needs
`.test.ts` globs → on `TypeScriptStoryMap`.

### The Uniform Callable Surface

Every channel's `StoryMap` root exposes exactly three public methods with the
same signatures, regardless of the channel's external form:

```
class {channel}StoryMap(StoryMap):
    def parse(external) -> {channel}StoryMap
    def render(canonical, previous: Optional = None) -> external
    def sync(external, canonical) -> UpdateReport
```

This is what lets the CLI dispatch to any channel with a two-line lookup:
look up the channel-specific `StoryMap` class by name, call the method.

**Locked disciplines:**

- **No stateful constructors.** `{channel}StoryMap()` takes no arguments beyond
  optional configuration that is truly per-instance (e.g., `tests_root` for
  code channels). It never accepts a canonical `StoryMap` or an external
  artifact — those flow through `render` / `parse` / `sync`.
- **`previous` is accepted and (usually) ignored.** Only channels that need it
  — currently only the code family, for preserving hand-written exports — do
  anything with it. Every other channel accepts and drops the parameter, so
  callers don't need to know which channels care.
- **No convenience methods on the seam.** No `append_epic`, `remove_epic`, etc.
  on channel `StoryMap`s. Those methods belong on the canonical `StoryMap`;
  callers build fixtures on `StoryMap` and pass it into `render` / `sync`.

---

## Workspace Assembly

A **`Workspace`** is the parsed-artifact aggregate that scanners consume. It
holds a fully-populated `StoryMap` plus flat views of scenarios, test suites,
and story contexts.

`Workspace.load(root)` is the single entry point. It calls each channel's
`from_workspace` in turn:

```
Workspace.load(root):
    story_map = JsonStoryMap.from_workspace(root)
             or MarkdownStoryMap.from_workspace(root)
             or StoryMap()

    scenarios = MarkdownScenario.from_workspace(root)
    story_map.attach_scenarios(scenarios)

    for inc in MarkdownIncrement.from_workspace(root):
        story_map.increments.append(inc)

    test_suites = [
        *TypeScriptStoryMap.from_workspace(root),
        *JavaScriptStoryMap.from_workspace(root),
        *PythonStoryMap.from_workspace(root),
        *JavaStoryMap.from_workspace(root),
    ]
    story_map.attach_test_suites(test_suites)

    return Workspace(root, story_map, scenarios, test_suites,
                     story_contexts=StoryContext.from_workspace(root))
```

There is no `loader.py`, no `scenarios_loader.py`, no `tests_loader.py`, no
`story_context_loader.py`. Every discovery-and-parse concern lives on the
domain object that produces the result.

---

## Source Layout

```
stories/                                    <- skill root
+-- src/
    +-- stories/                            <- domain package (this file's scope)
    |   +-- architecture-context.md         <- this file
    |   +-- domain-context.md
    |   +-- bdd-context.md
    |   +-- model/                          <- pure domain node hierarchy
    |   |   +-- story_node.py               <- StoryNode base (translate_from, reconcile)
    |   |   +-- nodes.py                    <- Epic, SubEpic, Story
    |   |   +-- story_map.py                <- StoryMap (attach_scenarios, all_stories, …)
    |   |   +-- scenario.py                 <- Scenario, Clause, Interaction, Phase
    |   |   +-- thin_slice.py               <- Increment
    |   |   +-- test_file.py                <- TestSuite, TestCase, Test, Tier, Language
    |   |   +-- story_context.py            <- StoryContext (from_workspace lives here)
    |   |   +-- source_location.py          <- SourceLocation
    |   |   +-- update_report.py            <- UpdateReport, NodeSnapshot, ChildCollectionPair
    |   |   +-- workspace.py                <- Workspace aggregate + Workspace.load(root)
    |   +-- document/                       <- document channels
    |   |   +-- architecture-context.md
    |   |   +-- markdown/nodes.py           <- MarkdownStoryMap/Epic/SubEpic/Story/Scenario/Increment + I/O
    |   |   +-- json/nodes.py               <- JsonStoryMap/Epic/SubEpic/Story/Scenario/Increment + I/O
    |   +-- diagram/                        <- diagram channels
    |   |   +-- architecture-context.md
    |   |   +-- drawio/nodes.py             <- DrawIOStoryMap/Epic/… + XML I/O + positioning
    |   |   +-- miro/nodes.py               <- MiroStoryMap/Epic/… + Miro I/O
    |   +-- code/                           <- code channels
    |   |   +-- architecture-context.md
    |   |   +-- typescript/nodes.py         <- TypeScriptStoryMap/… + test-file discovery
    |   |   +-- python/nodes.py             <- PythonStoryMap/… + test-file discovery
    |   |   +-- java/nodes.py               <- JavaStoryMap/… + test-file discovery
    |   |   +-- javascript/nodes.py         <- JavaScriptStoryMap/… + test-file discovery
    |   +-- workspace/                      <- (thin re-exports only)
    |       +-- __init__.py                 <- re-exports Workspace, Scenario, TestSuite, …
    +-- skill/                              <- skill packaging (sibling package, out of scope here)
        +-- assembly/                       <- Skill, Manifest, Fidelity, Phase, FrontMatter …
        +-- CLI/                            <- assemble_components entry point
        +-- scanners/                       <- ArtifactScanner base + Workspace.load consumer
        +-- evals/                          <- Cursor-agent evaluation harness
```

---

## Rules — Must Apply to Every Channel

These rules are **not style preferences**. Each one was violated at some point
and the violation produced a specific, painful mess. Read the "why this rule
exists" note under each rule before you consider bending it.

### Structural rules — where code lives

**R1. Channel-specific behaviour lives on the channel's node — never in a
sibling helper file.**

If the operation needs markdown regex, it lives on a Markdown node. If it
needs `.test.ts` globs, it lives on `TypeScriptStoryMap`. If it needs DrawIO
XML shapes, it lives on `DrawIOStoryMap` or its children.

Forbidden file names — do not create any of these, and delete any you find:

- `*_loader.py`         (e.g. `scenarios_loader.py`, `tests_loader.py`, `story_context_loader.py`)
- `*_adapter.py`
- `{channel}_story_map.py` living **separately from** `nodes.py`
  (e.g. `markdown_story_map.py` next to `markdown/nodes.py`)
- `tree.py`, `helpers.py`, `utils.py` at the channel or family level
- Free-function modules that iterate a `StoryMap` or open channel files

Correct location for a new operation on channel `X` for node type `N`:
`{X}/nodes.py`, as a method on class `X{N}`.

*Why this rule exists.* We shipped `scenarios_loader.py`, `thin_slice_loader.py`,
`story_map_loader.py`, `tests_loader.py`, `story_context_loader.py`,
`drawio/tree.py`, and four `{channel}_story_map.py` adapter files. Each one
duplicated tree iteration, hid parsing rules from the domain object that
owned them, and produced name-collision bugs (`class JsonStoryMap` in two
places). Total wasted work: several sessions. The pattern is banned.

**R2. Universal, node-shape logic lives on the base node in `model/` — not
copied into channels or into loaders.**

Tree traversal (`all_stories`, `all_sub_epics`), cross-linking
(`attach_scenarios`, `attach_test_suites`), reconciliation (`translate_from`),
snapshotting all live on the base classes in `model/`. Channels **use** these
methods; they do not reimplement them.

If you find yourself writing `for epic in sm.epics: for sub in epic.sub_epics:
...` inside a channel or a helper, stop. Add or use a method on `StoryMap`
instead.

*Why this rule exists.* `story_map_loader.py` had its own recursive walks for
"stamp source on this sub-epic by name" and duplicated the tree topology in
the free functions. Every fix had to be made twice. Banned.

**R3. Discovery of files IS channel behaviour.** File discovery is not
"plumbing" — knowing that markdown scenarios live under `**/scenarios/*.md`
is markdown-domain knowledge. It goes on the Markdown node
(`MarkdownScenario.from_workspace`), not in a loader.

Every channel node that owns a file family exposes a class method
`from_workspace(root: Path)`. `Workspace.load` calls those methods; it does
not glob.

*Why this rule exists.* The globs and file conventions were once split across
five loader files. Adding a new file family meant editing loaders, adding new
loaders, and updating the top-level orchestrator. Now it is one method on
one class.

### Contract rules — how nodes behave

**R4. `translate_from` is FINAL.** Channels extend `update_self`,
`child_collections`, and `create_child_*` only. There is exactly one place
where "how to reconcile a tree" is decided, so it cannot drift.

**R5. `create_child_*` returns the channel's own concrete type.** A
`MarkdownEpic.create_child_sub_epic` must return `MarkdownSubEpic`, not
`SubEpic`. Returning a base type produces a heterogeneous tree where child
nodes silently lose their channel behaviour under `translate_from`.

**R6. `update_self` reads `source` only via the `StoryNode` interface.**
Never `isinstance`-check for a concrete channel type inside `update_self`; the
whole point of the base pattern is that the algorithm does not know or care
which channel a `source` came from.

### Surface rules — what channels expose

**R7. `{channel}StoryMap` exposes exactly `parse`, `render`, `sync` on the
public seam.** Signatures per the Uniform Callable Surface. Do not add
`append_epic`, `remove_epic`, `add_scenario`, etc. — those are mutators on the
canonical `StoryMap` in `model/`. Callers build fixtures on `StoryMap` and
pass them in.

**R8. Channel `StoryMap` constructors take no arguments beyond truly
per-instance config.** No canonical `StoryMap` in the constructor. No
external artifact string. Those go through `parse` / `render` / `sync`.

**R9. `previous` is accepted and (usually) ignored.** Every channel's
`render` accepts an optional `previous` parameter for the source of truth on
hand-written preservation. Most channels ignore it. Callers must not need to
know which channels care.

### Dependency rules — one-way imports

**R10. `model/` imports nothing from `document/`, `diagram/`, or `code/`.**
Channels import from `model/`. If a channel needs to know about another
channel, that is a strong smell — usually the operation should be pulled up
to `model/` or expressed via the canonical `StoryMap`.

**R11. `UpdateReport` is authoritative in `model/`.** Channels do not
define their own report shape. Every channel returns the same
`UpdateReport`; downstream consumers (CLI, sync tools, scanners) never fork
per channel.

### Enforcement

- **Grep-check before every merge:** `rg -l "_loader\.py|_adapter\.py"` under
  `src/stories/` must return **zero** matches.
- **Grep-check for tree walks outside `model/`:**
  `rg -n "for .* in .*\.epics" src/stories/ | rg -v "^src/stories/model/"`
  should return **zero** matches. Any walk of `.epics` or `.sub_epics` outside
  `model/` is a candidate for a new `StoryMap` method.
- **Class location check:** every `class {Channel}StoryMap(StoryMap):`
  declaration lives in a file named `nodes.py`. No exceptions.

---

## Testing Architecture

Tests are **co-located with the code they exercise** using `mamba` specs
(`*_spec.py`). The `model/` package holds `story_map_spec.py` and
`story_node_spec.py`; each channel holds its own `*_story_map_spec.py`
alongside its `nodes.py`
(`document/markdown/markdown_story_map_spec.py`,
`diagram/drawio/drawio_story_map_spec.py`,
`code/typescript/typescript_story_map_spec.py`, etc.). Channel-node tests
exercise round-trips through `parse` / `render` / `sync`; end-to-end tests
call `Workspace.load` on real fixture folders and assert against the tree.

Skill-level specs (assembly, CLI, fidelity, phase, front matter, evals) live
under `stories/tests/` and cover the `skill/` sibling package.

---

## References

- **Domain specification:** [domain-context.md](domain-context.md)
- **BDD signatures:** [bdd-context.md](bdd-context.md)
- **Document channels:** [document/architecture-context.md](document/architecture-context.md)
- **Diagram channels:** [diagram/architecture-context.md](diagram/architecture-context.md)
- **Code channels:** [code/architecture-context.md](code/architecture-context.md)
