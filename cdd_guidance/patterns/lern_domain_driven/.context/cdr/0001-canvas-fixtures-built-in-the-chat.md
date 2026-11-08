# The LERN canvas fixtures bundle is built in the chat, not through an MCP tool

**Status:** decided, round 6 (finding M10).

## Decision

`LernCanvasFixtures` (`practices/stories/model/claude_design/fixtures.py`) stays a class the Claude Design canvas step runs in the chat's own shell, as the UX practice's `claude_design/story_canvas.md` step 2 says. It is not published as an MCP tool of the LERN pattern.

## Why

- `build` writes an entry beside the user's workspace sources and bundles every shared story and example with Node and esbuild. On a real workspace that takes far longer than the ten seconds an action call is allowed (`act_quickly`), and the one cdd server answers every chat, so a bundle built inside it stops every other chat's calls while it runs, the same stall as a graph build (B10).
- The bundle is built from the user's workspace with the user's Node install, so the chat that works in that workspace is the place it runs; the server would need the workspace's toolchain as well as its files.
- It is used: the canvas step names it, and `fixtures_spec.py` covers the entry it writes, so it is not dead code to delete.

## Consequences

The canvas step names the class and its `build(story_names, out_file)` call; a change to either changes that step in the same commit.
