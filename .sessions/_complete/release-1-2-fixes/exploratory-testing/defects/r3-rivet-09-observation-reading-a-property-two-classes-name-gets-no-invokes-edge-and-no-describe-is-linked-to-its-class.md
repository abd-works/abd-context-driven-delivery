# An observation that reads a property two classes both name (`cart.total`, `cart.lines`) gets no `invokes` edge, an observation whose own state only constructs is given an outer setup's call as its event, and no describe or observation is linked to the class it describes

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Map Work Into Knowledge Graph", sub-epic "Build Practice Trees From Source"; no scenario covers the links from a spec to the code it drives.
- **Module and class:** `cdd_guidance/practices/bdd/model/graph_reading.py` `ReachedMembers._members_reached` ("a read ... links only when one class owns the name") and `ObservationLinks._link_file` (takes the first enclosing setup that reaches a member, not the nearest setup); `cdd_guidance/practices/bdd/model/schema.yaml` (`description.alignsWith?: class`, `observation.demonstrates?: class`, `observation.specifies?: scenario`), which nothing in the reading makes.
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main` (`drv\run.py`, calls in `drv\g1.json`, `drv\trip-development.json`; `drv\gj.py` lists the saved graph's edges).

1. Production classes in `src/catalogue`, `src/ordering`, `src/fulfilment` (Book, Cart, CartLine, Order, Payment, Shipment; `Cart.total` and `CartLine.total`, `Cart.lines` and `Order.lines`) and the passing Mamba specs beside them (`cart_spec.py`, `order_spec.py`, `shipment_spec.py`: 3 describes, 8 states, 12 observations). The same in TypeScript with Vitest specs.
2. `graph.load_files {"folder": "C:/dev/_et/round3/rivet/work", "practices": ["bdd", "clean_engineering"], "files": ["src"]}`, `graph.save_json {}`, then read `.sessions/main/graph.json`.

## Expected
Nodes: 3 Spec, 3 Description, 8 Context, 12 Observation for each language. Nesting edges: 3 descriptions, 8 contexts, 12 observations. `invokes`: for each observation what its nearest enclosing setup calls, then what its body calls or reads (schema.yaml and bdd.md realization) - 22 edges for the Python specs. A link from `a cart` to class Cart, `an order` to Order, `a shipment` to Shipment (`alignsWith`), and from each observation to the class it proves (`demonstrates`).

## Actual
Nodes and nesting edges are all there, none doubled, none pointing at nothing (26 nodes, 23 nesting edges, 3 `owns` from the practice, per language).

`invokes`: 18 found per language against 22 expected.
- Missing, 6: `Cart.lines` (should hold no lines; should hold one line for the book), `Cart.total` (should total zero; should total the book's price; should total twice the book's price), `Order.lines` (should hold a line for each cart line). `self.cart` is built by `Cart()` in the describe's `before.each`, so the class is known from the spec. Two observations (`should hold no lines`, `should total zero`) have no edge at all, and the realization drawn from the graph says of them "// the graph holds no operation this observation calls".
- Not from the nearest setup, 2: under `that has been placed from a cart` the setup is `self.order = Order(self.cart)`; `should hold a line for each cart line` and `should await payment` are given `Cart.add`, called by the describe's outer `before.each`, as their event. A constructor is never an entry.
- The TypeScript specs give the same 18 and miss the same 6.

No `alignsWith`, `demonstrates` or `specifies` edge exists for any node, in either language; the edge kinds in the BDD part of the graph are `owns`, `descriptions`, `contexts`, `observations`, `invokes`. A describe reaches its class only through the operations its observations happen to invoke, so `a cart` under `that is new` reaches nothing.

## Tier that should catch it
Unit: `graph_bdd_model_spec.py` / the graph reading's spec with two classes that share a property name, and a state whose setup is a constructor.

## Also seen by
- Cog, round 3 second pass: the combined project: no describe is linked to its class (0 of 6). With two folders holding a class of one name the edges that are made go to the wrong class (r3-cog-01).
