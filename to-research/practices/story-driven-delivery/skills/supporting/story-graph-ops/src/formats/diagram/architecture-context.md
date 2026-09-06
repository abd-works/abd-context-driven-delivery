---
generating-skill: abd-architecture-specification
type: package-context
fidelity: specification
---

# Package: formats/diagram/

> **Base contract:** The `translateFrom` algorithm, four-slot pattern, abstract class
> specs, and rules shared by every backend are defined in the central
> [architecture-specification.md § Multi-Format Story Rendering](../architecture-context.md#multi-format-story-rendering).
> Read that section first. This file covers only what diagram backends add on top.

---

## Overview

Diagram backends (DrawIO, Miro) extend the base rendering contract with two additions:

1. **Positioning layer** — `DiagramStoryNode` computes absolute pixel coordinates from
   declarative rule methods (`placementRules`, `formattingRules`, `containmentRules`)
   and a shared `RowPositions` geometry calculator. No backend hard-codes coordinates.

2. **Structural sync diffing** — `{fmt}Synchronizer` reads an existing diagram back,
   compares the extracted node tree against the canonical graph by name and order, and
   produces an `UpdateReport` with rename/add/remove/reorder entries. The diff is
   format-agnostic; only the extraction step (XML parse vs Miro API call) is backend-specific.

Both DrawIO and Miro implement the full four-slot contract. `DiagramStoryNode` is the
shared Layer 2 mixin sitting between `StoryNode` (Layer 1) and the backend-specific
mixin (Layer 3). No format reaches into another format's layer.

---

## Why this shape

**The problem.** DrawIO and Miro write to totally different mediums (XML vs REST API), but they share two whole subsystems: positioning (an Epic sits at the same y-coordinate whether it's a mxCell or a Miro sticky) and structural diffing (a rename in DrawIO and a rename in Miro produce the same `UpdateReport`). If each backend implemented positioning and diffing itself, coordinates would drift the moment one backend was updated without the other, and diff semantics would fork.

**The three-layer inversion.** Positioning lives once in `DiagramStoryNode` (Layer 2) and is derived from a single geometry calculator, `RowPositions` — no backend hard-codes coordinates. Structural diffing lives once in `compare_node_lists`, parameterised only by a backend predicate for "is this node manually drawn?". Backend mixins (Layer 3) contribute only what is unique to their medium: how to write to an `mxCell` vs a Miro payload.

**The disciplines.** *Backends never reach sideways* — DrawIO does not know Miro exists; anything shared lives one layer up. *No hard-coded coordinates* — `RowPositions` is the only source, so both backends always align horizontally by construction. *`UpdateReport` is imported from `core/stories/`, never redefined* — otherwise each backend's report becomes subtly incompatible and downstream consumers fork.

---

## File Structure

```
formats/diagram/
+-- architecture-context.md           <- this file
+-- diagram_story_node.py             <- DiagramStoryNode mixin + DiagramEpic/SubEpic/Story
+-- row_positions.py                  <- RowPositions geometry calculator
+-- layout.py                         <- EPIC_Y, EPIC_HEIGHT, SUB_EPIC_HEIGHT, CELL_SIZE,
|                                        ROW_GAP, ACTOR_GAP, Position, Boundary, STYLE_DEFAULTS
+-- drawio/
|   +-- drawio_story_node.py          <- DrawIOStoryNode mixin + DrawIOEpic/SubEpic/Story
|   +-- drawio_element.py             <- DrawIOElement (XML/mxCell)
|   +-- drawio_story_map.py           <- render orchestration + XML extraction
|   +-- drawio_synchronizer.py        <- parse diagram back, diff, UpdateReport
+-- miro/
    +-- miro_story_node.py            <- MiroStoryNode mixin + MiroEpic/SubEpic/Story
    +-- miro_element.py               <- MiroElement (Miro v2 API payload)
    +-- miro_story_map.py             <- render orchestration + board read
    +-- miro_synchronizer.py          <- parse board back, diff, UpdateReport
```

---

## Layer 2: DiagramStoryNode

`DiagramStoryNode` is the shared intermediate mixin. It adds positioning to any node
type — Epic, SubEpic, Story — without knowing anything about XML or the Miro API.

```
DiagramStoryNode  << mixin — extends StoryNode >>
  position: Position       ← set by updateSelf
  boundary: Boundary       ← set by updateSelf

  + updateSelf(source: StoryNode): void
      rows = RowPositions(max_sub_epic_depth(source))
      self.position = Position(x_cursor, rows.sub_epic_y(self.depth))
      self.boundary = Boundary(self.position, placement.width, placement.height)

# declarative rule methods — override in each concrete node class
+ containmentRules(): ContainmentRule
+ placementRules():   PlacementRule      ← y offset, height, width strategy
+ formattingRules():  FormattingRule     ← fill colour, stroke, font, shape key
```

**`DiagramEpic` rules (example):**
```
containmentRules() → { allowed_parents: [],  contains_sub_epics: True }
placementRules()   → { y: EPIC_Y,  height: EPIC_HEIGHT,  span_children: True }
formattingRules()  → STYLE_DEFAULTS['epic']
```

**`DiagramSubEpic` rules (example):**
```
placementRules()   → { y_offset: 75,  height: SUB_EPIC_HEIGHT,  span_children: True }
```

**`RowPositions` formula:**
```
sub_epic_y(depth) = EPIC_Y + EPIC_HEIGHT + ROW_GAP + depth × (SUB_EPIC_HEIGHT + ROW_GAP)
actor_y           = deepest sub_epic_y + SUB_EPIC_HEIGHT + ACTOR_GAP
story_y           = actor_y + CELL_SIZE + ROW_GAP
```

`RowPositions` is a standalone value object — not a node. Both DrawIO and Miro use it
so stories across epics always align horizontally.

---

## Layer 3: Backend Mixins (DrawIOStoryNode / MiroStoryNode)

The backend mixin sits on top of `DiagramStoryNode`. It holds the backend element by
composition and delegates serialization to it in `updateSelf`.

```
DrawIOStoryNode  << mixin — extends DiagramStoryNode >>
  element: DrawIOElement   ← XML/mxCell; created in concrete constructor

  + updateSelf(source: StoryNode): void
      super.updateSelf(source)                    ← DiagramStoryNode sets position/boundary
      element.setPosition(self.position.x, self.position.y)
      element.setSize(self.boundary.width, self.boundary.height)
      element.applyStyleForType(self.formattingRules())

DrawIOEpic(DiagramEpic, DrawIOStoryNode)          ← concrete
  createChildSubEpic(source) → DrawIOSubEpic(source)

DrawIOSubEpic(DiagramSubEpic, DrawIOStoryNode)    ← concrete
  createChildSubEpic(source) → DrawIOSubEpic(source)
  createChildStory(source)   → DrawIOStory(source)

DrawIOStory(DiagramStory, DrawIOStoryNode)         ← concrete
```

```
MiroStoryNode  << mixin — same pattern; element: MiroElement (v2 API payload) >>
MiroEpic / MiroSubEpic / MiroStory — same structure as DrawIO counterparts
```

---

## Positioning Flow (updateSelf call chain)

```
translateFrom(source)                    ← fixed algorithm; step 2 calls updateSelf
  └─ DrawIOSubEpic.updateSelf(source)
       └─ DiagramSubEpic.updateSelf(source)    ← Layer 2: compute position/boundary
            rows = RowPositions(max_depth)
            self.position = Position(x, rows.sub_epic_y(depth))
            self.boundary = Boundary(…, SUB_EPIC_HEIGHT)
       └─ DrawIOStoryNode.updateSelf(source)   ← Layer 3: write to element
            element.setPosition(x, rows.sub_epic_y(depth))
            element.setSize(width, SUB_EPIC_HEIGHT)
            element.applyStyleForType(formattingRules())
```

**Walkthrough — `DrawIOSubEpic` at depth 1, `max_depth = 2`:**

1. `RowPositions(2).sub_epic_y(1)` = `20 + 30 + 10 + 1×(30 + 10)` = 100.
2. `DiagramSubEpic.placementRules()` → `height: SUB_EPIC_HEIGHT`.
3. `element.setPosition(x_cursor, 100)`, `element.setSize(computed_width, 30)`.
4. A `MiroSubEpic` in the same position would compute the same y=100 — both backends
   always align horizontally because both use `RowPositions`.

---

## Sync Diffing

Structural comparison is format-agnostic — it operates only on `name`,
`sequential_order`, and node type. Only the extraction step differs per backend.

```
Synchronizer.sync(artifact, canonical)
  1. extraction  → parse XML (DrawIO) or call Miro API → {fmt}StoryNode tree
  2. diff        → compare_node_lists(extracted, canonical,
                       is_manual_subtree_root={backend predicate})
  3. return UpdateReport { exact_matches, renames, new_*, removed_*, reorders }
```

**`compare_node_lists` — matching rules:**
- Exact match by name → recorded as `exact_match`.
- Name in extracted but not in canonical, paired with an unmatched canonical name → `rename`.
- Unmatched extracted → `new_*`.
- Unmatched canonical → `removed_*`.
- Position changes among siblings → `reorder`.

**Backend hook — `is_manual_subtree_root(node) → bool`:**
DrawIO passes `_drawio_is_manual_subtree_root` which returns `True` when a cell's `id`
has no `/` (manually drawn in the DrawIO canvas). Manual subtree roots are never
classified as renames — they are always treated as `new_*`. Miro passes the default
(always `False`).

**`UpdateReport` ownership:** Authoritative definition lives in `core/stories/`.
`formats/diagram/` imports from there — it does not redefine `UpdateReport`.

**Walkthrough — user renames "Login Flow" → "Sign-in Flow" in DrawIO:**

1. Extraction builds `[DrawIOEpic("Sign-in Flow")]`.
2. `compare_node_lists` against canonical `[Epic("Login Flow")]`.
3. Exact match fails. "Sign-in Flow" not in canonical names; "Login Flow" not in
   extracted names; `cell_id` contains `/` → not manual → rename candidate.
4. `report.add_rename("Sign-in Flow", "Login Flow")` recorded.
5. Caller writes rename back to `story-graph.json`.

---

## Rules — What Diagram Backends Must Not Do

- **Never hard-code pixel coordinates** — always read from `RowPositions` and `layout.py` constants.
- **Never override `translateFrom`** — only `updateSelf` and `childCollections`.
- **`DrawIOStoryNode.updateSelf` must call `super.updateSelf(source)` first** — so `DiagramStoryNode` sets `position`/`boundary` before the element is written.
- **`compare_node_lists` must receive an `is_manual_subtree_root` predicate** — never pass a hardcoded boolean.
- **`UpdateReport` is imported from `core/stories/`** — diagram backends do not define their own.

---

## Adding a New Diagram Backend

1. Create `formats/diagram/{fmt}/` with the four slots.
2. Create `{fmt}StoryNode` mixin: holds `{fmt}Element`; `updateSelf` calls `super` then writes to element.
3. Create concrete node classes (`{fmt}Epic`, `{fmt}SubEpic`, `{fmt}Story`) inheriting from both the matching `DiagramXxx` class and `{fmt}StoryNode`.
4. Implement `{fmt}Element` with `setPosition`, `setSize`, `applyStyle`, `serialize`.
5. Implement `{fmt}StoryMap.render` (calls `translateFrom`) and `parse` (extracts node tree from the backend format).
6. Implement `{fmt}Synchronizer.sync` (calls `compare_node_lists` with a backend predicate).
7. No changes to `DiagramStoryNode`, `RowPositions`, `layout.py`, `core/`, or any existing backend.
