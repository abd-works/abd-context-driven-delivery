# The call graph written as comments in a Python or TypeScript spec, the way the realization fidelity writes it, is not read back: rendered to markdown or sketch every call graph is gone

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Deliver Work With Context Guidance", sub-epic "Produce Formal Artifacts"; no scenario covers a realization through a render.
- **Module and class:** `cdd_guidance/practices/bdd/model/code_spec_model.py` `CodeBddModel._realization` writes an observation's call graph as comments; `PythonBddModel._node` / `TypeScriptBddModel._node` read the same lines back as the observation's code `body`, never as `call_graph`.
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main` (`drv\run.py`, calls in `drv\trip-realization.json`; `drv\cmp.py _trips/realization` counts the lines).

1. `_trips/realization/markdown/src/ordering/order-tree.md`, the tree with one fenced call graph per `it` (4 observations, 14 call lines).
2. `render.render {"guidance": "bdd-realization", "format": "python", "paths": [that file], "source": "markdown"}` gives the realization as bdd.md and `templates/bdd.py` describe it:

        with it("should be paid"):
            # order.pay(amount)
            #   -> Payment(amount)
            #   <- Payment
            # order.is_paid
            #   <- bool
            pass  # BDD: SIGNATURE

3. `render.render {"guidance": "bdd-realization", "format": "markdown", "paths": [that Python file], "source": "python"}`
4. The same through typescript; and from the Python and TypeScript realization specs written by hand (`_trips/realization/python`, `_trips/realization/typescript`) to markdown and to sketch.

## Expected
The same call graph under each `it` (bdd.md realization: "Store graphs on observations in the BDD model ... round-tripped through `practices/bdd/model`"; rule `hierarchy-preservation`: "One graph per `it should`").

## Actual
Step 3:

        an order
          that has been placed from a cart
            it should hold a line for each cart line
            it should await payment
            with a payment taken
              it should be paid
          that has been cancelled
            it should refuse a payment

No call line is left: markdown -> python -> markdown 14 lines to 0 (cart 24 to 0, shipment 7 to 0), the same through typescript, and from a hand-written Python or TypeScript realization spec to markdown or sketch. A realization kept in spec files therefore cannot be drawn as the fidelity's markdown except from the graph.

## Tier that should catch it
Unit: `code_spec_render_spec.py` renders a call graph into comments; no example reads those comments back.

## Also seen by
