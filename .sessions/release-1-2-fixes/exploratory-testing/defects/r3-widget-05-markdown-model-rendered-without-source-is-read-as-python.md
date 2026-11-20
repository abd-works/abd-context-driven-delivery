# A markdown class model rendered with source left out is read as Python and refused with "Python does not parse at line 11"

- **Charter:** Round 3 - Clean Engineering (modules, model, code) in every format, checks 1, 2 and 4
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/actions/render/render.py` `Render` (the source format of a path: `Format.from_extension` answers none for `.md`, so the fidelity's current format, python, is used)
- **Severity:** misleading message

## Steps
Sandbox `C:\dev\_et\round3\widget\work`, session `main`, throwaway cdd server on the build at 4d47fdf8e (`bash C:\dev\_et\round3\widget\drv\go.sh c1.json`). `src/ordering/.context/ordering-model.md` is a model written after `templates/class-model.md`, at the path the model fidelity gives markdown.

    render.render {"guidance":"clean-engineering-model","format":"drawio","paths":["src/ordering/.context/ordering-model.md"]}

The same to whiteboard, python and typescript.

## Expected
The file is read as markdown: render's description says "md is markdown" and to omit source "for a file whose extension says its format, such as .drawio, .whiteboard, or .py", and the same call at clean-engineering-modules, with a `module-context.md`, works with source left out. Or a refusal that says the source format is needed.

## Actual

    RenderFailed: the render's worker process exited with 1: cdd_guidance.practices.clean_engineering.model.base_class_model.UnreadableSource: Python does not parse at line 11: unterminated string literal (detected at line 11)

(`Python does not parse at line 1: invalid syntax` for the fulfilment model.) Nothing in the message says the markdown file was read as Python or that `"source":"markdown"` makes the call work, which it does. The `.drawio`, `.whiteboard`, `.py` and `.ts` files of the same model all render with source left out.

## Tier that should catch it
Unit, on `Render`'s choice of source format: no example renders a `.md` path at a fidelity whose default format is a programming language.
