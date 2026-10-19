# Story model

A story file is one file. Do not track a tier, a test suite, or a test case as a node.

`StoryMap.load` reads the story map from a folder. There is no scanner object beside the map.

A scenario's Given, When, and Then lines are its `Step` nodes. A step's type is `step_type`. An and or a but is a step in that step's `ands`, with its own order. Do not copy those lines into a second list.

A story map in every format is a `StoryMap`. It loads and saves epics, stories, and the rest of that tree. Do not wrap the tree in a second object for a file format.

A story file is `story`, `background`, `scenario`, and the step calls `given`, `when`, `then`, and `and`. Do not emit a helper protocol, a `create_*_story` factory, or a file per tier.

Render creates a diagram of the story map or a thin slice. Do not render scenarios on a diagram. Do not sync an edited diagram back into the story map, and do not return an update report from that copy.

`clone` is an instance method. `story.clone()` returns a new story and each scenario, step, and example clones itself. Do not make `clone` a class method.

`example.scope` is the story node that shares that example: a background, a scenario, a sub-epic, an epic, or the story map. That same node holds the example in `examples`. Do not store domain-concept names or ExampleFactory names on an epic.

The people in a story are `actors`.

An epic's `parent` is the story map. An increment's `parent` is the story map.

An increment is created with its `Story` nodes. Each of those stories has `increment` set to that increment. A story with no increment leaves `increment` empty. The story still sits under its epic or sub-epic.

Examples on a node are a map keyed by example name. The value is any object and defaults to a field map, so the map reads as a table and each value can be written as code.
