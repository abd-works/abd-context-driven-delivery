"""TDD's graph rules on the test files of the practices it supplements: a BDD spec, and a Stories acceptance test read
as its Story. Each example is read through the real working-copy build, with TDD's overlay recording the tier and the
real resources of each file, as a live load does."""

from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices and TDD with the practice catalogue
from cdd_guidance.practices.bdd.rules.rule_examples import spec_fixture
from cdd_guidance.practices.stories.rules.rule_examples import stories_fixture
from cdd_guidance.practices.tdd.rules import BY_SLUG
from cdd_guidance.practices.tdd.rules.rule_examples import SPEC_REACHING_A_PROCESS, assert_tdd_example_pair
from harness.graph.rule_fixture import RulePair

_STORY_EXAMPLES = Path(__file__).resolve().parent / "practices" / "stories" / "model" / "typescript" / "_examples"

def story_pair(slug: str) -> RulePair:
    root = _STORY_EXAMPLES / slug
    return RulePair(BY_SLUG[slug], stories_fixture(root / "faulty"), stories_fixture(root / "repaired"))


with description("a test file TDD checks in the graph") as self:
    with context("that is a BDD unit spec"):
        with it("should be flagged for reaching a real process, and pass once it fakes the boundary"):
            assert_tdd_example_pair("unit-tier-fakes-every-boundary")

        with it("should carry the rule under TDD's name"):
            schema = spec_fixture(SPEC_REACHING_A_PROCESS).practice.reading.in_graph.rule_run.schema
            expect(schema.rule_label("Spec", "unit-tier-fakes-every-boundary")).to(equal("tdd.bdd.Spec.unit-tier-fakes-every-boundary"))

    with context("that is a BDD heavy spec"):
        with it("should reach a real process without being flagged"):
            fixture = spec_fixture(SPEC_REACHING_A_PROCESS, filename="widget_heavy_spec.py")
            spec = next(iter(fixture.practice.reading.in_graph.nodes("Spec")))
            expect((spec.get_fact("tier"), fixture.hits(BY_SLUG["unit-tier-fakes-every-boundary"]))).to(equal(("heavy", [])))

    with context("that is a Stories acceptance test"):
        with it("should be flagged for reaching a real socket, and pass once it uses a fake"):
            story_pair("unit-tier-fakes-every-boundary").check()
