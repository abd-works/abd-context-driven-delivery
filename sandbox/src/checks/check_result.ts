/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

// interface ICheckResult
export class ICheckResult {
  /** *CheckResult* is the outcome of a resolved check, including graded degree. */
  constructor(succeeded, total, degree) {}
  get succeeded() {}
  get total() {}
  get degree() {}
}

// implements ICheckResult
export class CheckResult {
  /** *CheckResult* is the outcome of a resolved check, including graded degree. */
  constructor(succeeded, total, degree) {
    this._succeeded = Boolean(succeeded);
    this._total = Number(total);
    this._degree = Number(degree);
  }

  get succeeded() {
    return this._succeeded;
  }

  get total() {
    return this._total;
  }

  get degree() {
    return this._degree;
  }
}
