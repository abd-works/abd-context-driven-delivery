# Rendering a BDD sketch or tree markdown to Python or TypeScript moves a state's second observation below its nested state, so the order of observations changes on the trip

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Deliver Work With Context Guidance", sub-epic "Produce Formal Artifacts"; no scenario covers the order of observations and states through a render.
- **Module and class:** `cdd_guidance/practices/bdd/model/code_spec_model.py` `CodeBddModel._children` (sorts observations and contexts together by `sequential_order`), fed by `bdd_model.py` `_SketchReader` (`add_child` numbers observations and contexts each from 1, so the second observation and the first nested state both sort after the first observation, state first).
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main` (`drv\run.py`, calls in `drv\trip-behavior.json`; `drv\cmp.py _trips/behavior 40` prints the differences).

1. Behavior spec `_trips/behavior/python/src/ordering/cart_spec.py`:

        with description("a cart"):
            ...
            with context("with a book added"):
                with it("should hold one line for the book"):
                with it("should total the book's price"):
                with context("that has the same book added again"):
                    with it("should raise the line's quantity to two"):
                    with it("should total twice the book's price"):

2. `render.render {"guidance": "bdd-behavior", "format": "markdown", "paths": ["_trips/behavior/python/src/ordering/cart_spec.py"], "source": "python"}` (order kept in the markdown).
3. `render.render {"guidance": "bdd-behavior", "format": "python", "paths": [that markdown], "source": "markdown"}`
4. The same through `format: sketch`, from the TypeScript spec, and from the sketch file written by hand in the template's notation (`_trips/behavior/sketch/bookshop-sketch.md`) to python and to typescript.

## Expected
The same tree in the same order (bdd.md `usage-order-behaviors`: "Order describes, contexts, and examples as a usage story"; `hierarchy-preservation`: "1:1 from sketch nesting to code. Nothing added, removed, or flattened").

## Actual
Step 3 gives

        with context("with a book added"):
            with it("should hold one line for the book"):
            with context("that has the same book added again"):
                with it("should raise the line's quantity to two"):
                with it("should total twice the book's price"):
            with it("should total the book's price"):

`an order` changes the same way: `should await payment` lands below the state `with a payment taken`. It happens on every trip whose source is the sketch or the markdown tree (python -> markdown -> python, python -> sketch -> python, typescript -> markdown -> typescript, typescript -> sketch -> typescript, sketch -> python, sketch -> typescript); python <-> typescript keeps the order. Names, nesting depth and counts are kept (4 states, 6 observations for a cart). The spec with one observation before its nested state (a shipment) is unchanged.

## Tier that should catch it
Unit: `code_spec_render_spec.py` and `bdd_model_spec.py` have no example with two observations followed by a nested state read from a sketch.

## Also seen by
- Lens, round 3 second pass: the Files app graph view shows the same order on specs read from code, never rendered: under `that has been created for a paid order` of `src/fulfilment/shipment_spec.py` the nested state `that has been dispatched` (line 22) comes before the observation `should list the order's books` (line 19), and the same in the TypeScript spec and in `cart` and `order` specs; `graph.return_nodes` lists the children in that order, so the tree does not follow the file.
