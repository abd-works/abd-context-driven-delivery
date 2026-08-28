/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

import { DifficultyClass } from "./difficulty_class.js";

const examples = {
  targetTen: { target: 10 },
};

// interface IDifficultyClassExampleFactory
export class IDifficultyClassExampleFactory {
  loadTargetTen() {}
}

// implements IDifficultyClassExampleFactory
export class DifficultyClassExampleFactory {
  /**
   * Fake: mock/stub framework creates IDifficultyClass; feed examples.
   * Isolated / Production: new DifficultyClass(...).
   */
  loadTargetTen({ mode } = { mode: "fake" }) {
    // examples[targetTen] -> IDifficultyClass
    const bundle = examples.targetTen;
    if (mode === "fake") {
      const difficultyClass = {
        get target() {
          return bundle.target;
        },
      };
      return { difficultyClass, ...bundle };
    }
    return {
      difficultyClass: new DifficultyClass(bundle.target),
      ...bundle,
    };
  }
}
