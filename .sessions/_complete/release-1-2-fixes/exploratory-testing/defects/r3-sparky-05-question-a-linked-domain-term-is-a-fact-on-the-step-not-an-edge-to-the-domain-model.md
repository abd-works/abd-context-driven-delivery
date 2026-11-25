# Question: a domain term a step links to domain-model.md is kept as a fact on the step, with no edge to the DDD model's node, and an example has no demonstrates edge to a DDD class

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers a step's link to the domain model. The round 3 charter's check 4 expects an edge for each relationship "inside the practice and across practices".
- **Module and class:** `cdd_guidance/practices/stories/model/graph_reading.py` `StoryLinks` (links Stories only to Clean Engineering's `OoadClass`, `Property` and operations).
- **Severity:** question

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh g3.json`). The two markdown scenarios files under `story_tests/fill-cart/add-books/` link every domain term as `domain-terms-link-to-model` asks, such as `++[Book](../../../.context/domain-model.md#book-aggregate-root-entity)++`; `.context/domain-model.md` holds Book, Cart, CartLine, Order, Payment and Shipment.

1. `graph.load_files {"folder": "C:/dev/_et/round3/sparky/work", "practices": ["stories", "ddd", "clean_engineering"], "files": [".context/story-map.md", ".context/domain-model.md", "story_tests"]}`
2. `graph.save_json {}`; list the edges of `.sessions/main/graph.json` by kind (`drv\edges.py`).

## Expected
An edge from each step to the model node its link names (the 11 scenario steps and 2 Background steps hold 19 such links to Book, Cart and CartLine), so a person can follow a step to its definition in the graph, and a renamed class shows which steps name it.

## Actual
Stories edges: decomposedInto 24, observes 18, steps 11, examples 10, scenarios 4, ands 3, background 2. None has a DDD node at either end. The step keeps `"linked_terms": ["Book", "Cart"]` in its facts, and its name keeps the term without the link (`when the Customer adds ++Book++ ++Tiny Tales++ to the ++Cart++`). `ddd:EntityRoot:.context/domain-model.md:Book` has no edge from Stories and is reported by DDD's `no-orphaned-objects`. The Example `Tiny Tales`, a Book, has no `demonstrates` edge: `StoryLinks._link_example` makes one only to a Clean Engineering class named in code.

Also not in the graph, asked here once: a story's actor (Customer, Shop Clerk, Payment Provider) and its kind (`(S:system)`) are neither nodes nor facts on the Story node, and the sentence written under an epic or a story on the map is not held.

Is the link from a step to the DDD model meant to be an edge?

## Tier that should catch it
Unit (`graph_reading_spec.py`), once the answer is yes.

## Also seen by
- Cog, round 3 second pass: the combined project: 43 links from steps to `domain-model.md`, no edge; with the code loaded the model's nodes are not in the graph at all (r3-cog-05).
