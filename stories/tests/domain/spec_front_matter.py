from mamba import description, context, it
from expects import be_true, be_false, expect

from stories.src.skill.assembly.fidelity import Fidelity
from stories.src.skill.assembly.front_matter import FrontMatter


def front_matter_for(**kwargs) -> FrontMatter:
    """Minimal FrontMatter; caller supplies only the fields under test."""
    return FrontMatter(**kwargs)


with description('a Front Matter record'):
    with context('with a fidelity set that overlaps the requested set'):
        with it('should match the request'):
            front_matter = front_matter_for(
                fidelities=frozenset({Fidelity.EXPLORATION, Fidelity.SPECIFICATION})
            )
            expect(front_matter.matches(frozenset({Fidelity.SPECIFICATION}), "md")).to(be_true)

    with context('with a fidelity set that does not overlap the requested set'):
        with it('should not match the request'):
            front_matter = front_matter_for(fidelities=frozenset({Fidelity.ENGINEERING}))
            expect(front_matter.matches(frozenset({Fidelity.SHAPING}), "md")).to(be_false)

    with context('with no format declared'):
        with it('should match any requested format'):
            front_matter = front_matter_for(
                fidelities=frozenset({Fidelity.SHAPING}),
                format=None,
            )
            expect(front_matter.matches(frozenset({Fidelity.SHAPING}), "md")).to(be_true)
            expect(front_matter.matches(frozenset({Fidelity.SHAPING}), "ts")).to(be_true)

    with context('with a format declared'):
        with context('with the requested format matching the declared format'):
            with it('should match'):
                front_matter = front_matter_for(
                    fidelities=frozenset({Fidelity.SHAPING}),
                    format="md",
                )
                expect(front_matter.matches(frozenset({Fidelity.SHAPING}), "md")).to(be_true)

        with context('with the requested format differing from the declared format'):
            with it('should not match'):
                front_matter = front_matter_for(
                    fidelities=frozenset({Fidelity.SHAPING}),
                    format="md",
                )
                expect(front_matter.matches(frozenset({Fidelity.SHAPING}), "ts")).to(be_false)

    with context('with an empty fidelity set'):
        with it('should not match any request'):
            front_matter = front_matter_for(fidelities=frozenset())
            expect(front_matter.matches(frozenset({Fidelity.SHAPING}), "md")).to(be_false)
