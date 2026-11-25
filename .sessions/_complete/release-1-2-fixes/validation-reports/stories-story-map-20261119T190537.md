# Graph rule validation

**Generated:** 2026-11-19 19:06:19 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\stories-story-map-20261119T190537\graph.json`

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
- `tools/drawio_viewer`
- `tools/echo`
- `tools/error_display`
- `tools/granola`
- `tools/prompt_log`
- `tools/prompt_notify`
- `tools/prompt_queue`
- `tools/sub_agent`

## Summary

**Total graph violations:** 44
**Rules with graph hits:** 7
**AI rules in scope:** 12

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `verb-noun-format`

Rule text: [stories/stories.md:82](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L82)

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L488): SubEpic `Run Tickets Through Customized Workflow`: SubEpic 'Run Tickets Through Customized Workflow': opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L494): Story `Run Work Type Flows`: Story 'Run Work Type Flows': opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L859): Story `Run Fidelity Action With Overlays`: Story 'Run Fidelity Action With Overlays': opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1409): Story `Manage Increments`: Story 'Manage Increments': opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1417): Story `Manage Increment Stories`: Story 'Manage Increment Stories': opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1812): Story `Run A Scenario's Thens On The Canvas`: Story "Run A Scenario's Thens On The Canvas": opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L2337): Story `Comment On A Story Card`: Story 'Comment On A Story Card': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L2353): Story `Comment On A Story In Story UI`: Story 'Comment On A Story In Story UI': name should start with a verb (got nominalisation).

### `story-name-captures-system-mechanic`

Rule text: [stories/stories.md:83](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L83)

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L494): Story `Run Work Type Flows`: Story 'Run Work Type Flows' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L859): Story `Run Fidelity Action With Overlays`: Story 'Run Fidelity Action With Overlays' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1409): Story `Manage Increments`: Story 'Manage Increments' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1417): Story `Manage Increment Stories`: Story 'Manage Increment Stories' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1812): Story `Run A Scenario's Thens On The Canvas`: Story "Run A Scenario's Thens On The Canvas" names a generic handler; use the system mechanic (e.g. 'Submit Order').

### `child-count-fits-layer`

Rule text: [stories/stories.md:84](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L84)

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L86): Epic `Deliver Work With Context Guidance`: epic 'Deliver Work With Context Guidance': 7 children (target 2-6)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L198): Epic `Move Work Forward From Chat Bar`: epic 'Move Work Forward From Chat Bar': 7 children (target 2-6)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L240): Epic `Move Work Forward On Session Board`: epic 'Move Work Forward On Session Board': 9 children (target 2-6)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L620): Epic `Review Generated Work In File Viewer`: epic 'Review Generated Work In File Viewer': 7 children (target 2-6)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L656): SubEpic `Check CDD Server Health In Chat Bar`: sub-epic 'Check CDD Server Health In Chat Bar': 10 stories (target 2-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L730): SubEpic `Steer Sessions`: sub-epic 'Steer Sessions': 11 stories (target 2-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L776): SubEpic `Guide Work Through Practices In Chat Bar`: sub-epic 'Guide Work Through Practices In Chat Bar': 11 stories (target 2-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L968): SubEpic `Build Prompt Queue`: sub-epic 'Build Prompt Queue': 10 stories (target 2-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1487): SubEpic `Author Story Changes With AI`: sub-epic 'Author Story Changes With AI': 1 stories (target 2-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1577): Epic `Build Design Canvas Screens`: epic 'Build Design Canvas Screens': 8 children (target 2-6)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1860): Epic `Map Work Into Knowledge Graph`: epic 'Map Work Into Knowledge Graph': 9 children (target 2-6)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L2047): SubEpic `Check Nodes Against Graph Rules`: sub-epic 'Check Nodes Against Graph Rules': 8 children (target 2-6)

### `story-scenarios-at-most-seven`

Rule text: [stories/stories.md:85](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L85)

**Graph violations:** 13

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L276): Story `Display Board`: story 'Display Board': 11 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L288): Story `Display Ticket Card`: story 'Display Ticket Card': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L292): Story `Display Ticket Details`: story 'Display Ticket Details': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L312): Story `Open Ticket Session`: story 'Open Ticket Session': 12 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L316): Story `Activate Ticket`: story 'Activate Ticket': 14 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L320): Story `Close Active Session`: story 'Close Active Session': 14 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L350): Story `Add Backlog Item`: story 'Add Backlog Item': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L534): Story `Choose Action And Formats`: story 'Choose Action And Formats': 9 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L692): Story `Open App From Health Panel`: story 'Open App From Health Panel': 12 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L974): Story `Queue Draft Prompt`: story 'Queue Draft Prompt': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1190): Story `View File In Source View`: story 'View File In Source View': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1260): Story `Switch Files App To Graph View`: story 'Switch Files App To Graph View': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1272): Story `Open Several Files From Graph Nodes`: story 'Open Several Files From Graph Nodes': 10 scenarios — story is huge (target 1-7)

### `branch-on-mechanical-uniqueness`

Rule text: [stories/stories.md:86](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L86)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1423): SubEpic `Author Scenarios And Steps`: Stories under 'Author Scenarios And Steps' share the same verb 'add,'; split by distinct mechanics or merge.

### `right-size-story-nodes`

Rule text: [stories/stories.md:87](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L87)

### `behaviours-not-one-time-tasks`

Rule text: [stories/stories.md:88](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L88)

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L518): Story `Check Ticket Branches Once Per Board Build`: Story 'Check Ticket Branches Once Per Board Build' reads like a one-time task, not a repeatable behaviour.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L526): Story `Read Session File Once Per Board Build`: Story 'Read Session File Once Per Board Build' reads like a one-time task, not a repeatable behaviour.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1718): Story `Store Each Screenshot Once By Content Hash`: Story 'Store Each Screenshot Once By Content Hash' reads like a one-time task, not a repeatable behaviour.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L1792): Story `Reattach A Screen Once Its Change Reaches Production`: Story 'Reattach A Screen Once Its Change Reaches Production' reads like a one-time task, not a repeatable behaviour.

### `kebab-case-paths`

Rule text: [stories/stories.md:89](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L89)

### `story-map-links-to-markdown`

Rule text: [stories/stories.md:90](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L90)

### `conforms-to-schema`

Rule text: a graph rule, written in no practice document

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-release-1-2-fixes\.context\story-map.md#L618): SubEpic `Review Files In Viewer`: SubEpic 'Review Files In Viewer' has no decomposedInto relationship to Epic | SubEpic | Story, which the stories practice schema requires.
