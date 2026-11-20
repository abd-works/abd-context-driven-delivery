# The graph holds one Background node for every story that has scenarios, with none of its Given steps, filed at line 1 of the story map, and validate on the map reports it as a schema error

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers a markdown Background. Commit 4d47fdf8e says "A Background its story's scenarios share is recorded in the graph, so graph rules see its steps".
- **Module and class:** `cdd_guidance/practices/stories/model/graph_reading.py` `StoriesReading._link_background_givens`, and the recording of a markdown story's background in `cdd_guidance/practices/stories/model/story_recording.py`.
- **Severity:** wrong result (nodes missing, an edge to a Background a story does not have, and a valid file fails validate)

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh g1.json`, `g2.json`, `b1.json`). `.context/story-map.md` holds 4 epics and 16 stories; `story_tests/fill-cart/add-books/add_book_to_cart_story.test.md` and `change_cart_line_quantity_story.test.md` are markdown scenarios written after `templates/md/scenarios.md`, two scenarios each, linked from the map. The first has a `### Background` with a *Given* and an *And*; the second has no Background.

1. `graph.load_files {"folder": "C:/dev/_et/round3/sparky/work", "practices": ["stories", "ddd"], "files": [".context/story-map.md", ".context/domain-model.md", "story_tests"]}`
2. `graph.save_json {}`, then read `.sessions/main/graph.json` (`drv\edges.py`).
3. `validate.validate {"guidance": "stories-story-map", "paths": [".context/story-map.md"]}`

## Expected
One Background node under Add Book To Cart, in the scenarios file at its own line, with a `given` edge to its *Given* step and that step's *And*; no Background under Change Cart Line Quantity, which has none. Given nodes: 5 (the Background's two, and one in each of three scenarios).

## Actual
- One node, `stories:Background:.context/story-map.md:background`, file `.context/story-map.md`, line 1, no children.
- Two `background` edges reach it: from Add Book To Cart and from Change Cart Line Quantity, which has no Background.
- Given nodes: 3. The Background's `*Given* the Bookshop sells Book Tiny Tales` (line 37) and `*And* the Customer has Cart empty cart` (line 38) are no nodes, and no `given` or `steps` edge leaves the Background.
- Step 3 answers **Graph violations: 1**: `.context/story-map.md#L1: Background 'background' has no given relationship to Step | Given | Background, which the stories practice schema requires.` The story map holds no Background, and the one in the scenarios file has its Given.

## Tier that should catch it
Unit (`graph_reading_spec.py`): no example reads a markdown scenarios file with a Background beside one without, and checks the Background's node, its file and its `given` edge.

## Also seen by
- Cog, round 3 second pass: the combined project: one Background node at `.context/story-map.md` line 1, two `background` edges.
- Lens, round 3 second pass: in the Files app graph view the Background shows under both stories of Add Books (2 rows for the 1 node); selecting it opens `.context/story-map.md` at line 1, and selecting the story **Add Book To Cart** or **Change Cart Line Quantity**, the sub-epic **Add Books** or the epic **Fill Cart** marks the story map from line 1 (ranges 1 to 30, 1 to 31, 1 to 31, 1 to 36) with every epic heading left folded, where **Submit Order**, which has no Background, marks lines 42 to 44. Screenshot `C:\dev\_et\round3\lens\shots\20-s-story-add-book-to-cart.png`.
