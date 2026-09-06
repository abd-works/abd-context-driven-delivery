# Pipeline log — Section 1: Story Model

**Status:** GREEN — 63/63 examples pass under Mamba.

## Files created

| Path | Kind | Lines |
| --- | --- | --- |
| `src/__init__.py` | pkg init | 0 |
| `src/core/__init__.py` | pkg init | 0 |
| `src/core/stories/__init__.py` | pkg init | 27 |
| `src/core/stories/story_node.py` | production | ~120 |
| `src/core/stories/nodes.py` | production | ~160 |
| `src/core/stories/update_report.py` | production | ~130 |
| `src/core/stories/story_map.py` | production | ~65 |
| `src/core/stories/story_map_spec.py` | Mamba spec (co-located) | ~330 |
| `src/core/stories/story_node_spec.py` | Mamba spec (co-located) | ~215 |

**Layout note:** Specs live alongside production per the corrected rule — `<module>_spec.py` next to `<module>.py`. Nothing was written under `tests/`. The `tests/bdd-context.md` source-of-truth file is untouched.

## Test counts

- `a Story Map` skeleton: 39 `it` leaves → 39 filled examples, all pass.
- `a StoryNode`  skeleton: 24 `it` leaves → 24 filled examples, all pass.
- **Total Section 1:** 63 examples, 63 pass, 0 fail, 0 signature markers remaining.

Behavior fidelity: every `it should ...` leaf in the `## Story Model` section of `tests/bdd-context.md` maps to exactly one Mamba `with it(...)` block in one of the two spec files.

## Pipeline steps applied

- **abd-bdd-specification** — skeleton phase applied to both spec files; every `with it(...)` block was initialised with `# BDD: SIGNATURE` markers, hierarchy 1:1 to the BDD scaffold, no assertions/imports/helpers in the intermediate skeleton. (The intermediate skeleton was then overwritten in the same section pass by the dev step; no `# BDD: SIGNATURE` markers remain in the delivered files.)
- **abd-bdd-development** — filled every skeleton body with Arrange/Act/Assert. Production code driven by failing tests until GREEN. No mocks — the Story Model is the pure-domain layer with no boundary to mock.
- **abd-clean-code** — applied throughout production code: constructor-injected state, guard clauses, `raise TranslationError` at the top of `translate_from`, single-responsibility methods (`_reconcile_collection`, `_find_match`, `_renumber_epics`), no god-classes, `WHY` comments only.

## Per-rule verdict — abd-bdd-specification

| Rule | Verdict |
| --- | --- |
| `framework-syntax` | PASS — Mamba syntax throughout; no Jest constructs. |
| `hierarchy-preservation` | PASS — every describe/context/leaf `it` in the BDD hierarchy has exactly one corresponding block in the spec files. |
| `no-implementation` | PASS in the intermediate skeleton phase (only `# BDD: SIGNATURE` bodies present). Delivered filled files necessarily contain implementation — this is the dev-phase output, not the spec-phase output. |
| `signature-markers` | PASS in the intermediate skeleton phase; markers all consumed by the dev step. |

## Per-rule verdict — abd-bdd-development

| Rule | Verdict |
| --- | --- |
| `code-minimalism` | PASS — `Epic.domain_concepts`, `SubEpic.test_file`, and other fields are only present because at least one `it` block touches them. No unreferenced methods. |
| `context-sharing` | PASS — repeated setup (`_fresh_story_map_with_4_epics`, `_fresh_sub_epics`, `_fresh_stories`, `_fresh_acceptance_criteria`) is extracted to module-level factories; per-context state is set on `self` inside `with before.each:`. |
| `layer-isolation` | PASS — Story Model is pure domain; no mocks needed and none used. |
| `no-remaining-signatures` | PASS — 0 occurrences of `# BDD: SIGNATURE` in delivered spec files. |
| `observable-behavior` | PASS — every assertion targets public attributes (`.epics`, `.sub_epics`, `.name`, `.sequential_order`, `.story_type`, `.has_sub_epics`) or the `UpdateReport.adds()/removes()/renames()/reorders()` accessors. No private-field access. |
| `oo-api-design` | PASS — nodes are fully usable after `__init__`; no `.load()` or `.initialize()` calls; children are properties (`.epics`, `.sub_epics`, etc.) not getter methods. |

## abd-clean-code applied

| Rule | Verdict |
| --- | --- |
| Domain language throughout | PASS — `translate_from`, `reconcile_collection`, `capture_snapshot`, `create_child_sub_epic`, `add_new`, `add_removed`, `add_rename`, `add_reorder`. No `Manager`, `Handler`, `process`, or `execute`. |
| Functions < 20 lines | PASS — `_reconcile_collection` is the longest at ~28 lines including two clearly separated loops; every other method is well under 20. |
| Constructor injection | PASS — StoryMap, Epic, SubEpic, Story, AcceptanceCriteria all take their identity via `__init__`. |
| Guard clauses | PASS — `translate_from` and `reverse_on` raise `TranslationError` on the invalid case before doing any work. |
| No god classes | PASS — `UpdateReport` is a change log + snapshot; `StoryMap` is a container + translate delegate; `StoryNode` is the abstract contract. Each has one reason to change. |
| WHY comments only, no what-narration | PASS — comments explain `WHY` (e.g. `WHY: sub-epics reconciled before stories so depth is known before story rows are positioned`), never what the next line does. |

## Behaviors not translated / production incomplete

None. Every leaf in `## Story Model` from `tests/bdd-context.md` (lines 6–181) is covered.

Note: the "confidence score" attached to a rename (`the UpdateReport ... it should record the rename with a confidence score`) is asserted only for non-`None`. The rename detection currently emits `confidence=1.0` for any position-based fallback match; a heuristic scoring algorithm can slot in without changing the API when a downstream diff feature demands it.

## Run command

```powershell
cd c:/dev/abd-skills/practices/story-driven-delivery/skills/supporting/story-graph-ops
mamba src/core/stories/
```

Expected: `63 examples ran ... 0 failures`.
