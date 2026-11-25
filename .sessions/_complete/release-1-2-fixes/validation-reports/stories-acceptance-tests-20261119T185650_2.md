# Graph rule validation

**Generated:** 2026-11-19 18:57:30 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\stories-acceptance-tests-20261119T185650\graph.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `.context`
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

**Total graph violations:** 161
**Rules with graph hits:** 6
**AI rules in scope:** 78

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `examples-declare-seed-vs-interaction`

Rule text: [stories/stories.md:237](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L237)

### `shared-example-fixtures`

Rule text: [stories/stories.md:238](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L238)

### `seed-state-at-its-real-owner`

Rule text: [stories/stories.md:239](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L239)

### `missed-screen-change-tested-at-its-owner`

Rule text: [stories/stories.md:240](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L240)

### `every-step-captured`

Rule text: [stories/stories.md:241](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L241)

### `separate-test-controls-from-production-contracts`

Rule text: [stories/stories.md:242](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L242)

### `system-stubs-domain-real`

Rule text: [stories/stories.md:243](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L243)

### `assert-domain-behavior-not-seeded-state`

Rule text: [stories/stories.md:244](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L244)

### `infrastructure-in-lifecycle-hooks`

Rule text: [stories/stories.md:245](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L245)

### `inline-simple-gwt-bodies`

Rule text: [stories/stories.md:246](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L246)

### `domain-operations-inline-in-steps`

Rule text: [stories/stories.md:247](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L247)

### `code-steps-invoke-code`

Rule text: [stories/stories.md:248](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L248)

**Graph violations:** 24

- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L79): When `when the Person presses Update`: When 'when the Person presses Update' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L130): When `when the session board reads the board`: When 'when the session board reads the board' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L138): When `when the Person tags broken's session with billing`: When "when the Person tags broken's session with billing" calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L44): When `when the Person activates billing-report again`: When 'when the Person activates billing-report again' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L74): When `when the Person activates checkout-flow`: When 'when the Person activates checkout-flow' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L81): When `when the Person activates checkout-flow`: When 'when the Person activates checkout-flow' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L90): When `when the Person activates checkout-flow`: When 'when the Person activates checkout-flow' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L101): When `when the Person activates billing-report`: When 'when the Person activates billing-report' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L109): When `when the Person activates customer-order-history-export-weekly`: When 'when the Person activates customer-order-history-export-weekly' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L119): When `when the Person activates billing-report`: When 'when the Person activates billing-report' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L129): When `when three chats activate billing-report at the same moment`: When 'when three chats activate billing-report at the same moment' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L111): When `when the Person adds an idea titled Gift cards with another text`: When 'when the Person adds an idea titled Gift cards with another text' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L121): When `when the Person adds an idea whose title is empty, or 日本語`: When 'when the Person adds an idea whose title is empty, or 日本語' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L133): When `when the Person starts that idea`: When 'when the Person starts that idea' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\archive-ticket\archive_ticket_story.test.py#L42): When `when the Person archives pet-visits`: When 'when the Person archives pet-visits' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L143): When `when the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree`: When 'when the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L157): When `when the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree`: When 'when the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L173): When `when the Person closes checkout-flow, deleting its worktree`: When 'when the Person closes checkout-flow, deleting its worktree' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L179): When `when that program has ended and the Person activates checkout-flow`: When 'when that program has ended and the Person activates checkout-flow' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L45): When `when the session board draws its header`: When 'when the session board draws its header' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L104): When `when the Person opens a new ticket whose title is empty, or 日本語`: When 'when the Person opens a new ticket whose title is empty, or 日本語' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L114): When `when the Person opens a new ticket titled PET VISITS`: When 'when the Person opens a new ticket titled PET VISITS' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L120): When `when the Person opens a new ticket titled main`: When 'when the Person opens a new ticket titled main' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L128): When `when the Person opens a new ticket whose title makes a name longer than 64 characters`: When 'when the Person opens a new ticket whose title makes a name longer than 64 characters' calls nothing: call the domain operation it tests in the step.

