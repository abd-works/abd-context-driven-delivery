"""BDD spec for Transformers increment 1 — logical python story map from mm3e sketch."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import before, description, it

from harness.transformers.transformers import Transformers
from practices.clean_engineering.model.transformation.clean_engineering_transformer import (
    CleanEngineeringTransformer,
)
from practices.stories.model.transformation.story_map_transformer import StoryMapTransformer

_FIXTURE = _REPO_ROOT / "harness" / "transformers" / "fixtures" / "mm3e" / "mm3e-sketch.md"


with description("Transformers"):
    with before.each:
        self.sketch = _FIXTURE.read_text(encoding="utf-8")
        self.roots = Transformers().transform_sketch(self.sketch)
        self.story_map = next(
            root for root in self.roots if isinstance(root, StoryMapTransformer)
        )
        self.ce = next(
            root for root in self.roots if isinstance(root, CleanEngineeringTransformer)
        )
        self.files = self.story_map.render("logical")
        self.ce_files = self.ce.render("logical")

    with it("should load StoryMapTransformer from the stories lens"):
        expect(isinstance(self.story_map, StoryMapTransformer)).to(equal(True))
        expect(self.story_map.epics[0].name).to(equal("Resolve Checks"))
        expect(self.story_map.epics[0].sub_epics[0].name).to(equal("Make Check"))
        expect(self.story_map.epics[0].sub_epics[0].stories[0].name).to(
            equal("Make Trait Check")
        )

    with it("should write the python story file under the epic and sub-epic folders"):
        path = (
            "tests/resolve-checks/make-check/make-trait-check/"
            "make_trait_check_story.test.py"
        )
        expect(path in self.files).to(equal(True))
        expect(self.files[path]).to(contain("Story: Make Trait Check"))
        expect(self.files[path]).to(contain("Actor: Player"))
        expect(self.files[path]).to(contain("check succeeds when roll total meets dc"))

    with it("should write the epic helper beside the epic folder"):
        path = "tests/resolve-checks/resolve_checks_helper.py"
        expect(path in self.files).to(equal(True))
        expect(self.files[path]).to(contain("Epic helper"))

    with it("should load CleanEngineeringTransformer from the ce lens"):
        expect(self.ce.modules[0].name).to(equal("checks"))
        trait = self.ce.modules[0].classes[0]
        expect(trait.name).to(equal("Trait"))
        perform = next(op for op in trait.operation_nodes if op.name == "performCheck")
        expect(perform.parameters[0].name).to(equal("dc"))
        expect("..." in self.ce_files["src/checks/trait.py"]).to(equal(True))

    with it("should nest modules and write python class files"):
        power = next(module for module in self.ce.modules if module.name == "power")
        expect([child.name for child in power.modules]).to(
            contain("attack")
        )
        path = "src/checks/trait.py"
        expect(path in self.ce_files).to(equal(True))
        expect(self.ce_files[path]).to(contain("class Trait"))
        expect(self.ce_files[path]).to(contain("def performCheck"))
        graded = self.ce_files["src/checks/graded_check_result.py"]
        expect(graded).to(contain("class GradedCheckResult(CheckResult)"))
