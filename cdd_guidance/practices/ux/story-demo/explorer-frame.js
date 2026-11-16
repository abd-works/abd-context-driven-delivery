/**
 * # @toolset-manifest python -m tools manifest practices.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 */

import { StoryDemoControl } from "./control.js";

/** The story titles the explorer lists above the active scenario, in map order, and whether the list is open. */
export class StoryMapList {
  constructor() {
    this.titles = [];
    this.activeTitle = null;
    /** When false, only the active story's title shows. */
    this.expanded = true;
  }

  /**
   * @param {string[]} titles — story names in map order
   * @param {string | null} [activeTitle]
   */
  show(titles, activeTitle = null) {
    this.titles = [...titles];
    this.activeTitle = activeTitle;
    return this;
  }

  markActive(title) {
    this.activeTitle = title;
    return this;
  }

  expand() {
    this.expanded = true;
    return this;
  }

  toggle() {
    this.expanded = !this.expanded;
    return this.expanded;
  }

  /** The titles to draw: every title while the list is open, otherwise the active one alone. */
  visibleTitles() {
    return this.expanded ? this.titles : this.titles.filter((title) => title === this.activeTitle);
  }
}

export class ExplorerFrame {
  /**
   * @param {{ storyMap?: StoryMapList, playNextControl?: StoryDemoControl }} [parts]
   */
  constructor({ storyMap, playNextControl } = {}) {
    /** @type {{ name: string, scenarios: object[] } | null} */
    this.storyTree = null;
    this.storyMap = storyMap ?? new StoryMapList();
    this.currentStep = null;
    this.message = null;
    this.playNextControl = playNextControl ?? new StoryDemoControl({ name: "playNext", label: "Play next" });
  }

  showStory(story) {
    this.storyTree = story;
    if (story?.name) this.storyMap.markActive(story.name);
    return this;
  }

  shows(name) {
    return this.storyTree?.name === name;
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
}
