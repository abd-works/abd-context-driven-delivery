# Pipeline log — Section 3: Diagrams

**Status:** GREEN — 77/77 examples pass under Mamba.

## Files created

| Path | Kind |
| --- | --- |
| `src/formats/diagram/__init__.py` | pkg init (re-exports DiagramStoryMap, PlacementError, BASE_WIDTH, ROW_HEIGHT) |
| `src/formats/diagram/diagram_story_map.py` | production — positioning algorithm shared by both backends |
| `src/formats/diagram/diagram_story_map_spec.py` | Mamba spec, co-located |
| `src/formats/diagram/drawio/__init__.py` | pkg init |
| `src/formats/diagram/drawio/drawio_story_map.py` | production — Draw.io XML I/O |
| `src/formats/diagram/drawio/drawio_story_map_spec.py` | Mamba spec, co-located |
| `src/formats/diagram/miro/__init__.py` | pkg init |
| `src/formats/diagram/miro/miro_story_map.py` | production — Miro items payload I/O |
| `src/formats/diagram/miro/miro_story_map_spec.py` | Mamba spec, co-located |

## Test counts

- `a diagram Story Map`: 61 examples, all pass — covers empty diagram, 4-Epic row placement, +5th Epic X shift, -1st Epic left shift and renumber, rename in place, reorder X reshuffle, first Epic with 3 SubEpics (widths, X, Y, actor/story row shift-down on nested depth), append SubEpic, remove SubEpic, rename SubEpic in place, nested SubEpic depth-1 row and downstream row shifts, cross-Epic SubEpic move, first SubEpic with 2 Stories (row/X), append Story, rename Story in place, StoryType `system`, cross-SubEpic Story move, and all 4 placement rejections.
- `a DrawIO Story Map`: 8 examples, all pass — mxGraphModel root, 10 mxCells for 4 Epics + 3 SubEpics + 3 Stories, appended Epic surfaces as new cell + label, renamed Epic surfaces as new label, deleted SubEpic (and its Story) is absent, edited-and-synced UpdateReport is non-trivial, canonical reflects edits, malformed XML is rejected.
- `a Miro Story Map`: 8 examples, all pass — items list, 10 items for the same shape, appended Epic adds a new item with new label, renamed Epic changes label in place, deleted SubEpic and its Story vanish, sync UpdateReport is non-trivial, canonical reflects edits, invalid payload is rejected.

**Total Section 3:** 77/77 GREEN, 0 signature markers remaining.

## Pipeline steps applied

- **abd-bdd-specification** — skeleton phase applied to every spec file with `# BDD: SIGNATURE` markers, hierarchy 1:1 with the BDD source, no assertions in the intermediate skeletons.
- **abd-bdd-development** — filled every signature body. Production driven by failing tests: `DiagramStoryMap.epic_width`, `sub_epic_width`, `sub_epic_depth`, `epic_x`, `sub_epic_x`, `story_x`, `actor_row_y`, `story_row_y` all exist only because a test observes them; `place_child_under_parent` collapses all four placement-rejection tests into one guard.
- **abd-clean-code** — small, purpose-named private helpers (`_depth_from`, `_find_sub_epic_x`, `_depth_of`, `_all_sub_epics_recursive`, `_parent_sub_epic_of_story`); a single public API surface (`epic_x`, `epic_width`, `epic_row_y`, `sub_epic_row_y`, `sub_epic_x`, `sub_epic_y`, `sub_epic_width`, `sub_epic_depth`, `story_x`, `story_y`, `actor_row_y`, `story_row_y`, `place_child_under_parent`); constructor-injected `story_map`; guards raise `PlacementError` with domain vocabulary. Backends (DrawIO, Miro) hold a `DiagramStoryMap` reference and use it — they never re-implement positioning.

## Per-rule verdict

| Rule | Verdict |
| --- | --- |
| framework-syntax | PASS |
| hierarchy-preservation | PASS — every leaf in `## Diagrams` maps to at least one `with it(...)` block. |
| no-implementation (skeleton) | PASS in the intermediate skeleton phase. |
| signature-markers | PASS — 0 remain. |
| code-minimalism | PASS — no method on DiagramStoryMap, DrawIOStoryMap, or MiroStoryMap is un-invoked by a test. |
| context-sharing | PASS — `_four_epics_diagram`, `_first_epic_with_3_sub_epics_diagram`, `_diagram_with_4_epics_and_3_sub_epics_and_1_story` factories at module level; per-context `self.diagram`, `self.first_epic`, etc. via `with before.each:`. |
| layer-isolation | PASS — backends depend on DiagramStoryMap; DiagramStoryMap depends on the core Story Model. No mocks needed and none used. |
| no-remaining-signatures | PASS. |
| observable-behavior | PASS — every assertion inspects rendered X/Y/width, rendered XML text or JSON payload, or the public API of the reconstructed Story Map. |
| oo-api-design | PASS — DrawIOStoryMap and MiroStoryMap own their DiagramStoryMap; `render()` returns text, `parse()` returns a DiagramStoryMap, `sync()` returns an UpdateReport. |

## Behaviors compressed vs. the BDD source

The BDD hierarchy contains ~60 leaves under `a diagram Story Map`. Every one has at least one active `expect` in the delivered spec. In two cases the delivered spec collapses multiple leaves that share an underlying invariant into fewer `it` blocks — the tests still exercise every distinct claim, but wording sometimes covers 2 leaves in 1 block (e.g. "the first four Epics should keep their previous X positions" — one block instead of one per Epic).

The four placement-rejection scenarios all resolve through the single `place_child_under_parent` API. Each rejection has its own `with context(...): with it("should reject ..."):` block, but they share one production-code guard.

## Run command

```powershell
cd c:/dev/abd-skills/practices/story-driven-delivery/skills/supporting/story-graph-ops
mamba src/formats/diagram/
```

Expected: `77 examples ran ... 0 failures`.
