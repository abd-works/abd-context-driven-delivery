/**
 * Sandbox convenience — re-exports UX Story Demo play-dual-runner (browser-safe core).
 * Node tests: import story-test-node first to register the describe/it backend.
 */

export {
  collect,
  isCollecting,
  scenario,
  setTestBackend,
  story,
} from "../../context_tools/ux/story-demo/play-dual-runner/story-test-core.js";

export { assert } from "../../context_tools/ux/story-demo/play-dual-runner/soft-assert.js";
