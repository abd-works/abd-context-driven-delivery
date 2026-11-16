"""A practice supplement adds its guidance and rules to the fidelities of other practices it names, such as TDD on BDD
development and Clean Engineering code. The sample supplement in ``fixtures/sample_supplement`` supplements those two."""

from expects import be_empty, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.guidance.fixtures.sample_supplement.sample_supplement import SampleSupplement
from harness.guidance.fixtures.unknown_supplement.unknown_supplement import UnknownSupplement
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from harness.guidance.practice_supplement import UnknownSupplementedFidelity


def practices_by_key(practices):
    return {practice.key: practice for practice in practices}


with description("a practice supplement") as self:
    with context("that the catalogue makes with a set of practices"):
        with before.all:
            self.registered = PRACTICE_CATALOGUE.supplement_classes
            PRACTICE_CATALOGUE.register_supplements(SampleSupplement)
            self.practices = practices_by_key(PRACTICE_CATALOGUE.create_all(fidelity=None))
            self.bdd_development = self.practices["bdd"].fidelities.called("development")
            self.code = self.practices["clean_engineering"].fidelities.called("code")
            self.story_map = self.practices["stories"].fidelities.called("story_map")
            self.supplement = self.practices["bdd"].working_set.supplements[0]

        with after.all:
            PRACTICE_CATALOGUE.register_supplements(*self.registered)

        with it("should supplement the set's own fidelities its front matter names"):
            expect(self.supplement.supplemented_fidelities).to(equal([self.bdd_development, self.code]))

        with it("should be held by each practice it supplements"):
            expect(self.practices["clean_engineering"].working_set.supplements).to(equal([self.supplement]))

        with it("should not be held by a practice it does not supplement"):
            expect(self.practices["stories"].working_set.supplements).to(be_empty)

        with it("should not be listed among the practices"):
            expect(PRACTICE_CATALOGUE.names).not_to(contain("sample_supplement"))

        with context("read on its own"):
            with it("should hold every section named for a fidelity in its instructions"):
                expect(self.supplement.instructions).to(contain(
                    "Sample supplement guidance", "Sample guidance both fidelities share", "fill one signature at a time", "write code only to turn a test green"))

            with it("should hold the rules of every section named for a fidelity"):
                expect([rule.slug for rule in self.supplement.every_rule]).to(equal(["sample-shared-rule", "sample-bdd-rule", "sample-code-rule"]))

        with context("with a fidelity it supplements"):
            with it("should end the fidelity's instructions with its text for that fidelity"):
                expect(self.bdd_development.instructions).to(contain(
                    "## Supplement: sample_supplement", "Sample supplement guidance", "fill one signature at a time"))

            with it("should leave out its text for another fidelity it supplements"):
                expect(self.bdd_development.instructions).not_to(contain("write code only to turn a test green"))

            with it("should add its shared rules and that fidelity's rules to the rules a validate checks"):
                slugs = [rule.slug for rule in self.bdd_development.checked_rules()]
                expect(slugs).to(contain("sample-shared-rule", "sample-bdd-rule"))

            with it("should leave out the rules of another fidelity it supplements"):
                slugs = [rule.slug for rule in self.bdd_development.checked_rules()]
                expect(slugs).not_to(contain("sample-code-rule"))

        with context("with a fidelity it does not supplement"):
            with it("should add nothing to the fidelity's instructions"):
                expect(self.story_map.instructions).not_to(contain("## Supplement:"))

            with it("should add no rules to the rules a validate checks"):
                slugs = [rule.slug for rule in self.story_map.checked_rules()]
                expect(slugs).not_to(contain("sample-shared-rule"))

    with context("that names a fidelity its practice does not have"):
        with before.each:
            self.registered = PRACTICE_CATALOGUE.supplement_classes

        with after.each:
            PRACTICE_CATALOGUE.register_supplements(*self.registered)

        with it("should refuse the set it is made with"):
            PRACTICE_CATALOGUE.register_supplements(UnknownSupplement)
            expect(lambda: PRACTICE_CATALOGUE.create_all(fidelity=None)).to(raise_error(UnknownSupplementedFidelity))
