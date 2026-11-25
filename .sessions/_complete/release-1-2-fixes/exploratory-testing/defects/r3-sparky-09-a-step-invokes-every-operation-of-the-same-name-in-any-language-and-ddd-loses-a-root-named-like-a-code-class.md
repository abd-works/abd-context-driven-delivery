# A Python step gets invokes edges to the TypeScript operations of the same name (and a TypeScript step to the Python ones), and the DDD model's root Order leaves the graph when the code has a class Order

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers one project with Python and TypeScript code of the same names.
- **Module and class:** `cdd_guidance/practices/stories/model/graph_reading.py` `StoryLinks._link_step` (`self.clean.code_index.members_named(name)` matches by name alone); for the second part the DDD reading under `cdd_guidance/practices/ddd/model/`.
- **Severity:** wrong result (edges that point at code the step does not run; a node missing)

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh g5.json`). `src/bookshop/order.py` and `src/bookshop/order.ts` each hold `Order` and `OrderRepository` with `create` and `load`. `story_tests/fulfil-order/pack-order/pack_order_story.test.py` imports `from src.bookshop.order import OrderNotPaid, OrderRepository` and calls `orders.create(...)`, `orders.load("1001").pack()`. `.context/domain-model.md` holds the roots Book, Cart, Order and Shipment.

1. `graph.load_files {"folder": "C:/dev/_et/round3/sparky/work", "practices": ["stories", "ddd", "clean_engineering"], "files": ["story_tests/fulfil-order", "src"]}`, `graph.save_json`, list the `invokes` edges.
2. `graph.load_files {"folder": "C:/dev/_et/round3/sparky/work", "practices": ["ddd"], "files": [".context/domain-model.md", "src/bookshop/order.py"]}`, `graph.inventory`; then the same with `"practices": ["ddd", "clean_engineering"]`.

## Expected
1. A Python step's `invokes` edges reach the Python operations its file imports.
2. The DDD model's four roots are four nodes whichever other practice is loaded.

## Actual
1. Each Python step has an edge to both languages, such as `pack_order_story.test.py:17 -> src/bookshop/order.py:create:OrderRepository` and `pack_order_story.test.py:17 -> src/bookshop/order.ts:create:OrderRepository`; `pack_order_story.test.py:20` reaches `order.py:load`, `order.py:pack` and `order.ts:load`. 25 `invokes` edges, 10 of them to `order.ts`. The TypeScript story tests get the mirror: `view_order_confirmation_story.test.ts:25 -> src/bookshop/order.py:load:OrderRepository`.
2. With `["ddd"]`: `EntityRoot: 4`. With `["ddd", "clean_engineering"]`: `EntityRoot: 3` (Book, Cart, Shipment); the Aggregate Order is still there, its root Order is not. The load answers "Loaded 2 edited files." both times.

## Tier that should catch it
Unit (`graph_reading_spec.py` for the step's edges; the DDD reading's spec for the root): no example holds one operation name in two languages, or a model root with a code class of its name.

## Also seen by
- Cog, round 3 second pass: the combined project: all 57 Stories `invokes` edges leave `fulfil-order.story.shared.py`; 6 are calls the steps make (`src/bookshop/order.py`), 51 go to `create`, `load` and `pack` of BookRepository, CartRepository, ShipmentRepository, OrderFactory and Shipment in both languages. Part 2: with the DDD code loaded none of the 16 nodes of `.context/domain-model.md` is in the graph (r3-cog-05).
