/**
 * # @toolset-manifest python -m tools manifest practices.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 *
 * Vanilla Control + StoryDemoControl (UX Story Demo submodule).
 */

export class Control {
  constructor({ name, controlType = "button", label = "" } = {}) {
    this.name = name;
    this.controlType = controlType;
    this.label = label;
    this.interactions = [];
  }

  appendInteraction(interaction) {
    this.interactions.push(interaction);
    return this;
  }

  trigger(triggerName) {
    for (const interaction of this.interactions) {
      if (interaction.trigger === triggerName) {
        interaction.effect?.(this);
      }
    }
  }
}

export class StoryDemoControl extends Control {
  constructor({
    name,
    controlType,
    label,
    boundField = null,
    storySteps = [],
    element = null,
    fromBoundList = false,
  } = {}) {
    super({ name, controlType, label });
    this.boundField = boundField;
    this.storySteps = storySteps;
    /** The mockup element this control was read from or painted as; null for a control with no page. */
    this.element = element;
    /** A list line painted from the scenario's exposed list; it is dropped when the next story loads. */
    this.fromBoundList = fromBoundList;
    this.value = undefined;
    this.emphasized = false;
    this.tinted = false;
  }

  /** Read a control from UX-emitted HTML (`data-bound-field`, `data-story-steps`). */
  static fromElement(element) {
    if (!element) return null;
    // The steps are the list the UX map wrote; one that does not read back is a defect to show, not hide.
    const rawSteps = element.getAttribute("data-story-steps");
    const storySteps = rawSteps ? JSON.parse(rawSteps) : [];
    const control = new StoryDemoControl({
      name: element.getAttribute("data-name") || element.textContent?.trim() || "",
      controlType: element.tagName === "BUTTON" ? "button" : element.getAttribute("data-type") || "",
      label: element.textContent?.trim() || "",
      boundField: element.getAttribute("data-bound-field") || null,
      storySteps,
      element,
    });
    const trigger = element.getAttribute("data-trigger");
    if (trigger) {
      control.appendInteraction({
        trigger,
        effect: element.getAttribute("data-effect") || "",
      });
    }
    return control;
  }

  /** The scenario input this control sets to its own name when triggered (`data-set-input`), or null. */
  get inputKey() {
    return this.element?.getAttribute("data-set-input") ?? null;
  }

  /** The screen this control goes to after its When runs (`data-goto`), or null. */
  get destination() {
    return this.element?.getAttribute("data-goto") ?? null;
  }

  /** Call `onClick` whenever the person clicks this control's element. */
  listenForClicks(onClick) {
    this.element?.addEventListener("click", onClick);
    return this;
  }

  /** Show on the element whether the control is emphasized for the current step and tinted by a failed Then. */
  paintEmphasis() {
    this.element?.classList.toggle("emphasized", Boolean(this.emphasized));
    this.element?.classList.toggle("tinted", Boolean(this.tinted));
    return this;
  }

  show(boundValue) {
    this.value = boundValue;
  }

  emphasize() {
    this.emphasized = true;
  }

  clearEmphasis() {
    this.emphasized = false;
  }

  tint() {
    this.tinted = true;
  }

  matchesStep(step) {
    if (!step) return false;
    return this.storySteps.some(
      (s) => s.kind === step.kind && s.label === step.label,
    );
  }
}
