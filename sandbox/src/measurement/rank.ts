/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

// interface IRank
export class IRank {
  /** *Rank* is a game rank value with measure conversion and handbook rank formulas. */
  constructor(value, measurementsTable) {}
  get value() {}
  get measurementsTable() {}
  toMeasure(dimension) {}
  distanceFrom(timeRank, speedRank) {}
  timeFrom(distanceRank, speedRank) {}
  throwDistance(strengthRank, massRank) {}
}

// implements IRank
export class Rank {
  /** *Rank* is a game rank value with measure conversion and handbook rank formulas. */
  constructor(value, measurementsTable) {
    this._value = Number(value);
    this._measurementsTable = measurementsTable;
  }

  get value() {
    return this._value;
  }

  get measurementsTable() {
    return this._measurementsTable;
  }

  /** Convert this rank to a real-world measure via the measurements table (e.g. lift = mass). */
  toMeasure(dimension) {
    return this._measurementsTable.lookup(this, dimension);
  }

  /** Distance rank = time rank + speed rank. */
  distanceFrom(timeRank, speedRank) {
    return new Rank(
      Number(timeRank.value) + Number(speedRank.value),
      this._measurementsTable,
    );
  }

  /** Time rank = distance rank - speed rank. */
  timeFrom(distanceRank, speedRank) {
    return new Rank(
      Number(distanceRank.value) - Number(speedRank.value),
      this._measurementsTable,
    );
  }

  /** Throw distance rank = strength rank - mass rank. */
  throwDistance(strengthRank, massRank) {
    return new Rank(
      Number(strengthRank.value) - Number(massRank.value),
      this._measurementsTable,
    );
  }

  #addRanks(left, right) {}

  #subtractRanks(left, right) {}
}
