"""Scenario rules for what a person caught by hand on a design canvas: a step that only names an example, two scenarios
that say the same, and a scenario of a person's story in which the person never acts."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect  # noqa: E402
from mamba import before, context, description, it  # noqa: E402

from harness.graph.rule_fixture import RuleFixture  # noqa: E402
from cdd_guidance.practices.stories.rules import BY_SLUG  # noqa: E402
from cdd_guidance.practices.stories.rules.rule_examples import FILE_PAIRS  # noqa: E402
from cdd_guidance.practices.stories.stories import Stories  # noqa: E402


def _hits(slug: str, side: int) -> list[str]:
    """What the rule finds on one side of its example: 0 the failing files, 1 the repaired ones."""
    return RuleFixture(Stories, FILE_PAIRS[slug][side]).hits(BY_SLUG[slug])


with description("a scenario rule for what a person caught by hand") as self:
    with context("step-says-more-than-an-example-name"):
        with before.all:
            self.faulty, self.repaired = _hits("step-says-more-than-an-example-name", 0), _hits("step-says-more-than-an-example-name", 1)

        with it("should flag a Given whose whole predicate is an example's name"):
            expect(self.faulty).to(contain(contain("says only that the basket is the example 'Me on the checklist'")))

        with it("should pass the Given that says in domain words what the basket holds"):
            expect(self.repaired).to(equal([]))

    with context("scenarios-differ-in-when-or-outcome"):
        with before.all:
            self.faulty, self.repaired = _hits("scenarios-differ-in-when-or-outcome", 0), _hits("scenarios-differ-in-when-or-outcome", 1)

        with it("should flag the second of two scenarios that run the same operation and check mostly the same Thens"):
            expect(self.faulty).to(contain(contain("'Load catalog' runs the same When as 'See the catalog'")))

        with it("should pass two scenarios that run the same operation for different outcomes"):
            expect(self.repaired).to(equal([]))

    with context("person-stories-show-the-person-acting"):
        with before.all:
            self.faulty, self.repaired = _hits("person-stories-show-the-person-acting", 0), _hits("person-stories-show-the-person-acting", 1)

        with it("should flag a scenario of the Customer's story whose When is only the system looking something up"):
            expect(self.faulty).to(contain(contain("has no When in which the Customer acts")))

        with it("should pass the scenario once the Customer acts in it"):
            expect(self.repaired).to(equal([]))
