# play-dual-runner

UX Story Demo submodule — `PlayDualRunner` + browser-safe GWT collect.

## Seam

- `story-test-core` — `story` / `scenario` / `collect` / `expose` (no `node:test`)
- `story-test-node` — registers node:test backend for story files
- `PlayDualRunner.collect` / `start` / `playNext` — owns `steps[]`; soft-fails Then in the browser
- `soft-assert` — browser-safe Then asserts

Home: `context_tools/ux/story-demo/play-dual-runner/`.
