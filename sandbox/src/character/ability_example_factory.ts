/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

import { Ability } from "./abilities.js";

const examples = {
  strengthAtRankZero: { abilityName: "strength", rank: 0 },
  strengthAtRankFive: { abilityName: "strength", rank: 5 },
  strengthAtRankNegOne: { abilityName: "strength", rank: -1 },
  strengthDebilitated: { abilityName: "strength", rank: -6 },
};

// interface IAbilityExampleFactory
export class IAbilityExampleFactory {
  /** Loads examples[{example_key}] as Fake | Isolated | Production. */
  loadStrengthAtRankZero() {}
  loadStrengthAtRankFive() {}
  loadStrengthAtRankNegOne() {}
  loadStrengthDebilitated() {}
}

// implements IAbilityExampleFactory
export class AbilityExampleFactory {
  /**
   * Fake: mock/stub framework creates IAbility; feed examples.
   * Isolated: new Ability(...ctor-injected mocks/stubs...).
   * Production: new Ability(...real collaborators...).
   */
  loadStrengthAtRankZero({ mode } = { mode: "fake" }) {
    return this.#load(examples.strengthAtRankZero, mode);
  }

  loadStrengthAtRankFive({ mode } = { mode: "fake" }) {
    return this.#load(examples.strengthAtRankFive, mode);
  }

  loadStrengthAtRankNegOne({ mode } = { mode: "fake" }) {
    return this.#load(examples.strengthAtRankNegOne, mode);
  }

  loadStrengthDebilitated({ mode } = { mode: "fake" }) {
    return this.#load(examples.strengthDebilitated, mode);
  }

  #load(bundle, mode) {
    // examples[{example_key}] -> IAbility
    if (mode === "fake") {
      const ability = {
        get rank() {
          return bundle.rank;
        },
        get absent() {
          return false;
        },
        get debilitated() {
          return Number(bundle.rank) < -5;
        },
      };
      return { ability, ...bundle };
    }

    return { ability: new Ability(bundle.rank), ...bundle };
  }
}
