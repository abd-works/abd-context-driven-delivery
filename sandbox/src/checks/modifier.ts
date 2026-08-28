/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

// interface IModifier
export class IModifier {
  /** *Modifier* is a numeric adjustment to a check with a human-readable reason. */
  constructor(amount, reason) {}
  get amount() {}
  get reason() {}
}

// implements IModifier
export class Modifier {
  /** *Modifier* is a numeric adjustment to a check with a human-readable reason. */
  constructor(amount, reason) {
    this._amount = Number(amount);
    this._reason = reason;
  }

  get amount() {
    return this._amount;
  }

  get reason() {
    return this._reason;
  }
}
