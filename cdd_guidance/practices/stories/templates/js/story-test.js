/**
 * Given / When / Then helpers (Vitest, or Jest with globals) with Gherkin-style `.and()`. Copy to
 * tests/story-test.js once per tests/ tree, or into the step library folder when a pattern names one.
 *
 * ```
 * file: tests/story-test.js
 * ```
 */

import { afterAll, beforeAll, beforeEach, describe, it } from "vitest";

export function story(name, build) {
  describe(name, build);
}

/** Active `background('each')` layers — outer index runs before inner. */
const eachBackgroundStack = [];

function snapshotEachBackgroundLayers() {
  return eachBackgroundStack.map((layer) => [...layer]);
}

function makeStep(push) {
  const step = (label, fn) => {
    push(label, fn);
    return { and: step };
  };
  return step;
}

function makeThenStep(push) {
  return (label, fn) => {
    let chainIndex = 0;
    const step = (stepLabel, stepFn) => {
      const prefix = chainIndex === 0 ? "Then" : "And";
      chainIndex++;
      push({ step: `${prefix} ${stepLabel}`, fn: stepFn });
      return { and: step };
    };
    return step(label, fn);
  };
}

/** Shared scenario steps plus optional tier-specific When/Then extensions in one scenario. */
export function scenarioShared(name, shared, extend) {
  scenario(name, (steps) => {
    shared(steps);
    extend?.(steps);
  });
}

export function scenario(name, build) {
  const eachLayers = snapshotEachBackgroundLayers();

  describe(name, () => {
    const givens = [];
    const whens = [];
    const thens = [];

    build({
      given: makeStep((_label, fn) => givens.push(fn)),
      when: makeStep((_label, fn) => whens.push(fn)),
      then: makeThenStep((entry) => thens.push(entry)),
    });

    let setupDone = false;
    beforeEach(async () => {
      if (setupDone) return;
      setupDone = true;
      for (const layer of eachLayers) {
        for (const g of layer) await g();
      }
      for (const g of givens) await g();
      for (const w of whens) await w();
    });

    thens.forEach(({ step, fn }) => {
      it(step, fn);
    });
  });
}

/**
 * Register domain stories once; tier spec files replay them with `runStory` /
 * `runScenario` / `runBackground` and optional extensions.
 */
export function createStorySuite() {
  const stories = new Map();
  const scenarios = new Map();
  const backgrounds = new Map();

  return {
    defineStory(name, build) {
      stories.set(name, build);
    },

    defineScenario(name, build) {
      scenarios.set(name, build);
    },

    defineBackground(name, scope, build) {
      backgrounds.set(name, { scope, build });
    },

    runStory(name) {
      const build = stories.get(name);
      if (!build) throw new Error(`Story suite: unknown story "${name}"`);
      story(name, build);
    },

    runStories(...names) {
      for (const storyName of names) this.runStory(storyName);
    },

    runAllStories() {
      for (const storyName of stories.keys()) this.runStory(storyName);
    },

    runScenario(name, extend) {
      const shared = scenarios.get(name);
      if (!shared) throw new Error(`Story suite: unknown scenario "${name}"`);
      if (extend) scenarioShared(name, shared, extend);
      else scenario(name, shared);
    },

    runBackground(name, extend) {
      const registration = backgrounds.get(name);
      if (!registration) throw new Error(`Story suite: unknown background "${name}"`);
      background(registration.scope, (steps) => {
        registration.build(steps);
        extend?.(steps);
      });
    },
  };
}

/**
 * Background — Given steps shared by every `scenario` (and nested `background`) written inside `build`.
 *
 * - `background('all', …)` (default) — `beforeAll`: runs once for all scenarios in this block. Use for expensive,
 *   read-only setup (seed catalog, stub flags).
 * - `background('each', …)` — runs once at the start of each child scenario (in that scenario's first `beforeEach`,
 *   not before every `it`, so chained `then`/`and` assertions still share the same `when` outcome). Use for fresh
 *   browser sandboxes and other mutable preconditions.
 *
 * Nested backgrounds cascade: an outer `all` runs once through `beforeAll`; each `each` layer registered while a
 * scenario is declared is replayed when that scenario's hook runs.
 */
export function background(scopeOrBuild, maybeBuild) {
  const scope = typeof scopeOrBuild === "string" ? scopeOrBuild : "all";
  const build = typeof scopeOrBuild === "string" ? maybeBuild : scopeOrBuild;

  if (scope === "each") {
    describe("Background (each scenario)", () => {
      const givens = [];
      eachBackgroundStack.push(givens);
      build({ given: makeStep((_label, fn) => givens.push(fn)) });
      afterAll(() => {
        eachBackgroundStack.pop();
      });
    });
    return;
  }

  describe("Background", () => {
    const givens = [];
    build({ given: makeStep((_label, fn) => givens.push(fn)) });
    beforeAll(async () => {
      for (const g of givens) await g();
    });
  });
}
