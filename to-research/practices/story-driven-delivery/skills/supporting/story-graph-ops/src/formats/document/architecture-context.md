---
generating-skill: abd-architecture-specification
type: package-context
fidelity: specification
---

# Package: formats/document/

> **Base contract:** All behaviour shared across every backend — `translateFrom`,
> the four-slot pattern, abstract class specs, and rules — is defined in the central
> [architecture-specification.md § Base Rendering Contract](../architecture-context.md#base-rendering-contract).
> Read that section first. This file covers only what is specific to document backends.

---

## Overview

Document backends (Markdown, JSON) are the **reference implementation** of the base
rendering contract. They use only the core domain layer — no positioning, no AST, no
external API calls. If you want to understand how the four-slot contract works in
practice before adding a diagram or code backend, start here.

- **Markdown** — renders the story graph as a nested heading outline; parses headings
  back in to produce an `UpdateReport`. Element is a heading/bullet string fragment.
- **JSON** — is the canonical source of truth: `json_story_map.py` owns all
  `story-graph.json` I/O. Element is a plain dict.

---

## Why this shape

**Documents are the minimal instance of the four-slot contract.** Element is a string or a dict; there is no positioning layer, no AST layer, no external system. Anything that appears in a document backend is required by the base contract itself — which makes this the correct place to learn the pattern before tackling diagrams or code, and the correct place to reproduce the contract in isolation when debugging a broken invariant elsewhere.

**JSON owns `story-graph.json` I/O — nothing else may read or write it.** Discipline: every other module that needs the persisted graph goes through `formats/document/json/`. Without this, the graph gets deserialised in three places with three subtly different rules and drifts. With it, there is one file, one format, one owner, and every other backend consumes the parsed `StoryMap` object.

---

## File Structure

```
formats/document/
+-- architecture-context.md           <- this file
+-- markdown/
|   +-- markdown_story_node.py        <- MarkdownStoryNode mixin + MarkdownEpic/SubEpic/Story/AC
|   +-- markdown_element.py           <- heading/bullet string fragment
|   +-- markdown_story_map.py         <- parse Markdown headings ↔ StoryMap
|   +-- markdown_synchronizer.py      <- parse Markdown back, diff, UpdateReport
+-- json/
    +-- json_story_node.py            <- JsonStoryNode mixin + JsonEpic/SubEpic/Story/AC
    +-- json_element.py               <- dict / JSON object
    +-- json_story_map.py             <- JSON ↔ StoryMap (owns story-graph.json I/O)
    +-- json_synchronizer.py          <- parse JSON back, diff, UpdateReport
```

---

## What Each Backend Adds Beyond the Base Contract

| Backend | Element type | `updateSelf` extras | Owns story-graph.json I/O |
| --- | --- | --- | --- |
| **Markdown** | heading string | formats name as `# / ## / ###` by node type | no |
| **JSON** | dict | writes `sequential_order`, `domain_concepts` fields | **yes** |

Neither backend overrides `reconcileCollection`, `childCollections` structure, or the
`translateFrom` algorithm — they extend only `updateSelf`, the element slot, and the
`createChildXxx` factories.

---

## Canonical Patterns

```python
# formats/document/markdown/markdown_story_node.py
class MarkdownStoryNode:
    def __init__(self, source: StoryNode):
        self.element = MarkdownElement()
        self.translateFrom(source)

    def updateSelf(self, source: StoryNode) -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.element.write(self)               # ← required; see base contract rule

    def childCollections(self, source: StoryNode) -> list[ChildCollectionPair]:
        raise NotImplementedError              # ← concrete node class provides this


class MarkdownEpic(Epic, MarkdownStoryNode):
    def childCollections(self, source: StoryNode) -> list[ChildCollectionPair]:
        return [ChildCollectionPair(self.sub_epics, source.sub_epics)]

    def createChildSubEpic(self, source: SubEpic) -> "MarkdownSubEpic":
        return MarkdownSubEpic(source)         # ← must return concrete backend type
```

```python
# formats/document/markdown/markdown_synchronizer.py
class MarkdownSynchronizer:
    def sync(self, path: Path, canonical: StoryMap) -> UpdateReport:
        md_root = MarkdownStoryMap().parse(path)
        return canonical.translateFrom(md_root)
```

---

## Adding a New Document Backend

1. Create `formats/document/{fmt}/` with the four slots.
2. Implement `{fmt}StoryNode` mixin: `updateSelf`, `childCollections`, `createChildXxx`.
3. Implement `{fmt}Element.write(node)` and `serialize()`.
4. Implement `{fmt}StoryMap.render` and `parse`.
5. Implement `{fmt}Synchronizer.sync`.
6. No changes to `core/`, `formats/diagram/`, `formats/code/`, or `cli/`.
