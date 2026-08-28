"""BDD spec for Generate Type Extending Interface story data (factory modes).
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import be_true, equal, expect
from mamba import before, context, description, it

from generate_type_extending_interface_stories import GENERATE_TYPE_EXTENDING_INTERFACE


with description("a generate-type-extending-interface story"):
    with context("that is loaded"):
        with before.each:
            self.story = GENERATE_TYPE_EXTENDING_INTERFACE

        with it("should name the story Generate Type Extending Interface"):
            expect(self.story["story"]).to(equal("Generate Type Extending Interface"))

        with it("should cast the Generator as actor"):
            expect(self.story["actor"]).to(equal("Generator"))

        with it("should include TypeExampleFactory and mode in domain terms"):
            terms = self.story["domain_terms"]
            expect("TypeExampleFactory" in terms).to(be_true)
            expect("mode" in terms).to(be_true)

        with it("should omit FakeType IsolatedType ProductionType subclass names"):
            terms = set(self.story["domain_terms"])
            expect("FakeType" in terms).to(equal(False))
            expect("IsolatedType" in terms).to(equal(False))
            expect("ProductionType" in terms).to(equal(False))

    with context("that describes factory modes"):
        with before.each:
            self.story = GENERATE_TYPE_EXTENDING_INTERFACE

        with it("should include a fake mode scenario"):
            expect("fake_mode_for_explore_spec" in self.story).to(be_true)

        with it("should include an isolated mode scenario"):
            expect("isolated_mode_for_a_story_test_tier" in self.story).to(be_true)

        with it("should include a production mode scenario"):
            expect("production_mode_for_a_story_test_tier" in self.story).to(be_true)

        with it("should state that FakeType subclasses are not emitted"):
            then_lines = self.story["isolated_mode_for_a_story_test_tier"][
                "interactions"
            ][0]["then"]
            joined = " ".join(then_lines)
            expect("FakeType" in joined and "subclasses are emitted" in joined).to(
                be_true
            )
