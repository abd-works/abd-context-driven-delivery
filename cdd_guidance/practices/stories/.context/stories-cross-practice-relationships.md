# Stories CodeQL relationships that cross a practice

Recorded on the CodeQL story types in `practices/stories/model/codeql/codeql_model.py`. `owns` and `scopes` stay inside stories.

```
Example -- demonstrates --> * OoadClass
Example -- retrieved using --> 0..1 Operation or Property

Epic -- uses --> * Module
Given Step -- loads --> * Example
When Step -- invokes --> * Operation or Property
Then Step -- observes --> 0..1 Example
Background -- loads --> * Example
Scenario -- invokes / observes --> union of its steps
Story -- invokes / observes --> union of its scenarios
```

`OoadClass`, `Operation`, `Property`, and `Module` are the Clean Engineering nodes in `practices/clean_engineering/model/.context/ooad-model.md`. The class that owns an invoked member may be a DDD stereotype in `practices/ddd/model/.context/ddd-model.md`.

## Base story model

The walk in `practices/stories/model/.context/story-model.md` loads the example on `Step`. The CodeQL extensions hold the other links: `CodeQLEpic.uses`, `CodeQLStory` and `CodeQLScenario` aggregate invokes and observes, `CodeQLBackground.loads`, `CodeQLStep` loads, invokes, and observes, and `CodeQLExample` demonstrates and is retrieved using. CodeQL resolves each name when its map is built. A transform to markdown or another language copies that map and traverses the edge. The copy reads the node already on the edge.

## Queries

`steps.ql` already returns the given / when / then keyword. `example_exports.ql` returns the export name, not the operation or property that reads the example back, so `retrieved using` only appears when a then-step observation is already in the fact file. No query names the modules an epic uses; the object model takes those from the class that the example demonstrates or the member the when step invokes.
