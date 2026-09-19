/** Tiny Given / When / Then helpers (Jest/Vitest-style) with Gherkin-style `.and()`. */

export function story(name: string, build: () => void): void {
  describe(name, build)
}

export type StepFn = (label: string, fn: () => void | Promise<void>) => StepChain

export interface StepChain {
  and: StepFn
}

export type BackgroundScope = 'all' | 'each'

/** Active `background('each')` layers — outer index runs before inner. */
const eachBackgroundStack: Array<Array<() => void | Promise<void>>> = []

function snapshotEachBackgroundLayers(): Array<Array<() => void | Promise<void>>> {
  return eachBackgroundStack.map((layer) => [...layer])
}

function makeStep(push: (label: string, fn: () => void | Promise<void>) => void): StepFn {
  const step: StepFn = (label, fn) => {
    push(label, fn)
    return { and: step }
  }
  return step
}

function makeThenStep(
  push: (entry: { step: string; fn: () => void | Promise<void> }) => void,
): StepFn {
  return (label, fn) => {
    let chainIndex = 0
    const step: StepFn = (stepLabel, stepFn) => {
      const prefix = chainIndex === 0 ? 'Then' : 'And'
      chainIndex++
      push({ step: `${prefix} ${stepLabel}`, fn: stepFn })
      return { and: step }
    }
    return step(label, fn)
  }
}

export function scenario(
  name: string,
  build: (steps: {
    given: StepFn
    when: StepFn
    then: StepFn
  }) => void,
): void {
  const eachLayers = snapshotEachBackgroundLayers()

  describe(name, () => {
    const givens: Array<() => void | Promise<void>> = []
    const whens: Array<() => void | Promise<void>> = []
    const thens: Array<{ step: string; fn: () => void | Promise<void> }> = []

    build({
      given: makeStep((_label, fn) => givens.push(fn)),
      when: makeStep((_label, fn) => whens.push(fn)),
      then: makeThenStep((entry) => thens.push(entry)),
    })

    let setupDone = false
    beforeEach(async () => {
      if (setupDone) return
      setupDone = true
      for (const layer of eachLayers) {
        for (const g of layer) await g()
      }
      for (const g of givens) await g()
      for (const w of whens) await w()
    })

    thens.forEach(({ step, fn }) => {
      it(step, fn)
    })
  })
}

type BackgroundBuild = (steps: { given: StepFn }) => void

/**
 * Background — Given steps shared by every `scenario` (and nested `background`)
 * written inside `build`.
 *
 * - `background('all', …)` (default) — `beforeAll`: runs once for all scenarios
 *   in this block. Use for expensive, read-only setup (seed catalog, stub flags).
 * - `background('each', …)` — runs once at the start of **each** child
 *   scenario (in that scenario's first `beforeEach`, after any parent
 *   `beforeEach` such as sandbox open — not before every `it`, so chained
 *   `then`/`and` assertions still share the same `when` outcome). Use for
 *   fresh browser sandboxes and other mutable preconditions.
 *
 * Nested backgrounds cascade: outer `all` runs once via vitest `beforeAll`;
 * each `each` layer registered while a scenario is declared is replayed when
 * that scenario's hook runs.
 */
export function background(build: BackgroundBuild): void
export function background(scope: BackgroundScope, build: BackgroundBuild): void
export function background(
  scopeOrBuild: BackgroundScope | BackgroundBuild,
  maybeBuild?: BackgroundBuild,
): void {
  const scope: BackgroundScope =
    typeof scopeOrBuild === 'string' ? scopeOrBuild : 'all'
  const build: BackgroundBuild =
    typeof scopeOrBuild === 'string' ? maybeBuild! : scopeOrBuild

  if (scope === 'each') {
    describe('Background (each scenario)', () => {
      const givens: Array<() => void | Promise<void>> = []
      eachBackgroundStack.push(givens)
      build({ given: makeStep((_label, fn) => givens.push(fn)) })
      afterAll(() => {
        eachBackgroundStack.pop()
      })
    })
    return
  }

  describe('Background', () => {
    const givens: Array<() => void | Promise<void>> = []
    build({ given: makeStep((_label, fn) => givens.push(fn)) })
    beforeAll(async () => {
      for (const g of givens) await g()
    })
  })
}
