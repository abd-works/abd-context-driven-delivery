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
