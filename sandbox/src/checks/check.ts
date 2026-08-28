/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

import { CheckResult } from "./check_result.js";

class StandardD20 {
  roll() {
    return Math.floor(Math.random() * 20) + 1;
  }
}

// interface ICheck
export class ICheck {
  /** *Check* is an uncertain action resolved by d20 + trait rank + modifiers against a difficulty class. */
  constructor(trait, difficultyClass, dice) {}
  get trait() {}
  get difficultyClass() {}
  get dieRoll() {}
  resolve(modifiers, routine) {}
}

// implements ICheck
export class Check {
  /** *Check* is an uncertain action resolved by d20 + trait rank + modifiers against a difficulty class. */
  constructor(trait, difficultyClass, dice = null) {
    this._trait = trait;
    this._difficultyClass = difficultyClass;
    this._dice = dice ?? new StandardD20();
    this._dieRoll = null;
  }

  get trait() {
    return this._trait;
  }

  get difficultyClass() {
    return this._difficultyClass;
  }

  get dieRoll() {
    return this._dieRoll;
  }

  /**
   * Sum trait rank and modifiers vs difficulty; routine uses die 10; natural 20 adds one degree.
   */
  resolve(modifiers = [], routine = false) {
    this._dieRoll = routine ? 10 : this._dice.roll();
    const traitRank = Number(this._trait.rank?.value ?? this._trait.rank);
    const total =
      this._dieRoll + traitRank + this.#sumModifierAmounts(modifiers);
    let degree = this.#degreeFromMargin(
      total,
      Number(this._difficultyClass.target),
    );
    let succeeded = degree > 0;
    [degree, succeeded] = this.#applyCriticalSuccess(
      this._dieRoll,
      degree,
      succeeded,
    );
    return new CheckResult(succeeded, total, degree);
  }

  #sumModifierAmounts(modifiers) {
    return modifiers.reduce((sum, m) => sum + Number(m.amount), 0);
  }

  #degreeFromMargin(total, difficultyTarget) {
    const diff = total - difficultyTarget;
    if (diff >= 0) {
      return Math.floor(diff / 5) + 1;
    }
    return -(Math.floor(-diff / 5) + 1);
  }

  #applyCriticalSuccess(dieRoll, degree, succeeded) {
    if (dieRoll !== 20) {
      return [degree, succeeded];
    }
    if (degree === -1) {
      degree = 1;
    } else {
      degree += 1;
    }
    return [degree, degree > 0];
  }
}

// interface IOpposedCheck — delta only
export class IOpposedCheck {
  get opposingTrait() {}
  resolve(modifiers, routine, comparison, routineOpposition) {}
}

// implements IOpposedCheck
export class OpposedCheck extends Check {
  /** *OpposedCheck* is a check against another trait — opposed, routine opposition, or comparison. */
  constructor(trait, difficultyClass, opposingTrait, dice = null) {
    super(trait, difficultyClass, dice);
    this._opposingTrait = opposingTrait;
  }

  get opposingTrait() {
    return this._opposingTrait;
  }

  resolve(
    modifiers = [],
    routine = false,
    comparison = false,
    routineOpposition = false,
  ) {
    // Spec: opposed / comparison / routine-opposition paths filled at code fidelity.
    throw new Error("OpposedCheck.resolve not implemented");
  }

  #buildOpposingCheck(opposingTrait) {}

  #breakOpposedTie(leftBonus, rightBonus) {}
}
