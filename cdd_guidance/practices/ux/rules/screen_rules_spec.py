"""UX screen graph rules - a failing and a passing example of each, on a graph that also holds the stories."""

import sys
from pathlib import Path

from expects import contain, equal, expect, have_len
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


from cdd_guidance.practices.ux.rules.rule_examples import ScreenExample
from cdd_guidance.practices.ux.rules.screen_rules import ScreenNamesUseDomainTerms, ScreenStoryBudget

with description("a screen checked against the screen-story-budget rule"):
    with context("that shows five stories"):
        with before.each:
            self.example = ScreenExample("Catalog", 5)

        with it("should record that it shows each story"):
            practice = self.example.graph.practices.named("ux")
            expect([edge.child.name for edge in practice.reading.in_graph.edge_index.of("shows")]).to(have_len(5))

        with it("should be over the budget"):
            expect(self.example.violations(ScreenStoryBudget())).to(
                equal(["Screen 'Catalog' has 5 stories (budget ~4)."])
            )

    with context("that shows four stories"):
        with it("should be within the budget"):
            expect(ScreenExample("Catalog", 4).violations(ScreenStoryBudget())).to(equal([]))


with description("a screen checked against the screen-names-use-domain-terms rule"):
    with context("that is named with a generic label"):
        with it("should ask for a domain term"):
            expect(ScreenExample("Home", 0).violations(ScreenNamesUseDomainTerms())).to(
                contain("Screen 'Home' should use a domain term, not a generic label.")
            )

    with context("that is named with a domain term"):
        with it("should pass"):
            expect(ScreenExample("Catalog", 0).violations(ScreenNamesUseDomainTerms())).to(equal([]))
