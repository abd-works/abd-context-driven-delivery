# A story test in code loaded together with the story map loses its invokes edges and its Example nodes, a shared TypeScript file loses a scenario, and without the map the same scenario is two nodes

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers a story map loaded with story tests in Python and TypeScript.
- **Module and class:** `cdd_guidance/practices/stories/stories.py` `Stories.read_files` (`_take_story_test`, which puts a story test's scenarios on the map's Story) and `cdd_guidance/practices/stories/model/graph_reading.py` `StoryLinks._link_step`, `_link_example`.
- **Severity:** wrong result (edges and nodes missing from the graph of the whole project, which is the graph a person looks at)

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh g4.json`, `g5.json`; the edges are listed by `drv\m3.py`). The map has 16 stories. Acceptance tests with real bodies:

- Python: `story_tests/fulfil-order/pack-order/pack_order_story.test.py` (Pack Order, 2 scenarios; its When is `orders.load("1001").pack()`), `fulfil-order.story.shared.py` (Mark Order Shipped, 2 scenarios), `examples/order_examples.py`, production code `src/bookshop/order.py` (`Order.pack`, `OrderRepository.create`, `load`).
- TypeScript: `story_tests/check-out/confirm-order/view-order-confirmation/view_order_confirmation_story.test.ts` (2 scenarios), `confirm-order.story.shared.ts` (Cancel Order: "Cancel a submitted order", "Keep the total of a cancelled order"), `confirm-order.story.ui.spec.ts` (one test for each of the two stories), `examples/order.examples.ts`, `src/bookshop/order.ts`.

1. `graph.load_files {"folder": "C:/dev/_et/round3/sparky/work", "practices": ["stories", "ddd", "clean_engineering"], "files": ["story_tests/fulfil-order", "src"]}`, `graph.save_json`.
2. The same with `"files": ["story_tests/check-out/confirm-order", "src"]`.
3. The same with `"files": [".context/story-map.md", ".context/domain-model.md", "story_tests", "src"]`.

## Expected
Step 3 holds what steps 1 and 2 hold for those files, under the map's own epics: each When with its `invokes` edges, each example as a node, each scenario once.

## Actual
| | Step 1 or 2 (no map) | Step 3 (with the map) |
|---|---|---|
| `invokes` edges from `pack_order_story.test.py` | 14 (create, load, pack) | 0; both Whens have `calls_reach: none`, `callees: []` |
| `invokes` edges from `view_order_confirmation_story.test.ts` | 8 | 0, `calls_reach: none` |
| `invokes` edges from `fulfil-order.story.shared.py` | 11 | 11 (kept) |
| Example nodes `paid_order`, `unpaid_order`, `submittedOrder`, `missingOrderNumber` | 5 | 0 (the 8 Example nodes are all the markdown files') |
| Scenario "Keep the total of a cancelled order" (`confirm-order.story.shared.ts`) | 1 | 0: Cancel Order holds one scenario, the ui spec's |
| Scenario "Cancel a submitted order" | 2 nodes (shared.ts and ui.spec.ts) | 1 |
| Scenario "Show the confirmation of a submitted order" | 2 nodes (story test and ui.spec.ts) | 1 |

Scenario nodes in step 3: 17, where the files hold 18 by story and name. In step 2 validate reports the doubled story as `Story 'Cancel Order' is too similar to another story on the same map node`.

In no load is there a `demonstrates` edge from an example to the class `Order` it is made of; validate at `stories-acceptance-tests` reports each as `Example 'paid_order' has no demonstrates relationship to OoadClass | Class` and `no retrievedUsing relationship to Operation | Property`.

## Tier that should catch it
Unit (`graph_reading_spec.py`, `story_test_load_spec.py`): no example loads a story map with a story test in code that has real bodies and checks the step's `invokes` edge and its examples against the load without the map.

## Also seen by
- Cog, round 3 second pass: the combined project: 17 scenarios of 18 ("Keep the total of a cancelled order" missing); `pack_order_story.test.py`, `view_order_confirmation_story.test.ts` and `confirm-order.story.shared.ts` have no `invokes` edge. A refresh of the map alone detaches all 13 scenarios in code (r3-cog-02).
