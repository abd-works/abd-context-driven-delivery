# Graph rule validation

**Generated:** 2026-11-25 20:15:15 UTC
**Project:** abd-cdd-toggle-ui-only
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-toggle-ui-only\.sessions\backlog-in-session-choices\.context\checked-graphs\stories-story-map-20261125T200128\graph.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `cdd_guidance`
- `cdd_guidance/actions`
- `cdd_guidance/align`
- `cdd_guidance/builders`
- `cdd_guidance/catalog`
- `cdd_guidance/context_setup`
- `cdd_guidance/diagnostics`
- `cdd_guidance/patterns`
- `cdd_guidance/practices`
- `harness`
- `harness/.context`
- `harness/agent_tools`
- `harness/annotations`
- `harness/apps`
- `harness/catalog_generator`
- `harness/chat`
- `harness/chat-ui`
- `harness/design_canvas`
- `harness/diagnostics`
- `harness/drawio`
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
- `harness/release`
- `harness/whiteboard`
- `scripts`
- `scripts/names_exist`
- `scripts/unit_guard`
- `space`
- `space/.context`
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
- `story_tests/review-end-to-end-screens`
- `story_tests/review-generated-work-in-file-viewer`
- `tools`
- `tools/.context`
- `tools/drawio_viewer`
- `tools/echo`
- `tools/error_display`
- `tools/granola`
- `tools/prompt_log`
- `tools/prompt_notify`
- `tools/prompt_queue`
- `tools/sub_agent`

## Summary

**Total graph violations:** 31
**Rules with graph hits:** 2
**Candidates for the judge to read:** 3. A rule that requires a judge listed each; none is a violation until the judge reads it and fails it.
**AI rules in scope:** 12

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6). A hit marked `**CANDIDATE**` comes from a rule that requires a judge: its check only lists places to read, so read each and fail the rule only where the reading finds it broken.

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `verb-noun-format`

Rule text: [stories/stories.md:83](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L83)

### `story-name-captures-system-mechanic`

Rule text: [stories/stories.md:84](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L84)

**Candidates for the judge to read:** 2

- [?] **CANDIDATE** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L690): Story `Run Chosen Formats`: Story 'Run Chosen Formats' opens with a generic verb; judge from its context whether it hides the system mechanic (e.g. 'Submit Order').
- [?] **CANDIDATE** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L2836): Story `Run Test Tier`: Story 'Run Test Tier' opens with a generic verb; judge from its context whether it hides the system mechanic (e.g. 'Submit Order').

### `child-count-fits-layer`

Rule text: [stories/stories.md:85](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L85)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L684): SubEpic `Generate Fidelity Outputs On Board`: sub-epic 'Generate Fidelity Outputs On Board': 10 children (target 2-9)

### `story-scenarios-at-most-seven`

Rule text: [stories/stories.md:86](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L86)

**Graph violations:** 30

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L374): Story `Display Ticket Card`: story 'Display Ticket Card': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L386): Story `Arrange Board And Details`: story 'Arrange Board And Details': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L390): Story `Display Ticket Details`: story 'Display Ticket Details': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L394): Story `Set Stage WIP Limit`: story 'Set Stage WIP Limit': 9 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L398): Story `Arrange Side Panel`: story 'Arrange Side Panel': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L416): Story `Open Ticket Session`: story 'Open Ticket Session': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L440): Story `Activate Ticket`: story 'Activate Ticket': 11 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L444): Story `Find Ticket Branch And Worktree`: story 'Find Ticket Branch And Worktree': 9 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L452): Story `Restrict Actions To Active Session`: story 'Restrict Actions To Active Session': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L456): Story `Move Ticket`: story 'Move Ticket': 16 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L464): Story `Close Active Session`: story 'Close Active Session': 16 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L480): Story `Write Ticket Handoff`: story 'Write Ticket Handoff': 9 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L490): Story `Add Backlog Item`: story 'Add Backlog Item': 11 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L494): Story `Start Backlog Item`: story 'Start Backlog Item': 11 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L498): Story `Edit Ticket Text`: story 'Edit Ticket Text': 12 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L516): Story `Delete Ticket`: story 'Delete Ticket': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L536): Story `Split Ticket Into Child Tickets`: story 'Split Ticket Into Child Tickets': 9 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L564): Story `Reassign Ticket Parent`: story 'Reassign Ticket Parent': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L584): Story `Display Fidelity Progress`: story 'Display Fidelity Progress': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L588): Story `Open Practice Tile`: story 'Open Practice Tile': 14 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L592): Story `Choose Ticket Practices`: story 'Choose Ticket Practices': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L596): Story `Send Next Fidelity Action`: story 'Send Next Fidelity Action': 12 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L686): Story `Choose Action And Formats`: story 'Choose Action And Formats': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L694): Story `Resolve Fidelity Output Paths`: story 'Resolve Fidelity Output Paths': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L724): Story `Validate Fidelity`: story 'Validate Fidelity': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L732): Story `Open Validation Report`: story 'Open Validation Report': 14 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L736): Story `Fix Report Violations`: story 'Fix Report Violations': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L740): Story `Accept Report Violation`: story 'Accept Report Violation': 15 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L760): Story `List Ticket Files`: story 'List Ticket Files': 9 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L940): Story `Debug A Failure From Chat Bar`: story 'Debug A Failure From Chat Bar': 8 scenarios — story is huge (target 1-7)

### `branch-on-mechanical-uniqueness`

Rule text: [stories/stories.md:87](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L87)

**Candidates for the judge to read:** 1

- [?] **CANDIDATE** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-toggle-ui-only\.context\story-map.md#L152): SubEpic `Take UX Artifacts To Other Formats And Back`: Stories under 'Take UX Artifacts To Other Formats And Back' share the same verb 'take'; split by distinct mechanics or merge.

### `right-size-story-nodes`

Rule text: [stories/stories.md:88](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L88)

### `behaviours-not-build-tasks`

Rule text: [stories/stories.md:89](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L89)

### `kebab-case-paths`

Rule text: [stories/stories.md:90](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L90)

### `story-map-links-to-markdown`

Rule text: [stories/stories.md:91](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L91)

## Judgment — `.context/story-map.md`

Scope: the two stories this ticket adds under Move Work Forward From Chat Bar › Steer Sessions, Show Backlog Items In Session List (line 924) and Start Backlog Item From Session List (line 928). Every graph hit in this report is on a story or sub-epic outside that scope, left as it was by earlier work, and is not judged here.

### `story-map-links-to-markdown` — Fail
- story-map.md:924 `Show Backlog Items In Session List`: written as plain text while its scenarios are in steer_sessions_story.test.md; fixed after this report by linking it to `#story-show-backlog-items-in-session-list`.
- story-map.md:928 `Start Backlog Item From Session List`: the same; fixed by linking it to `#story-start-backlog-item-from-session-list`.

Passes for the two stories: verb-noun-format, story-name-captures-system-mechanic (Show and Start name the operations, Backlog Item and Session List the records), child-count-fits-layer (Steer Sessions holds 9 stories), right-size-story-nodes (showing is the session list's display, starting is one press reaching backlog-item.start then ticket.activate, kept together as the board's way out of the Backlog), behaviours-not-build-tasks, do-not-invent-requirements (both quote the person's request of 2026-11-25), read-all-source-context-in-full (`SessionListView`, `BacklogItem.start`, `root-choice-client.ts` `start` named).
