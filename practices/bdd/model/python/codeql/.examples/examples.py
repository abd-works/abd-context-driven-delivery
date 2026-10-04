"""BDD examples — Mamba/Python. Index in examples.md; TypeScript in examples.ts."""

# Behavior fidelity — signatures (character_spec.py)

from mamba import description, context, it

with description('a Character'):
    with context('that has been created'):
        with it('should have initial stats assigned'):
            # BDD: SIGNATURE
            pass
        with it('should have zero starting wounds'):
            # BDD: SIGNATURE
            pass

    with context('that is in combat'):
        with context('that has suffered wounds'):
            with it('should have current wounds'):
                # BDD: SIGNATURE
                pass

        with context('that has been attacked with the following damage'):
            with it('should add the attack damage to current wounds'):
                # BDD: SIGNATURE
                pass

    with description('an Attack'):
        with context('that has targeted an enemy'):
            with it('should calculate hit chance using character stats'):
                # BDD: SIGNATURE
                pass
            with it('should consume one action from the active turn'):
                # BDD: SIGNATURE
                pass

        with context('that has missed'):
            with it('should deal no damage'):
                # BDD: SIGNATURE
                pass
            with it('should still consume one action'):
                # BDD: SIGNATURE
                pass

    with context('that has been defeated'):
        with it('should be removed from the initiative order'):
            # BDD: SIGNATURE
            pass


# Development fidelity — test implementation (character_spec.py)

from mamba import description, context, it, before
from expects import equal, expect
from character import Character


def default_stats():
    return {'strength': 10, 'agility': 8, 'endurance': 6}


with description('a Character'):
    with context('that has been created'):
        with it('should have initial stats assigned'):
            # Arrange / Act
            character = Character(name='Test', stats=default_stats())
            # Assert
            expect(character.stats['strength']).to(equal(10))
            expect(character.stats['agility']).to(equal(8))

        with it('should have zero starting wounds'):
            # Arrange / Act
            character = Character(name='Test', stats=default_stats())
            # Assert
            expect(character.wounds).to(equal(0))

    with context('that is in combat'):
        with before.each:
            self.character = Character(name='Test', stats=default_stats())

        with context('that has suffered wounds'):
            with it('should have current wounds'):
                self.character.apply_damage(3)
                expect(self.character.wounds).to(equal(3))

        with context('that has been attacked with the following damage'):
            with it('should add the attack damage to current wounds'):
                self.character.apply_damage(2)
                self.character.apply_damage(4)
                expect(self.character.wounds).to(equal(6))


# Development fidelity — minimal production code (character.py)


class Character:
    def __init__(self, name: str, stats: dict):
        self.name = name
        self.stats = stats
        self.wounds = 0

    def apply_damage(self, amount: int) -> None:
        self.wounds += amount
