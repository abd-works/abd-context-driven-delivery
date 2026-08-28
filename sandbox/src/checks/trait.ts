/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

// interface ITrait
export class ITrait {
  /** *Trait* is a game trait a check is made against — carries only its rank at this seam. */
  constructor(rank) {}
  get rank() {}
}

// implements ITrait
export class Trait {
  /** *Trait* is a game trait a check is made against — carries only its rank at this seam. */
  constructor(rank) {
    this._rank = rank;
  }

  /** Numeric rank used when resolving checks and comparisons. */
  get rank() {
    return this._rank;
  }
}
