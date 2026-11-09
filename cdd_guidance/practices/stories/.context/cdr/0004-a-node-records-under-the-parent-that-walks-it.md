# A story node records under the parent that walks it

**Status:** decided, round 8 (finding R8-L8, the `record` half). The `add` half is done.

## Decision

`StoryRecording.add(story_object, node_id, at, facts)` reads the node's graph name and type from the object (`recorded_name`, `recorded_type`) and its lines from one *Source* (the graph's; Stories' own location class is gone), instead of being handed the name, type, file, and span as separate values.

Each `record` keeps receiving the graph node of the parent that walks it: `Epic.record(recording, parent)`, `Story.record(recording, parent)`, `Background.record(recording, file, parent)`, `Scenario.record(recording, file, parent, scoped)`, `Step.record(recording, file, parent)`, `Example.record(recording, scenario, at)`. An epic no longer takes a `top` flag (it asks `is_sub_epic`), and a step no longer takes its edge kind (an `ands` step's parent is a step).

## Why

- A node's model `parent` is not always the node it sits under on the graph. `StoryModel.take_scenarios` hands the scenarios and backgrounds read from one story test to every Story of the same name in a merged map (the markdown map and the draw.io map each hold the Story), so a shared scenario's `parent` is only the last of them; the scenario must be linked under each story that walks it.
- An example's graph parent is the scenario that uses it; its model `parent` is the node whose `Examples` hold it, often the story's background or the map.
- When two objects share a node id, the node `add` returns is the one already held, not the object; children link under that node so the second object's children land on the first object's node, as they did before.
- The file a background, scenario, or step is recorded in is its story's file, or its own when it was read from a story test. Deriving it from the parent node's source would turn a story with no file into `.`, changing the ids of every node under it.

## Consequences

`record` keeps a parent parameter on every story node. If a merged map ever stops sharing scenarios between same-named stories, the parent can be read from `parent` and this decision closes.
