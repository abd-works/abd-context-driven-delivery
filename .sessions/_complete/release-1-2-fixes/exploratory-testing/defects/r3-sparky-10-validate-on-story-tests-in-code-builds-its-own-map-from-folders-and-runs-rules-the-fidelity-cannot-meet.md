# Validate on story tests in code ignores the story map beside them: it reports child counts of a map built from the folders, calls a browser story test a unit test, and asks a scenarios-fidelity When to call code

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Deliver Work With Context Guidance", Check Artifacts Against Rules; no scenario covers validate on a story test in code whose story is on a markdown map.
- **Module and class:** `cdd_guidance/practices/stories/stories.py` `Stories.read_files` and `_story_map_of_code` ("With no story map among files, story tests in code under a project's story_tests are the map themselves"); the graph rules `child-count-fits-layer`, `code-steps-invoke-code` and TDD's `unit-tier-fakes-every-boundary`.
- **Severity:** wrong result (files written where and how the fidelity says cannot pass validate; the agent is told to restructure a map that is right)

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh v1.json`, answers in `drv\v1.out`). `.context/story-map.md` holds Check Out with sub-epics Place Order (2 stories) and Confirm Order (2 stories), and the flat epics Browse Books and Fulfil Order (4 stories each). The story tests sit at the fidelity's paths, each headed with `# Map: ../../../../.context/story-map.md#...`.

1. `validate.validate {"guidance": "stories-scenarios", "paths": ["story_tests/check-out/place-order"]}` (two Python scenarios files after `templates/py/scenarios.py`, step bodies `pass`)
2. `validate.validate {"guidance": "stories-scenarios", "paths": ["story_tests/browse-books/search-books/search_books_story.test.ts"]}`
3. `validate.validate {"guidance": "stories-acceptance-tests", "paths": ["story_tests/check-out/confirm-order", "src/bookshop/order.ts"]}` (the five TypeScript files the fidelity lists, among them `confirm-order.story.ui.spec.ts`, which imports `@playwright/test`)
4. `validate.validate {"guidance": "stories-acceptance-tests", "paths": ["story_tests/fulfil-order", "src/bookshop/order.py"]}`

## Expected
The story's place comes from the map the file names, so no child-count finding; a `*.story.ui.spec.ts`, which the fidelity lists as its browser tier, is not judged as a unit test; a When at the scenarios fidelity, whose template body is `pass`, is not asked to call code.

## Actual
1. `child-count-fits-layer`: `Epic 'Check Out': 1 children (target 2-6)` and `SubEpic 'Place Order': 1 children (target 2-6)`, though both stories of Place Order were in the path. `code-steps-invoke-code`, 3 errors: `When '...' calls nothing: call the domain operation it tests in the step.` `conforms-to-schema`, 4 errors: Then `has no observes relationship to Example`.
2. `Epic 'Browse Books': 1 children (target 2-6)` and `SubEpic 'Browse Books': 1 stories (target 2-9)`: the flat epic is read as an epic holding a sub-epic of its own name. 2 `calls nothing` errors.
3. `SubEpic 'Check Out': 1 stories (target 2-9)` (the sub-epic is Confirm Order, and it has 2 stories). `Story 'View Order Confirmation': confirm-order.story.ui.spec.ts:2: a unit test imports @playwright/test; put a fake at that boundary and cover the real one in a heavy test.` and the same for Cancel Order. `Story 'Cancel Order' is too similar to another story on the same map node` (the story is read once from the shared file and once from the ui spec).
4. `SubEpic 'Fulfil Order': 1 stories (target 2-9)`.

With `.context/story-map.md` added to a load of the same files, the graph has the map's own tree: 4 epics, 4 sub-epics, 16 stories, none doubled.

## Tier that should catch it
Unit (`story_test_load_spec.py` and the rule examples): no example validates a story test in code that names its map on a `# Map:` line while the map is not among the paths.
