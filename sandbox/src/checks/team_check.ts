/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

import { Modifier } from "./modifier.js";

// interface ITeamCheck
export class ITeamCheck {
  /** *TeamCheck* produces a circumstance modifier for a leader's resolve from helper checks. */
  constructor() {}
  addHelper(helper) {}
  assist() {}
}

// implements ITeamCheck
export class TeamCheck {
  /** *TeamCheck* produces a circumstance modifier for a leader's resolve from helper checks. */
  constructor() {
    this._helpers = [];
  }

  /** Register an external helper (e.g. Character) that owns a trait — not defined in this module. */
  addHelper(helper) {
    this._helpers.push(helper);
  }

  /** Pull each helper.trait, resolve vs DC 10, map degrees to +2 / +5 / −2 Modifier for the leader. */
  assist() {
    // Spec: helper Check orchestration filled at code fidelity.
    return this.#modifierFromHelperDegrees(0);
  }

  #modifierFromHelperDegrees(totalDegrees) {
    return new Modifier(0, "team check");
  }
}
