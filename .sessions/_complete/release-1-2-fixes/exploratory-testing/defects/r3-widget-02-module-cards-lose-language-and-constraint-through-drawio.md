# A module card loses its language (the definitions of its terms) and its Constraint section on a trip through drawio or whiteboard, and its purpose comes back twice

- **Charter:** Round 3 - Clean Engineering (modules, model, code) in every format, checks 1, 2 and 4
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/practices/clean_engineering/model/drawio/drawio_class_model.py` (modules view) and `model/whiteboard/whiteboard_class_model.py`; the module card writer in `model/markdown`
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\widget\work`, session `main`, throwaway cdd server on the build at 4d47fdf8e (`bash C:\dev\_et\round3\widget\drv\go.sh b1.json`, then `b2.json`, `b3.json`). `src/ordering/.context/module-context.md`, written after `templates/modules.md`:

    # src/ordering
    *Cart* is what a customer fills while browsing: it holds one *CartLine* for each book chosen and checks itself out into an *Order*.

    *Order* is the cart's lines as bought, with the *Payment* that paid for them.

    - **Purpose:** let a customer fill a cart with books and check it out into a paid order
    - **Seam (terms):** Cart, CartLine, Order, Payment
    - **Dependencies (one-way):** src/catalogue

    ## Constraint

    Make an *Order* only through `Cart.check_out`; an order built by hand has no authorised payment.

1. `render.render {"guidance":"clean-engineering-modules","format":"drawio","paths":[the three module-context.md files]}`
2. `render.render {"guidance":"clean-engineering-modules","format":"markdown","paths":["src/catalogue/.context/modules.drawio"]}`

## Expected
Check 2 of the round: the trip there and back holds what the card held. The modules fidelity asks for the language under the heading and for the Constraint (rules `language-opens-the-card`, `named-seam-and-constraint`).

## Actual
`modules.md` (kept as `C:\dev\_et\round3\widget\drv\out-modules-from-drawio.md`):

    # src/ordering

    let a customer fill a cart with books and check it out into a paid order

    - **Purpose:** let a customer fill a cart with books and check it out into a paid order
    - **Seam (terms):** Cart, CartLine, Order, Payment
    - **Dependencies (one-way):** src/catalogue

Lost for all three modules: both language paragraphs and the whole `## Constraint` section (neither is in the drawing or the whiteboard file). Changed: the purpose is written a second time where the language was; `none` became `*(none)*`. Kept: module paths, purpose, seam terms, the three dependencies. The same loss through whiteboard (`drv\out-modules-from-whiteboard.md`).

## Tier that should catch it
Unit: `drawio_module_model_spec.py` checks the drawing of modules; no example compares a card written after the template before and after markdown -> drawio -> markdown.
