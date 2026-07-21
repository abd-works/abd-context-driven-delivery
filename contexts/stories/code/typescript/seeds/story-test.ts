/** Tiny Given / When / Then helpers (Jest/Vitest-style). */

export function story(name: string, build: () => void): void {
  describe(name, build);
}

export function scenario(
  name: string,
  build: (steps: {
    given: (s: string, fn: () => void) => void;
    when: (s: string, fn: () => void) => void;
    then: (s: string, fn: () => void) => void;
  }) => void,
): void {
  describe(name, () => {
    const givens: Array<() => void> = [];
    const whens: Array<() => void> = [];
    const thens: Array<{ step: string; fn: () => void }> = [];
    build({
      given: (_s, fn) => givens.push(fn),
      when: (_s, fn) => whens.push(fn),
      then: (s, fn) => thens.push({ step: s, fn }),
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
