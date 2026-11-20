# Markdown scenarios written after the template fail validate with 12 graph errors: every Then "has no observes relationship to Example", and every example "should end with .examples.ts ... under an examples/ folder"

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Deliver Work With Context Guidance", Check Artifacts Against Rules; no scenario covers validate on a markdown scenarios file.
- **Module and class:** `cdd_guidance/practices/stories/model/graph_reading.py` `StoryLinks._link_step` (the `observes` edge is made only inside `StoryLinks`, which runs only when Clean Engineering's reading is in the graph); the graph rule `domain-fixture-example-files` under `cdd_guidance/practices/stories/rules/`; `model/schema.yaml` (`then: observes: example`, not optional).
- **Severity:** wrong result (a file that follows the fidelity's own template cannot pass validate)

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh g2.json`, `g3.json`). `story_tests/fill-cart/add-books/add_book_to_cart_story.test.md` and `change_cart_line_quantity_story.test.md` are markdown scenarios written after `templates/md/scenarios.md`, with their examples in tables under `### Examples`, as the template and `_examples/telco-website` write them. Both stories are on `.context/story-map.md`.

1. `validate.validate {"guidance": "stories-scenarios", "paths": ["story_tests/fill-cart/add-books/add_book_to_cart_story.test.md", "story_tests/fill-cart/add-books/change_cart_line_quantity_story.test.md"]}` (answer kept in `drv\g2.out`)
2. `graph.load_files` of the map, the model and `story_tests` with practices `["stories", "ddd"]`, then with `["stories", "ddd", "clean_engineering"]`; `graph.save_json`; count the `observes` edges (`drv\m2.py`).

## Expected
Markdown is a format the scenarios fidelity offers, so a file after its template passes the graph rules, and a rule only code can meet is not run on markdown.

## Actual
Step 1:
- `conforms-to-schema`, **Graph violations: 7**, one for each Then, And and But step, such as `add_book_to_cart_story.test.md#L52: Then 'then the ++Cart++ holds a ++Cart Line++ of 1 x Tiny Tales' has no observes relationship to Example, which the stories practice schema requires.`
- `domain-fixture-example-files`, **Graph violations: 5**, one for each example row, such as `Example 'Tiny Tales': Example file 'add_book_to_cart_story.test.md' should end with .examples.ts or .examples.js or _examples.py or examples.java under an examples/ folder.` The rule is not among the scenarios rules in `stories.md`, and a markdown table can never meet it.

Step 2: with Stories and DDD loaded the graph holds 0 `observes` edges; with Clean Engineering added (it reads one Package here and nothing else) it holds 18. So an edge from a Then to an Example of its own story file depends on whether another practice was loaded. Even then `and the Cart total is *5*` has none, because neither it nor a Given of its own scenario names an example (the Given is the Background's), so that step can never meet the schema.

With Clean Engineering loaded, 7 of the 18 edges go from steps of `change_cart_line_quantity_story.test.md` to the Example `Tiny Tales` of `add_book_to_cart_story.test.md`, another story's file, because the step text holds the words "Tiny Tales" as the book's title ("the Cart Line of Tiny Tales"), not as the example.

Smaller, in the same file: a Scenario Outline's rows written under `#### Examples` as the template shows (`| scenario | quantity | total |`, rows named one copy, two copies, three copies) become Example nodes named `example-1`, `example-2`, `example-3`; the names in the `scenario` column are not kept.

## Tier that should catch it
Unit (`graph_reading_spec.py` and the rule examples under `stories/rules`): no example validates a markdown scenarios file after the template with only Stories loaded.
