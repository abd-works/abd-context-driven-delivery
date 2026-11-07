# Stories relationships that cross a practice

Stories records its links to Clean Engineering after both practices are read onto the graph: `Stories.link_to_other_practices` runs `link_steps_and_examples` (`practices/stories/model/graph_reading.py`) when the graph holds both practices. Links to UX screens come from the schema fields the graph records when both nodes are on it (`harness/graph/schema_edges.py`). `owns` and `scopes` stay inside Stories.

| Kind | From | To | When |
|------|------|-----|------|
| invokes | Step | Operation | The step's callees, or a `.name(` call in the step's line and the lines after it, name the operation |
| invokes, invokedBy | Operation | Step | Recorded on Clean Engineering with each step that invokes the operation |
| uses | Epic | Module | The module is the folder of an operation a step in the epic invokes |
| usedBy | Module | Epic | Recorded on Clean Engineering with uses |
| observes | Step | Example | A Given, When, or Then step's lines name the example |
| demonstrates | Example | OoadClass | The `.ts` file that declares a function named after the example names the class |
| demonstrates, demonstratedThrough | OoadClass | Example | Recorded on Clean Engineering with demonstrates |
| retrievedUsing | Example | Property | That same file reads `.property`; recorded on both practices |
| shownOn | Story, Scenario, Step | Screen | The screen's `story_names`, `scenario_names` (`Story › Scenario`), or `step_names` (`Story › Scenario › Step`) hold the node's key |
| shows | Screen | Story | Recorded on UX with shownOn |

A story model loaded on the graph (`GraphStoryModel.record`, described in `practices/stories/model/.context/story-model.md`) carries the steps and examples these links start from.
