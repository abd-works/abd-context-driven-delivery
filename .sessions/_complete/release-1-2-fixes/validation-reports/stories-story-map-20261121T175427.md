# Graph rule validation

**Generated:** 2026-11-21 17:55:14 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\stories-story-map-20261121T175427\graph.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `cdd_guidance`
- `cdd_guidance/actions`
- `cdd_guidance/builders`
- `cdd_guidance/catalog`
- `cdd_guidance/context_setup`
- `cdd_guidance/patterns`
- `cdd_guidance/practices`
- `harness`
- `harness/agent_tools`
- `harness/annotations`
- `harness/catalog_generator`
- `harness/chat`
- `harness/chat-ui`
- `harness/design_canvas`
- `harness/diagnostics`
- `harness/e2e_review`
- `harness/files_app`
- `harness/git`
- `harness/graph`
- `harness/guidance`
- `harness/guidance_actions`
- `harness/hooks`
- `harness/installation`
- `harness/markdown`
- `harness/mcp`
- `harness/process`
- `harness/whiteboard`
- `scripts`
- `scripts/unit_guard`
- `space`
- `space/kanban`
- `space/repo`
- `space/session`
- `story_tests`
- `story_tests/author-story-maps`
- `story_tests/build-design-canvas-screens`
- `story_tests/connect-sessions-across-channels-and-apps`
- `story_tests/deliver-work-with-context-guidance`
- `story_tests/draw-practice-models-on-claude-whiteboard`
- `story_tests/explore-stories-in-story-ui`
- `story_tests/map-work-into-knowledge-graph`
- `story_tests/move-work-forward-from-chat-bar`
- `story_tests/move-work-forward-on-session-board`
- `story_tests/queue-prompts-for-later`
- `story_tests/register-and-install-toolsets`
- `story_tests/review-generated-work-in-file-viewer`
- `tools`
- `tools/desktop_walk`
- `tools/drawio_viewer`
- `tools/echo`
- `tools/error_display`
- `tools/granola`
- `tools/prompt_log`
- `tools/prompt_notify`
- `tools/prompt_queue`
- `tools/sub_agent`

## Summary

**Total graph violations:** 66
**Rules with graph hits:** 7
**AI rules in scope:** 1

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `story-name-captures-system-mechanic`

Rule text: [stories/stories.md:83](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L83)

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L494): Story `Run Work Type Flows`: Story 'Run Work Type Flows' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L859): Story `Run Fidelity Action With Overlays`: Story 'Run Fidelity Action With Overlays' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1427): Story `Manage Increments`: Story 'Manage Increments' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1435): Story `Manage Increment Stories`: Story 'Manage Increment Stories' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1830): Story `Run A Scenario's Thens On The Canvas`: Story "Run A Scenario's Thens On The Canvas" names a generic handler; use the system mechanic (e.g. 'Submit Order').