### `extract-assertion-helper`

Rule text: [stories/stories.md:249](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L249)

### `suffix-names-the-tier`

Rule text: [tdd/tdd.md:126](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L126)

### `unit-tier-fakes-every-boundary`

Rule text: [tdd/tdd.md:127](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L127)

### `heavy-tier-holds-a-real-resource`

Rule text: [tdd/tdd.md:128](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L128)

### `e2e-tier-drives-browser-or-agent`

Rule text: [tdd/tdd.md:129](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L129)

### `slow-example-moves-not-the-file`

Rule text: [tdd/tdd.md:130](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L130)

### `no-skipped-or-empty-test`

Rule text: [tdd/tdd.md:131](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L131)

### `unit-example-within-100-ms`

Rule text: [tdd/tdd.md:134](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L134)

### `unit-file-within-2-seconds`

Rule text: [tdd/tdd.md:135](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L135)

### `unit-tier-within-25-seconds`

Rule text: [tdd/tdd.md:136](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L136)

### `specs-run-in-parallel`

Rule text: [tdd/tdd.md:137](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L137)

### `heavy-spec-owns-its-resources`

Rule text: [tdd/tdd.md:138](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L138)

### `expensive-fixture-built-once`

Rule text: [tdd/tdd.md:139](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L139)

### `no-wait-in-unit-test`

Rule text: [tdd/tdd.md:140](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L140)

### `noise-is-fixed-in-the-harness`

Rule text: [tdd/tdd.md:141](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L141)

### `budget-never-raised`

Rule text: [tdd/tdd.md:142](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L142)

### `stubbed-boundary-has-heavy-coverage`

Rule text: [tdd/tdd.md:145](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L145)

### `heavy-example-has-a-stubbed-twin`

Rule text: [tdd/tdd.md:146](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L146)

### `heavy-run-within-the-hour`

Rule text: [tdd/tdd.md:149](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L149)

### `e2e-run-within-the-day`

Rule text: [tdd/tdd.md:150](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L150)

### `every-run-reviewed`

Rule text: [tdd/tdd.md:151](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L151)

### `missed-change-adds-a-test-first`

Rule text: [tdd/tdd.md:152](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L152)

### `release-follows-a-green-e2e`

Rule text: [tdd/tdd.md:153](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L153)

### `person-accepts-the-baseline`

Rule text: [tdd/tdd.md:154](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L154)

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `examples-declare-seed-vs-interaction`

Rule text: [stories/stories.md:237](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L237)

### `shared-example-fixtures`

Rule text: [stories/stories.md:238](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L238)

### `seed-state-at-its-real-owner`

Rule text: [stories/stories.md:239](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L239)

### `missed-screen-change-tested-at-its-owner`

Rule text: [stories/stories.md:240](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L240)

### `every-step-captured`

Rule text: [stories/stories.md:241](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L241)

### `separate-test-controls-from-production-contracts`

Rule text: [stories/stories.md:242](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L242)

### `system-stubs-domain-real`

Rule text: [stories/stories.md:243](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L243)

### `assert-domain-behavior-not-seeded-state`

Rule text: [stories/stories.md:244](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L244)

### `infrastructure-in-lifecycle-hooks`

Rule text: [stories/stories.md:245](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L245)

### `inline-simple-gwt-bodies`

Rule text: [stories/stories.md:246](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L246)

### `domain-operations-inline-in-steps`

Rule text: [stories/stories.md:247](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L247)

### `code-steps-invoke-code`

Rule text: [stories/stories.md:248](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L248)

**Graph violations:** 24

- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L79): When `when the Person presses Update`: When 'when the Person presses Update' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L130): When `when the session board reads the board`: When 'when the session board reads the board' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L138): When `when the Person tags broken's session with billing`: When "when the Person tags broken's session with billing" calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L44): When `when the Person activates billing-report again`: When 'when the Person activates billing-report again' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L74): When `when the Person activates checkout-flow`: When 'when the Person activates checkout-flow' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L81): When `when the Person activates checkout-flow`: When 'when the Person activates checkout-flow' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L90): When `when the Person activates checkout-flow`: When 'when the Person activates checkout-flow' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L101): When `when the Person activates billing-report`: When 'when the Person activates billing-report' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L109): When `when the Person activates customer-order-history-export-weekly`: When 'when the Person activates customer-order-history-export-weekly' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L119): When `when the Person activates billing-report`: When 'when the Person activates billing-report' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L129): When `when three chats activate billing-report at the same moment`: When 'when three chats activate billing-report at the same moment' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L111): When `when the Person adds an idea titled Gift cards with another text`: When 'when the Person adds an idea titled Gift cards with another text' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L121): When `when the Person adds an idea whose title is empty, or 日本語`: When 'when the Person adds an idea whose title is empty, or 日本語' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L133): When `when the Person starts that idea`: When 'when the Person starts that idea' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\archive-ticket\archive_ticket_story.test.py#L42): When `when the Person archives pet-visits`: When 'when the Person archives pet-visits' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L143): When `when the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree`: When 'when the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L157): When `when the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree`: When 'when the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L173): When `when the Person closes checkout-flow, deleting its worktree`: When 'when the Person closes checkout-flow, deleting its worktree' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L179): When `when that program has ended and the Person activates checkout-flow`: When 'when that program has ended and the Person activates checkout-flow' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L45): When `when the session board draws its header`: When 'when the session board draws its header' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L104): When `when the Person opens a new ticket whose title is empty, or 日本語`: When 'when the Person opens a new ticket whose title is empty, or 日本語' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L114): When `when the Person opens a new ticket titled PET VISITS`: When 'when the Person opens a new ticket titled PET VISITS' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L120): When `when the Person opens a new ticket titled main`: When 'when the Person opens a new ticket titled main' calls nothing: call the domain operation it tests in the step.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L128): When `when the Person opens a new ticket whose title makes a name longer than 64 characters`: When 'when the Person opens a new ticket whose title makes a name longer than 64 characters' calls nothing: call the domain operation it tests in the step.

### `extract-assertion-helper`

Rule text: [stories/stories.md:249](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L249)

### `suffix-names-the-tier`

Rule text: [tdd/tdd.md:126](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L126)

### `unit-tier-fakes-every-boundary`

Rule text: [tdd/tdd.md:127](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L127)

### `heavy-tier-holds-a-real-resource`

Rule text: [tdd/tdd.md:128](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L128)

### `e2e-tier-drives-browser-or-agent`

Rule text: [tdd/tdd.md:129](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L129)

### `slow-example-moves-not-the-file`

Rule text: [tdd/tdd.md:130](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L130)

### `no-skipped-or-empty-test`

Rule text: [tdd/tdd.md:131](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L131)

### `unit-example-within-100-ms`

Rule text: [tdd/tdd.md:134](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L134)

### `unit-file-within-2-seconds`

Rule text: [tdd/tdd.md:135](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L135)

### `unit-tier-within-25-seconds`

Rule text: [tdd/tdd.md:136](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L136)

### `specs-run-in-parallel`

Rule text: [tdd/tdd.md:137](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L137)

### `heavy-spec-owns-its-resources`

Rule text: [tdd/tdd.md:138](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L138)

### `expensive-fixture-built-once`

Rule text: [tdd/tdd.md:139](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L139)

### `no-wait-in-unit-test`

Rule text: [tdd/tdd.md:140](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L140)

### `noise-is-fixed-in-the-harness`

Rule text: [tdd/tdd.md:141](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L141)

### `budget-never-raised`

Rule text: [tdd/tdd.md:142](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L142)

### `stubbed-boundary-has-heavy-coverage`

Rule text: [tdd/tdd.md:145](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L145)

### `heavy-example-has-a-stubbed-twin`

Rule text: [tdd/tdd.md:146](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L146)

### `heavy-run-within-the-hour`

Rule text: [tdd/tdd.md:149](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L149)

