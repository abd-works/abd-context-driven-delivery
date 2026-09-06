# Pipeline log — Section 4: Code

**Status:** GREEN — 69/69 examples pass under Mamba across the abstract + three language backends.

## Files created

| Path | Kind |
| --- | --- |
| `src/formats/code/__init__.py` | pkg init (re-exports CodeStoryMap, CodeStoryMapError, slug utilities) |
| `src/formats/code/code_story_map.py` | production — abstract base: folder layout, hand-written region preservation, parse/sync |
| `src/formats/code/code_story_map_spec.py` | Mamba spec, co-located |
| `src/formats/code/typescript/__init__.py` | pkg init |
| `src/formats/code/typescript/typescript_story_map.py` | production — TypeScript story-spec backend |
| `src/formats/code/typescript/typescript_story_map_spec.py` | Mamba spec, co-located |
| `src/formats/code/python/__init__.py` | pkg init |
| `src/formats/code/python/python_story_map.py` | production — Python pytest-shaped acceptance-test backend |
| `src/formats/code/python/python_story_map_spec.py` | Mamba spec, co-located |
| `src/formats/code/java/__init__.py` | pkg init |
| `src/formats/code/java/java_story_map.py` | production — Java JUnit 5 acceptance-test backend |
| `src/formats/code/java/java_story_map_spec.py` | Mamba spec, co-located |

## Test counts

- `a code Story Map` (abstract base): 25 examples pass — folder layout, leaf-file semantics, folder creation on new SubEpic, folder removal on removed SubEpic, folder rename on renamed SubEpic, nested SubEpic → nested folders, hand-written region preservation.
- `a TypeScript story-spec Story Map`: 14 examples pass — `-stories.ts` naming, relative `story-types` imports, balanced braces, `export const … as const`, `story`/`actor`/`acceptance_criteria`/`domain_terms`/`evidence` fields, camelCased scenario properties, Step object shape, sync UpdateReport + reconstructed StoryMap.
- `a Python acceptance-test Story Map`: 13 examples pass — `.py` naming, `import pytest`, valid Python AST, per-Epic `<epic_snake>_helper.py`, `class Test<StoryPascalCase>(<Epic>Helper)`, Gherkin docstrings, `def test_<scenario_snake>` orchestration, appended AC extends class + helper, sync UpdateReport + reconstructed StoryMap.
- `a Java acceptance-test Story Map`: 17 examples pass — `<SubEpicPascalCase>Test.java` naming, `package` declaration, JUnit 5 imports, balanced braces, `@DisplayName` on outer class, `private static` helper stubs, `@Nested class <StoryPascalCase>Tests`, `@Test void <scenarioNameCamelCase>()` methods, `@DisplayName` per scenario, Given/When/Then orchestrator body, appended AC extends `@Nested` class + helpers, sync UpdateReport + reconstructed StoryMap.

**Total Section 4:** 69/69 GREEN, 0 signature markers remaining.

## Pipeline steps applied

- **abd-bdd-specification** — skeleton phase applied to every spec file with `# BDD: SIGNATURE` markers, hierarchy mirroring the BDD source, no assertions/imports/helpers in the intermediate skeleton. Skeletons then overwritten by the dev step in the same pass; delivered files hold filled bodies.
- **abd-bdd-development** — filled every signature. Production driven by failing tests: `CodeStoryMap._preserve_hand_written`, `_render_epic_helper`, `_render_sub_epic`, and language-specific `_render_leaf_file` implementations all exist only because a test observes them. `parse()` was tightened iteratively to recognise Epic-level helper files at depth 3 (a real bug surfaced by the sync tests). Signature markers all consumed.
- **abd-clean-code** — small, purpose-named private helpers (`_epic_helper_path`, `_render_epic_helper`, `_render_leaf_file`, `_render_story_class`, `_render_sub_epic`, `_walk_leaf_sub_epics`, `_preserve_hand_written`, `_is_leaf_path`, slug utilities `to_kebab`, `to_snake`, `to_upper_snake`, `to_pascal`, `to_camel`). Public API surface is `render`/`parse`/`sync`. Constructor-injected `story_map`. Guards raise `CodeStoryMapError` with domain vocabulary at the `parse()` boundary. Language backends override only what varies; layout, hand-written preservation, and parse live once in the base.

## Per-rule verdict

| Rule | Verdict |
| --- | --- |
| framework-syntax | PASS |
| hierarchy-preservation | PASS — every `it should …` from `## Code` in `tests/bdd-context.md` maps to at least one `with it(...)` block. |
| no-implementation (skeleton) | PASS in the intermediate skeleton phase. |
| signature-markers | PASS — 0 remain. |
| code-minimalism | PASS — every method on CodeStoryMap, TypeScriptStoryMap, PythonStoryMap, JavaStoryMap is called by at least one test. |
| context-sharing | PASS — `_story_map_with_stories()` module-level factories at the top of each spec; per-context state via `with before.each:`. |
| layer-isolation | PASS — backends depend on CodeStoryMap and on the core Story Model; no mocks used. |
| no-remaining-signatures | PASS. |
| observable-behavior | PASS — every assertion inspects rendered file contents (leaf-file text, folder tree, comment markers, Java `@Test`/`@Nested` annotations, TS `export const … as const`, Python `class Test…`) or the public API of the reconstructed Story Map. |
| oo-api-design | PASS — every backend is fully usable after `__init__`; `render()` returns `{path: content}`, `parse()` returns a StoryMap, `sync()` returns an UpdateReport. |

## Behaviors compressed vs. the BDD source

The `## Code` block groups its scenarios "for the TypeScript / Python / Java backend". The delivered specs collapse the abstract-shared behaviors ("every leaf file lives in the right folder", "renaming a SubEpic renames its folder", "removing a SubEpic removes its folder", "hand-written regions survive re-render") into a single `code_story_map_spec.py` exercising a minimal representative backend. The three language specs then verify only the parts that legitimately differ per language: file extension, import statements, block structure, decorators/annotations, helper location, comment style, scenario key case (camelCase for TS/Java, snake_case for Python), and JUnit 5 vs pytest conventions. This mirrors the abstract-then-concrete pattern the abd-bdd-development skill asks for.

The "reflect every edit" sync test in each language spec asserts on the SubEpic layer (not the Epic layer). WHY: TypeScript and Java only produce files under leaf SubEpics — empty Epics have no file representation, so an Epic-level add is not observable through parse/sync for these backends. This is a genuine property of the code layer, not an under-tested one; the exhaustive Epic-level translate_from coverage lives in `src/core/stories/story_node_spec.py` and `src/core/stories/story_map_spec.py`.

## Run command

```powershell
cd c:/dev/abd-skills/practices/story-driven-delivery/skills/supporting/story-graph-ops
mamba src/formats/code/
```

Expected: `69 examples ran ... 0 failures`.
