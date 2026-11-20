# render to `sketch` writes the plain indented tree, not the heading-and-fence notation of the BDD sketch template, so a sketch that goes to code and back loses its `Fidelity:` line, its section heading and its heading levels

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Deliver Work With Context Guidance", sub-epic "Produce Formal Artifacts"; no scenario covers a BDD sketch through a render.
- **Module and class:** `cdd_guidance/practices/bdd/model/sketch/sketch_bdd_model.py` `SketchBddModel` (its docstring: "render stays the sketch tree"; it inherits `BddModel.render`, the same text the `markdown` format gives). `cdd_guidance/practices/bdd/templates/bdd-sketch.md` section "Notation - headings carry the hierarchy".
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main` (`drv\run.py`, calls in `drv\trip-behavior.json`).

1. `_trips/behavior/sketch/bookshop-sketch.md`, in the template's notation:

        Fidelity: behavior

        ## behavior driven development:

        ### a cart

        #### that is new

        ```
        it should hold no lines
        ```

2. `render.render {"guidance": "bdd-behavior", "format": "python", "paths": ["_trips/behavior/sketch/bookshop-sketch.md"], "source": "sketch"}`, save the content as `bookshop_spec.py`.
3. `render.render {"guidance": "bdd-behavior", "format": "sketch", "paths": [that bookshop_spec.py], "source": "python"}`
4. The same through typescript and markdown.

## Expected
The sketch in the notation its template gives: "Subjects and their enabling conditions nest through markdown headings, so each folds on its own. `## behavior driven development:` is the section heading" and "Declare fidelity once at the top of the file". A file that reads as the BDD section of the session's sketch when put back.

## Actual
Step 3 returns

        a cart
          that is new
            it should hold no lines
            it should total zero

character for character what `format: markdown` gives. No `Fidelity:` line, no `## behavior driven development:` heading, no `###`/`####` headings, no fences. Names and counts are kept (11 blocks, 12 observations), and the order changes as in r3-rivet-03. Put back into a session sketch that holds other practices' sections, the result has no heading the BDD lens (`bdd:` / `behavior driven development:`) can find.

The sketch render is also returned as content, not saved, while the markdown render of the same file is saved beside the source (`bookshop.md` beside `bookshop-sketch.md`, `order_spec.md` beside `order_spec.py` in `src/ordering`).

## Tier that should catch it
Unit: `bdd_model_spec.py` reads the sketch notation; no example renders to `sketch` and compares with the template's notation.

## Also seen by
