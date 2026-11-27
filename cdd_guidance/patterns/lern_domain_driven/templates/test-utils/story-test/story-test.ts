/**
 * The LERN story runtime: `shareStory`, `scenario`, `background`, `withStory`, `ctx`, and the Given / When / Then chain
 * with Gherkin-style `.and()` / `.but()`. Vitest runs it by default (globals on); another runner, such as the canvas
 * fixtures, replaces the host with `installStoryHost`. The canvas fixtures need three things from it: the host's
 * `it(name, fn, steps)` receives `{ whens, entries }`, the When steps the Then runs before its body and what each
 * of them enters; `storyBindings()` gives what the steps bound; and `withStory` replays a shared story on the
 * repositories it is given.
 *
 * A When names what the Customer enters as its third argument, `enters`: the objects it binds by name before its
 * action runs, such as `when('the Customer registers valid credentials', register, () => ({ credentials }))`. The
 * When binds them and then acts, so its body reads them through `ctx`; the canvas binds them before the When runs,
 * so the When's screen shows and types what the Customer enters.
 *
 * ```
 * file: test-utils/story-test/story-test.ts
 * ```
 */

/** What a When enters: the objects it binds by name before its action runs. */
export type Entered = () => Record<string, unknown>;

export type StepFn = (label: string, fn: () => void | Promise<void>, enters?: Entered) => StepChain;

export interface StepChain {
  and: StepFn;
  but: StepFn;
}

export type BackgroundScope = 'all' | 'each';

let activeEachBackgrounds: Array<Array<() => void | Promise<void>>> | null = null;

type StoryHost = {
  describe(name: string, fn: () => void): void;
  /**
   * whens: the When steps this Then runs before its own body, in order, so a host can replay a scenario's actions;
   * entries: what each of those Whens enters, where it names it, so a host can show it before the When acts.
   */
  it(name: string, fn: () => void | Promise<void>, steps?: { whens: Array<() => void | Promise<void>>; entries: Array<Entered | undefined> }): void;
  beforeEach(fn: () => void | Promise<void>): void;
  beforeAll(fn: () => void | Promise<void>): void;
  afterAll(fn: () => void | Promise<void>): void;
};

const vitestHost: StoryHost = {
  describe: (name, fn) => describe(name, fn),
  it: (name, fn) => it(name, fn),
  beforeEach: (fn) => beforeEach(fn),
  beforeAll: (fn) => beforeAll(fn),
  afterAll: (fn) => afterAll(fn),
};

let host: StoryHost = vitestHost;

/** Point story, scenario, and when/then at another runner. Vitest is the default. */
export function installStoryHost(next: StoryHost): void {
  host = next;
}

/** Bind a fixture the current when/then can read through `ctx`. */
export function setStoryBinding(name: string, value: unknown): void {
  storyContext[name] = value;
}

/** The fixtures bound for the story running now: withStory's bindings and what its steps bound since. */
export function storyBindings(): Record<string, unknown> {
  return { ...storyContext };
}

/** A Playwright file runs its own story. It does not register a shared story. */
export function stopRegistering(): void {
  registering = false;
}

function currentEachBackgrounds(): Array<Array<() => void | Promise<void>>> {
  return activeEachBackgrounds ?? [];
}

function makeStep(push: (label: string, fn: () => void | Promise<void>, enters?: Entered) => void): StepFn {
  const step: StepFn = (label, fn, enters) => {
    push(label, fn, enters);
    return { and: step, but: step };
  };
  return step;
}

/** Bind what a When enters, so its action and the steps after it read it through `ctx`. */
export function bindEntered(enters: Entered | undefined): void {
  if (!enters) return;
  for (const [name, value] of Object.entries(enters())) setStoryBinding(name, value);
}

function makeThenStep(
  push: (entry: { step: string; fn: () => void | Promise<void> }) => void,
): StepFn {
  return (label, fn) => {
    let chainIndex = 0;
    const step: StepFn = (stepLabel, stepFn) => {
      const prefix = chainIndex === 0 ? 'Then' : 'And';
      chainIndex++;
      push({ step: `${prefix} ${stepLabel}`, fn: stepFn });
      return { and: step, but: step };
    };
    return step(label, fn);
  };
}

function makeAndStep(
  push: (entry: { step: string; fn: () => void | Promise<void> }) => void,
): StepFn {
  const step: StepFn = (label, fn) => {
    push({ step: `And ${label}`, fn });
    return { and: step, but: step };
  };
  return step;
}

export type ScenarioSteps = {
  given: StepFn;
  when: StepFn;
  then: StepFn;
  /** Tier extension steps chained after the shared scenario — always reported as And. */
  and: StepFn;
};

