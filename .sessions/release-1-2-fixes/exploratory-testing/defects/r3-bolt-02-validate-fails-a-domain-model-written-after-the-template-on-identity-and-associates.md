# Validate fails a domain model written after the template with nine conforms-to-schema errors: every root "has no identity relationship" and "has no associates relationship", though each card holds its identity and its association

- **Charter:** Round 3 - DDD (bounded_context, model, tactics), checks 1, 2 and 4
- **Tester:** Bolt
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers validate on a domain model document.
- **Module and class:** `cdd_guidance/practices/ddd/model/schema.yaml` (`entityRoot`: `associates: [entity]`, `identity: property`; `entity`: `associates: [entity]`) against `cdd_guidance/practices/ddd/model/graph_reading.py` `_WorkingCopyRead._described_aggregate` / `_relate_described`, which make neither edge for a class a document describes.
- **Severity:** wrong result (generate's own next step, validate, cannot pass on the file generate asks for)

## Steps
Sandbox `C:\dev\_et\round3\bolt\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\bolt\drv\run.py`, calls in `drv\m1.json`; the answer is kept in `drv\out\val-model-md.txt`).

1. `.context/domain-model.md` written after `templates/model.md` (kept as `C:\dev\_et\round3\bolt\orig\domain-model.md`): four aggregates, each root `<<Aggregate Root>> <<Entity>>` with its identity first (`+ cartId: CartId`), a composition, and on Cart, Order and Shipment a `+ << association >> bookId: BookId` with the `// held by identity` note. Book depends on no other aggregate.
2. `validate.validate {"guidance": "ddd-model", "paths": [".context/domain-model.md"]}`

## Expected
No graph violation: the cards hold what the template and the model rules ask for (`aggregate-root-identity-and-entry`, `cross-aggregate-dependency-drawn`). A root that needs no other aggregate (Book) is not an error.

## Actual
`**Total graph violations:** 9`, all under `conforms-to-schema`:

    EntityRoot `Cart`: EntityRoot 'Cart' has no associates relationship to Entity | EntityRoot, which the ddd practice schema requires.
    EntityRoot `Cart`: EntityRoot 'Cart' has no identity relationship to Property | DomainEvent, which the ddd practice schema requires.
    (the same two for Order, Book and Shipment)
    Entity `Payment`: Entity 'Payment' has no associates relationship to Entity | EntityRoot, which the ddd practice schema requires.

The graph built from the file has no `identity` and no `associates` edge at all (see r3-bolt-01), so no wording of the markdown clears them. `graph.load_files` of the same file followed by `graph.save_json` records 0 violations for it, so the two ways of checking the same file disagree.

## Tier that should catch it
Unit: `ddd/rules/ddd_rules_spec.py` or `graph_reading_spec.py` has no example that runs conforms-to-schema on `ddd/model/_examples/trip/domain-model.md`, the practice's own example of a model.

## Later in the same charter
The same nine errors come from `validate.validate {"guidance": "ddd-tactics", "paths": [...]}` on the Python the product's own render wrote from this model (`ordering/cart/cart.py` and the rest), and again on the TypeScript (`drv\out\val-tactics-py.txt`, `val-tactics-ts.txt`), so no format of the model or its code passes. Validate on `.context/domain-model.drawio` and `.context/domain-model.whiteboard` answers "No graph rule violations": nothing is read from a drawing, so it passes without being checked.
