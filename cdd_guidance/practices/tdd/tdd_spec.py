"""TDD supplements the implementation fidelities of Clean Engineering, Stories, BDD, and DDD, and the hardening fidelities
of Stories and BDD, in every session, and holds the test tier, speed, stub, and cadence rules that Stories acceptance
tests and BDD development share."""

from expects import contain, equal, expect
from mamba import before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices and TDD with the practice catalogue
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

SUPPLEMENTED = (
    ("clean_engineering", "code"), ("stories", "acceptance_tests"), ("stories", "hardening"), ("bdd", "development"),
    ("bdd", "hardening"), ("ddd", "tactics"),
)


def slugs_of(fidelity):
    return [rule.slug for rule in fidelity.checked_rules()]


with description("the TDD supplement") as self:
    with before.all:
        self.practices = {practice.key: practice for practice in PRACTICE_CATALOGUE.create_all(fidelity=None)}
        self.fidelity = lambda key, name: self.practices[key].fidelities.called(name)
        self.tdd = self.practices["bdd"].working_set.supplements[0]

    with context("that the catalogue makes with a session's practices"):
        with it("should supplement the four implementation fidelities and the two hardening fidelities"):
            expect([(f.practice_guidance.key, f.name) for f in self.tdd.supplemented_fidelities]).to(equal(list(SUPPLEMENTED)))

        with it("should be on without being chosen"):
            expect(self.tdd.always_apply).to(equal(True))

        with it("should not be listed among the practices"):
            expect(PRACTICE_CATALOGUE.names).not_to(contain("tdd"))

    # The installer writes the shared rules into the rule file every IDE loads on every turn. Without them the file is
    # empty, and the flow is read only inside a generate reply, where an agent can skip it.
    with context("with its shared rules, which every IDE loads on every turn"):
        with it("should hold the rule that the flow is chosen before code is written"):
            expect([rule.slug for rule in self.tdd.rules]).to(contain("flow-chosen-before-code"))

        with it("should apply always, to every file"):
            expect(self.tdd.rules.markdown).to(contain("alwaysApply: true"))

    with context("with a fidelity it supplements"):
        with it("should add the tier rules to the acceptance tests and BDD development"):
            for key, name in (("stories", "acceptance_tests"), ("bdd", "development")):
                expect(slugs_of(self.fidelity(key, name))).to(contain("suffix-names-the-tier", "unit-example-within-100-ms"))

        with it("should leave the tier rules off Clean Engineering code and DDD tactics"):
            for key, name in (("clean_engineering", "code"), ("ddd", "tactics")):
                expect(slugs_of(self.fidelity(key, name))).not_to(contain("suffix-names-the-tier"))

        with it("should add the rules of that practice's section"):
            expect(slugs_of(self.fidelity("ddd", "tactics"))).to(contain("aggregate-tested-through-its-root"))

        with it("should add its flow guidance to the fidelity's instructions"):
            expect(self.fidelity("bdd", "development").instructions).to(contain("## Supplement: tdd", "Flow A"))

    with context("with a hardening fidelity of Stories or BDD, which holds no text of its own yet"):
        with it("should be a fidelity of the Hardening stage"):
            for key in ("stories", "bdd"):
                expect(self.fidelity(key, "hardening").stage).to(equal("hardening"))

        with it("should give the fidelity its guidance on exploratory testing and regression, not only its rules"):
            for key in ("stories", "bdd"):
                expect(self.fidelity(key, "hardening").instructions).to(contain(
                    f"## Supplement: tdd for {key}-hardening", "Exploratory testing", "Regression",
                ))

        with it("should add the rules a finished hardening pass is checked by"):
            for key in ("stories", "bdd"):
                expect(slugs_of(self.fidelity(key, "hardening"))).to(contain(
                    "every-theme-has-a-robot-report", "every-story-judged-against-the-last-release",
                ))

        with it("should leave the hardening rules off the implementation fidelities"):
            expect(slugs_of(self.fidelity("bdd", "development"))).not_to(contain("every-theme-has-a-robot-report"))

    with context("with UX front-end code, which it does not supplement"):
        with it("should add no TDD rules"):
            expect(slugs_of(self.fidelity("ux", "front_end_code"))).not_to(contain("suffix-names-the-tier"))

    with context("with the tier rules it took over"):
        with it("should leave BDD development without its own tier-by-speed rule"):
            expect(slugs_of(self.fidelity("bdd", "development"))).not_to(contain("tier-by-speed"))

        with it("should leave Stories acceptance tests without their own story-tier-by-speed rule"):
            expect(slugs_of(self.fidelity("stories", "acceptance_tests"))).not_to(contain("story-tier-by-speed"))
