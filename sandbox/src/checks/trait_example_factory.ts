/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

import { Trait } from "./trait.js";

const examples = {
  strengthRankFive: { rank: 5 },
};

// interface ITraitExampleFactory
export class ITraitExampleFactory {
  /** Loads examples[{example_key}] as Fake | Isolated | Production. */
  loadStrengthRankFive() {}
}

// implements ITraitExampleFactory
export class TraitExampleFactory {
  /**
   * Fake: mock/stub framework creates ITrait; feed examples.
   * Isolated / Production: new Trait(...).
   */
  loadStrengthRankFive({ mode } = { mode: "fake" }) {
    // examples[strengthRankFive] -> ITrait
    const bundle = examples.strengthRankFive;
    if (mode === "fake") {
      const trait = {
        get rank() {
          return bundle.rank;
        },
      };
      return { trait, ...bundle };
    }
    return { trait: new Trait(bundle.rank), ...bundle };
  }
}
