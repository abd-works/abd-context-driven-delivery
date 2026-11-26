# A realization sketch written in the BDD sketch template's notation is misread: an observation's call graph is dropped or given to the observation before it, and `<-` lines become nested states

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Deliver Work With Context Guidance", sub-epic "Produce Formal Artifacts"; no scenario covers a realization sketch through a render.
- **Module and class:** `cdd_guidance/practices/bdd/model/sketch/sketch_bdd_model.py` `SketchBddModel.parse` (`SketchOutline.body_for` hands the section on without its fences), then `bdd_model.py` `_SketchReader` (`_read_surface`, `_read_block`). The indented tree with fences that `format: markdown` writes is read correctly; the heading notation of `templates/bdd-sketch.md` is not.
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main` (`drv\run.py`; calls in `drv\c2.json` and `drv\trip-realization.json`).

1. `_trips/probe/arrow-sketch.md`, as the template's "Template" block spells a realization:

        Fidelity: realization

        ## behavior driven development:

        ### a cart

        #### with a book added

        ```
        -> cart.add(book)
          -> CartLine(book)
          <- CartLine
        it should hold one line for the book
        ```

        ```
        -> cart.total
          -> line.total
        it should total the price of the book
        ```

2. `render.render {"guidance": "bdd-realization", "format": "python", "paths": ["_trips/probe/arrow-sketch.md"], "source": "sketch"}`
3. The same file to `format: sketch`.
4. `_trips/realization/sketch/bookshop-sketch.md` (12 observations, call lines written without a leading arrow, as `templates/bdd.py` writes them: `cart.lines` / `  <- list[CartLine]`) to python, typescript and markdown.

## Expected
Each `it should` keeps the call graph written above it in its fence (bdd.md realization: "One graph per `it should`"; `hierarchy-preservation`: "do not add or remove observations").

## Actual
Step 2:

        with context("with a book added"):
            with it("should hold one line for the book"):
                # -> cart.total
                # -> line.total
                pass  # BDD: SIGNATURE

            with context("<- CartLine"):
                pass

            with it("should total the price of the book"):
                pass  # BDD: SIGNATURE

The first observation carries the second one's calls; its own (`cart.add(book)`, `CartLine(book)`) are gone; the second has none; `<- CartLine` is a state.

Step 4, to python: every call line is a state (`with context("cart.lines"):` holding `with context("<- list[CartLine]"): pass`), 12 observations with no call graph, 128 lines. To markdown: the fences are gone, every `->` line is dropped (`-> CartLine(book)`, `-> line.total`, `-> book.price`, `-> order.fulfil()`), and the remaining lines stand after all the observations of their state, belonging to none.

Also seen on the same trips: the tree markdown with fences keeps its call graphs through `sketch` and back, but each trip indents the call lines further (4 spaces, then 12, then 16 under the same `it`), so the text changes on every trip.

## Tier that should catch it
Unit: `bdd_model_spec.py` has no example that reads the template's own realization block (headings plus a fence holding arrows above `it should`).

## Also seen by
