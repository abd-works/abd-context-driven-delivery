# Python code gives the graph no property node and no edge for inheritance, composition, aggregation or association; a list-typed property or return gives no edge in any format

- **Charter:** Round 3 - Clean Engineering (modules, model, code) in every format, checks 1, 2 and 4
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/practices/clean_engineering/model/graph_reading.py` `GraphReading`, with `model/python/python_class_model.py` (properties set in `__init__` are kept as the class's `held_fields` fact only)
- **Severity:** wrong result (question if properties assigned in `__init__` are meant to stay facts)

## Steps
Sandbox `C:\dev\_et\round3\widget\work`, session `main`, throwaway cdd server on the build at 4d47fdf8e (`drv\go.sh g1.json`, `g3.json`). Code under `src/` (copy in `drv\seed\code`): 3 modules, 13 classes (8 of the model and 5 exceptions), 18 properties set in `__init__` (such as `self.lines: list[CartLine] = []`, `self.order: Order = order`), 23 operations with 24 parameters, `class ExpressShipment(Shipment)`.

1. `graph.load_files {"folder":"C:/dev/_et/round3/widget/work","practices":["clean_engineering"],"files":["src"]}`
2. `graph.inventory {}`, `graph.save_json {}`

## Expected
Check 4 of the round: every module, class, property and operation is a node; every containment, inheritance, association, dependency between modules and call is an edge.

## Actual

| | Expected | Found |
|---|---|---|
| Package / Module / class / operation / parameter nodes | 1 / 3 / 13 / 23 / 24 | 1 / 3 / 13 / 23 / 24 |
| Property nodes | 18 | 0 (names are in each class's `held_fields` fact; types only where annotated) |
| owns, hasParameter edges | 39, 24 | 40, 24 |
| Inheritance edges | 1 (ExpressShipment to Shipment), 5 to built-in errors | 0 (`bases` fact only) |
| Class to class (composition, aggregation, association) | 6: Catalogue-Book, Cart-CartLine, CartLine-Book, Order-CartLine, Order-Payment, Shipment-Order | 0 |
| Module dependsOn | 2 by the imports (3 by the cards: fulfilment's card also names src/catalogue) | 2; nothing reports the card's third |
| returns | 4 | 3 (`search(): list[Book]` has none) |
| invokes | 10 | 17 (r3-widget-09) |

Two edges point at `Practice:.:clean_engineering`, which is not among the practice's nodes. The same model rendered to TypeScript with declared fields (`g3.json`, `drv\out\graph-ts-model.json`) does get 18 Property nodes, `properties`, `hasType` and class `dependsOn` edges, but only for the 3 plain-typed properties; the 3 typed `list[...]` get none, and no edge there or anywhere says ExpressShipment extends Shipment. No edge carries the kind (composition, aggregation, association) in any format.

## Tier that should catch it
Unit, `graph_reading_spec.py`: no example builds the graph of a Python class whose properties are assigned in `__init__`, of a subclass, or of a `list[...]`-typed property, and counts Property nodes and relationship edges.

## Also seen by
- Lens, round 3 second pass: in the Files app graph view a Python class shows operations only; of the 21 Property rows at a class's home all are TypeScript's, so `Order` of `src/ordering/order.py` and its TypeScript twin differ in what can be selected.
