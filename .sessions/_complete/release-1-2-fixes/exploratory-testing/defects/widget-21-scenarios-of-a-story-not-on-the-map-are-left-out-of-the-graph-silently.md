# A scenarios file whose stories are not on the story map adds nothing to the graph: its scenarios and examples are left out with no violation and no word

- **Charter:** Round 2 - the knowledge graph and the formats of the other practices, as an agent whose files move, rename and stop parsing between two calls
- **Tester:** Widget
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers this.
- **Module and class:** `harness/graph/graph_reads.py` with the Stories reading `cdd_guidance/practices/stories/model/graph_reading.py`.
- **Severity:** wrong result if a story file must be reported when it names no story of the map; question if leaving it out is meant

## Steps
Sandbox `repo` (`C:\dev\_et\widget\work\repo`), session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`, calls in `drv\d10.json`, file changes in `drv\m9.py`). The story map has stories Place Order and Cancel Order.

1. `graph.load_files {"folder": "C:/dev/_et/widget/work/repo", "practices": ["stories"], "files": ["story_tests", ".context/story-map.md"]}` with the scenarios file's stories named Place Order and Cancel Order: Story x2, Scenario x4, Example x4.
2. Rename the two stories in the scenarios file to Gift Order and Wrap Order (nothing else changed), then `graph.refresh {"paths": ["story_tests"]}`.
3. `graph.return_nodes {"filter": {"types": ["Story", "Scenario", "Example"]}}` and `{"filter": {"violations": true}}`.

## Expected
Either the scenarios are in the graph under their own stories, or a violation says the file names stories the map does not have, so that validate on that file is not silently empty.

## Actual
"Refreshed 2 files." The graph holds Story x2 (the map's) and no Scenario or Example at all; the only violation is the map's own `child-count-fits-layer`. Nothing names the scenarios file.

The same file saved with CRLF line ends, or with a byte-order mark, and the map's story names is read in full (Story x2, Scenario x4, Example x4), so neither of those is the cause.

## Tier that should catch it
Unit (the Stories graph reading's spec): no example reads a scenarios file whose stories the map lacks.

## Confirmation (Cog)
- Result: confirmed
- What I ran and saw: The Stories reading on a real folder of my own through the rule fixture (`C:\dev\_et\cog\w21.py`): a story map with Place Order and Cancel Order and one scenarios file. With the file's stories named as on the map the graph holds Story x2 and Scenario x2; with them renamed Gift Order and Wrap Order it holds Story x2 (the map's), no Scenario, and no violation. The cdd server was not run.
- Cause: `cdd_guidance/practices/stories/model/markdown/nodes.py` `MarkdownStoryModel._attach_markdown` gives each story of the map the sections of the scenarios files headed with its name, and a section no story of the map names was dropped there.
- Fix: such a section's story is kept on the map as one it does not hold (`StoryModel.unplaced_stories`), recorded in the graph with its scenarios under no epic, and reported by the new rule `scenarios-name-a-story-on-the-map`.
