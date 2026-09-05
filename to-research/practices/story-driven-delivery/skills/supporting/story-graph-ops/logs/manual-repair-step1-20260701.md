# Manual Repair Loop — Step 1 (Locate Original Bad Artifacts)

Source report used:

- `c:/dev/paradise-mobile/pml-domain/docs/sand-box/story-graph-cli-matrix-rigorous-20260701-011614/rigorous-results.md`

This file captures the original bad artifacts and the test gaps that allowed them.

## Failure Group A — Diagram round-trip dropped AcceptanceCriteria

- Symptom:
  - `acceptance_criteria` counts dropped to `0` after `markdown/json -> drawio/miro -> *`.
- Original bad artifacts:
  - `.../011614/raw/acceptance-criteria__acceptance-criteria_md/from_drawio_to_json.json`
  - `.../011614/raw/acceptance-criteria__acceptance-criteria_md/from_miro_to_json.json`
- Earlier tests that were insufficient:
  - `src/formats/diagram/drawio/drawio_story_map_spec.py` (validated node counts only, no AC round-trip assertions)
  - `src/formats/diagram/miro/miro_story_map_spec.py` (validated node counts only, no AC round-trip assertions)

## Failure Group B — Code round-trip dropped Stories/Scenarios

- Symptom:
  - Story counts dropped to `0` after `* -> typescript/python/java -> *`.
- Original bad artifacts:
  - `.../011614/raw/acceptance-criteria__acceptance-criteria_md/from_drawio_to_typescript.tree.json`
  - `.../011614/raw/acceptance-criteria__acceptance-criteria_md/from_drawio_to_python.tree.json`
  - `.../011614/raw/acceptance-criteria__acceptance-criteria_md/from_drawio_to_java.tree.json`
- Earlier tests that were insufficient:
  - `src/formats/code/typescript/typescript_story_map_spec.py` (render-only assertions, no parse(render()) story/AC fidelity assertion)
  - `src/formats/code/python/python_story_map_spec.py` (render-only assertions, no parse(render()) story/AC fidelity assertion)
  - `src/formats/code/java/java_story_map_spec.py` (render-only assertions, no parse(render()) story/AC fidelity assertion)

## Failure Group C — Rich markdown parsing under-modeled story/AC structure

- Symptom:
  - Prose-heavy docs parsed, but heading-depth story nodes and numbered AC lists were not fully preserved for conversion fidelity.
- Original bad artifacts:
  - `.../011614/raw/acceptance-criteria__acceptance-criteria_md/from_markdown_to_json.json`
  - `.../011614/raw/specifications__specification-by-example_md/from_markdown_to_json.json`
- Earlier tests that were insufficient:
  - `src/formats/document/markdown/markdown_story_map_spec.py` did not enforce heading-style stories and numbered AC parsing.

## BDD Rule Gaps (for `/abd-bdd-development`)

These failures passed because tests focused on conversion success and file-shape checks, but not semantic parity.

1. Add a mandatory **round-trip parity assertion** rule for any new adapter test:
   - `counts(parse(render(canonical))) == counts(canonical)` for epics/sub-epics/stories/AC.
2. Add a mandatory **special-character fixture** rule:
   - Include backticks/code spans and punctuation in at least one acceptance-criteria text fixture.
3. Add a mandatory **duplicate-name collision fixture** rule:
   - Include sibling epics/sub-epics with same normalized slug to force path-collision behavior.
4. Add a mandatory **diagram protocol fidelity** rule:
   - At least one test must assert AC survives `canonical -> drawio/miro -> parse`.

## Failure Group D — CLI allowed unsafe model->code regeneration

- Symptom:
  - CLI permitted `markdown/json/drawio/miro -> typescript/python/java`, which can overwrite user-crafted code artifacts.
- Original bad artifact pattern:
  - Any `from_<model>_to_<code>.tree.json` output produced by `story_graph_cli convert`.
- Earlier tests that were insufficient:
  - No CLI spec existed to enforce conversion policy.

