"""
# @toolset-manifest python -m tools manifest bdd.bdd:Bdd
"""
from types import SimpleNamespace

from expects import be_true, equal, expect
from mamba import before, context, description, it

from check import Check


with description('a Check'):
    with context('that is resolved with no modifiers'):
        with before.each:
            trait = SimpleNamespace(rank=5)
            dc = SimpleNamespace(target=10)
            stub_dice = SimpleNamespace(roll=lambda: 8)
            self.check = Check(trait, dc, dice=stub_dice)
            self.result = self.check.resolve([])

        with it('should expose the die roll that was used'):
            # Arrange / Act — before.each
            # Assert
            expect(self.check.die_roll).to(equal(8))

        with it('should report whether the total met the difficulty'):
            # Arrange / Act — before.each
            # Assert
            expect(self.result.succeeded).to(be_true)

        with it('should report the total of the outcome'):
            # Arrange / Act — before.each
            # Assert
            expect(self.result.total).to(equal(13))

        with it('should report the degree of the outcome'):
            # Arrange / Act — before.each
            # Assert
            expect(self.result.degree).to(equal(1))

    with context('that is resolved as routine'):
        with it('should treat the die as ten'):
            # Arrange
            trait = SimpleNamespace(rank=5)
            dc = SimpleNamespace(target=10)
            check = Check(trait, dc)
            # Act
            check.resolve([], routine=True)
            # Assert
            expect(check.die_roll).to(equal(10))

    with context('that rolls a natural twenty'):
        with before.each:
            stub_dice = SimpleNamespace(roll=lambda: 20)
            trait = SimpleNamespace(rank=0)
            dc = SimpleNamespace(target=21)
            self.check = Check(trait, dc, dice=stub_dice)
            self.result = self.check.resolve([])

        with it('should gain one degree of success'):
            # Arrange / Act — before.each
            # Assert
            expect(self.result.degree).to(equal(1))

        with it('should succeed when the critical flips a near miss into a hit'):
            # Arrange / Act — before.each
            # Assert
            expect(self.result.succeeded).to(be_true)

    with context('with modifiers that raise the total'):
        with it('should include the modifier amounts in the total'):
            # Arrange
            trait = SimpleNamespace(rank=5)
            dc = SimpleNamespace(target=15)
            stub_dice = SimpleNamespace(roll=lambda: 10)
            mod = SimpleNamespace(amount=5, reason='circumstance')
            check = Check(trait, dc, dice=stub_dice)
            # Act
            result = check.resolve([mod])
            # Assert
            expect(result.total).to(equal(20))
