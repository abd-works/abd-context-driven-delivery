/**
 * BDD examples — Jest/TypeScript. Narrative and index live in examples.md.
 * Mamba/Python: examples.py
 */

// Behavior hierarchy input (prerequisite) — character-behavior.md
//
// a Character
//   that has been created
//     should have initial stats assigned
//     should have zero starting wounds
//   that is in combat
//     that has suffered wounds
//       should have current wounds
//     that has been attacked with the following damage
//       should add the attack damage to current wounds
//   an Attack
//     that has targeted an enemy
//       should calculate hit chance using character stats
//       should consume one action from the active turn
//     that has missed
//       should deal no damage
//       should still consume one action
//   that has been defeated
//     should be removed from the initiative order

// Behavior fidelity — signatures (character.test.ts)

describe('a Character', () => {
  describe('that has been created', () => {
    it('should have initial stats assigned', () => {
      // BDD: SIGNATURE
    });
    it('should have zero starting wounds', () => {
      // BDD: SIGNATURE
    });
  });

  describe('that is in combat', () => {
    describe('that has suffered wounds', () => {
      it('should have current wounds', () => {
        // BDD: SIGNATURE
      });
    });

    describe('that has been attacked with the following damage', () => {
      it('should add the attack damage to current wounds', () => {
        // BDD: SIGNATURE
      });
    });
  });

  describe('an Attack', () => {
    describe('that has targeted an enemy', () => {
      it('should calculate hit chance using character stats', () => {
        // BDD: SIGNATURE
      });
      it('should consume one action from the active turn', () => {
        // BDD: SIGNATURE
      });
    });

    describe('that has missed', () => {
      it('should deal no damage', () => {
        // BDD: SIGNATURE
      });
      it('should still consume one action', () => {
        // BDD: SIGNATURE
      });
    });
  });

  describe('that has been defeated', () => {
    it('should be removed from the initiative order', () => {
      // BDD: SIGNATURE
    });
  });
});

// Development fidelity — signature input (character.test.ts, partial)

describe('Character', () => {
  describe('that has been created', () => {
    it('should have initial stats assigned', () => {
      // BDD: SIGNATURE
    });
    it('should have zero starting wounds', () => {
      // BDD: SIGNATURE
    });
  });

  describe('that is in combat', () => {
    describe('that has suffered wounds', () => {
      it('should have current wounds', () => {
        // BDD: SIGNATURE
      });
    });

    describe('that has been attacked with the following damage', () => {
      it('should add the attack damage to current wounds', () => {
        // BDD: SIGNATURE
      });
    });
  });
});

// Development fidelity — test implementation (character.test.ts)

import { Character } from '../Character';

function defaultStats() {
  return { strength: 10, agility: 8, endurance: 6 };
}

describe('Character', () => {
  describe('that has been created', () => {
    it('should have initial stats assigned', () => {
      // Arrange
      const stats = defaultStats();
      // Act
      const character = new Character({ name: 'Test', stats });
      // Assert
      expect(character.stats.strength).toBe(10);
      expect(character.stats.agility).toBe(8);
    });

    it('should have zero starting wounds', () => {
      // Arrange / Act
      const character = new Character({ name: 'Test', stats: defaultStats() });
      // Assert
      expect(character.wounds).toBe(0);
    });
  });

  describe('that is in combat', () => {
    let character: Character;

    beforeEach(() => {
      character = new Character({ name: 'Test', stats: defaultStats() });
    });

    describe('that has suffered wounds', () => {
      it('should have current wounds', () => {
        // Act
        character.applyDamage(3);
        // Assert
        expect(character.wounds).toBe(3);
      });
    });

    describe('that has been attacked with the following damage', () => {
      it('should add the attack damage to current wounds', () => {
        // Arrange
        character.applyDamage(2);
        // Act
        character.applyDamage(4);
        // Assert
        expect(character.wounds).toBe(6);
      });
    });
  });
});

// Development fidelity — minimal production code (Character.ts)

interface Stats {
  strength: number;
  agility: number;
  endurance: number;
}

interface CharacterProps {
  name: string;
  stats: Stats;
}

export class Character {
  readonly name: string;
  readonly stats: Stats;
  wounds = 0;

  constructor({ name, stats }: CharacterProps) {
    this.name = name;
    this.stats = stats;
  }

  applyDamage(amount: number): void {
    this.wounds += amount;
  }
}

// Layer boundary mocking example (service layer)

import { VoucherService } from '../VoucherService';
import { VoucherRepository } from '../VoucherRepository';

describe('VoucherService', () => {
  describe('that is creating a voucher', () => {
    let service: VoucherService;
    let mockRepo: jest.Mocked<Pick<VoucherRepository, 'save'>>;

    beforeEach(() => {
      mockRepo = { save: jest.fn().mockResolvedValue(undefined) };
      service = new VoucherService(mockRepo as VoucherRepository);
    });

    it('should persist the voucher when input is valid', async () => {
      // Arrange
      const input = { code: 'ABC-001', campaignId: 'camp-1' };
      // Act
      await service.create(input);
      // Assert
      expect(mockRepo.save).toHaveBeenCalledWith(
        expect.objectContaining({ code: 'ABC-001' })
      );
    });
  });
});
