/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

// interface IPoint
export class IPoint {
  /** *Point* is one sourced power-point total contributed by a trait container. */
  constructor(source, amount) {}
  get source() {}
  get amount() {}
}

// implements IPoint
export class Point {
  /** *Point* is one sourced power-point total contributed by a trait container. */
  constructor(source, amount) {
    this._source = source;
    this._amount = Number(amount);
  }

  get source() {
    return this._source;
  }

  get amount() {
    return this._amount;
  }
}

// interface IPointTotals
export class IPointTotals {
  /** *PointTotals* is a collection of sourced power-point totals with a sum invariant on total. */
  constructor(points) {}
  get points() {}
  get total() {}
  refresh(points) {}
}

// implements IPointTotals
export class PointTotals {
  /** *PointTotals* is a collection of sourced power-point totals with a sum invariant on total. */
  constructor(points = null) {
    this._points = points ?? [];
  }

  get points() {
    return this._points;
  }

  /** Sum of all Point.amount values — invariant: total == sum(points.amount). */
  get total() {
    return this._points.reduce((sum, p) => sum + Number(p.amount), 0);
  }

  /** Rebuild points from the character's trait containers after rank mutations. */
  refresh(points) {
    this._points = points ?? [];
  }
}