export type ScenarioBuild = (steps: ScenarioSteps) => void;

export type BackgroundBuild = (steps: { given: StepFn }) => void;

type StoryCompositionEntry =
  | { kind: 'scenario'; name: string }
  | { kind: 'background'; scope: BackgroundScope; build: BackgroundBuild };

type RegisteredStory = {
  composition: StoryCompositionEntry[];
  play: (extensions?: Record<string, ScenarioBuild>) => void;
};

const registry = {
  scenarios: new Map<string, ScenarioBuild>(),
  stories: new Map<string, RegisteredStory>(),
};

/** True while a `*.story.shared.ts` file loads — `shareStory` / `scenario` / `background` register only. */
let registering = true;
let composing: StoryCompositionEntry[] | null = null;
let activeStory: string | null = null;
/** The shared story whose scenarios are registering — scenarios are looked up per story, so two stories may share a scenario name. */
let registeringStory: string | null = null;
let storyContext: Record<string, unknown> = {};

function storyScenarioKey(story: string, name: string): string {
  return `${story}::${name}`;
}

/** The shared scenario by name: the active story's own first, then any story's (for tier files outside withStory). */
function lookupScenario(name: string): ScenarioBuild | undefined {
  if (activeStory) {
    const own = registry.scenarios.get(storyScenarioKey(activeStory, name));
    if (own) return own;
  }
  return registry.scenarios.get(name);
}

function createCtxProxy(): Record<string, any> {
  return new Proxy({} as Record<string, any>, {
    get(_target, prop: string | symbol) {
      if (typeof prop !== 'string') return undefined;
      if (!(prop in storyContext)) {
        throw new Error(`Story context: unknown binding "${prop}"`);
      }
      return storyContext[prop];
    },
    set(_target, prop: string | symbol, value: unknown) {
      if (typeof prop !== 'string') return false;
      storyContext[prop] = value;
      return true;
    },
  });
}

/** Named fixtures bound by `withStory` — use anywhere inside shared or tier story steps. */
export const ctx = createCtxProxy();

function withContext(bindings: Record<string, unknown>, run: () => void): void {
  const previousContext = storyContext;
  storyContext = { ...bindings };
  registering = false;
  run();
  storyContext = previousContext;
}

function executeScenario(
  name: string,
  build: ScenarioBuild,
  leadingGivens: Array<() => void | Promise<void>> = [],
): void {
  const backgroundLayers = currentEachBackgrounds();
  host.describe(name, () => {
    const givens: Array<() => void | Promise<void>> = [];
    const whens: Array<() => void | Promise<void>> = [];
    const entries: Array<Entered | undefined> = [];
    const thens: Array<{
      step: string;
      fn: () => void | Promise<void>;
      whens: Array<() => void | Promise<void>>;
      entries: Array<Entered | undefined>;
    }> = [];

    build({
      given: makeStep((_label, fn) => givens.push(fn)),
      when: makeStep((_label, fn, enters) => {
        whens.push(async () => {
          bindEntered(enters);
          await fn();
        });
        entries.push(enters);
      }),
      then: makeThenStep((entry) => thens.push({ ...entry, whens: [...whens], entries: [...entries] })),
      and: makeAndStep((entry) => thens.push({ ...entry, whens: [...whens], entries: [...entries] })),
    });

    host.beforeEach(async () => {
      for (const layer of backgroundLayers) {
        for (const g of layer) await g();
      }
      for (const g of leadingGivens) await g();
      for (const g of givens) await g();
    });

    thens.forEach(({ step, fn, whens: precedingWhens, entries: precedingEntries }) => {
      host.it(step, async () => {
        for (const when of precedingWhens) await when();
        await fn();
      }, { whens: precedingWhens, entries: precedingEntries });
    });
  });
}

export function extendScenario(...builds: ScenarioBuild[]): ScenarioBuild {
  return (steps) => {
    for (const build of builds) build(steps);
  };
}

export function scenarioShared(
  name: string,
  shared: ScenarioBuild,
  extend?: ScenarioBuild,
): void {
  executeScenario(name, (steps) => {
    shared(steps);
    extend?.(steps);
  });
}

function playScenario(name: string, extend?: ScenarioBuild): void {
  const shared = lookupScenario(name);
  if (!shared) throw new Error(`Story registry: unknown scenario "${name}"`);
  if (extend) scenarioShared(name, shared, extend);
  else executeScenario(name, shared);
}

function playStoryComposition(
  composition: StoryCompositionEntry[],
  extensions?: Record<string, ScenarioBuild>,
): void {
  for (const entry of composition) {
    if (entry.kind === 'background') executeBackground(entry.scope, entry.build);
    else playScenario(entry.name, extensions?.[entry.name]);
  }
}

