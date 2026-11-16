/**
 * # @toolset-manifest python -m tools manifest practices.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 */

import { PlayDualRunner } from "./play-dual-runner/play-dual-runner.js";
import { ExplorerFrame } from "./explorer-frame.js";
import { PaintReflect } from "./paint-reflect.js";
import { StoryDemoFrame } from "./story-demo-frame.js";
import { ThenFeedback } from "./then-feedback.js";

export class StoryDemoPage {
  /**
   * @param {{ mode?: 'Play' | 'Interactive', storyDemoFrame?: StoryDemoFrame, explorerFrame?: ExplorerFrame }} [demoSetup]
   */
  constructor({ mode = "Play", storyDemoFrame, explorerFrame } = {}) {
    this.mode = mode;
    this.storyDemoFrame = storyDemoFrame ?? new StoryDemoFrame();
    this.explorerFrame = explorerFrame ?? new ExplorerFrame();
    this.paintReflect = new PaintReflect(this.storyDemoFrame);
    this.thenFeedback = new ThenFeedback(this.explorerFrame, this.storyDemoFrame);
    this.runner = new PlayDualRunner({
      paintReflect: this.paintReflect,
      thenFeedback: this.thenFeedback,
      storyDemoFrame: this.storyDemoFrame,
      explorerFrame: this.explorerFrame,
    });
    this.story = null;
    this._playNextCount = 0;

    this.explorerFrame.playNextControl.appendInteraction({
      trigger: "click",
      effect: () => {
        this._playNextCount += 1;
        this.runner.playNext();
      },
    });
  }

  /**
   * @param {(collectMode: string) => void} createStory
   * @param {string} collectMode — the mode the story function is collected in
   * @param {{ mode?: 'Play' | 'Interactive', storyDemoFrame?: StoryDemoFrame, explorerFrame?: ExplorerFrame }} [demoSetup]
   */
  static load(createStory, collectMode, demoSetup = {}) {
    const page = new StoryDemoPage(demoSetup);
    page.load(createStory, collectMode);
    return page;
  }

  load(createStory, collectMode) {
    this.story = this.runner.collect(createStory, collectMode);
    this.explorerFrame.showStory(this.story);
    return this.story;
  }

  selectScenario(scenarioIndex) {
    this.runner.start(this.story, scenarioIndex);
    const scenario = this.runner.scenario;
    this.explorerFrame.highlightStep(scenario.steps[0] ?? null);
    this.storyDemoFrame.clearEmphasis();
  }

  /**
   * Push DOM `[data-input-field]` values into the scenario so When/Then can
   * call `input("quantity", 2)` instead of hardcoding Interactive values.
   * @param {ParentNode} [root]
   */
  syncInputsFromDom(root = typeof document !== "undefined" ? document : null) {
    const scenario = this.runner.scenario;
    if (!scenario?.setInputs || !root?.querySelectorAll) return;
    const values = {};
    root.querySelectorAll("[data-input-field]").forEach((element) => {
      const key = element.getAttribute("data-input-field");
      const field = element.matches("input, select, textarea")
        ? element
        : element.querySelector("input, select, textarea");
      if (!key || !field) return;
      values[key] = this._fieldValue(field);
    });
    scenario.setInputs(values);
  }

  _fieldValue(field) {
    if (field.type !== "number") return field.value;
    const number = Number(field.value);
    return Number.isFinite(number) ? number : field.value;
  }

  /**
   * Interactive — product control runs When via story_steps.
   * @returns {boolean} true when a When ran
   */
  onControlTrigger(control, root) {
    if (this.mode !== "Interactive") return false;
    const scenario = this.runner.scenario;
    if (!scenario) return false;
    const whenStep = scenario.stepMatching(control.story_steps, { kind: "when" });
    if (!whenStep) return false;
    this._playGivensBefore(scenario, whenStep);
    this._takeInputs(scenario, control, root);
    whenStep.fn();
    const snapshot = scenario.expose();
    this.paintReflect.apply(snapshot);
    this.storyDemoFrame.bind(snapshot);
    return true;
  }

  /** The shell plays the pending Givens, so Interactive does not need Play next first. */
  _playGivensBefore(scenario, whenStep) {
    const whenIndex = scenario.steps.indexOf(whenStep);
    while (scenario.index < whenIndex) {
      if (scenario.steps[scenario.index]?.kind !== "given") break;
      this.runner.playNext();
    }
  }

  /** Read the page's input fields, then the input the control picks: a list line sets `data-set-input` to its name. */
  _takeInputs(scenario, control, root) {
    this.syncInputsFromDom(root);
    const inputKey = control.inputKey;
    if (inputKey && control.name) {
      scenario.setInputs({ [inputKey]: control.name });
    }
  }

  get playNextInvocations() {
    return this._playNextCount;
  }
}
