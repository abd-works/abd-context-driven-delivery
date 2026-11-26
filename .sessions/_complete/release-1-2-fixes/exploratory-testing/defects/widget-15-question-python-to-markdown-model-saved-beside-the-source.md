# Question: is a class model rendered from Python meant to be saved as `src/order.md` beside the source rather than under the name the fidelity writes markdown to

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/actions/render/rendered_file.py`, `RenderedFile.from_sources`
- **Severity:** answered question

## Steps
Sandbox `repo`, session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`).

    render.render {"guidance":"clean-engineering-model","format":"markdown","paths":["src/order.py"],"source":"python"}

## Expected
Not known: nothing read says which is meant.

## Actual
The answer names `src\order.md`. The model fidelity declares markdown as `{module}/.context/{module}-model.md`, and render's description says the file is saved "under the name the fidelity writes that format to"; for the story map that name is used (story-map.drawio), here the source's own name is.

## Tier that should catch it
Once the person answers, a unit example that states the answer.

## Also seen by
- Widget, round 3 (build 4d47fdf8e): unchanged. `src/ordering/ordering.py` and `src/ordering/ordering.ts` rendered to markdown are both saved as `src\ordering\ordering.md`, not `src/ordering/.context/ordering-model.md`. See also r3-widget-01 for the modules fidelity.

## Answer (2026-11-23)

A class model rendered from Python or TypeScript to markdown is saved under the name the model fidelity writes markdown to, `{module}/.context/{module}-model.md`, the module being the folder that holds the code. Built in `harness/guidance/declared_outputs.py` (`DeclaredFile.folder_holding`, `DeclaredOutputs.is_in_code_folder`, a code file in a declared code folder such as `{module}/` is one of the fidelity's files; `RenderPlacement.owns`); tested by `harness/guidance/declared_outputs_spec.py` "with code declared as a folder for each module, and a code file in a module's folder" and `cdd_guidance/actions/render/render_spec.py` "that is TypeScript code in a module's folder, named for none of its classes, rendered to markdown at the class model"; scenario "Save a class model drawn from code under the name the model fidelity writes markdown to" in `story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md`.
