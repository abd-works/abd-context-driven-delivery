/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

import { Trait } from "../checks/trait.js";
import { Point } from "./point_totals.js";

// interface IDefense — delta only
export class IDefense {
  get linkedAbility() {}
  get boughtRanks() {}
  get rank() {}
}

// implements IDefense
export class Defense extends Trait {
  /**
   * *Defense* is a trait whose rank tracks a linked ability plus bought ranks.
   *
   * rank = linked_ability.rank + bought_ranks.
   * Cost: 1 PP per +1 bought rank. Toughness cannot buy ranks with power points.
   */
  constructor(linkedAbility, boughtRanks = 0) {
    super(null);
    this._linkedAbility = linkedAbility;
    this._boughtRanks = Number(boughtRanks);
  }

  get linkedAbility() {
    return this._linkedAbility;
  }

  get boughtRanks() {
    return this._boughtRanks;
  }

  /** Effective defense rank — linked ability rank plus bought ranks. */
  get rank() {
    const base = Number(
      this._linkedAbility.rank?.value ?? this._linkedAbility.rank,
    );
    return base + this._boughtRanks;
  }
}

// interface IDefenses
export class IDefenses {
  /** *Defenses* is the fixed handbook defense set — named access and iterable over all five. */
  constructor(dodge, parry, fortitude, toughness, will) {}
  get dodge() {}
  get parry() {}
  get fortitude() {}
  get toughness() {}
  get will() {}
  [Symbol.iterator]() {}
  pointContribution() {}
}

// implements IDefenses
export class Defenses {
  /** *Defenses* is the fixed handbook defense set — named access and iterable over all five. */
  constructor(dodge, parry, fortitude, toughness, will) {
    this._dodge = dodge;
    this._parry = parry;
    this._fortitude = fortitude;
    this._toughness = toughness;
    this._will = will;
  }

  get dodge() {
    return this._dodge;
  }
  get parry() {
    return this._parry;
  }
  get fortitude() {
    return this._fortitude;
  }
  get toughness() {
    return this._toughness;
  }
  get will() {
    return this._will;
  }

  *[Symbol.iterator]() {
    yield this._dodge;
    yield this._parry;
    yield this._fortitude;
    yield this._toughness;
    yield this._will;
  }

  /** Power-point total for this container (1 PP per bought defense rank). */
  pointContribution() {
    let amount = 0;
    for (const defense of this) {
      amount += Number(defense.boughtRanks);
    }
    return new Point("defenses", amount);
  }
}
