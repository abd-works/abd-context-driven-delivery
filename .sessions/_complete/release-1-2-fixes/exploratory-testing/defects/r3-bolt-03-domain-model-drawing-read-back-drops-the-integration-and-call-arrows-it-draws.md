# The domain model's drawing and whiteboard show an arrow for each integration and each call to another aggregate, but reading either back drops all of them, and the model's own title

- **Charter:** Round 3 - DDD (bounded_context, model, tactics), checks 1, 2 and 4
- **Tester:** Bolt
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers a domain model's trip between its drawn formats.
- **Module and class:** `cdd_guidance/practices/ddd/model/drawio/drawio_bounded_context_map.py` `DrawIOBoundedContextMap`, `model/whiteboard/whiteboard_bounded_context_map.py` `WhiteboardBoundedContextMap`, `model/drawn/drawn_map.py` (the read side), at fidelity `model`.
- **Severity:** wrong result
- **Related:** widget-20 covers what the drawing never holds (prose, notes, invariants). This one is about what the drawing does hold and loses when read.

## Steps
Sandbox `C:\dev\_et\round3\bolt\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\bolt\drv\run.py`; the batch is `drv\t2.json`, made by `drv\mk.py ddd-model domain-model`; answers in `drv\out\t2.out`; each file of each trip is kept in `C:\dev\_et\round3\bolt\trips\`).

1. `.context/domain-model.md` as in `C:\dev\_et\round3\bolt\orig\domain-model.md`: Cart calls `-> BookRepository.load(bookId)` and `-> OrderRepository.create(cart)`, Shipment calls `-> OrderRepository.load(orderId)`, and Cart, Order and Shipment each have an `Integrations:` entry (Customer/Supplier, Open Host / Published Language, Conformist).
2. `render.render {"guidance": "ddd-model", "format": "drawio", "paths": [".context/domain-model.md"]}`. The drawing has 14 arrows; six cross aggregates: `«addBook»` Cart to BookRepository, `«checkOut»` Cart to OrderRepository, `«dispatch»` Shipment to OrderRepository, `«Customer/Supplier»` Cart to Book, `«Open Host / Published Language»` Order to Shipment, `«Conformist»` Shipment to Order.
3. Delete `domain-model.md`; `render.render {"guidance": "ddd-model", "format": "markdown", "paths": [".context/domain-model.drawio"]}`; delete the drawing; render the new markdown to `drawio` again. The same from the drawing to `whiteboard` and back, and starting from `domain-model.whiteboard` to `markdown` or `drawio` and back.

## Expected
Round 3 check 2: a trip between two formats the fidelity offers keeps what the first one holds. An arrow the drawing shows comes back as the `Integrations:` entry or the call it was drawn from.

## Actual
All four trips that start from a drawing lose the same six arrows (`6 lost, 0 gained`); the eight arrows inside an aggregate (compositions and each repository's collection) stay. The markdown read from the drawing or the whiteboard has no `Integrations:` line and no `->` call at all, so the three patterns are gone from every later file.

The title goes too: the markdown read from the drawing is headed `# Domain Model`, the one read from the whiteboard `# Classes`, where the file said `# Domain Model — Bookshop`. The whiteboard itself is titled `Bounded Context Map - Classes`, and the drawing's page is named `CleanEngineering Model`; neither shows the model's title. (The bounded-context map's title does survive both trips on this build.)

## Tier that should catch it
Unit (`ddd/model/format_round_trip_spec.py`, `drawio_bounded_context_map_spec.py`, `whiteboard_bounded_context_map_spec.py`): no example reads back a model drawing whose aggregates call or integrate with one another and counts the arrows.