function requireActiveStory(): RegisteredStory {
  if (!activeStory) throw new Error('Story helpers must be called inside withStory()');
  const registered = registry.stories.get(activeStory);
  if (!registered) throw new Error(`Story registry: unknown story "${activeStory}"`);
  return registered;
}

type ScenarioAndFn = {
  (label: string, fn: () => void | Promise<void>): void;
  (build: ScenarioBuild): void;
};

export type ScenarioComposer = {
  and: ScenarioAndFn;
  /** Replay the shared scenario's Givens, then run this When/Then. */
  given: (build: ScenarioBuild) => void;
  run: () => void;
};

export function withScenario(name: string): ScenarioComposer;
export function withScenario(name: string, extend: ScenarioBuild): void;
export function withScenario(name: string, extend?: ScenarioBuild): void | ScenarioComposer {
  if (extend !== undefined) {
    playScenario(name, extend);
    return;
  }
  const and: ScenarioAndFn = (labelOrBuild: string | ScenarioBuild, fn?: () => void | Promise<void>) => {
    if (typeof labelOrBuild === 'function') {
      playScenario(name, labelOrBuild);
      return;
    }
    playScenario(name, ({ and: andStep }) => {
      andStep(labelOrBuild, fn!);
    });
  };

  return {
    and,
    given(build: ScenarioBuild) {
      playScenarioGivens(name, build);
    },
    run: () => playScenario(name),
  };
}

/** Shared Givens only. The registered When and Then stay on the server story. */
function sharedScenarioGivens(name: string): Array<() => void | Promise<void>> {
  const shared = lookupScenario(name);
  if (!shared) {
    throw new Error(`No shared scenario "${name}". Import its *.story.shared.ts file.`);
  }
  const givens: Array<() => void | Promise<void>> = [];
  const skip = makeStep(() => {});
  shared({
    given: makeStep((_label, fn) => givens.push(fn)),
    when: skip,
    then: skip,
    and: skip,
  });
  return givens;
}

function playScenarioGivens(name: string, next: ScenarioBuild): void {
  executeScenario(name, next, sharedScenarioGivens(name));
}

export function scenario(name: string, build?: ScenarioBuild): void {
  if (registering) {
    if (!build) {
      throw new Error(`scenario("${name}") must include steps during story registration`);
    }
    registry.scenarios.set(name, build);
    if (registeringStory) registry.scenarios.set(storyScenarioKey(registeringStory, name), build);
    if (composing) composing.push({ kind: 'scenario', name });
    return;
  }

  if (!build) {
    withScenario(name)?.run();
    return;
  }

  const shared = lookupScenario(name);
  if (shared) scenarioShared(name, shared, build);
  else executeScenario(name, build);
}

/** Register a story and its scenarios for tier specs — does not create tests. */
export function shareStory(name: string, build: () => void): void {
  const previousRegistering = registering;
  const previousRegisteringStory = registeringStory;
  registering = true;
  registeringStory = name;
  composing = [];
  try {
    build();
    const composition = [...composing];
    registry.stories.set(name, {
      composition,
      play(extensions) {
        host.describe(name, () => {
          const previousActive = activeStory;
          activeStory = name;
          playStoryComposition(composition, extensions);
          activeStory = previousActive;
        });
      },
    });
  } finally {
    composing = null;
    registering = previousRegistering;
    registeringStory = previousRegisteringStory;
  }
}

export type StoryComposer = {
  run: () => void;
};

function withStoryContext(name: string, bindings: Record<string, unknown>, run: () => void): void {
  host.describe(name, () => {
    host.beforeEach(() => {
      storyContext = { ...bindings };
      registering = false;
    });
    const previousContext = storyContext;
    const previousActive = activeStory;
    storyContext = { ...bindings };
    registering = false;
    activeStory = name;
    const previousBackgrounds = activeEachBackgrounds;
    activeEachBackgrounds = [];
    try {
      run();
    } finally {
      activeEachBackgrounds = previousBackgrounds;
      activeStory = previousActive;
      storyContext = previousContext;
    }
  });
}

/**
 * Replay a shared story with named context bindings — like `included_context` after `shared_context`.
 *
 * @example
 * withStory('Place Order', domainRepositories()).run();
 *
 * @example
 * withStory('Place Order', nodeRepositories(), () => {
 *   scenario('Customer places an order', ({ given, then }) => { ... });
 *   withScenario('Customer reviews the order').run();
 * });
 */
