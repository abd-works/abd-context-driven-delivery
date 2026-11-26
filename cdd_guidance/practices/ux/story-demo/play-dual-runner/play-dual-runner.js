/**
 * # @toolset-manifest python -m tools manifest practices.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 *
 * UX Story Demo — collect / start / playNext. Owns steps[] + expose; not HTML.
 */

import { collect as collectStory } from "./story-test-core.js";

export class PlayDualRunner {
  /**
   * @param {{ thenFeedback?: { apply(result: object): void }, storyDemoFrame?: { emphasis: { emphasize(step: object): void }, bind?(snapshot: object): void }, explorerFrame?: { highlightStep(step: object): void } }} [collaborators]
   */
  constructor(collaborators = {}) {
    this._thenFeedback = collaborators.thenFeedback ?? null;
    this._storyDemoFrame = collaborators.storyDemoFrame ?? null;
    this._explorerFrame = collaborators.explorerFrame ?? null;
    this._story = null;
    this._scenario = null;
  }

  /** @returns {{ name: string, scenarios: object[] }} */
  collect(createStory, mode) {
    this._story = collectStory(createStory, mode);
    return this._story;
  }

  start(story, scenarioIndex) {
    this._story = story;
    this._scenario = story.scenarios[scenarioIndex];
    this._scenario.index = 0;
    return this._scenario;
  }

  get scenario() {
    return this._scenario;
  }

  get story() {
    return this._story;
  }

  playNext() {
    const scenario = this._scenario;
    if (!scenario) {
      throw new Error("PlayDualRunner.start(story, scenarioIndex) required before playNext");
    }
    const step = scenario.steps[scenario.index];
    if (!step) {
      throw new Error("No more steps in scenario");
    }
    const result = this._run(step);
    scenario.index += 1;
    this._reflect(scenario.expose(), step, result);
    return result;
  }

  /** Run one step; a step that throws is a failed result, not a stopped runner. */
  _run(step) {
    try {
      step.fn();
      return { step, ok: true, message: null };
    } catch (err) {
      return { step, ok: false, message: err && err.message ? err.message : String(err) };
    }
  }

  /** Show what the step left behind on both frames, and a Then's result in the explorer. */
  _reflect(snapshot, step, result) {
    this._storyDemoFrame?.bind?.(snapshot);
    this._explorerFrame?.highlightStep(step);
    this._storyDemoFrame?.emphasis.emphasize(step);
    if (step.kind === "then") {
      this._thenFeedback?.apply(result);
    }
  }
}
