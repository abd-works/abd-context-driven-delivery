/**
 * Given / When / Then helpers (Vitest). Copy to tests/story-test.ts once per tests/ tree.
 *
 * ```
 * file: tests/story-test.ts
 * ```
 */

type WhenChain = {
  and: (s: string, fn: () => void | Promise<void>) => WhenChain;
};

type GivenStep = (s: string, fn: () => void | Promise<void>) => GivenChain;

type GivenChain = {
  and: GivenStep;
};

type ThenChain = {
  and: (s: string, fn: () => void | Promise<void>) => ThenChain;
};

let activeBackgroundGivens: Array<() => void | Promise<void>> = [];

function makeGivenStep(
  push: (fn: () => void | Promise<void>) => void,
): GivenStep {
  const given: GivenStep = (_s, fn) => {
    push(fn);
    return { and: given };
  };
  return given;
}

export function story(name: string, build: () => void): void {
  describe(name, build);
}

export function background(
  build: (steps: { given: GivenStep }) => void,
): void {
  const givens: Array<() => void | Promise<void>> = [];
  build({
    given: makeGivenStep((fn) => givens.push(fn)),
  });
  activeBackgroundGivens = givens;
}

export function scenario(
  name: string,
  build: (steps: {
    given: GivenStep;
    when: (s: string, fn: () => void | Promise<void>) => WhenChain;
    then: (s: string, fn: () => void | Promise<void>) => ThenChain;
  }) => void,
): void {
  describe(name, () => {
    const givens: Array<() => void | Promise<void>> = [];
    const whens: Array<() => void | Promise<void>> = [];
    const thens: Array<{ step: string; fn: () => void | Promise<void> }> = [];
    const pushThen = (s: string, fn: () => void | Promise<void>) => {
      thens.push({ step: s, fn });
    };
    const thenChain: ThenChain = {
      and: (s, fn) => {
        pushThen(s, fn);
        return thenChain;
      },
    };
    const whenChain: WhenChain = {
      and: (s, fn) => {
        whens.push(fn);
        return whenChain;
      },
    };

    build({
      given: makeGivenStep((fn) => givens.push(fn)),
      when: (_s, fn) => {
        whens.push(fn);
        return whenChain;
      },
      then: (s, fn) => {
        pushThen(s, fn);
        return thenChain;
      },
    });

    beforeAll(async () => {
      for (const g of [...activeBackgroundGivens, ...givens]) {
        await g();
      }
      for (const w of whens) {
        await w();
      }
    });

    thens.forEach(({ step, fn }, i) => {
      it(i === 0 ? `Then ${step}` : step, fn);
    });
  });
}
