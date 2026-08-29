/** Tiny Given / When / Then helpers (Jest/Vitest-style). */

declare function describe(name: string, fn: () => void): void;
declare function it(name: string, fn: () => void): void;
declare function beforeAll(fn: () => void): void;

type ThenChain = {
  and: (s: string, fn: () => void) => ThenChain;
};

export function story(name: string, build: () => void): void {
  describe(name, build);
}

export function scenario(
  name: string,
  build: (steps: {
    given: (s: string, fn: () => void) => void;
    when: (s: string, fn: () => void) => void;
    then: (s: string, fn: () => void) => ThenChain;
  }) => void,
): void {
  describe(name, () => {
    const givens: Array<() => void> = [];
    const whens: Array<() => void> = [];
    const thens: Array<{ step: string; fn: () => void }> = [];
    const pushThen = (s: string, fn: () => void) => {
      thens.push({ step: s, fn });
    };
    const chain: ThenChain = {
      and: (s, fn) => {
        pushThen(s, fn);
        return chain;
      },
    };
    build({
      given: (_s, fn) => givens.push(fn),
      when: (_s, fn) => whens.push(fn),
      then: (s, fn) => {
        pushThen(s, fn);
        return chain;
      },
    });
    beforeAll(() => {
      for (const g of givens) g();
      for (const w of whens) w();
    });
    thens.forEach(({ step, fn }, i) => {
      it(i === 0 ? `Then ${step}` : step, fn);
    });
  });
}

export function expect(actual: unknown) {
  return {
    toBe(expected: unknown) {
      if (actual !== expected) {
        throw new Error(`expected ${String(expected)}, got ${String(actual)}`);
      }
    },
    toEqual(expected: unknown) {
      const a = JSON.stringify(actual);
      const e = JSON.stringify(expected);
      if (a !== e) {
        throw new Error(`expected ${e}, got ${a}`);
      }
    },
    toContain(item: unknown) {
      if (typeof actual === "string") {
        if (!actual.includes(String(item))) {
          throw new Error(`expected string to contain ${String(item)}`);
        }
        return;
      }
      if (!(actual as unknown[]).includes(item)) {
        throw new Error(`expected to contain ${String(item)}`);
      }
    },
    not: {
      toBe(expected: unknown) {
        if (actual === expected) {
          throw new Error(`expected not ${String(expected)}`);
        }
      },
      toBeNull() {
        if (actual === null) {
          throw new Error("expected not null");
        }
      },
    },
    toBeNull() {
      if (actual !== null) {
        throw new Error(`expected null, got ${String(actual)}`);
      }
    },
  };
}
