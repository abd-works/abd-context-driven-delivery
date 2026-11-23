# Question: is a class model rendered from Python meant to be saved as `src/order.md` beside the source rather than under the name the fidelity writes markdown to

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/actions/render/rendered_file.py`, `RenderedFile.from_sources`
- **Severity:** question

## Steps
Sandbox `repo`, session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`).

    render.render {"guidance":"clean-engineering-model","format":"markdown","paths":["src/order.py"],"source":"python"}

## Expected
Not known: nothing read says which is meant.

## Actual
The answer names `src\order.md`. The model fidelity declares markdown as `{module}/.context/{module}-model.md`, and render's description says the file is saved "under the name the fidelity writes that format to"; for the story map that name is used (story-map.drawio), here the source's own name is.

## Tier that should catch it
Once the person answers, a unit example that states the answer.
