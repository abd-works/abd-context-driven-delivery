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

## Python and TypeScript story classes

`python_story_model.py` and `typescript_story_model.py` read a test file into the story tree. They do not record these edges. Nothing in those channels has to change for the CodeQL graph. A later channel would add the same operations — `loads`, `invokes`, `observes`, `uses`, `retrieved_using` — only if that channel itself should hold the edges.

## Queries

`steps.ql` already returns the given / when / then keyword. `example_exports.ql` returns the export name, not the operation or property that reads the example back, so `retrieved using` only appears when a then-step observation is already in the fact file. No query names the modules an epic uses; the object model takes those from the class that the example demonstrates or the member the when step invokes.
