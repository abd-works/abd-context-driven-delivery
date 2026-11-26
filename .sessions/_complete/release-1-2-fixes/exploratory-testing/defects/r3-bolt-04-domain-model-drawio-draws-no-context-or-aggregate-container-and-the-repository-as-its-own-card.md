# The domain model's drawio shows twelve loose class cards: no bounded context, no aggregate, and each repository as a card of its own, where the model fidelity says containers and the repository inside the root's card

- **Charter:** Round 3 - DDD (bounded_context, model, tactics), checks 1, 2 and 4
- **Tester:** Bolt
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers what the domain model's drawing shows.
- **Module and class:** `cdd_guidance/practices/ddd/model/drawio/drawio_bounded_context_map.py` `DrawIOBoundedContextMap` at fidelity `model`; `ddd/model/markdown/class_cards.py` `ClassCard.drawn_in_root`.
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\bolt\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\bolt\drv\run.py`, calls in `drv\m1.json`).

1. `.context/domain-model.md` written after `templates/model.md` (kept as `C:\dev\_et\round3\bolt\orig\domain-model.md`): `## Ordering | custom` with `### Cart` and `### Order`, `## Catalogue | custom` with `### Book`, `## Fulfilment | ShipFast` with `### Shipment`; under each aggregate `#### Root <<Aggregate Root>> <<Entity>>`, then `#### RootRepository <<Repository>>`, then a member, as the template lays them out.
2. `render.render {"guidance": "ddd-model", "format": "drawio", "paths": [".context/domain-model.md"]}`
3. Read `.context/domain-model.drawio` (kept as `orig\domain-model.drawio`).

## Expected
`ddd.md`, model fidelity: "DDD adds three things to it: bounded contexts and aggregates drawn as containers, a stereotype on each class, and the root's repository drawn in the root's card below its domain operations", and rule `root-card-carries-repository`. `templates/model.md` says of the `#### {{Root}}Repository <<Repository>>` heading: "Rendered views draw it inside the root's card".

## Actual
The drawing is one page named `CleanEngineering Model` with 12 class cards and 14 arrows, every card's parent the page itself. No cell is a container and no cell's text holds Ordering, Catalogue, Fulfilment or an aggregate's name: the context and the aggregate are kept only in each card's style, `module=Ordering | custom · Cart`, which a person looking at the drawing does not see. CartRepository, OrderRepository, BookRepository and ShipmentRepository are four cards of their own.

The whiteboard of the same file does draw a container for each bounded context and a page for each aggregate, so the two drawn formats of one fidelity disagree; it too draws each repository as its own card.

## Tier that should catch it
Unit (`ddd/model/drawio/drawio_bounded_context_map_spec.py`): no example renders a model with two contexts and checks for a container per context and aggregate, or for the repository inside the root's card when the markdown writes the repository under the template's own heading.

## Status

Fixed on release-1-2-fixes (2026-11-23). The domain model's draw.io render draws the aggregate view the model fidelity describes.

- Each bounded context is a container titled with its label (`Ordering | custom`), and each aggregate a container inside it titled with the aggregate's name, holding the root's card and the cards of the entities and values it owns (*AggregateViewDiagram* and *AggregateViewPage*, `cdd_guidance/practices/ddd/model/drawio/drawio_bounded_context_map.py`, through Clean Engineering's new `class_diagram_type`, `page_type` and `enclose` on its draw.io writers). Every aggregate is drawn on one page. The containers lie behind the cards on the page itself, so the cards keep their places on the page, the arrow router and layout scanners measure them where they stand, and a read takes nothing from a container.
- Every drawing (draw.io and whiteboard) draws each repository inside its root's card, below the root's operations, however the markdown writes it: under the template's own `#### CartRepository <<Repository>>` heading or as a `**CartRepository** «Repository»` line (`BoundedContextMap.write_classes(model, draws_repository_in_root=True)`). Code renders keep the repository a class of its own; before, a repository written as a `**Name** «Repository»` line was left out of the Python and TypeScript code altogether.
- A call to another aggregate's repository now lands on its root's card. Read back with no markdown beside it, the call reads as one to that root; written back over the markdown it was drawn from, the markdown keeps the call as written (`-> BookRepository.load(bookId)`), since the arrow still reaches the card the repository is drawn in (`ReplacedDocument.drawn_in`).
- `DomainClass.drawn_in_root` is now `written_in_root`: it says only how the markdown writes the repository, since every drawing draws it inside the root's card.
- The `prefer-short-routes` layout scanner holds only two classes of one module to its 320px gap; an arrow between two aggregates' containers is as long as the containers' places make it (`cdd_guidance/practices/clean_engineering/model/drawio/drawio.md` says so).

Specs: `cdd_guidance/practices/ddd/model/drawio/drawio_bounded_context_map_spec.py` ("that draws a domain model of three bounded contexts written after the template": a container per context and per aggregate, each card inside its aggregate's container, each repository under the template's heading inside its root's card, no two contexts, aggregates or cards over each other, every layout scanner passing, and the read back of every context, aggregate, card and repository operation); `format_round_trip_spec.py` (the three contexts' calls kept when written over the markdown, read as calls to the card the arrow points at without it); `whiteboard_bounded_context_map_spec.py`; `clean_engineering/model/drawio/scanners/drawio_scanner_spec.py` (two modules' classes far apart are not held to the gap).
