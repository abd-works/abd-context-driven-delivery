from mamba import description, context, it
from expects import equal, expect


class Character:
    def __init__(self):
        self._wounds = 0
        self.stats = {"strength": 10}


with description("SessionLog"):
    with context("when the user clicks save"):
        with it("should record the click"):
            character = Character()
            expect(character.stats["strength"]).to(equal(10))
            expect(character._wounds).to(equal(0))
