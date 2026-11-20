# A BDD observation is linked to an operation of the same name in another class and folder, and to a function of a React view, while the operation of the class its spec imports gets no edge

- **Charter:** Round 3, second pass - the knowledge graph of the combined project, check 4
- **Tester:** Cog
- **Story:** epic "Map Work Into Knowledge Graph", sub-epic "Build Practice Trees From Source"; no scenario covers a spec whose class shares its name with a class in another folder.
- **Module and class:** `cdd_guidance/practices/bdd/model/graph_reading.py` `ReachedMembers.invoked` and `_code_members`: members are found by name alone through `code_index.members_named(name)`, then one is kept "per class and name" (`unique.setdefault((owner, name), member)`), which is the first in path order. The spec's imports are not read.
- **Severity:** wrong result
- **Related:** r3-rivet-09 (edges missing for reads), r3-widget-09 and r3-sparky-09 (the same joining by name in the Clean Engineering and Stories readings). This is the BDD reading, and it shows only when two folders hold a class of one name, which is how the practices lay a project out (DDD tactics in `ordering/order/`, Clean Engineering code in `src/ordering/`).

## Steps
Sandbox `C:\dev\_et\round3\cog\work` (a copy of the combined Bookshop, `C:\dev\_et\round3\combined\work`), session `main`, throwaway cdd server on the build under test: `sh C:/dev/_et/round3/cog/drv/go.sh a3.json`.

    graph.load_files {"folder": "C:/dev/_et/round3/cog/work", "practices": ["stories","ddd","ux","clean_engineering","bdd"], "files": [".context","story_tests","src","catalogue","ordering","fulfilment","bookshop","ux"]}   -> "Loaded 84 edited files."
    graph.save_json {}

Then list the BDD `invokes` edges: `python C:/dev/_et/round3/cog/drv/an.py C:/dev/_et/round3/cog/drv/all.graph.json edges invokes bdd:`.

`src/ordering/order.spec.ts` imports `{ Order, OrderCancelled } from "./order"`, and `src/ordering/order.ts` holds `Order.pay`, `Order.cancel`, `Order.isPaid`; the graph holds `clean_engineering:Operation:src/ordering/order.ts:pay:Order`.

## Expected
Each observation invokes the operation of the class its spec imports and builds: `should be paid` -> `src/ordering/order.ts:pay:Order`. Check 4 of the round asks for an edge for each relationship, with the right node at both ends.

## Actual
31 `invokes` edges from the six specs; 15 end at a member the spec never touches, and the right member has no edge:

    src/ordering/order.spec.ts:34 should be paid          -> ordering/order/order.ts:pay:Order           (Bolt's DDD class, another folder)
    src/ordering/order.spec.ts:34 should be paid          -> bookshop/src/CheckoutView.tsx:pay:_module    (a function inside a React view)
    src/ordering/order.spec.ts:46 should refuse a payment -> ordering/order/order.ts:cancel:Order, ordering/order/order.ts:pay:Order, CheckoutView.tsx:pay:_module
    src/ordering/cart.spec.ts:44 should raise the line's quantity to two -> Property ordering/cart/cart.ts:quantity:CartLine   (src/ordering/cart.ts holds quantity too)
    src/fulfilment/shipment.spec.ts:31 should report the order as fulfilled -> fulfilment/shipment/shipment.ts:dispatch:Shipment   (the spec imports ./shipment, which holds dispatch)
    src/fulfilment/shipment_spec.py:26 should report the order as fulfilled -> fulfilment/shipment/shipment.py:dispatch:Shipment   (the spec imports src.fulfilment.shipment)

No edge reaches `src/ordering/order.ts:pay`, `src/ordering/order.ts:cancel`, `src/ordering/cart.ts:quantity`, `src/fulfilment/shipment.ts:dispatch` or `src/fulfilment/shipment.py:dispatch`. Wrong edges by member: `pay` to the DDD class 6, `pay` to the view 3, `cancel` 2, `quantity` 2, `dispatch` 2.

In the Python specs `pay` and `cancel` are members Widget's `src/ordering/order.py` lacks, because the specs were written against Rivet's classes; that is the combining, not the product. The TypeScript rows and both `dispatch` rows are free of it: the imported class holds the member.

A realization drawn from the graph, the rules that follow `invokes`, and "which specs drive this operation" all name the wrong class.

## Tier that should catch it
Unit (the BDD graph reading's spec): no example holds two classes of one name in two folders with a spec that imports one of them.
