# Graph rule validation

**Generated:** 2026-11-21 17:54:17 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\stories-acceptance-tests-20261121T175345\graph.json`

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

**No graph rule ran on:** `story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/display_server_health_mark_story.desktop.md`, `story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/open_server_health_panel_story.desktop.md`, `story_tests/move-work-forward-from-chat-bar/see-work-in-chat-bar/display_session_card_story.desktop.md`, `story_tests/move-work-forward-from-chat-bar/see-work-in-chat-bar/select_fidelity_story.desktop.md`, `story_tests/queue-prompts-for-later/build-prompt-queue/open_prompt_queue_story.desktop.md`, `story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/open_stage_files_from_chat_bar_story.desktop.md`. The graph read no node from them, so only the AI rules judge them.
**AI rules in scope:** 39

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `examples-declare-seed-vs-interaction`

Rule text: [stories/stories.md:276](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L276)

### `shared-example-fixtures`

Rule text: [stories/stories.md:277](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L277)

### `seed-state-at-its-real-owner`

Rule text: [stories/stories.md:278](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L278)

### `missed-screen-change-tested-at-its-owner`

Rule text: [stories/stories.md:279](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L279)

### `every-step-captured`

Rule text: [stories/stories.md:280](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L280)

### `separate-test-controls-from-production-contracts`

Rule text: [stories/stories.md:281](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L281)

### `system-stubs-domain-real`

Rule text: [stories/stories.md:282](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L282)

### `assert-domain-behavior-not-seeded-state`

Rule text: [stories/stories.md:283](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L283)

### `infrastructure-in-lifecycle-hooks`

Rule text: [stories/stories.md:284](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L284)

### `inline-simple-gwt-bodies`

Rule text: [stories/stories.md:285](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L285)

### `domain-operations-inline-in-steps`

Rule text: [stories/stories.md:286](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L286)

### `code-steps-invoke-code`

Rule text: [stories/stories.md:287](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L287)

### `extract-assertion-helper`

Rule text: [stories/stories.md:288](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L288)

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

## Judgment — the six desktop story tests

Judged by Lens, who wrote them, on 2026-11-21. No rule fails. The server that ran this validate serves the dev lane's
pin, which does not yet hold the two rules written for this file kind (`desktop-test-repeats-its-scenarios`,
`desktop-step-says-what-to-see`), so they were judged by hand:

- `desktop-test-repeats-its-scenarios`: Pass. Every scenario's name and steps were copied by script from its story's
  `*_story.test.md`; read with the story map, each story holds each scenario once, from its scenarios file.
- `desktop-step-says-what-to-see`: Pass. Every Then, and each And that continues one, has a See line.
- `do-not-invent-requirements`: Pass for the scenarios, which are the existing ones. The Do and See lines are test
  directions written from the chat bar's code and the story map's notes, not from a walk: the first walk is expected
  to correct them where the screen differs.
- The code-shaped rules (fixtures, seeding, stubs, tiers, speed budgets) judge story tests in code and apply to none
  of these files, which hold no code and run in no tier.

The graph read no node from these files at the acceptance tests fidelity: markdown scenarios are read at the scenarios
fidelity, where each desktop scenario is the same scenario its story's scenarios file holds.
