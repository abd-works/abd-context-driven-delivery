# The modules whiteboard read back adds a module "src" nobody wrote and makes every module depend on it

- **Charter:** Round 3 - Clean Engineering (modules, model, code) in every format, checks 1, 2 and 4
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/practices/clean_engineering/model/whiteboard/whiteboard_class_model.py` (reading the modules board: the box that groups nested modules is read as a module, and being inside it as a dependency)
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\widget\work`, session `main`, throwaway cdd server on the build at 4d47fdf8e (`bash C:\dev\_et\round3\widget\drv\go.sh b1.json`, then `b3.json`). Three cards: `src/catalogue` (no dependency), `src/ordering` (depends on src/catalogue), `src/fulfilment` (depends on src/ordering, src/catalogue).

1. `render.render {"guidance":"clean-engineering-modules","format":"whiteboard","paths":[the three module-context.md files]}`
2. `render.render {"guidance":"clean-engineering-modules","format":"markdown","paths":["src/catalogue/.context/modules.whiteboard"]}`
3. `render.render {"guidance":"clean-engineering-modules","format":"drawio","paths":["src/catalogue/.context/modules.whiteboard"]}`

## Expected
Three modules and three dependencies, as written, and as the drawio trip gives back.

## Actual
Step 2 (`C:\dev\_et\round3\widget\drv\out-modules-from-whiteboard.md`) holds four modules and six dependencies:

    # src

    nested modules

    # src/catalogue
    ...
    - **Dependencies (one-way):** src
    # src/ordering
    ...
    - **Dependencies (one-way):** src, src/catalogue
    # src/fulfilment
    ...
    - **Dependencies (one-way):** src, src/ordering, src/catalogue

Step 3 rewrites the drawing with the grouping box as cell `id="src"` in place of `id="nest-src"`, the id the markdown render gives a box that only groups. A module that depends on the folder holding it is also the wrong way round for `one-way-deps`.

## Tier that should catch it
Unit: `whiteboard_class_model_spec.py` has no example that reads a modules board holding nested modules back and counts modules and dependencies.
