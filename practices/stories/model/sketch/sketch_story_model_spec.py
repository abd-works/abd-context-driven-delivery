"""BDD spec — sketch channel parses Stories sketches into a story map."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import description, it

from actions.render.render import Render
from practices.stories.model.sketch.sketch_story_model import SketchStoryModel

_SKETCH = """# Single Client View - sketch

source: `.context/single-client-view.md`

---

## stories:

### Unify Client Identity Across Banks

##### Call Center --> Resolve Client From Record In Hand

##### Single Client View --> Match Client Records Across Customer Files

### Offer PC Mastercard Across Both Banks

##### Single Client View --> Qualify Client For PC Mastercard Offer

##### Call Center --> Present PC Mastercard Offer

```
~> Increment 1: first slice
     Show Card Holding In Onboarding
```
"""


with description("SketchStoryModel"):
    with it("should ignore fenced increment prose when parsing scenarios"):
        model = SketchStoryModel().parse(_SKETCH)
        for epic in model.epics:
            for story in epic.stories:
                expect(len(story.scenarios)).to(equal(0))

    with it("should attach stories directly under an epic when no sub-epic exists"):
        model = SketchStoryModel().parse(_SKETCH)
        expect(len(model.epics)).to(equal(2))
        expect(model.epics[0].name).to(equal("Unify Client Identity Across Banks"))
        expect(len(model.epics[0].stories)).to(equal(2))
        expect(model.epics[0].stories[0].name).to(equal("Resolve Client From Record In Hand"))
        expect(model.epics[0].stories[0].actors).to(equal(["Call Center"]))

    with it("should render markdown story-map outline from a sketch via Render"):
        results = Render().render(
            "practices.stories.stories:Stories",
            format="markdown",
            content=_SKETCH,
            source="sketch",
        )
        text = str(results[0]["content"])
        expect(text).to(contain("Single Client View"))
        expect(text).to(contain("(E) Unify Client Identity Across Banks"))
        expect(text).to(contain("(E) Unify Client Identity Across Banks"))
        expect(text).to(contain("(S) Call Center --> Resolve Client From Record In Hand"))
        expect(text).to(contain("## Scope boundary"))
        expect("## domain driven design:" in text).to(equal(False))
