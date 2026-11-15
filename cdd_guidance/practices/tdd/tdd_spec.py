"""TDD supplements the implementation fidelities of Clean Engineering, Stories, BDD, and DDD in every session, and
holds the test tier, speed, stub, and cadence rules they share."""

from expects import contain, equal, expect
from mamba import before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices and TDD with the practice catalogue
from harness.guidance.practice_catalogue import PracticeCatalogue

SUPPLEMENTED = (("clean_engineering", "code"), ("stories", "acceptance_tests"), ("bdd", "development"), ("ddd", "tactics"))


def slugs_of(fidelity):
    return [rule.slug for rule in fidelity.checked_rules()]


with description("the TDD supplement") as self:
    with before.all:
        self.practices = {practice.key: practice for practice in PracticeCatalogue.create_all(fidelity=None)}
        self.fidelity = lambda key, name: self.practices[key].fidelity_called(name)
        self.tdd = self.practices["bdd"].supplements[0]

    with context("that the catalogue makes with a session's practices"):
        with it("should supplement the four implementation fidelities"):
            expect([(f.practice_guidance.key, f.name) for f in self.tdd.supplemented_fidelities]).to(equal(list(SUPPLEMENTED)))

        with it("should be on without being chosen"):
            expect(self.tdd.always_apply).to(equal(True))

        with it("should not be listed among the practices"):
            expect(PracticeCatalogue.keys()).not_to(contain("tdd"))

    with context("with a fidelity it supplements"):
        with it("should add the tier rules every supplemented fidelity shares"):
            for key, name in SUPPLEMENTED:
                expect(slugs_of(self.fidelity(key, name))).to(contain("suffix-names-the-tier", "unit-example-within-100-ms"))

        with it("should add the rules of that practice's section"):
            expect(slugs_of(self.fidelity("ddd", "tactics"))).to(contain("aggregate-tested-through-its-root"))

        with it("should add its flow guidance to the fidelity's instructions"):
            expect(self.fidelity("bdd", "development").instructions).to(contain("## Supplement: tdd", "Flow A"))

    with context("with UX front-end code, which it does not supplement"):
        with it("should add no TDD rules"):
            expect(slugs_of(self.fidelity("ux", "front_end_code"))).not_to(contain("suffix-names-the-tier"))

    with context("with the tier rules it took over"):
        with it("should leave BDD development without its own tier-by-speed rule"):
            expect(slugs_of(self.fidelity("bdd", "development"))).not_to(contain("tier-by-speed"))

        with it("should leave Stories acceptance tests without their own story-tier-by-speed rule"):
            expect(slugs_of(self.fidelity("stories", "acceptance_tests"))).not_to(contain("story-tier-by-speed"))
