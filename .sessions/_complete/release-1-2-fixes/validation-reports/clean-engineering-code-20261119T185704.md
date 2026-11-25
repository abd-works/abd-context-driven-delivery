# Graph rule validation

**Generated:** 2026-11-19 18:58:17 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\stories-acceptance-tests-20261119T185704\graph.json`

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

**Total graph violations:** 151
**Rules with graph hits:** 6
**AI rules in scope:** 102

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

### `vocabulary-traces-to-source`

Rule text: [clean_engineering/clean_engineering.md:18](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L18)

### `do-not-invent-terms`

Rule text: [clean_engineering/clean_engineering.md:19](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L19)

### `do-not-invent-parallel-object-models`

Rule text: [clean_engineering/clean_engineering.md:20](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L20)

### `hide-inner-details`

Rule text: [clean_engineering/clean_engineering.md:233](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L233)

### `hold-state-on-the-object-not-in-parameters`

Rule text: [clean_engineering/clean_engineering.md:243](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L243)

### `keep-operations-small-focused`

Rule text: [clean_engineering/clean_engineering.md:325](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L325)

### `prefer-instance-operations`

Rule text: [clean_engineering/clean_engineering.md:326](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L326)

### `keep-operations-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:241](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L241)

### `simplify-control-flow`

Rule text: [clean_engineering/clean_engineering.md:328](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L328)

### `errors-out-of-existence`

Rule text: [clean_engineering/clean_engineering.md:245](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L245)

### `no-prototype-swapping`

Rule text: [clean_engineering/clean_engineering.md:330](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L330)

### `use-intention-revealing-names`

Rule text: [clean_engineering/clean_engineering.md:258](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L258)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L195): Parameter `to`: Parameter 'to' does not reveal intent.

### `use-consistent-naming`

Rule text: [clean_engineering/clean_engineering.md:259](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L259)

### `provide-meaningful-context`

Rule text: [clean_engineering/clean_engineering.md:335](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L335)

### `eliminate-duplication`

Rule text: [clean_engineering/clean_engineering.md:260](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L260)

### `no-legacy-api-after-refactor`

Rule text: [clean_engineering/clean_engineering.md:337](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L337)

### `use-exceptions-properly`

Rule text: [clean_engineering/clean_engineering.md:340](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L340)

### `never-swallow-exceptions`

Rule text: [clean_engineering/clean_engineering.md:341](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L341)

### `limit-comments`

Rule text: [clean_engineering/clean_engineering.md:248](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L248)

### `source-parses`

Rule text: [clean_engineering/clean_engineering.md:343](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L343)

### `operation-has-a-proving-test`

Rule text: [tdd/tdd.md:162](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L162)

### `class-demonstrated-by-a-test`

Rule text: [tdd/tdd.md:163](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L163)

### `invariant-has-a-failing-case`

Rule text: [tdd/tdd.md:164](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L164)

### `every-branch-taken-by-a-test`

Rule text: [tdd/tdd.md:165](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L165)

### `avoid-vague-parameter-names`

Rule text: [clean_engineering/clean_engineering.md:244](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L244)

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L282): Operation `attach`: Parameter 'data' in 'attach' is vague.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L282): Parameter `data`: Parameter 'data' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L328): Operation `_saved_attachment`: Parameter 'data' in '_saved_attachment' is vague.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L328): Parameter `data`: Parameter 'data' is vague. Use a domain-specific name.

### `conforms-to-schema`

Rule text: a graph rule, written in no practice document

**Graph violations:** 141

- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L112): Then `then the queue holds ++Write the scenarios++, ++Run the unit tier++, then ++Run the heavy tier++`: Then 'then the queue holds ++Write the scenarios++, ++Run the unit tier++, then ++Run the heavy tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L113): Then `and the prompt box is empty`: Then 'and the prompt box is empty' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L119): Then `then the submission is dropped as "Queued for later"`: Then 'then the submission is dropped as "Queued for later"' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L120): Then `and the agent is not sent ++Run the heavy tier++`: Then 'and the agent is not sent ++Run the heavy tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L126): Then `then the submission is dropped as "Queued for later"`: Then 'then the submission is dropped as "Queued for later"' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L133): Then `then the queue still holds only ++Write the scenarios++`: Then 'then the queue still holds only ++Write the scenarios++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L139): Then `then every caller is answered without a refusal`: Then 'then every caller is answered without a refusal' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L140): Then `and the queue holds ++Write the scenarios++, done, then ++Run the unit tier++, then ++Run the heavy tier++ and ++Run the e2e tier++ in the order their callers took their turn`: Then 'and the queue holds ++Write the scenarios++, done, then ++Run the unit tier++, then ++Run the heavy tier++ and ++Run the e2e tier++ in the order their callers took their turn' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L146): Then `then ++reading caller++ is shown ++Write the scenarios++ and ++Run the unit tier++ at the front of the queue every time it reads`: Then 'then ++reading caller++ is shown ++Write the scenarios++ and ++Run the unit tier++ at the front of the queue every time it reads' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L152): Then `then the queue holds ++Run the heavy tier++ at its bottom`: Then 'then the queue holds ++Run the heavy tier++ at its bottom' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L158): Then `then the agent is told the queue's file is held for a change by another caller, with the file's path`: Then 'then the agent is told the queue's file is held for a change by another caller, with the file's path' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L159): Then `and the queue is as it was`: Then 'and the queue is as it was' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L169): Then `then the model is asked where ++also run the heavy tier++ belongs, shown each goal with its id, such as [b] Run the unit tier`: Then 'then the model is asked where ++also run the heavy tier++ belongs, shown each goal with its id, such as [b] Run the unit tier' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L170): Then `and ++Run the unit tier++ has the step "[interruption] Run the heavy tier too", not started`: Then 'and ++Run the unit tier++ has the step "[interruption] Run the heavy tier too", not started' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L171): Then `and the queue still holds two cards`: Then 'and the queue still holds two cards' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L172): Then `and the prompt box is empty`: Then 'and the prompt box is empty' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L180): Then `then the queue ends with Run the heavy tier, given to no robot`: Then 'then the queue ends with Run the heavy tier, given to no robot' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L181): Then `and the model was not asked about robots, which Group Queue Into Robots decides`: Then 'and the model was not asked about robots, which Group Queue Into Robots decides' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L188): Then `then the queue still holds only ++Write the scenarios++ and ++Run the unit tier++`: Then 'then the queue still holds only ++Write the scenarios++ and ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L189): Then `and the prompt box still holds ++also run the heavy tier++`: Then 'and the prompt box still holds ++also run the heavy tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L190): Then `and the failure line shows "The draft was not placed on the queue: the model is busy"`: Then 'and the failure line shows "The draft was not placed on the queue: the model is busy"' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L197): Then `then the queue holds the three numbered items of ++outstanding items++, in order, without their numbers`: Then 'then the queue holds the three numbered items of ++outstanding items++, in order, without their numbers' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L198): Then `and the heading Session roots setup is not queued`: Then 'and the heading Session roots setup is not queued' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L199): Then `and /queue answers "Queued 3 prompt(s)."`: Then 'and /queue answers "Queued 3 prompt(s)."' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L200): Then `and the model is not asked`: Then 'and the model is not asked' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L211): Then `then the queue holds ++Write the scenarios++, then ++Run the unit tier++`: Then 'then the queue holds ++Write the scenarios++, then ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L212): Then `and the queue opens`: Then 'and the queue opens' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L213): Then `and /queue answers "Queued 2 prompt(s) from this conversation."`: Then 'and /queue answers "Queued 2 prompt(s) from this conversation."' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L220): Then `then /queue answers "Queued 0 prompt(s): the model proposed none. It answered: Nothing is left to do."`: Then 'then /queue answers "Queued 0 prompt(s): the model proposed none. It answered: Nothing is left to do."' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L221): Then `and the queue is still empty`: Then 'and the queue is still empty' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L229): Then `then ++Write the scenarios++ lists one attached file`: Then 'then ++Write the scenarios++ lists one attached file' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L230): Then `and that file holds ++screenshot.png++'s bytes, named for the prompt`: Then 'and that file holds ++screenshot.png++'s bytes, named for the prompt' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L236): Then `then it is told no prompt z is on the queue`: Then 'then it is told no prompt z is on the queue' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L242): Then `then the queue beside the prompt lists "1. [a] Write the scenarios (attached, open each: C:/chats/chat-1/attachments/a-1.png)"`: Then 'then the queue beside the prompt lists "1. [a] Write the scenarios (attached, open each: C:/chats/chat-1/attachments/a-1.png)"' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L243): Then `and ++Run the unit tier++ is listed with no files`: Then 'and ++Run the unit tier++ is listed with no files' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L249): Then `then the card of ++Write the scenarios++ shows 📎1`: Then 'then the card of ++Write the scenarios++ shows 📎1' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L250): Then `and the card of ++Run the unit tier++ shows no 📎`: Then 'and the card of ++Run the unit tier++ shows no 📎' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L259): Then `then a card shows for ++Write the scenarios++, then for ++Run the unit tier++`: Then 'then a card shows for ++Write the scenarios++, then for ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L260): Then `and the open queue and each card fill the chat box's width`: Then 'and the open queue and each card fill the chat box's width' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L261): Then `and each card's buttons sit on a solid dark bar over its right end`: Then 'and each card's buttons sit on a solid dark bar over its right end' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L267): Then `then only the stack shows, with its count, 2`: Then 'then only the stack shows, with its count, 2' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L273): Then `then the card of ++Write the scenarios++ shows first, dim`: Then 'then the card of ++Write the scenarios++ shows first, dim' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L274): Then `and the card of ++Run the unit tier++ is not dim`: Then 'and the card of ++Run the unit tier++ is not dim' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L275): Then `and the stack counts 1 prompt still to do`: Then 'and the stack counts 1 prompt still to do' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L282): Then `then the failure line shows failure 1, "The queue did not change: prompt-queue: $.mcp.call: no MCP server plugin:cdd:cdd", from calling prompt-queue.clear on the cdd server, tried as cdd then plugin:cdd:cdd`: Then 'then the failure line shows failure 1, "The queue did not change: prompt-queue: $.mcp.call: no MCP server plugin:cdd:cdd", from calling prompt-queue.clear on the cdd server, tried as cdd then plugin:cdd:cdd' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L283): Then `and the queue box shows no failure line or Fix button of its own`: Then 'and the queue box shows no failure line or Fix button of its own' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L285): Then `then the failure line shows failure 2, so it shows again after Fix or ✕ handled failure 1`: Then 'then the failure line shows failure 2, so it shows again after Fix or ✕ handled failure 1' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L293): Then `then the prompt box holds Run the unit tier`: Then 'then the prompt box holds Run the unit tier' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L294): Then `and the card of ++Run the unit tier++ keeps its place, shaded and marked editing`: Then 'and the card of ++Run the unit tier++ keeps its place, shaded and marked editing' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L301): Then `then the queue holds ++Write the scenarios again++ as a, then ++Run the unit tier++ (b)`: Then 'then the queue holds ++Write the scenarios again++ as a, then ++Run the unit tier++ (b)' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L308): Then `then the queue beside the prompt lists only "1. [b] Run the unit tier"`: Then 'then the queue beside the prompt lists only "1. [b] Run the unit tier"' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L314): Then `then the queue still holds ++Write the scenarios++, then ++Run the unit tier++`: Then 'then the queue still holds ++Write the scenarios++, then ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L322): Then `then the queue holds ++Run the unit tier++, then ++Write the scenarios++`: Then 'then the queue holds ++Run the unit tier++, then ++Write the scenarios++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L330): Then `then the queue holds ++Run the unit tier++, then ++Write the scenarios++`: Then 'then the queue holds ++Run the unit tier++, then ++Write the scenarios++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L338): Then `then the queue holds only ++Write the scenarios++`: Then 'then the queue holds only ++Write the scenarios++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L339): Then `and the queue archive holds one copy, holding ++Run the unit tier++`: Then 'and the queue archive holds one copy, holding ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L345): Then `then the queue holds only ++Run the unit tier++`: Then 'then the queue holds only ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L346): Then `and the queue archive holds one copy, holding ++Write the scenarios++`: Then 'and the queue archive holds one copy, holding ++Write the scenarios++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L352): Then `then the queue is empty`: Then 'then the queue is empty' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L353): Then `and the queue archive holds one copy, holding ++Write the scenarios++ and ++Run the unit tier++`: Then 'and the queue archive holds one copy, holding ++Write the scenarios++ and ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\build-prompt-queue\build_prompt_queue_story.test.md#L360): Then `then .sessions/simple-queue/queue-archive in the ticket's worktree holds one copy`: Then 'then .sessions/simple-queue/queue-archive in the ticket's worktree holds one copy' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L73): Then `then the queue answers ++Write the scenarios++ with those three steps, in that order, none done`: Then 'then the queue answers ++Write the scenarios++ with those three steps, in that order, none done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L74): Then `and ++Run the unit tier++ still has no steps`: Then 'and ++Run the unit tier++ still has no steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L80): Then `then the queue answers ++Write the scenarios++ with ++Read the epic++ done, ++Write the stories++ being worked and ++Validate the scenarios++ pending`: Then 'then the queue answers ++Write the scenarios++ with ++Read the epic++ done, ++Write the stories++ being worked and ++Validate the scenarios++ pending' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L86): Then `then the queue answers ++Write the scenarios++ with only ++Read the epic++ done and ++Validate the scenarios++ pending`: Then 'then the queue answers ++Write the scenarios++ with only ++Read the epic++ done and ++Validate the scenarios++ pending' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L93): Then `then the agent is told no prompt z is on the queue`: Then 'then the agent is told no prompt z is on the queue' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L94): Then `and the queue still holds ++Write the scenarios++ with no steps`: Then 'and the queue still holds ++Write the scenarios++ with no steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L100): Then `then the queue answers ++Write the scenarios++ with only ++Read the epic++ done`: Then 'then the queue answers ++Write the scenarios++ with only ++Read the epic++ done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L106): Then `then the agent is told completed is not a step's state, which is one of pending, in_progress, done`: Then 'then the agent is told completed is not a step's state, which is one of pending, in_progress, done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L107): Then `and ++Write the scenarios++ still has only ++Read the epic++ done`: Then 'and ++Write the scenarios++ still has only ++Read the epic++ done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L115): Then `then the queue answers ++Write the scenarios++ with ++Read the epic++ done and the other two not done`: Then 'then the queue answers ++Write the scenarios++ with ++Read the epic++ done and the other two not done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L121): Then `then the queue answers ++Write the scenarios++ with every step done`: Then 'then the queue answers ++Write the scenarios++ with every step done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L122): Then `and ++Write the scenarios++ stays on the queue until the agent marks it done with prompt-queue.done, as in Work Through Prompt Queue`: Then 'and ++Write the scenarios++ stays on the queue until the agent marks it done with prompt-queue.done, as in Work Through Prompt Queue' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L128): Then `then the agent is told ++Write the scenarios++ has three steps`: Then 'then the agent is told ++Write the scenarios++ has three steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L129): Then `and ++Write the scenarios++ still has no step done`: Then 'and ++Write the scenarios++ still has no step done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L139): Then `then the queue answers ++Write the scenarios++ with those three steps, ++Read the epic++ being worked`: Then 'then the queue answers ++Write the scenarios++ with those three steps, ++Read the epic++ being worked' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L140): Then `and the queue box shows ++Write the scenarios++ with them, as in Show Prompt Steps In Queue`: Then 'and the queue box shows ++Write the scenarios++ with them, as in Show Prompt Steps In Queue' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L146): Then `then the queue answers ++Write the scenarios++ with ++Read the epic++ done and ++Write the stories++ being worked`: Then 'then the queue answers ++Write the scenarios++ with ++Read the epic++ done and ++Write the stories++ being worked' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L153): Then `then the queue beside ++Fix the Files app++ tells the agent to set the steps of ++Write the scenarios++ when it takes it and to mark each one done as it goes`: Then 'then the queue beside ++Fix the Files app++ tells the agent to set the steps of ++Write the scenarios++ when it takes it and to mark each one done as it goes' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L162): Then `then the queue holds "[interruption] Fix the Files app" first, then ++Write the scenarios++, then ++Run the unit tier++`: Then 'then the queue holds "[interruption] Fix the Files app" first, then ++Write the scenarios++, then ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L163): Then `and the agent is told the prompt is on the queue as its id, to mark it done when its work is done`: Then 'and the agent is told the prompt is on the queue as its id, to mark it done when its work is done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L164): Then `and "[interruption] Fix the Files app" is the working prompt its steps are copied onto, as in Copy Task List Onto Working Prompt`: Then 'and "[interruption] Fix the Files app" is the working prompt its steps are copied onto, as in Copy Task List Onto Working Prompt' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L171): Then `then the queue holds ++Write the scenarios++, "[interruption] Fix the Files app", then ++Run the unit tier++`: Then 'then the queue holds ++Write the scenarios++, "[interruption] Fix the Files app", then ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L177): Then `then the queue still holds only ++Write the scenarios++ and ++Run the unit tier++`: Then 'then the queue still holds only ++Write the scenarios++ and ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L183): Then `then the queue still holds only ++Write the scenarios++`: Then 'then the queue still holds only ++Write the scenarios++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L184): Then `and ++Write the scenarios++ is the working prompt`: Then 'and ++Write the scenarios++ is the working prompt' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L193): Then `then ++Write the scenarios++ has the step "[interruption] cut the text with an ellipsis", not started`: Then 'then ++Write the scenarios++ has the step "[interruption] cut the text with an ellipsis", not started' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L194): Then `and the queue still holds only ++Write the scenarios++ and ++Run the unit tier++`: Then 'and the queue still holds only ++Write the scenarios++ and ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L195): Then `and the agent is told the queue filed it under the goal last worked, [a], and to decide before any other work where it belongs, with each goal on the queue listed, such as [b] Run the unit tier`: Then 'and the agent is told the queue filed it under the goal last worked, [a], and to decide before any other work where it belongs, with each goal on the queue listed, such as [b] Run the unit tier' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L203): Then `then ++Write the scenarios++ is no longer done and has the step "[interruption] cut the text with an ellipsis", not started`: Then 'then ++Write the scenarios++ is no longer done and has the step "[interruption] cut the text with an ellipsis", not started' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L204): Then `and the queue still holds only ++Write the scenarios++ and ++Run the unit tier++`: Then 'and the queue still holds only ++Write the scenarios++ and ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L210): Then `then the steps of ++Write the scenarios++ still hold "[interruption] cut the text with an ellipsis"`: Then 'then the steps of ++Write the scenarios++ still hold "[interruption] cut the text with an ellipsis"' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L217): Then `then the agent reads each robot's queue beside it, such as "Bolt: [b] Run the unit tier"`: Then 'then the agent reads each robot's queue beside it, such as "Bolt: [b] Run the unit tier"' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L218): Then `and it is told it decides where the message goes: do it itself, make it a task of an item in a robot's queue, or give it to a robot as a new item starting "[for <robot name>]"`: Then 'and it is told it decides where the message goes: do it itself, make it a task of an item in a robot's queue, or give it to a robot as a new item starting "[for <robot name>]"' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L225): Then `then it is told no prompt z is on the queue`: Then 'then it is told no prompt z is on the queue' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L231): Then `then ++Write the scenarios++ still has no steps`: Then 'then ++Write the scenarios++ still has no steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L232): Then `and ++Write the scenarios++ is still done`: Then 'and ++Write the scenarios++ is still done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L240): Then `then ++Write the scenarios++' card shows 1/3`: Then 'then ++Write the scenarios++' card shows 1/3' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L241): Then `and ++Run the unit tier++'s card shows no progress`: Then 'and ++Run the unit tier++'s card shows no progress' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L247): Then `then ++Read the epic++, ++Write the stories++ and ++Validate the scenarios++ show under its card, in order`: Then 'then ++Read the epic++, ++Write the stories++ and ++Validate the scenarios++ show under its card, in order' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L248): Then `and ++Read the epic++ is ticked and ++Write the stories++ is marked as being worked`: Then 'and ++Read the epic++ is ticked and ++Write the stories++ is marked as being worked' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L254): Then `then only the card of ++Write the scenarios++ shows, with 1/3`: Then 'then only the card of ++Write the scenarios++ shows, with 1/3' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L263): Then `then ++Run the unit tier++ has the one step ++Render the map++, not started`: Then 'then ++Run the unit tier++ has the one step ++Render the map++, not started' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L264): Then `and the prompt box is empty`: Then 'and the prompt box is empty' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L265): Then `and the steps of ++Run the unit tier++ show under its card`: Then 'and the steps of ++Run the unit tier++ show under its card' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L271): Then `then ++Write the scenarios++ has the steps ++Read the epic++, then ++Validate them++`: Then 'then ++Write the scenarios++ has the steps ++Read the epic++, then ++Validate them++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L277): Then `then the steps are ++Read the epic++, ++Validate them++, ++Write the stories++`: Then 'then the steps are ++Read the epic++, ++Validate them++, ++Write the stories++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L279): Then `then the steps are ++Validate them++, ++Read the epic++, ++Write the stories++`: Then 'then the steps are ++Validate them++, ++Read the epic++, ++Write the stories++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L286): Then `then the prompt box holds Write them`: Then 'then the prompt box holds Write them' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L293): Then `then ++Write the scenarios++ has the steps ++Read the epic++, then ++Write them all++`: Then 'then ++Write the scenarios++ has the steps ++Read the epic++, then ++Write them all++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L294): Then `and the prompt box is empty`: Then 'and the prompt box is empty' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L302): Then `then the chat is sent "Take step 2 of prompt [a] on the queue now: Write them"`: Then 'then the chat is sent "Take step 2 of prompt [a] on the queue now: Write them"' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L303): Then `and ++Write the scenarios++ is the working prompt`: Then 'and ++Write the scenarios++ is the working prompt' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L312): Then `then ++Read the epic++ is being worked and ++Write them++ is not started`: Then 'then ++Read the epic++ is being worked and ++Write them++ is not started' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L318): Then `then ++Read the epic++ and ++Write them++ are done`: Then 'then ++Read the epic++ and ++Write them++ are done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L319): Then `and ++Validate them++ is being worked`: Then 'and ++Validate them++ is being worked' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L54): Then `then ++Write the scenarios++ is given to ++Sparky++ and ++Run the unit tier++ to ++Bolt++`: Then 'then ++Write the scenarios++ is given to ++Sparky++ and ++Run the unit tier++ to ++Bolt++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L55): Then `and the open queue shows ++Sparky++'s queue holding ++Write the scenarios++ beside ++Bolt++'s holding ++Run the unit tier++, each under its own robot drawing and name, sharing the width evenly`: Then 'and the open queue shows ++Sparky++'s queue holding ++Write the scenarios++ beside ++Bolt++'s holding ++Run the unit tier++, each under its own robot drawing and name, sharing the width evenly' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L56): Then `and every robot's queue is open, each with its own pointer`: Then 'and every robot's queue is open, each with its own pointer' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L62): Then `then the model is asked to group only ++Run the unit tier++`: Then 'then the model is asked to group only ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L69): Then `then ++Run the unit tier++ is given to ++Bolt++`: Then 'then ++Run the unit tier++ is given to ++Bolt++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L70): Then `and ++Write the scenarios++ stays with ++Sparky++`: Then 'and ++Write the scenarios++ stays with ++Sparky++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L77): Then `then ++Bolt++'s queue shows ++[for Bolt] Run the heavy tier++`: Then 'then ++Bolt++'s queue shows ++[for Bolt] Run the heavy tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L84): Then `then ++Sparky++'s queue shows ++[for Bolt] Run the heavy tier++`: Then 'then ++Sparky++'s queue shows ++[for Bolt] Run the heavy tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L85): Then `and ++Bolt++'s queue does not show ++[for Bolt] Run the heavy tier++`: Then 'and ++Bolt++'s queue does not show ++[for Bolt] Run the heavy tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L93): Then `then the queue answers ++Write the scenarios++ with the robot ++Bolt++ and ++Run the unit tier++ with none`: Then 'then the queue answers ++Write the scenarios++ with the robot ++Bolt++ and ++Run the unit tier++ with none' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L99): Then `then the queue answers ++Write the scenarios++ with no robot`: Then 'then the queue answers ++Write the scenarios++ with no robot' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L106): Then `then ++Sparky++'s queue shows ++Write the scenarios++`: Then 'then ++Sparky++'s queue shows ++Write the scenarios++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L107): Then `and ++Bolt++'s queue shows ++Run the unit tier++`: Then 'and ++Bolt++'s queue shows ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L115): Then `then two sub-agents start, each described by its robot, ++Sparky++ or ++Bolt++, and what that robot does`: Then 'then two sub-agents start, each described by its robot, ++Sparky++ or ++Bolt++, and what that robot does' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L116): Then `and the queue still holds ++Write the scenarios++ and ++Run the unit tier++, so each sub-agent marks its own card done`: Then 'and the queue still holds ++Write the scenarios++ and ++Run the unit tier++, so each sub-agent marks its own card done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L123): Then `then ++Sparky++'s queue still shows ++Write the scenarios++, dim`: Then 'then ++Sparky++'s queue still shows ++Write the scenarios++, dim' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L129): Then `then ++Write the scenarios++'s card in ++Sparky++'s queue has send now, edit, move up, move down and remove, shown on hover`: Then 'then ++Write the scenarios++'s card in ++Sparky++'s queue has send now, edit, move up, move down and remove, shown on hover' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L138): Then `then ++Run the unit tier++ is given to ++Captain Tests++`: Then 'then ++Run the unit tier++ is given to ++Captain Tests++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L139): Then `and ++Write the scenarios++ stays with ++Sparky++`: Then 'and ++Write the scenarios++ stays with ++Sparky++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L140): Then `and the prompt box is empty`: Then 'and the prompt box is empty' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L146): Then `then the first sub-agent starts described by ++Captain Tests++ and what that robot does`: Then 'then the first sub-agent starts described by ++Captain Tests++ and what that robot does' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L154): Then `then ++Sparky++ shows without ++Write the scenarios++'s card`: Then 'then ++Sparky++ shows without ++Write the scenarios++'s card' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L155): Then `and ++Bolt++'s queue takes the room`: Then 'and ++Bolt++'s queue takes the room' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L162): Then `then ++Sparky++ shows 1/2 under it`: Then 'then ++Sparky++ shows 1/2 under it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\queue-prompts-for-later\share-queue-among-robots\share_queue_among_robots_story.test.md#L168): Then `then ++Sparky++'s queue shows ++Write the scenarios++'s card again`: Then 'then ++Sparky++'s queue shows ++Write the scenarios++'s card again' has no observes relationship to Example, which the stories practice schema requires.

### `keep-classes-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:230](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L230)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L120): OoadClass `PromptQueue`: Class 'PromptQueue' exposes 17 public operations (budget ~9). Split responsibilities.

### `limit-operation-parameters`

Rule text: [clean_engineering/clean_engineering.md:242](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L242)

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L108): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L328): Operation `_saved_attachment`: Operation '_saved_attachment' takes 5 parameters (maximum 3, excluding self).

### `use-typed-signatures`

Rule text: [clean_engineering/clean_engineering.md:140](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L140)

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L83): Parameter `state`: Parameter 'state' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L307): Parameter `held`: Parameter 'held' needs a domain-specific type, not a generic container.
