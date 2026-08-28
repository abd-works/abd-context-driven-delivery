/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

/** Measurement column on the Measurements Table. */
export const Dimension = Object.freeze({
  MASS: "mass",
  TIME: "time",
  DISTANCE: "distance",
  VOLUME: "volume",
});

// interface IMeasure
export class IMeasure {
  /** *Measure* is a real-world amount in one measurement dimension. */
  constructor(amount, dimension) {}
  get amount() {}
  get dimension() {}
}

// implements IMeasure
export class Measure {
  /** *Measure* is a real-world amount in one measurement dimension. */
  constructor(amount, dimension) {
    this._amount = amount;
    this._dimension = dimension;
  }

  get amount() {
    return this._amount;
  }

  get dimension() {
    return this._dimension;
  }
}
