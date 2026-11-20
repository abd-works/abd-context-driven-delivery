# The graph holds none of the bounded contexts, integrations, events or cross-aggregate dependencies that the bounded-context map and the domain model write; every aggregate sits under one context called "bounded context"

- **Charter:** Round 3 - DDD (bounded_context, model, tactics), checks 1, 2 and 4
- **Tester:** Bolt
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers a bounded-context map's contexts and integrations in the graph.
- **Module and class:** `cdd_guidance/practices/ddd/model/graph_reading.py` `_WorkingCopyRead` (`_bounded_contexts`, `_unmarked_context`, `_read_domain_model`, `_relate_described`, `_map_contexts`).
- **Severity:** wrong result
- **Related:** widget-22 (question, item 3) saw the one context called "bounded context"; this report adds the integrations, events and dependencies, on the round 3 build.

## Steps
Sandbox `C:\dev\_et\round3\bolt\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\bolt\drv\run.py`, calls in `drv\g3.json`, edges listed by `drv\edges.py`).

1. `.context/bounded-context-map.md` written after `templates/bounded-context.md`: contexts `## Ordering | custom` (aggregates Cart, Order), `## Catalogue | custom` (Book), `## Fulfilment | ShipFast` (Shipment); three `Integrations:` entries (Cart → Catalogue · Book · Book, Order → Fulfilment · Shipment · Shipment, Shipment → Ordering · Order · Order, each with pattern, direction, crosses, integration); `emits events:` / `consumes events:` and an `## event map` with CartCheckedOut and OrderPaid.
2. `.context/domain-model.md` written after `templates/model.md`: the same three contexts and four aggregates, each with root, repository and a member; `<< association >> bookId: BookId` on Cart, `cartId: CartId` on Order, `orderId: OrderId` on Shipment, each with its `// held by identity` note; calls `-> BookRepository.load(bookId)`, `-> OrderRepository.create(cart)`, `-> OrderRepository.load(orderId)`; `checkOut(): Order`; an `Integrations:` block under three aggregates.
3. `graph.load_files {"folder": "C:/dev/_et/round3/bolt/work", "practices": ["ddd","clean_engineering"], "files": [".context/bounded-context-map.md", ".context/domain-model.md"]}`, then `graph.inventory {}`, `graph.return_nodes {}`, `graph.save_json {}`.

## Expected
Round 3 check 4: a node for each thing in the file and an edge for each relationship. `ddd/model/schema.yaml` names them: `boundedContext` holding `aggregate`, `mappedTo: contextMapping` with `local`, `remote` and `pattern`, `domainEvent`, and `associates` between roots.

| Thing | In the files | In the graph |
|---|---|---|
| BoundedContext | 3 (Ordering, Catalogue, Fulfilment) | 1, named `bounded context`, at `.`; none of the three |
| Aggregate | 4 | 4, all four owned by `bounded context` |
| EntityRoot / Entity / ValueObject / Repository | 4 / 1 / 3 / 4 | 4 / 1 / 3 / 4 |
| ContextMapping (integration) | 3 | 0 |
| DomainEvent | 2 | 0 |
| Operation | 26 | 0 (no node of any practice) |
| context owns aggregate | Ordering 2, Catalogue 1, Fulfilment 1 | 4, from the wrong context |
| aggregate to its blocks (`root`, `owns`), repository `accesses` root | 12, 4 | 12, 4 |
| root composes member | 4 | 4 (`dependsOn`) |
| dependency between aggregates (Cart → Book, Cart → Order, Order → Cart, Shipment → Order) | 4 | 0 |
| integration between contexts | 3 | 0 |

## Actual
With the map loaded alone the whole DDD part is one node, `ddd:BoundedContext:.:bounded context`, and one edge. With the model loaded too, inventory answers `{"BoundedContext": 1, "Aggregate": 4, "EntityRoot": 4, "Repository": 4, "ValueObject": 3, "Entity": 1}`, 45 edges of kinds `root`, `owns`, `accesses`, `dependsOn`, `belongsTo`. No edge leaves an aggregate for another aggregate. The saved `graph.json` lists them all.

Why, as far as the reading shows: a bounded context is read only from a folder holding `.context/bounded-context.md`, never from the map the bounded_context fidelity writes; `_map_contexts` reads mappings only from those marker files; a described block is linked only to classes its property types name, so a root held by identity (`bookId: BookId`, as the template says to write it) names no class; the `Integrations:` blocks, the calls and the event lines of both documents are not read into the graph at all.

## Tier that should catch it
Unit (`ddd/model/graph_reading_spec.py`): no example loads a bounded-context map with integrations and events, or a domain model whose aggregates depend on one another by identity, and counts the contexts, mappings and dependencies.

## Also seen by
- Cog, round 3 second pass: the combined project, full load: nothing of `.context/bounded-context-map.md` is a node; the three contexts come from the marker files only.
- Lens, round 3 second pass: in the Files app graph view the ddd tree holds the 3 contexts, 4 aggregates and the code's building blocks only; nothing of `.context/bounded-context-map.md` or `domain-model.md` shows while code is listed. With only markdown listed (the format chip), `Aggregate Cart, Order, Book, Shipment` show at the practice's root beside `BoundedContext Fulfilment, Ordering`, under no context, and Catalogue is gone. Screenshot `C:\dev\_et\round3\lens\shots\32-format-markdown.png`.
