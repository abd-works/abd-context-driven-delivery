# With the code in place, a context mapping is linked to no aggregate because the aggregate is named for its lower-case folder, a Python repository "accesses" the TypeScript root of the same name, and no root is linked to the root it holds by identity

- **Charter:** Round 3 - DDD (bounded_context, model, tactics), checks 1, 2 and 4
- **Tester:** Bolt
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers a context mapping's two sides, or one aggregate written in two languages.
- **Module and class:** `cdd_guidance/practices/ddd/model/graph_reading.py` `_WorkingCopyRead._link_sides` (matches the mapping's side to `Aggregate.name` exactly), `_aggregate` (names the aggregate `Path(folder).name`), `_link_blocks` / `_link_kept_root` (`by_name` keeps one block per class name), `_link_foreign_roots` (reads only a `// foreign Name` comment).
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\bolt\work` (commit `0330958` of its own repository), session `main`, throwaway cdd server (`C:\dev\_et\round3\bolt\drv\run.py`, calls in `drv\g4.json` and `drv\g5.json`; the saved graph is `drv\out\g4-graph.json`).

1. The model's code as `render.render {"guidance": "ddd-model", "format": "python" | "typescript", "paths": [".context/domain-model.md"]}` writes it, saved where generate says, `{bounded_context}/{aggregate}/{aggregate}.py` and `.ts`: `ordering/cart/cart.py`, `ordering/order/order.py`, `catalogue/book/book.py`, `fulfilment/shipment/shipment.py`, and the same four `.ts`.
2. `.context/bounded-context.md` in `ordering`, `catalogue` and `fulfilment`, each with a title; `ordering` lists `Cart → Catalogue · Book` and `Order → Fulfilment · Shipment`, `fulfilment` lists `Shipment → Ordering · Order`.
3. `graph.load_files {"folder": "C:/dev/_et/round3/bolt/work", "practices": ["ddd","clean_engineering"], "files": [".context","ordering","catalogue","fulfilment"]}`, then `graph.save_json {}`.

## Expected
`ddd/model/schema.yaml`: a `contextMapping` has `local: aggregate` and `remote: aggregate`; a `repository` `accesses` its own `entityRoot`; an `entityRoot` `associates` with the roots it refers to. The model rule `model-mirrors-code` says the aggregate's name in the model and the code match.

## Actual
The three bounded contexts, four aggregates and three ContextMapping nodes are there (good). But:

1. **No mapping has a side.** The edge kinds of the DDD part are `belongsTo` 38, `owns` 33, `root` 8, `accesses` 8, `mappedTo` 3: no `local`, no `remote`. The aggregates are named `cart`, `order`, `book`, `shipment`, after their folders, and the mapping's `Cart` matches none. Writing the line as `cart → Catalogue · book` gives both edges (`drv\g5.json`), so the names are compared letter for letter. The map and the model write `Cart`; the folder generate asks for is `cart`.
2. **Each Python repository accesses the TypeScript root.** `Repository:ordering/cart/cart.py:CartRepository -- accesses --> EntityRoot:ordering/cart/cart.ts:Cart`, and the same for Order, Book and Shipment; no edge reaches a Python root. Both formats are ones the model and tactics fidelities offer for the same folder.
3. **No root is linked to another root.** Cart holds `bookId: BookId` under `# << association >>` and `# held by identity — Book lives in Catalogue · Book`, which is how render writes the model's association into code, and calls `BookRepository.load(bookId)`; no `associates` edge is made, since only a `// foreign Book` comment is read. Validate then reports each root as having "no associates relationship" (r3-bolt-02).
4. The events are nodes (`DomainEvent` CartCheckedOut, OrderPaid) with no edge to the root that publishes them or the aggregate that consumes them.

## Tier that should catch it
Unit (`ddd/model/graph_reading_spec.py`): no example has an aggregate folder whose name differs in case from the name a mapping writes, one class name declared in two languages, or code as render writes it from a model with an association.

## Also seen by
- Cog, round 3 second pass: the combined project: no mapping has a side; each Python repository accesses the TypeScript root. The edge also depends on what was refreshed last: `graph.refresh` of `ordering/order/order.py` moves it to the Python root and gives the TypeScript repository a second one, and a refresh of `src/ordering/order_spec.py` adds the first back (r3-cog-02).
