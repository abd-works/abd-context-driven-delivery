/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

import { StoryDemoControl } from "./control.js";

export class ExplorerFrame {
  constructor() {
    /** @type {{ name: string, scenarios: object[] } | null} */
    this.storyTree = null;
    /** Story map titles (above the active scenario in the explorer). */
    this.storyMap = [];
    this.activeStoryName = null;
    /** When false, story map list is collapsed (active story still shown). */
    this.storyMapExpanded = true;
    this.currentStep = null;
    this.message = null;
    this.stepMarks = [];
    this.playNextControl = new StoryDemoControl({
      name: "playNext",
      label: "Play next",
    });
    this.resetControl = new StoryDemoControl({
      name: "reset",
      label: "Reset",
    });
  }

  /**
   * @param {string[]} titles — story names in map order (shown above the scenario)
   * @param {string | null} [activeTitle]
   */
  bindStoryMap(titles, activeTitle = null) {
    this.storyMap = [...titles];
    this.activeStoryName = activeTitle;
  }

  bindStoryTree(story) {
    this.storyTree = story;
    if (story?.name) this.activeStoryName = story.name;
  }

  shows(name) {
    return this.storyTree?.name === name;
  }

  showsStoryMapAboveScenario() {
    return this.storyMap.length > 0;
  }

  expandStoryMap() {
    this.storyMapExpanded = true;
  }

  collapseStoryMap() {
    this.storyMapExpanded = false;
  }

  toggleStoryMap() {
    this.storyMapExpanded = !this.storyMapExpanded;
    return this.storyMapExpanded;
  }

  isStoryMapExpanded() {
    return this.storyMapExpanded;
  }

  showsStepLabels() {
    const scenarios = this.storyTree?.scenarios ?? [];
    return scenarios.some((s) => (s.steps?.length ?? 0) > 0);
  }

  highlightStep(step) {
    this.currentStep = step;
  }

  currentStepHighlighted() {
    return this.currentStep != null;
  }

  showMessage(message) {
    this.message = message;
  }

  clearMessage() {
    this.message = null;
  }

  messageVisible() {
    return Boolean(this.message);
  }

  markStep(step, ok) {
    this.stepMarks.push({ step, ok });
  }
}
