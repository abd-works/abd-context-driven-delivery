/** Tiny Given / When / Then helpers (Jest/Vitest-style) with Gherkin-style `.and()`. */

export function story(name: string, build: () => void): void {
  describe(name, build)
}

export type StepFn = (label: string, fn: () => void | Promise<void>) => StepChain

export interface StepChain {
  and: StepFn
}

export type BackgroundScope = 'all' | 'each'

export type ScenarioSteps = {
  given: StepFn
  when: StepFn
  then: StepFn
}

export type ScenarioBuild = (steps: ScenarioSteps) => void

export type BackgroundBuild = (steps: { given: StepFn }) => void

type BackgroundRegistration = {
  scope: BackgroundScope
  build: BackgroundBuild
}

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

/** Shared scenario steps plus optional tier-specific When/Then extensions in one scenario. */
export function scenarioShared(
  name: string,
  shared: ScenarioBuild,
  extend?: ScenarioBuild,
): void {
  scenario(name, (steps) => {
    shared(steps)
    extend?.(steps)
  })
}

export function scenario(
  name: string,
  build: ScenarioBuild,
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

/**
 * Register domain stories once; tier spec files replay them with `runStory` /
 * `runScenario` / `runBackground` and optional extensions.
 */
export type StorySuite = {
  defineStory(name: string, build: () => void): void
  defineScenario(name: string, build: ScenarioBuild): void
  defineBackground(name: string, scope: BackgroundScope, build: BackgroundBuild): void
  runStory(name: string): void
  runStories(...names: string[]): void
  runAllStories(): void
  runScenario(name: string, extend?: ScenarioBuild): void
  runBackground(name: string, extend?: BackgroundBuild): void
}

export function createStorySuite(): StorySuite {
  const stories = new Map<string, () => void>()
  const scenarios = new Map<string, ScenarioBuild>()
  const backgrounds = new Map<string, BackgroundRegistration>()

  return {
    defineStory(name, build) {
      stories.set(name, build)
    },

    defineScenario(name, build) {
      scenarios.set(name, build)
    },

    defineBackground(name, scope, build) {
      backgrounds.set(name, { scope, build })
    },

    runStory(name) {
      const build = stories.get(name)
      if (!build) throw new Error(`Story suite: unknown story "${name}"`)
      story(name, build)
    },

    runStories(...names) {
      for (const storyName of names) this.runStory(storyName)
    },

    runAllStories() {
      for (const storyName of stories.keys()) this.runStory(storyName)
    },

    runScenario(name, extend) {
      const shared = scenarios.get(name)
      if (!shared) throw new Error(`Story suite: unknown scenario "${name}"`)
      if (extend) scenarioShared(name, shared, extend)
      else scenario(name, shared)
    },

    runBackground(name, extend) {
      const registration = backgrounds.get(name)
      if (!registration) throw new Error(`Story suite: unknown background "${name}"`)
      background(registration.scope, (steps) => {
        registration.build(steps)
        extend?.(steps)
      })
    },
  }
}

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
