---
generating-skill: abd-architecture-specification
type: package-context
fidelity: specification
---

# Package: core/stories/

> **Base contract:** `translateFrom`, the four-slot pattern, and the abstract `StoryNode`
> spec are defined in the central
> [architecture-specification.md § Multi-Format Story Rendering](../architecture-context.md#multi-format-story-rendering).
> This file describes the pure domain types that implement that contract — no format
> dependencies, no infrastructure.

---

## Overview

`core/stories/` is the pure domain layer. It contains:

- **`StoryNode`** — the abstract base for every node in the system; owns `translateFrom`
  and `reconcileCollection`; declares the abstract hooks every backend must override.
- **`Epic`, `SubEpic`, `Story`, `AcceptanceCriteria`** — concrete domain node types;
  implement `updateSelf`, `childCollections`, and `createChildXxx` for the domain layer
  with no format-specific code.
- **`StoryMap`** — the root container; holds a list of `Epic` nodes and delegates
  rendering to them.
- **`UpdateReport`, `NodeSnapshot`, `ChildCollectionPair`** — the result and supporting
  types produced by `translateFrom`.

Nothing in this package imports from `formats/`. All format backends import from here.

---

## Why this shape

**The problem.** If the domain types depended on any format (say, `Epic` imported anything from `formats/diagram/`), the dependency graph would immediately become a mesh — every backend would transitively pull every other backend, and adding a new format would ripple into the core. The whole four-slot pattern presupposes that formats can be added additively; that only works if the core has zero knowledge of formats.

**The inversion — one-way dependency.** `core/stories/` imports from nothing in this project. Every backend imports from here. `translateFrom` and `reconcileCollection` are defined here as **FINAL** (never overridden) so that no backend can subvert the tree walk; every backend must extend `updateSelf`, `childCollections`, and `createChildXxx`.

**The disciplines.** *No format imports* — the day this rule breaks, the mesh starts forming. *`UpdateReport` is authoritative here* — every format returns the same report shape, so downstream consumers (CLI, sync tools) don't fork per backend. *`AcceptanceCriteria` is a leaf, always* — no backend adds children to it; leaf-ness is a domain invariant, not a per-backend choice.

---

## File Structure

```
core/stories/
+-- architecture-context.md    <- this file
+-- story_node.py              <- StoryNode (translateFrom, reconcileCollection)
+-- nodes.py                   <- Epic, SubEpic, Story, AcceptanceCriteria
+-- update_report.py           <- UpdateReport, NodeSnapshot, ChildCollectionPair
+-- story_map.py               <- StoryMap
```

---

## Class Specification

```
## StoryNode  << abstract >>
Properties:
  name:             str
  sequential_order: int

Methods — FINAL (never overridden):
  + translateFrom(source: StoryNode): UpdateReport
  - reconcileCollection(pair: ChildCollectionPair, report: UpdateReport): void

Methods — abstract (every backend mixin must implement):
  + updateSelf(source: StoryNode): void
  + childCollections(source: StoryNode): List[ChildCollectionPair]
  + createChildSubEpic(source: SubEpic): SubEpic
  + createChildStory(source: Story): Story
  + createChildAC(source: AcceptanceCriteria): AcceptanceCriteria


## Epic(StoryNode)
Properties:
  domain_concepts:  List[str]
  sub_epics:        List[SubEpic]

+ updateSelf(source: StoryNode): void
    self.name = source.name
    self.sequential_order = source.sequential_order
    self.domain_concepts = source.domain_concepts

+ childCollections(source: StoryNode): List[ChildCollectionPair]
    return [ChildCollectionPair(self.sub_epics, source.sub_epics,
                                lambda s: self.createChildSubEpic(s))]

+ createChildSubEpic(source: SubEpic): SubEpic
    return SubEpic(source)            ← overridden by format backends to return concrete type


## SubEpic(StoryNode)
Properties:
  stories: List[Story]
  sub_epics: List[SubEpic]           ← nested sub-epics supported

+ childCollections(source: StoryNode): List[ChildCollectionPair]
    return [ChildCollectionPair(self.sub_epics, source.sub_epics, ...),
            ChildCollectionPair(self.stories, source.stories, ...)]

+ createChildSubEpic(source: SubEpic): SubEpic   ← overridden by backends
+ createChildStory(source: Story): Story          ← overridden by backends


## Story(StoryNode)
Properties:
  acceptance_criteria: List[AcceptanceCriteria]

+ childCollections(source: StoryNode): List[ChildCollectionPair]
    return [ChildCollectionPair(self.acceptance_criteria, source.acceptance_criteria, ...)]

+ createChildAC(source: AcceptanceCriteria): AcceptanceCriteria  ← overridden by backends


## AcceptanceCriteria(StoryNode)
Properties:
  text: str

+ updateSelf(source: StoryNode): void
    self.name = source.name
    self.text = source.text

+ childCollections(source: StoryNode): List[ChildCollectionPair]
    return []           ← leaf node; no children


## StoryMap
Properties:
  epics: List[Epic]

+ translateFrom(source: StoryMap): UpdateReport
    reconcile self.epics against source.epics via Epic.translateFrom


## UpdateReport
Properties:
  changes:  List[Change]      ← add / rename / remove / reorder entries
  snapshot: NodeSnapshot      ← before-state for reversal

+ reverseOn(node: StoryNode): void   ← restores node to snapshot state


## NodeSnapshot
  Captures the recursive before-state of a node tree at the moment translateFrom begins.
  Used by UpdateReport.reverseOn to restore prior state.


## ChildCollectionPair
  self_children:   List[StoryNode]
  source_children: List[StoryNode]
  create_child:    Callable[[StoryNode], StoryNode]   ← factory (createChildXxx)
```

---

## Rules

- **No format imports** — `core/stories/` must never import from `formats/` or `cli/`.
- **Domain `createChildXxx` returns the domain type** — format backends override to return their concrete type; the domain default is the fallback.
- **`UpdateReport` is authoritative here** — all format backends import `UpdateReport` and `NodeSnapshot` from this package; they do not define their own.
- **`AcceptanceCriteria` is a leaf** — `childCollections` always returns an empty list; no backend adds children to it.
