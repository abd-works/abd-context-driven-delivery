# Graph rule validation

**Generated:** 2026-11-25 20:18:56 UTC
**Project:** abd-cdd-toggle-ui-only
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-toggle-ui-only\.sessions\backlog-in-session-choices\.context\checked-graphs\bdd-realization-20261125T200629\graph.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `.context`
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

**Total graph violations:** 9
**Rules with graph hits:** 2
**Candidates for the judge to read:** 1. A rule that requires a judge listed each; none is a violation until the judge reads it and fails it.
**AI rules in scope:** 17

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6). A hit marked `**CANDIDATE**` comes from a rule that requires a judge: its check only lists places to read, so read each and fail the rule only where the reading finds it broken.

### `observable-behavior`

Rule text: [bdd/bdd.md:109](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L109)

### `domain-practice-alignment`

Rule text: [bdd/bdd.md:110](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L110)

### `usage-order-behaviors`

Rule text: [bdd/bdd.md:111](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L111)

### `describe-is-subject-not-internal`

Rule text: [bdd/bdd.md:112](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L112)

### `describe-is-plain-english`

Rule text: [bdd/bdd.md:113](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L113)

### `shared-describe-subject`

Rule text: [bdd/bdd.md:114](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L114)

### `state-not-when`

Rule text: [bdd/bdd.md:115](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L115)

### `nest-by-enabling-events`

Rule text: [bdd/bdd.md:116](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L116)

### `context-setup-expresses-state`

Rule text: [bdd/bdd.md:117](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L117)

### `full-surface-coverage`

Rule text: [bdd/bdd.md:118](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L118)

### `scan-fixture-pair`

Rule text: [bdd/bdd.md:119](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L119)

### `strip-helpers-to-domain-calls`

Rule text: [bdd/bdd.md:245](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L245)

### `full-call-graph-per-observation`

Rule text: [bdd/bdd.md:246](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L246)

### `external-systems-at-their-boundary`

Rule text: [bdd/bdd.md:247](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L247)

### `no-typescript-internals`

Rule text: [bdd/bdd.md:248](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L248)

### `sketch-fidelity`

Rule text: [bdd/bdd.md:249](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L249)

### `hierarchy-preservation`

Rule text: [bdd/bdd.md:250](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L250)

### `layer-isolation`

Rule text: [bdd/bdd.md:334](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L334)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/kanban/kanban_tools_spec.py](C:\dev\abd-cdd-toggle-ui-only\space\kanban\kanban_tools_spec.py#L1): Spec `kanban_tools_spec`: Spec patches infrastructure at import time; isolate layers through ports and adapters.

### `one-assertion-per-test`

Rule text: [bdd/bdd.md:333](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\bdd\bdd.md#L333)

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [space/kanban/kanban_tools_spec.py](C:\dev\abd-cdd-toggle-ui-only\space\kanban\kanban_tools_spec.py#L482): Observation `should refuse a change to that ticket, leaving its file as it was`: Observation 'should refuse a change to that ticket, leaving its file as it was' has 2 expects; use one outcome per it.
- [X] **ERROR** **[graph rule]** - [space/kanban/kanban_tools_spec.py](C:\dev\abd-cdd-toggle-ui-only\space\kanban\kanban_tools_spec.py#L570): Observation `should write no session into the sessions folder itself`: Observation 'should write no session into the sessions folder itself' has 2 expects; use one outcome per it.
- [X] **ERROR** **[graph rule]** - [space/kanban/kanban_tools_spec.py](C:\dev\abd-cdd-toggle-ui-only\space\kanban\kanban_tools_spec.py#L578): Observation `should keep that ticket's title`: Observation "should keep that ticket's title" has 2 expects; use one outcome per it.
- [X] **ERROR** **[graph rule]** - [space/kanban/kanban_tools_spec.py](C:\dev\abd-cdd-toggle-ui-only\space\kanban\kanban_tools_spec.py#L593): Observation `should make no session folder`: Observation 'should make no session folder' has 2 expects; use one outcome per it.
- [X] **ERROR** **[graph rule]** - [space/kanban/kanban_tools_spec.py](C:\dev\abd-cdd-toggle-ui-only\space\kanban\kanban_tools_spec.py#L621): Observation `should keep the first idea's text`: Observation "should keep the first idea's text" has 2 expects; use one outcome per it.
- [X] **ERROR** **[graph rule]** - [space/kanban/kanban_tools_spec.py](C:\dev\abd-cdd-toggle-ui-only\space\kanban\kanban_tools_spec.py#L630): Observation `should write no file without a name`: Observation 'should write no file without a name' has 2 expects; use one outcome per it.
- [X] **ERROR** **[graph rule]** - [space/kanban/kanban_tools_spec.py](C:\dev\abd-cdd-toggle-ui-only\space\kanban\kanban_tools_spec.py#L641): Observation `should keep the idea in the Backlog`: Observation 'should keep the idea in the Backlog' has 2 expects; use one outcome per it.
- [X] **ERROR** **[graph rule]** - [space/kanban/kanban_tools_spec.py](C:\dev\abd-cdd-toggle-ui-only\space\kanban\kanban_tools_spec.py#L1421): Observation `should tell an agent opening a ticket to activate it and work in a chat in its worktree`: Observation 'should tell an agent opening a ticket to activate it and work in a chat in its worktree' has 2 expects; use one outcome per it.

### `stubbed-boundary-has-heavy-coverage`

Rule text: a graph rule, written in no practice document

**Candidates for the judge to read:** 1

- [?] **CANDIDATE** **[graph rule]** - [space/kanban/kanban_tools_spec.py](C:\dev\abd-cdd-toggle-ui-only\space\kanban\kanban_tools_spec.py#L1): Spec `kanban_tools_spec`: space/kanban/kanban_tools_spec.py:736: a unit spec stubs a boundary with patch.object, and no heavy or e2e example has one of its `should` sentences under the subject 'the board tools': run that boundary for real in one.