### `e2e-run-within-the-day`

Rule text: [tdd/tdd.md:150](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L150)

### `every-run-reviewed`

Rule text: [tdd/tdd.md:151](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L151)

### `missed-change-adds-a-test-first`

Rule text: [tdd/tdd.md:152](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L152)

### `release-follows-a-green-e2e`

Rule text: [tdd/tdd.md:153](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L153)

### `person-accepts-the-baseline`

Rule text: [tdd/tdd.md:154](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L154)

### `but-marks-missing-state`

Rule text: [stories/stories.md:151](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L151)

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L99): Given `but a person deleted that worktree's folder outside CDD`: But step should mark missing or absent state, not a consequence: "a person deleted that worktree's folder outside CDD".
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\archive-ticket\archive_ticket_story.test.py#L36): Then `but nothing is moved to .sessions/_archive`: But step should mark missing or absent state, not a consequence: 'nothing is moved to .sessions/_archive'.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\steer-ticket-sessions.story.shared.py#L930): Then `but nothing is moved to .sessions/_archive`: But step should mark missing or absent state, not a consequence: 'nothing is moved to .sessions/_archive'.

### `child-count-fits-layer`

Rule text: [stories/stories.md:84](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L84)

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L5): SubEpic `Move Work Forward On Session Board`: sub-epic 'Move Work Forward On Session Board': 1 stories (target 2-9)
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/see-work-on-session-board.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\see-work-on-session-board.story.shared.py#L1): SubEpic `See Work On Session Board`: sub-epic 'See Work On Session Board': 7 children (target 2-6)
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\steer-ticket-sessions.story.shared.py#L1): SubEpic `Steer Ticket Sessions`: sub-epic 'Steer Ticket Sessions': 10 children (target 2-6)

### `conforms-to-schema`

Rule text: a graph rule, written in no practice document

**Graph violations:** 123

- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L31): Then `then the [columns](../../../.context/kanban-model.md#column) read Backlog, Discovery, Specification, Implementation, and Complete, in that order`: Then 'then the [columns](../../../.context/kanban-model.md#column) read Backlog, Discovery, Specification, Implementation, and Complete, in that order' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L33): Then `and each [stage](../../../.context/kanban-model.md#stage--column) shows an In progress list and a Done list`: Then 'and each [stage](../../../.context/kanban-model.md#stage--column) shows an In progress list and a Done list' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L35): Then `and the Discovery [stage](../../../.context/kanban-model.md#stage--column) requires story_map, bounded_context, and ia, each through Generate and Validate`: Then 'and the Discovery [stage](../../../.context/kanban-model.md#stage--column) requires story_map, bounded_context, and ia, each through Generate and Validate' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L45): Then `then a band across the top of the page says The cdd server is not connected`: Then 'then a band across the top of the page says The cdd server is not connected' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L47): Then `and the header offers Update`: Then 'and the header offers Update' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L58): Then `then a toast says cdd board.show failed: JsonFileUnreadable: .sessions/broken/session.json is not a readable JSON object (Expecting property name enclosed in double quotes: line 1 column 2 (char 1))`: Then 'then a toast says cdd board.show failed: JsonFileUnreadable: .sessions/broken/session.json is not a readable JSON object (Expecting property name enclosed in double quotes: line 1 column 2 (char 1))' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L60): Then `but no band says the cdd server is lost`: Then 'but no band says the cdd server is lost' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L71): Then `then the Kanban app is installed again through App.install, which installs its packages and rebuilds its page`: Then 'then the Kanban app is installed again through App.install, which installs its packages and rebuilds its page' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L73): Then `and the page loads again from the new build`: Then 'and the page loads again from the new build' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L83): Then `then a toast says the Kanban install failed, with the reason and the fix`: Then 'then a toast says the Kanban install failed, with the reason and the fix' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L85): Then `and the page keeps running as it was`: Then 'and the page keeps running as it was' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L99): Then `then the session board shows move-me in Discovery's Done even though the older read answered last`: Then 'then the session board shows move-me in Discovery's Done even though the older read answered last' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L111): Then `then a toast says Move me moved to Discovery · Done`: Then 'then a toast says Move me moved to Discovery · Done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L122): Then `then a toast says stories-story-map done on billing-report`: Then 'then a toast says stories-story-map done on billing-report' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L132): Then `then pet-visits shows in Discovery`: Then 'then pet-visits shows in Discovery' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L134): Then `and no column shows broken`: Then 'and no column shows broken' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L136): Then `and the board names .sessions/broken/session.json as a file it could not read, with what is wrong in it`: Then 'and the board names .sessions/broken/session.json as a file it could not read, with what is wrong in it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L140): Then `then the board says .sessions/broken/session.json is not a readable JSON object`: Then 'then the board says .sessions/broken/session.json is not a readable JSON object' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L142): Then `and that file is as it was`: Then 'and that file is as it was' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/see-work-on-session-board.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\see-work-on-session-board.story.shared.py#L100): Then `then the columns read Backlog, Discovery, Specification, Implementation, and Complete, in that order`: Then 'then the columns read Backlog, Discovery, Specification, Implementation, and Complete, in that order' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/see-work-on-session-board.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\see-work-on-session-board.story.shared.py#L104): Then `and each stage shows an In progress list and a Done list`: Then 'and each stage shows an In progress list and a Done list' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/see-work-on-session-board.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\see-work-on-session-board.story.shared.py#L108): Then `and the Discovery stage requires story_map, bounded_context, and ia, each through Generate and Validate`: Then 'and the Discovery stage requires story_map, bounded_context, and ia, each through Generate and Validate' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L27): Then `then billing-report has its own worktree, on the branch billing-report`: Then 'then billing-report has its own worktree, on the branch billing-report' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L29): Then `and the repository's own folder stays on main`: Then 'and the repository's own folder stays on main' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L31): Then `and main is still the session of the chat that activated it`: Then 'and main is still the session of the chat that activated it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L39): Then `then main on origin holds billing-report's session folder`: Then 'then main on origin holds billing-report's session folder' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L46): Then `then billing-report keeps that worktree`: Then 'then billing-report keeps that worktree' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L54): Then `then the answer is billing-report`: Then 'then the answer is billing-report' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L65): Then `then checkout-flow opens in that worktree, creating nothing`: Then 'then checkout-flow opens in that worktree, creating nothing' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L67): Then `and checkout-flow's session records claude/checkout-flow-cef4bc and its worktree`: Then 'and checkout-flow's session records claude/checkout-flow-cef4bc and its worktree' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L76): Then `then checkout-flow's session records claude/checkout-flow-cef4bc and its worktree`: Then 'then checkout-flow's session records claude/checkout-flow-cef4bc and its worktree' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L83): Then `then the Person is told both branches could be checkout-flow's`: Then 'then the Person is told both branches could be checkout-flow's' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L85): Then `and checkout-flow's session records no branch`: Then 'and checkout-flow's session records no branch' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L93): Then `then checkout-flow's session records its own branch checkout-flow`: Then 'then checkout-flow's session records its own branch checkout-flow' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L103): Then `then billing-report has its own worktree again, on the branch billing-report`: Then 'then billing-report has its own worktree again, on the branch billing-report' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L111): Then `then customer-order-history-export-weekly has a worktree of its own, in another folder`: Then 'then customer-order-history-export-weekly has a worktree of its own, in another folder' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L121): Then `then the board says billing-report cannot open in a worktree, naming that folder`: Then 'then the board says billing-report cannot open in a worktree, naming that folder' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L123): Then `and the folder's files are as they were`: Then 'and the folder's files are as they were' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L131): Then `then each is answered billing-report, in the one worktree`: Then 'then each is answered billing-report, in the one worktree' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L27): Then `then the Backlog shows Gift cards with the text Sell gift cards.`: Then 'then the Backlog shows Gift cards with the text Sell gift cards.' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L29): Then `and Gift cards is selected and the form is closed`: Then 'and Gift cards is selected and the form is closed' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L31): Then `and a toast says Gift cards added to Backlog`: Then 'and a toast says Gift cards added to Backlog' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L42): Then `then Add stays off`: Then 'then Add stays off' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L44): Then `and no [backlog item](../../../.context/kanban-model.md#backlogitem--card) is written`: Then 'and no [backlog item](../../../.context/kanban-model.md#backlogitem--card) is written' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L56): Then `then the roots dialog lists the top folders of the repository`: Then 'then the roots dialog lists the top folders of the repository' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L58): Then `and Gift cards is still in the Backlog`: Then 'and Gift cards is still in the Backlog' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L68): Then `then the [ticket](../../../.context/kanban-model.md#ticket--card) gift-cards is In progress in Discovery with root src/visits`: Then 'then the [ticket](../../../.context/kanban-model.md#ticket--card) gift-cards is In progress in Discovery with root src/visits' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L70): Then `and the roots dialog stays open on gift-cards so its practices' roots can be set`: Then 'and the roots dialog stays open on gift-cards so its practices' roots can be set' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L72): Then `and a toast says Gift cards started in Discovery`: Then 'and a toast says Gift cards started in Discovery' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L84): Then `then the [ticket](../../../.context/kanban-model.md#ticket--card) returns-and-refunds is In progress in Discovery`: Then 'then the [ticket](../../../.context/kanban-model.md#ticket--card) returns-and-refunds is In progress in Discovery' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L86): Then `and its session folder holds returns-and-refunds.md, text and all`: Then 'and its session folder holds returns-and-refunds.md, text and all' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L88): Then `and its session log names the item's file`: Then 'and its session log names the item's file' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L90): Then `but the Backlog no longer shows Returns and refunds`: Then 'but the Backlog no longer shows Returns and refunds' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L103): Then `then sign-up is back on the board with its session log and session.json`: Then 'then sign-up is back on the board with its session log and session.json' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L105): Then `but no new ticket is opened`: Then 'but no new ticket is opened' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L113): Then `then the board says the Backlog already keeps an idea in .sessions/_backlog/gift-cards.md`: Then 'then the board says the Backlog already keeps an idea in .sessions/_backlog/gift-cards.md' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L115): Then `and that file still says Sell gift cards.`: Then 'and that file still says Sell gift cards.' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L123): Then `then the board says the title gives no name`: Then 'then the board says the title gives no name' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L125): Then `and no file named .md is written in the Backlog`: Then 'and no file named .md is written in the Backlog' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L135): Then `then the board says a ticket named pet-visits already exists`: Then 'then the board says a ticket named pet-visits already exists' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L137): Then `and the idea stays in the Backlog`: Then 'and the idea stays in the Backlog' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\archive-ticket\archive_ticket_story.test.py#L23): Then `then no [column](../../../.context/kanban-model.md#column) shows pet-visits`: Then 'then no [column](../../../.context/kanban-model.md#column) shows pet-visits' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\archive-ticket\archive_ticket_story.test.py#L25): Then `and its folder is in .sessions/_archive/pet-visits`: Then 'and its folder is in .sessions/_archive/pet-visits' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\archive-ticket\archive_ticket_story.test.py#L34): Then `then the board says no ticket named 'no-such-ticket' on the board`: Then 'then the board says no ticket named 'no-such-ticket' on the board' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\archive-ticket\archive_ticket_story.test.py#L36): Then `but nothing is moved to .sessions/_archive`: Then 'but nothing is moved to .sessions/_archive' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\archive-ticket\archive_ticket_story.test.py#L44): Then `then that work is committed on the branch pet-visits on origin`: Then 'then that work is committed on the branch pet-visits on origin' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\archive-ticket\archive_ticket_story.test.py#L46): Then `and pet-visits's worktree is gone`: Then 'and pet-visits's worktree is gone' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\archive-ticket\archive_ticket_story.test.py#L48): Then `and its folder is in .sessions/_archive/pet-visits`: Then 'and its folder is in .sessions/_archive/pet-visits' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L22): Then `then the chat is sent /space:session:close-session`: Then 'then the chat is sent /space:session:close-session' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L24): Then `and checkout-flow stays In progress in Discovery`: Then 'and checkout-flow stays In progress in Discovery' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L33): Then `then a dialog headed Close session Checkout flow offers commit and push, none chosen`: Then 'then a dialog headed Close session Checkout flow offers commit and push, none chosen' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L42): Then `then checkout-flow shows in Complete and is selected`: Then 'then checkout-flow shows in Complete and is selected' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L44): Then `and a toast says Checkout flow: committed, pushed · Session Checkout flow closed`: Then 'and a toast says Checkout flow: committed, pushed · Session Checkout flow closed' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L46): Then `and main is the active ticket`: Then 'and main is the active ticket' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L59): Then `then nothing is left uncommitted`: Then 'then nothing is left uncommitted' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L61): Then `and the checkout is back on main`: Then 'and the checkout is back on main' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L71): Then `then the checkout is back on main`: Then 'then the checkout is back on main' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L73): Then `and main is the active ticket`: Then 'and main is the active ticket' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L82): Then `then the close dialog offers a handoff, and to commit and push checkout-flow`: Then 'then the close dialog offers a handoff, and to commit and push checkout-flow' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L92): Then `then the close dialog offers to commit and push main`: Then 'then the close dialog offers to commit and push main' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L100): Then `then main on origin holds the commit checkout-flow: leave session`: Then 'then main on origin holds the commit checkout-flow: leave session' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L102): Then `and the checkout is still on main`: Then 'and the checkout is still on main' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L104): Then `and checkout-flow shows in Complete`: Then 'and checkout-flow shows in Complete' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L116): Then `then checkout-flow's folder in .sessions/_complete holds a handoff`: Then 'then checkout-flow's folder in .sessions/_complete holds a handoff' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L118): Then `and the handoff names stories-story-map as what comes next`: Then 'and the handoff names stories-story-map as what comes next' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L131): Then `then checkout-flow shows in Complete`: Then 'then checkout-flow shows in Complete' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L133): Then `and its folder is in .sessions/_complete/checkout-flow`: Then 'and its folder is in .sessions/_complete/checkout-flow' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L135): Then `but checkout-flow's work is not committed`: Then 'but checkout-flow's work is not committed' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L145): Then `then main on origin holds checkout-flow's work`: Then 'then main on origin holds checkout-flow's work' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L147): Then `but main on origin does not hold the edit to README.md`: Then 'but main on origin does not hold the edit to README.md' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L149): Then `and that edit is still uncommitted in the repository's own folder`: Then 'and that edit is still uncommitted in the repository's own folder' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L159): Then `then the board says checkout-flow does not merge into main`: Then 'then the board says checkout-flow does not merge into main' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L161): Then `and main has no merge half done`: Then 'and main has no merge half done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L163): Then `and checkout-flow still has its worktree`: Then 'and checkout-flow still has its worktree' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L165): Then `and checkout-flow stays In progress in Discovery`: Then 'and checkout-flow stays In progress in Discovery' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L175): Then `then the board says the worktree could not be removed, naming its folder`: Then 'then the board says the worktree could not be removed, naming its folder' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L177): Then `and checkout-flow's work is committed on its branch on origin`: Then 'and checkout-flow's work is committed on its branch on origin' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L181): Then `then checkout-flow has its own worktree again`: Then 'then checkout-flow has its own worktree again' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L26): Then `then pet-visits is In progress in Discovery, titled Pet visits`: Then 'then pet-visits is In progress in Discovery, titled Pet visits' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L28): Then `and its next step is Generate on stories-story-map`: Then 'and its next step is Generate on stories-story-map' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L30): Then `and checkout-flow is still the active ticket`: Then 'and checkout-flow is still the active ticket' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L39): Then `then the chat's prompt holds Open a new ticket with ticket.create, titled: for the Person to finish`: Then 'then the chat's prompt holds Open a new ticket with ticket.create, titled: for the Person to finish' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L48): Then `then + Ticket is off`: Then 'then + Ticket is off' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L58): Then `then billing-report's [session](../../../.context/kanban-model.md#session) works in src/billing`: Then 'then billing-report's [session](../../../.context/kanban-model.md#session) works in src/billing' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L60): Then `and the details show its workpath as src/billing`: Then 'and the details show its workpath as src/billing' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L72): Then `then the roots dialog lists src/billing and src/visits`: Then 'then the roots dialog lists src/billing and src/visits' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L78): Then `then checkout-flow's workpath reads src/visits`: Then 'then checkout-flow's workpath reads src/visits' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L80): Then `and each practice's default practice root sits under src/visits`: Then 'and each practice's default practice root sits under src/visits' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L90): Then `then the Stories root reads src/billing, chosen by the Person`: Then 'then the Stories root reads src/billing, chosen by the Person' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L92): Then `and every other practice stays on its default root`: Then 'and every other practice stays on its default root' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L98): Then `then the Stories root is the default again`: Then 'then the Stories root is the default again' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L106): Then `then the board says the title gives no name, naming the title`: Then 'then the board says the title gives no name, naming the title' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L108): Then `and no session file is written in .sessions itself`: Then 'and no session file is written in .sessions itself' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L116): Then `then the board says a ticket named pet-visits already exists`: Then 'then the board says a ticket named pet-visits already exists' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L118): Then `and pet-visits is still titled Pet visits`: Then 'and pet-visits is still titled Pet visits' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L122): Then `then the board says a ticket named main already exists`: Then 'then the board says a ticket named main already exists' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L130): Then `then the board says the title makes too long a name, naming the limit`: Then 'then the board says the title makes too long a name, naming the limit' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L132): Then `and no session folder is made for it`: Then 'and no session folder is made for it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\steer-ticket-sessions.story.shared.py#L405): Then `and the handoff names stories-story-map as what comes next`: Then 'and the handoff names stories-story-map as what comes next' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\steer-ticket-sessions.story.shared.py#L425): Then `then checkout-flow shows in Complete`: Then 'then checkout-flow shows in Complete' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\steer-ticket-sessions.story.shared.py#L434): Then `but checkout-flow's work is not committed`: Then 'but checkout-flow's work is not committed' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\steer-ticket-sessions.story.shared.py#L926): Then `then the board says no ticket named 'no-such-ticket' on the board`: Then 'then the board says no ticket named 'no-such-ticket' on the board' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\steer-ticket-sessions.story.shared.py#L930): Then `but nothing is moved to .sessions/_archive`: Then 'but nothing is moved to .sessions/_archive' has no observes relationship to Example, which the stories practice schema requires.

### `story-scenarios-at-most-seven`

Rule text: [stories/stories.md:85](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L85)

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L19): Story `Display Board`: story 'Display Board': 9 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\activate-ticket\activate_ticket_story.test.py#L18): Story `Activate Ticket`: story 'Activate Ticket': 12 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\add-backlog-item\add_backlog_item_story.test.py#L16): Story `Add Backlog Item`: story 'Add Backlog Item': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\close-active-session\close_active_session_story.test.py#L13): Story `Close Active Session`: story 'Close Active Session': 11 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\open-ticket-session\open_ticket_session_story.test.py#L16): Story `Open Ticket Session`: story 'Open Ticket Session': 9 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\steer-ticket-sessions\steer-ticket-sessions.story.shared.py#L576): Story `Activate Ticket`: story 'Activate Ticket': 8 scenarios — story is huge (target 1-7)

### `when-names-intent-not-interface-gesture`

Rule text: [stories/stories.md:153](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L153)

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L66): When `when the Person presses Update`: When step 'the Person presses Update' names a UI gesture; state the domain intent instead.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-on-session-board\see-work-on-session-board\display-board\display_board_story.test.py#L79): When `when the Person presses Update`: When step 'the Person presses Update' names a UI gesture; state the domain intent instead.
