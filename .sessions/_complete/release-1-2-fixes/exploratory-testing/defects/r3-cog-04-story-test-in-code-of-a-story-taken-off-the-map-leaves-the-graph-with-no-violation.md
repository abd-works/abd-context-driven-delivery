# A Python story test whose story was taken off the story map leaves the graph on the next load, scenarios and steps, with no violation; after a refresh of the map alone its scenarios stay, held by no story

- **Charter:** Round 3, second pass - the knowledge graph of the combined project, check 4
- **Tester:** Cog
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers a story test in code whose story the map lacks. The rule `scenarios-name-a-story-on-the-map` says: "A scenarios file that names a story the map does not hold is read with its scenarios under no epic and reported, because scenarios the map cannot place are otherwise left out of every check without a word."
- **Module and class:** `cdd_guidance/practices/stories/stories.py` `Stories.read_files` (`_take_story_test`). The fix of widget-21 keeps such a story for markdown scenarios files (`MarkdownStoryModel._attach_markdown`, `StoryModel.unplaced_stories`); a story test in code does not go that way.
- **Severity:** wrong result
- **Related:** widget-21 (markdown, fixed), r3-cog-02 (what a refresh of the map does).

## Steps
Sandbox `C:\dev\_et\round3\cog\work` (a copy of the combined Bookshop), throwaway cdd server: `sh C:/dev/_et/round3/cog/drv/go.sh r1.json`.

1. `graph.load_files {"folder": "C:/dev/_et/round3/cog/work", "practices": ["stories","ddd","ux","clean_engineering","bdd"], "files": [".context","story_tests","src","catalogue","ordering","fulfilment","bookshop","ux"]}`: Story Submit Order holds two scenarios from `story_tests/check-out/place-order/submit-order/submit_order_story.test.py`.
2. In `.context/story-map.md` delete the line `### (S) Customer --> Submit Order` and the sentence under it. The story test stays.
3. `graph.refresh {"paths": [".context/story-map.md"]}`, `graph.save_json {}` (`r1b.graph.json`).
4. The same `graph.load_files` again, `graph.save_json {}` (`r1f.graph.json`).

## Expected
After step 3 and after step 4 alike: the story test's two scenarios are in the graph under a story the map does not hold, and `scenarios-name-a-story-on-the-map` reports `submit_order_story.test.py`.

## Actual
- Step 3: the Story node Submit Order is gone; its two Scenario nodes and their 8 steps stay, with no story above them and no violation. (The scenarios of every other story test in code lose their story in the same call, r3-cog-02.)
- Step 4: 10 nodes gone: both scenarios and all their steps. The text "Submit" appears nowhere in the saved graph. The Stories part lists 17 violations, none under `scenarios-name-a-story-on-the-map` and none naming the file. The answer is "Loaded 84 edited files."

So "which story tests have no story" cannot be asked of the graph: the test is not there.

## Tier that should catch it
Unit (the Stories graph reading's spec): the example added for widget-21 reads a markdown scenarios file; none reads a Python or TypeScript story test whose story the map lacks.