export function withStory(
  name: string,
  bindings: Record<string, unknown>,
): StoryComposer;
export function withStory(
  name: string,
  bindings: Record<string, unknown>,
  run: () => void,
): void;
export function withStory(
  name: string,
  bindings: Record<string, unknown>,
  run?: () => void,
): void | StoryComposer {
  if (run) {
    withStoryContext(name, bindings, run);
    return;
  }

  return {
    run() {
      const registered = registry.stories.get(name);
      if (!registered) throw new Error(`Story registry: unknown story "${name}"`);
      withStoryContext(name, bindings, () => {
        playStoryComposition(registered.composition);
      });
    },
  };
}

/** Compose and run an inline tier spec (no shared story registry). */
export function story(name: string, build: () => void): void {
  if (registering) {
    shareStory(name, build);
    return;
  }

  host.describe(name, () => {
    activeStory = name;
    build();
    activeStory = null;
  });
}

/** Replay every background and scenario registered on the active shared story. */
export function runAll(): void {
  playStoryComposition(requireActiveStory().composition);
}

/** Replay shared story composition, skipping named scenarios (for tier overrides). */
export function runAllExcept(...exclude: string[]): void {
  const skip = new Set(exclude);
  const { composition } = requireActiveStory();
  for (const entry of composition) {
    if (entry.kind === 'background') executeBackground(entry.scope, entry.build);
    else if (!skip.has(entry.name)) playScenario(entry.name);
  }
}

/** Replay backgrounds registered on the active shared story, optionally extending them. */
export function withBackground(extend?: BackgroundBuild): void {
  const { composition } = requireActiveStory();
  for (const entry of composition) {
    if (entry.kind !== 'background') continue;
    if (extend) {
      executeBackground(entry.scope, (steps) => {
        entry.build(steps);
        extend(steps);
      });
    } else {
      executeBackground(entry.scope, entry.build);
    }
  }
}

function executeBackground(scope: BackgroundScope, build: BackgroundBuild): void {
  if (scope === 'each') {
    const givens: Array<() => void | Promise<void>> = [];
    activeEachBackgrounds?.push(givens);
    host.describe('Background (each scenario)', () => {
      build({ given: makeStep((_label, fn) => givens.push(fn)) });
      // Vitest rejects describe blocks with no tests; givens run from scenario beforeEach.
      host.it('registers per-scenario background givens', () => {});
    });
    return;
  }

  host.describe('Background', () => {
    const givens: Array<() => void | Promise<void>> = [];
    build({ given: makeStep((_label, fn) => givens.push(fn)) });
    host.beforeAll(async () => {
      for (const g of givens) await g();
    });
  });
}

export function background(build: BackgroundBuild): void;
export function background(scope: BackgroundScope, build: BackgroundBuild): void;
export function background(
  scopeOrBuild: BackgroundScope | BackgroundBuild,
  maybeBuild?: BackgroundBuild,
): void {
  if (registering) {
    const scope = typeof scopeOrBuild === 'string' ? scopeOrBuild : 'all';
    const build = typeof scopeOrBuild === 'string' ? maybeBuild! : scopeOrBuild;
    if (!composing) {
      throw new Error('background during story registration must sit inside shareStory()');
    }
    composing.push({ kind: 'background', scope, build });
    return;
  }

  if (typeof scopeOrBuild === 'function') {
    executeBackground('all', scopeOrBuild);
    return;
  }
  executeBackground(scopeOrBuild as BackgroundScope, maybeBuild!);
}

export function runScenario(
  name: string,
  bindings: Record<string, unknown>,
  extend?: ScenarioBuild,
): void {
  withContext(bindings, () => playScenario(name, extend));
}

export function runStory(
  name: string,
  bindings: Record<string, unknown> | unknown[],
  extensions?: Record<string, ScenarioBuild>,
): void {
  const resolvedBindings = Array.isArray(bindings)
    ? Object.fromEntries(bindings.map((fixture, index) => [`fixture${index}`, fixture]))
    : bindings;

  withContext(resolvedBindings, () => {
    const registered = registry.stories.get(name);
    if (!registered) throw new Error(`Story registry: unknown story "${name}"`);
    host.describe(name, () => {
      activeStory = name;
      playStoryComposition(registered.composition, extensions);
      activeStory = null;
    });
  });
}

export function runStories(bindings: Record<string, unknown>, ...names: string[]): void {
  for (const storyName of names) runStory(storyName, bindings);
}

export function runAllStories(bindings: Record<string, unknown>): void {
  withContext(bindings, () => {
    for (const storyName of registry.stories.keys()) {
      const registered = registry.stories.get(storyName)!;
      host.describe(storyName, () => {
        activeStory = storyName;
        playStoryComposition(registered.composition);
        activeStory = null;
      });
    }
  });
}
