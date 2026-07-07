from mamba import description, context, it
from expects import equal, be_true, expect

from stories.src.skill.assembly.phase import Phase, UnknownPhaseError


with description('a Phase'):
    with context('with the Interview scope requested'):
        with it('should include concepts and grill-me-questions only'):
            expect(set(Phase.INTERVIEW.directories())).to(equal({"concepts", "grill-me-questions"}))

    with context('with the Generate scope requested'):
        with it('should include templates, rules, behavior, and concepts'):
            expect(
                {"templates", "rules", "behavior", "concepts"}.issubset(
                    set(Phase.GENERATE.directories())
                )
            ).to(be_true)

    with context('with the Validate scope requested'):
        with it('should include rules only'):
            expect(Phase.VALIDATE.directories()).to(equal(("rules",)))

    with context('with an unrecognised phase string'):
        with it('should not be resolved'):
            caught = None
            try:
                Phase.parse("execute")
            except UnknownPhaseError as error:
                caught = error
            expect(caught).not_to(equal(None))
