/**
 * # @toolset-manifest python -m tools manifest practices.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: practices.clean_engineering.clean_engineering:CleanEngineering
 */

export class StoryDemoFrame {
  constructor(controls = []) {
    this.controls = controls;
    this._lastSnapshot = null;
    this.emphasis = new ControlEmphasis(this);
  }

  appendControl(control) {
    this.controls.push(control);
    return this;
  }

  /** Drop the list-line controls painted for the last story; the page's own controls stay. */
  dropBoundListControls() {
    this.controls = this.controls.filter((control) => !control.fromBoundList);
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
}

/** Which controls of a story demo frame a step emphasizes, and the tint a failed Then leaves on them. */
export class ControlEmphasis {
  constructor(frame) {
    this._frame = frame;
    this._hasTint = false;
  }

  /** Show each control's emphasis and tint on its page element. */
  paint() {
    for (const control of this._frame.controls) control.paintEmphasis?.();
    return this;
  }

  emphasize(step) {
    for (const control of this._frame.controls) {
      control.clearEmphasis?.();
      if (control.matchesStep?.(step)) {
        control.emphasize();
      }
    }
  }

  clear() {
    for (const control of this._frame.controls) {
      control.clearEmphasis?.();
    }
  }

  emphasizedFor(step) {
    return this._frame.controls.some(
      (c) => c.emphasized && c.matchesStep?.(step),
    );
  }

  tintFailed(_result) {
    this._hasTint = true;
    for (const control of this._frame.controls) {
      if (control.emphasized) control.tint?.();
    }
  }

  hasTint() {
    return this._hasTint || this._frame.controls.some((c) => c.tinted);
  }
}
