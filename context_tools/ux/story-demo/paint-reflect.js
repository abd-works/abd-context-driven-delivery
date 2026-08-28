/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

export class PaintReflect {
  constructor(storyDemoFrame) {
    this._frame = storyDemoFrame;
  }

  apply(snapshot) {
    this._frame.bind(snapshot);
  }
}
