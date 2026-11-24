# Question: when one render call lists two fidelities of a practice, are both meant to write the same file

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/actions/render/render.py`, `Render.render` / `_render_files`
- **Severity:** answered question

## Steps
Sandbox `repo`, session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`).

    render.render {"guidance":["stories-story-map","stories-scenarios"],"format":"drawio","paths":[".context/story-map.md"],"source":"markdown"}

## Expected
Not known: nothing read says which is meant.

## Actual
Two results, both `{"format": "drawio", "path": "...\.context\story-map.drawio"}`: the second fidelity's drawing is written over the first's. The scenarios fidelity declares no drawio output.

## Tier that should catch it
Once the person answers, a unit example that states the answer.

## Answer (2026-11-23)

Each fidelity saves under its own declared name for the format, and a fidelity that declares no file in the format is refused for it by name, before anything is saved, never written over another fidelity's file. Built in `cdd_guidance/actions/render/render.py` (`FormatNotDeclared`, `Render._refuse_undeclared`, checked for every listed fidelity before any is rendered); tested by `cdd_guidance/actions/render/render_spec.py` "that is the story map, rendered to drawio at the story map and at the scenarios at once" and "that is the story map, rendered to drawio at the story map alone"; scenario "Refuse a fidelity that declares no file in the format rendered to" in `story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md`.
