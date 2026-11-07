from expects import expect, equal
from mamba import description, it

from cdd_guidance.practices.clean_engineering.model.sketch.sketch_class_model import SketchCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import (
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
    return SketchCleanEngineeringModel().parse(_SKETCH)


def _graph():
    return next(member for member in _model().modules[0].classes if member.name == "KnowledgeGraph")


def _render() -> str:
    return TypeScriptCleanEngineeringModel().render(_model())


with description("a boxed sketch class"):
    with it("should treat a single word as a property"):
        names = [member.name for member in _graph().properties]
        expect("storyModel" in names).to(equal(True))
        expect("createDatabase" in names).to(equal(True))
        expect("createDatabase" in [member.name for member in _graph().operations]).to(equal(False))

    with it("should treat a line with words after the name as an operation"):
        load = next(member for member in _graph().operations if member.name == "load")
        expect(load.return_type).to(equal("Path"))
        expect([member.name for member in load.parameters]).to(equal(["folder"]))

    with it("should treat a single word with interactions as an operation"):
        names = [member.name for member in _graph().operations]
        expect("saveKnowledgeGraph" in names).to(equal(True))
        expect("refreshMaster" in names).to(equal(True))

    with it("should keep nested arrows as interactions and notes as invariants"):
        refresh = next(member for member in _graph().operations if member.name == "refreshMaster")
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


_UML = """
**Module:** `space/session`

## clean engineering:

### **Session**

+ new(name: str, workpath: Path, repo_path: Path): str
	-> keep_log()
------
+ name: str
+ workpath: Path

**Invariants**

- new keeps the name it was given.

### **Loop**

+ Loop(number: int)
+ number: int

## behavior driven development:

### a session
"""


with description("a sketch that names its classes in bold headings"):
    with it("should read Session and Loop from the clean engineering section"):
        model = SketchCleanEngineeringModel().parse(_UML)
        names = [member.name for member in model.modules[0].classes]
        expect(names).to(equal(["Session", "Loop"]))

    with it("should read the uml operation and its callee"):
        model = SketchCleanEngineeringModel().parse(_UML)
        session = next(member for member in model.modules[0].classes if member.name == "Session")
        new = next(member for member in session.operations if member.name == "new")
        expect(new.return_type).to(equal("str"))
        expect([member.save() for member in new.parameters]).to(equal([
            "name: str",
            "workpath: Path",
            "repo_path: Path",
        ]))
        expect(new.callees).to(equal(["keep_log()"]))

    with it("should leave prose headings out of the classes"):
        model = SketchCleanEngineeringModel().parse(_UML)
        names = [member.name for member in model.modules[0].classes]
        expect("Invariants" in names).to(equal(False))
        expect("Instructions" in names).to(equal(False))

    with it("should name the module the sketch declares"):
        model = SketchCleanEngineeringModel().parse(_UML)
        expect(model.modules[0].name).to(equal("space/session"))
