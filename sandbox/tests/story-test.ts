/**
 * Tiny Given / When / Then helpers for node:test (TypeScript).
 */

import { before, describe, it } from "node:test";

export function story(name: string, build: () => void): void {
  describe(name, build);
}

type StepFn = (step: string, fn: () => void) => void;

type ScenarioApi = {
  given: StepFn;
  when: StepFn;
  then: StepFn;
  expose: (fn: () => unknown) => void;
  input: (key: string, defaultValue: unknown) => unknown;
  session: (key: string, defaultValue: unknown) => unknown;
};

export function scenario(
  name: string,
  build: (steps: ScenarioApi) => void,
): void {
  describe(name, () => {
    const givens: Array<() => void> = [];
    const whens: Array<() => void> = [];
    const thens: Array<{ step: string; fn: () => void }> = [];

    build({
      given: (_s, fn) => {
        givens.push(fn);
      },
      when: (_s, fn) => {
        whens.push(fn);
      },
      then: (s, fn) => {
        thens.push({ step: s, fn });
      },
      expose: () => {
        /* Play collect only */
      },
      input: (_key, defaultValue) => defaultValue,
      session: (_key, defaultValue) =>
        typeof defaultValue === "function"
          ? (defaultValue as () => unknown)()
          : defaultValue,
    });

    before(() => {
      for (const g of givens) g();
      for (const w of whens) w();
    });

    thens.forEach(({ step, fn }, i) => {
      it(i === 0 ? `Then ${step}` : step, fn);
    });
  });
}

function fail(message: string): never {
  throw new Error(message);
}

export const assert = {
  ok(value: unknown, message = "expected value to be truthy") {
    if (!value) fail(message);
  },
  equal(actual: unknown, expected: unknown, message?: string) {
    if (actual !== expected) {
      fail(
        message ||
          `expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`,
      );
    }
  },
  deepEqual(actual: unknown, expected: unknown, message?: string) {
    const a = JSON.stringify(actual);
    const b = JSON.stringify(expected);
    if (a !== b) {
      fail(message || `expected ${b}, got ${a}`);
    }
  },
};
