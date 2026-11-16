/**
 * # @toolset-manifest python -m tools manifest practices.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 *
 * Browser-safe Given/When/Then — no node:test import.
 * PlayDualRunner#collect uses the collector path.
 * Node tests: import story-test-node first (registers testBackend).
 */

let activeCollector = null;
/** @type {{ story(name: string, build: Function): void, scenario(name: string, build: Function): void } | null } */
let testBackend = null;

export function isCollecting() {
  return activeCollector != null;
}

/** Register node:test (or other) backend. Call from story-test-node on load. */
export function setTestBackend(backend) {
  testBackend = backend;
}

/**
 * @param {(mode: string) => void} createStory
 * @param {string} mode
 * @returns {{ name: string, scenarios: object[] }}
 */
export function collect(createStory, mode) {
  const scenarios = [];
  let storyName = "";
  activeCollector = {
    beginStory(name) {
      storyName = name;
    },
    addScenario(scenario) {
      scenarios.push(scenario);
    },
  };
  try {
    createStory(mode);
    return { name: storyName, scenarios };
  } finally {
    activeCollector = null;
  }
}

export function story(name, build) {
  if (activeCollector) {
    activeCollector.beginStory(name);
    build();
    return;
  }
  if (testBackend) {
    return testBackend.story(name, build);
  }
  throw new Error(
    "story() requires PlayDualRunner#collect (browser) or import story-test-node first (node tests)",
  );
}

/**
 * A scenario the runner collected: its Given/When/Then steps, which step plays next, and the inputs and
 * seeded domain values Interactive gives it.
 */
class CollectedScenario {
  constructor(name, build) {
    this.name = name;
    this.steps = [];
    this.index = 0;
    /** @type {Record<string, unknown>} Interactive / Play overrides (e.g. quantity). */
    this.inputs = {};
    /** @type {Record<string, unknown>} Interactive domain carried across stories (cart, …). */
    this.seed = {};
    this._exposeGetter = () => ({});
    this.input = this.input.bind(this);
    this.session = this.session.bind(this);
    build(this._steps());
  }

  /** What the story function's `scenario(name, build)` callback receives to declare its steps. */
  _steps() {
    const declare = (kind) => (label, fn) => this.steps.push({ kind, label, fn });
    return {
      given: declare("given"),
      when: declare("when"),
      then: declare("then"),
      expose: (getter) => {
        this._exposeGetter = getter;
      },
      input: this.input,
      session: this.session,
    };
  }

  input(key, defaultValue) {
    if (key in this.inputs && this.inputs[key] !== undefined && this.inputs[key] !== "") {
      return this.inputs[key];
    }
    return defaultValue;
  }

  /** Prefer live Interactive domain; otherwise factory default (Play / first visit). */
  session(key, defaultValue) {
    if (key in this.seed && this.seed[key] != null) return this.seed[key];
    return typeof defaultValue === "function" ? defaultValue() : defaultValue;
  }

  setInputs(values = {}) {
    Object.assign(this.inputs, values);
  }

  setSeed(values = {}) {
    Object.assign(this.seed, values);
  }

  expose() {
    return this._exposeGetter();
  }

  stepMatching(storySteps, { kind } = {}) {
    const wanted = (storySteps || []).filter((s) => !kind || s.kind === kind);
    for (const wantedStep of wanted) {
      const hit = this.steps.find((s) => s.kind === wantedStep.kind && s.label === wantedStep.label);
      if (hit) return hit;
    }
    return null;
  }

  get currentStep() {
    if (this.index === 0) return this.steps[0] ?? null;
    return this.steps[this.index - 1] ?? null;
  }
}

export function scenario(name, build) {
  if (activeCollector) {
    activeCollector.addScenario(new CollectedScenario(name, build));
    return;
  }
  if (testBackend) {
    return testBackend.scenario(name, build);
  }
  throw new Error(
    "scenario() requires PlayDualRunner#collect (browser) or import story-test-node first (node tests)",
  );
}
