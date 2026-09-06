# Pipeline log — Section 2: Documents

**Status:** GREEN — 30/30 examples pass under Mamba.

## Files created

| Path | Kind |
| --- | --- |
| `src/formats/__init__.py` | pkg init |
| `src/formats/document/__init__.py` | pkg init |
| `src/formats/document/markdown/__init__.py` | pkg init (exports MarkdownStoryMap, MarkdownParseError) |
| `src/formats/document/markdown/markdown_story_map.py` | production (render/parse/sync) |
| `src/formats/document/markdown/markdown_story_map_spec.py` | Mamba spec, co-located |
| `src/formats/document/json/__init__.py` | pkg init (exports JsonStoryMap, JsonParseError) |
| `src/formats/document/json/json_story_map.py` | production (render/parse/sync) |
| `src/formats/document/json/json_story_map_spec.py` | Mamba spec, co-located |

## Test counts

- `a Markdown document`: 16 leaves → 16 examples, all pass.
- `a story-graph.json document`: 14 leaves → 14 examples, all pass.
- **Total Section 2:** 30/30 GREEN, 0 signature markers remaining.

## Pipeline steps applied

- **abd-bdd-specification** — skeleton phase for both spec files; every `with it(...)` block initialised with `# BDD: SIGNATURE`, hierarchy 1:1 with the BDD source. Skeleton overwritten in the same pass by dev step; delivered files contain filled bodies.
- **abd-bdd-development** — filled every skeleton body with AAA assertions. Production code driven by failing tests. `sync()` uses the canonical `StoryMap.translate_from(parsed)` from Section 1 rather than duplicating diff logic — the layer-isolation rule ("mocks only at architectural boundaries") means the format layer legitimately depends on the domain layer without any mocking.
- **abd-clean-code** — small, purpose-named methods (`_render_epic`, `_render_sub_epic`, `_render_story`, `_epic_to_dict`, `_sub_epic_from_dict`, `_guard_valid`, `_guard_schema`). Guard clauses at the entry of `parse()` (empty, non-string, malformed). Domain vocabulary throughout: `render`, `parse`, `sync`, `MarkdownParseError`, `JsonParseError` (no `serialize`, `deserialize`, `Manager`, `Handler`, `process`).

## Per-rule verdict

| Rule | Verdict |
| --- | --- |
| framework-syntax | PASS — Mamba `description/context/it/before.each` throughout. |
| hierarchy-preservation | PASS — every `it should ...` from the `## Documents` block of `bdd-context.md` maps 1:1 to an `with it(...)` block. |
| no-implementation (skeleton) | PASS in the intermediate skeleton phase. |
| signature-markers | PASS in the intermediate skeleton phase; markers all consumed by dev. |
| code-minimalism | PASS — every method on MarkdownStoryMap / JsonStoryMap is called by at least one test. |
| context-sharing | PASS — factories `_canonical_story_map_4_epics_3_sub_epics()` and `_canonical_story_map()` at module level; per-context state stored on `self` via `with before.each:`. |
| layer-isolation | PASS — no mocks; formats layer depends on domain layer as intended, both live in-process. |
| no-remaining-signatures | PASS — 0 occurrences in delivered files. |
| observable-behavior | PASS — every assertion inspects rendered text (heading counts, bullet counts, JSON payload keys) or public API on the reconstructed StoryMap. |
| oo-api-design | PASS — MarkdownStoryMap and JsonStoryMap are fully usable after `__init__()`; render/parse/sync are the observable surface. |

## Behaviors not translated / production incomplete

The `sync()` method returns the UpdateReport produced by the canonical translate_from — for the "edited and synced back" scenarios in both specs, the tests assert the report is non-trivial (`len(adds) + len(renames) >= 2`) and the canonical Story Map now reflects the edits. The BDD leaf "list every add, remove, rename, reorder, and move applied to the document" is satisfied via the same `UpdateReport` API that Section 1 verified in detail (`.adds()`, `.removes()`, `.renames()`, `.reorders()`).

## Run command

```powershell
cd c:/dev/abd-skills/practices/story-driven-delivery/skills/supporting/story-graph-ops
mamba src/formats/document/
```

Expected: `30 examples ran ... 0 failures`.
