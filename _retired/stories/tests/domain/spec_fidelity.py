from mamba import description, context, it
from expects import equal, expect

from stories.src.skill.assembly.fidelity import Fidelity, UnknownFidelityError


with description('a Fidelity level'):
    with context('with a known string value'):
        with it('should resolve to the matching level'):
            expect(Fidelity.parse("exploration")).to(equal(Fidelity.EXPLORATION))

    with context('with all five level strings supplied in pipeline order'):
        with it('should resolve to all five levels in that order'):
            parsed = [Fidelity.parse(v) for v in
                      ("shaping", "discovery", "exploration", "specification", "engineering")]
            expect(parsed).to(equal(list(Fidelity.all())))

    with context('with a string that contains a typo'):
        with it('should not be recognised as a valid level'):
            caught = None
            try:
                Fidelity.parse("expolration")
            except UnknownFidelityError as error:
                caught = error
            expect(caught).not_to(equal(None))

        with context('the error'):
            with it('should carry the unrecognised string'):
                caught = None
                try:
                    Fidelity.parse("expolration")
                except UnknownFidelityError as error:
                    caught = error
                expect(caught.value).to(equal("expolration"))

    with context('the full ordered set of levels'):
        with it('should run from shaping through to engineering'):
            expect(list(Fidelity.all())).to(equal([
                Fidelity.SHAPING,
                Fidelity.DISCOVERY,
                Fidelity.EXPLORATION,
                Fidelity.SPECIFICATION,
                Fidelity.ENGINEERING,
            ]))
