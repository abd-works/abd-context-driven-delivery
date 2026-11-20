# The modules drawing and whiteboard are saved in the first module's own .context folder, not at .context/modules.drawio where generate says, and the trip back writes a modules.md the fidelity never names

- **Charter:** Round 3 - Clean Engineering (modules, model, code) in every format, checks 1, 2 and 4
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/actions/render/rendered_file.py` `RenderedFile.from_sources` (name from `DeclaredOutputs.file_name_beside`, folder from the first source)
- **Severity:** wrong result (check 1: the file is not at the place the fidelity says)

## Steps
Sandbox `C:\dev\_et\round3\widget\work` (git), session `main`, throwaway cdd server on the build at 4d47fdf8e: `bash C:\dev\_et\round3\widget\drv\go.sh b1.json` (driver `drv\run.py`; seed files in `drv\seed`). Three cards: `src/catalogue/.context/module-context.md`, `src/ordering/...`, `src/fulfilment/...`.

1. `generate.generate {"guidance":"clean-engineering-modules"}` answers: "Save each format you write at its path ...: markdown: .../work/{module}/.context/module-context.md; drawio: .../work/.context/modules.drawio; whiteboard: .../work/.context/modules.whiteboard", and for drawio says to call the render.
2. `render.render {"guidance":"clean-engineering-modules","format":"drawio","paths":["src/catalogue/.context/module-context.md","src/ordering/.context/module-context.md","src/fulfilment/.context/module-context.md"]}`
3. The same with `"format":"whiteboard"`.
4. `render.render {"guidance":"clean-engineering-modules","format":"markdown","paths":["src/catalogue/.context/modules.drawio"]}`

## Expected
One drawing of all the project's modules at `.context/modules.drawio` and `.context/modules.whiteboard` in the project's root, as the fidelity's outputs (`clean_engineering.md`, modules) and generate's own answer say. Back to markdown: each module's `module-context.md`, the only markdown the fidelity names.

## Actual
2 answers `src\catalogue\.context\modules.drawio`; 3 answers `src\catalogue\.context\modules.whiteboard`: the drawing of all three modules sits inside the catalogue module's folder, and the root `.context` holds no drawing. With the paths given in another order the drawing moves to another module's folder. 4 answers `src\catalogue\.context\modules.md`, one file holding all three cards under a name no fidelity writes; the three `module-context.md` files are untouched (good that they are not written over, but the cards now exist twice).

## Tier that should catch it
Unit, on `RenderedFile`: the examples cover a fidelity whose drawing sits beside its one markdown file (story map); none covers a fidelity whose markdown is one file per module and whose drawing is one file for the project. Related question: widget-15.

## Also seen by
- Bolt, round 3: the same placing at `ddd-model`. Rendering the four aggregates' Python or TypeScript to markdown, drawio or whiteboard saves `ordering/cart/domain-model.md`, `.drawio` and `.whiteboard`, inside the first aggregate's folder, not `.context/domain-model.*` (r3-bolt-06, step 3).
