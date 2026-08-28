/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

export class ThenFeedback {
  constructor(explorerFrame, storyDemoFrame) {
    this._explorer = explorerFrame;
    this._frame = storyDemoFrame;
  }

  apply(result) {
    this._explorer.markStep(result.step, result.ok);
    if (result.ok) {
      this._explorer.clearMessage();
    } else {
      this._explorer.showMessage(result.message);
      this._frame.tintFailed(result);
    }
  }
}
