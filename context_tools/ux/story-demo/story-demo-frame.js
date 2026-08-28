/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

export class StoryDemoFrame {
  constructor(controls = []) {
    this.controls = controls;
    this._lastSnapshot = null;
    this._hasTint = false;
  }

  appendControl(control) {
    this.controls.push(control);
    return this;
  }

  controlFor(whenLabel) {
    return this.controls.find((c) =>
      c.story_steps?.some((s) => s.kind === "when" && s.label === whenLabel),
    );
  }

  bind(snapshot) {
    this._lastSnapshot = snapshot;
    for (const control of this.controls) {
      if (!control.bound_field) continue;
      const value = snapshot?.[control.bound_field];
      control.show(value);
    }
  }

  shows(snapshot) {
    if (!this._lastSnapshot) return false;
    return JSON.stringify(this._lastSnapshot) === JSON.stringify(snapshot);
  }

  emphasize(step) {
    for (const control of this.controls) {
      control.clearEmphasis?.();
      if (control.matchesStep?.(step)) {
        control.emphasize();
      }
    }
  }

  clearEmphasis() {
    for (const control of this.controls) {
      control.clearEmphasis?.();
    }
  }

  emphasizedFor(step) {
    return this.controls.some(
      (c) => c.emphasized && c.matchesStep?.(step),
    );
  }

  tintFailed(_result) {
    this._hasTint = true;
    for (const control of this.controls) {
      if (control.emphasized) control.tint?.();
    }
  }

  hasTint() {
    return this._hasTint || this.controls.some((c) => c.tinted);
  }
}
