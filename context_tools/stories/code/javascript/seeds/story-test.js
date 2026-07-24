/**
 * Tiny Given / When / Then helpers — re-exports UX Story Demo play-dual-runner core.
 * For node:test runs, import story-test-node first from:
 *   context_tools/ux/story-demo/play-dual-runner/story-test-node.js
 */

export {
  collect,
  isCollecting,
  scenario,
  setTestBackend,
  story,
} from "../../../../ux/story-demo/play-dual-runner/story-test-core.js";

export { assert } from "../../../../ux/story-demo/play-dual-runner/soft-assert.js";
