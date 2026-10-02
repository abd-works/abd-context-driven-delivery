from expects import expect, equal
from mamba import description, it

from practices.clean_engineering.model.sketch.sketch_class_model import SketchCleanEngineeringModel
from practices.clean_engineering.model.typescript.typescript_class_model import (
    TypeScriptCleanEngineeringModel,
)

_SKETCH = """
```
KnowledgeGraph
  storyModel
  filter
  createDatabase
  Path load folder
  KnowledgeGraph storyModel
    -> KnowledgeGraphStoryModel storyModel
  saveKnowledgeGraph
    -> CodeStoryModel.load
  refreshMaster
    -> copyWorkingCopyToMaster
    // after the working copy is current
  ----
KnowledgeGraphCallSource : KnowledgeGraphSource
  loadCalls
  source
    -> super.source
    -> loadCalls
```
"""


def _model():
    return SketchCleanEngineeringModel.parse(_SKETCH)


def _graph():
    return next(row for row in _model().modules[0].classes if row.name == "KnowledgeGraph")


def _render() -> str:
    return TypeScriptCleanEngineeringModel().render(_model())


with description("a boxed sketch class"):
    with it("should treat a single word as a property"):
        names = [row.name for row in _graph().properties]
        expect("storyModel" in names).to(equal(True))
        expect("createDatabase" in names).to(equal(True))
        expect("createDatabase" in [row.name for row in _graph().operations]).to(equal(False))

    with it("should treat a line with words after the name as an operation"):
        load = next(row for row in _graph().operations if row.name == "load")
        expect(load.return_type).to(equal("Path"))
        expect([row.name for row in load.parameters]).to(equal(["folder"]))

    with it("should treat a single word with interactions as an operation"):
        names = [row.name for row in _graph().operations]
        expect("saveKnowledgeGraph" in names).to(equal(True))
        expect("refreshMaster" in names).to(equal(True))

    with it("should keep nested arrows as interactions and notes as invariants"):
        refresh = next(row for row in _graph().operations if row.name == "refreshMaster")
        expect(refresh.callees).to(equal(["copyWorkingCopyToMaster"]))
        expect(refresh.invariants[0].text).to(equal("after the working copy is current"))


with description("a sketch rendered as TypeScript"):
    with it("should take constructor parameters from the constructor operation"):
        text = _render()
        expect("  constructor(storyModel: any) {" in text).to(equal(True))
        expect("createDatabase: any" in text.split("constructor")[1].split(")")[0]).to(
            equal(False)
        )

    with it("should construct a collaborator instead of emitting an invalid callee"):
        text = _render()
        expect("    this.storyModel = new KnowledgeGraphStoryModel(storyModel);" in text).to(
            equal(True)
        )
        expect("KnowledgeGraphStoryModel storyModel();" in text).to(equal(False))

    with it("should call super.source from the source operation"):
        text = _render()
        expect("  source(): void {" in text).to(equal(True))
        expect("    super.source();" in text).to(equal(True))
        expect("    loadCalls();" in text).to(equal(True))
