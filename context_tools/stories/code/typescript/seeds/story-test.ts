/** Tiny Given / When / Then helpers (Jest/Vitest-style). */

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
