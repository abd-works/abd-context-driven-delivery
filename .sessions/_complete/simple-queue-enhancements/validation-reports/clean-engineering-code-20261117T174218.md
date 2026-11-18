# Graph rule validation

**Generated:** 2026-11-17 17:43:35 UTC
**Project:** abd-cdd-simple-queue-enhancement
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\simple-queue-enhancements\.context\checked-graphs\stories-acceptance-tests-20261117T174218\graph.json`

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

**Total graph violations:** 17
**Rules with graph hits:** 5
**AI rules in scope:** 57

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `examples-declare-seed-vs-interaction`

Rule text: [stories/stories.md:232](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L232)

### `shared-example-fixtures`

Rule text: [stories/stories.md:233](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L233)

### `seed-state-at-its-real-owner`

Rule text: [stories/stories.md:234](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L234)

### `separate-test-controls-from-production-contracts`

Rule text: [stories/stories.md:235](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L235)

### `system-stubs-domain-real`

Rule text: [stories/stories.md:236](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L236)

### `assert-domain-behavior-not-seeded-state`

Rule text: [stories/stories.md:237](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L237)

### `infrastructure-in-lifecycle-hooks`

Rule text: [stories/stories.md:238](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L238)

### `inline-simple-gwt-bodies`

Rule text: [stories/stories.md:239](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L239)

### `domain-operations-inline-in-steps`

Rule text: [stories/stories.md:240](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L240)

### `code-steps-invoke-code`

Rule text: [stories/stories.md:241](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L241)

### `extract-assertion-helper`

Rule text: [stories/stories.md:242](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L242)

### `suffix-names-the-tier`

Rule text: [tdd/tdd.md:112](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L112)

### `unit-tier-fakes-every-boundary`

Rule text: [tdd/tdd.md:113](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L113)

### `heavy-tier-holds-a-real-resource`

Rule text: [tdd/tdd.md:114](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L114)

### `e2e-tier-drives-browser-or-agent`

Rule text: [tdd/tdd.md:115](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L115)

### `slow-example-moves-not-the-file`

Rule text: [tdd/tdd.md:116](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L116)

### `no-skipped-or-empty-test`

Rule text: [tdd/tdd.md:117](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L117)

### `unit-example-within-100-ms`

Rule text: [tdd/tdd.md:120](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L120)

### `unit-file-within-2-seconds`

Rule text: [tdd/tdd.md:121](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L121)

### `unit-tier-within-25-seconds`

Rule text: [tdd/tdd.md:122](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L122)

### `specs-run-in-parallel`

Rule text: [tdd/tdd.md:123](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L123)

### `heavy-spec-owns-its-resources`

Rule text: [tdd/tdd.md:124](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L124)

### `expensive-fixture-built-once`

Rule text: [tdd/tdd.md:125](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L125)

### `no-wait-in-unit-test`

Rule text: [tdd/tdd.md:126](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L126)

### `budget-never-raised`

Rule text: [tdd/tdd.md:127](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L127)

### `stubbed-boundary-has-heavy-coverage`

Rule text: [tdd/tdd.md:130](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L130)

### `heavy-example-has-a-stubbed-twin`

Rule text: [tdd/tdd.md:131](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L131)

### `heavy-run-within-the-hour`

Rule text: [tdd/tdd.md:134](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L134)

### `e2e-run-within-the-day`

Rule text: [tdd/tdd.md:135](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L135)

### `release-follows-a-green-e2e`

Rule text: [tdd/tdd.md:136](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L136)

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

- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-simple-queue-enhancement\tools\prompt_queue\prompt_queue.py#L131): Parameter `to`: Parameter 'to' does not reveal intent.

### `use-consistent-naming`

Rule text: [clean_engineering/clean_engineering.md:259](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L259)

### `provide-meaningful-context`

Rule text: [clean_engineering/clean_engineering.md:335](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L335)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-simple-queue-enhancement\tools\prompt_queue\prompt_queue.py#L118): Operation `add_all`: Operation 'add_all' uses the unnamed number 12.

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

Rule text: [tdd/tdd.md:144](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L144)

### `class-demonstrated-by-a-test`

Rule text: [tdd/tdd.md:145](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L145)

### `invariant-has-a-failing-case`

Rule text: [tdd/tdd.md:146](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L146)

### `every-branch-taken-by-a-test`

Rule text: [tdd/tdd.md:147](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L147)

### `conforms-to-schema`

Rule text: a graph rule, written in no practice document

**Graph violations:** 11

- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/set-steps-of-queued-prompt/set_steps_of_queued_prompt_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\set-steps-of-queued-prompt\set_steps_of_queued_prompt_story.test.py#L39): Then `then the queue answers WRITE_THE_SCENARIOS with those three steps, in that order, none done`: Then 'then the queue answers WRITE_THE_SCENARIOS with those three steps, in that order, none done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/set-steps-of-queued-prompt/set_steps_of_queued_prompt_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\set-steps-of-queued-prompt\set_steps_of_queued_prompt_story.test.py#L41): Then `and RUN_THE_UNIT_TIER still has no steps`: Then 'and RUN_THE_UNIT_TIER still has no steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/set-steps-of-queued-prompt/set_steps_of_queued_prompt_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\set-steps-of-queued-prompt\set_steps_of_queued_prompt_story.test.py#L49): Then `then the queue answers WRITE_THE_SCENARIOS with READ_THE_EPIC done, WRITE_THE_STORIES in progress and VALIDATE_THE_SCENARIOS pending`: Then 'then the queue answers WRITE_THE_SCENARIOS with READ_THE_EPIC done, WRITE_THE_STORIES in progress and VALIDATE_THE_SCENARIOS pending' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/set-steps-of-queued-prompt/set_steps_of_queued_prompt_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\set-steps-of-queued-prompt\set_steps_of_queued_prompt_story.test.py#L58): Then `then the queue answers WRITE_THE_SCENARIOS with only READ_THE_EPIC done and VALIDATE_THE_SCENARIOS pending`: Then 'then the queue answers WRITE_THE_SCENARIOS with only READ_THE_EPIC done and VALIDATE_THE_SCENARIOS pending' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/set-steps-of-queued-prompt/set_steps_of_queued_prompt_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\set-steps-of-queued-prompt\set_steps_of_queued_prompt_story.test.py#L67): Then `then the agent is told no prompt MISSING_PROMPT is on the queue`: Then 'then the agent is told no prompt MISSING_PROMPT is on the queue' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/set-steps-of-queued-prompt/set_steps_of_queued_prompt_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\set-steps-of-queued-prompt\set_steps_of_queued_prompt_story.test.py#L69): Then `and the queue still holds WRITE_THE_SCENARIOS with no steps`: Then 'and the queue still holds WRITE_THE_SCENARIOS with no steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/tick-off-prompt-step/tick_off_prompt_step_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\tick-off-prompt-step\tick_off_prompt_step_story.test.py#L34): Then `then the queue answers WRITE_THE_SCENARIOS with READ_THE_EPIC done and the other two not done`: Then 'then the queue answers WRITE_THE_SCENARIOS with READ_THE_EPIC done and the other two not done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/tick-off-prompt-step/tick_off_prompt_step_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\tick-off-prompt-step\tick_off_prompt_step_story.test.py#L44): Then `then the queue answers WRITE_THE_SCENARIOS with every step done`: Then 'then the queue answers WRITE_THE_SCENARIOS with every step done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/tick-off-prompt-step/tick_off_prompt_step_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\tick-off-prompt-step\tick_off_prompt_step_story.test.py#L46): Then `and WRITE_THE_SCENARIOS stays on the queue until the agent marks it done`: Then 'and WRITE_THE_SCENARIOS stays on the queue until the agent marks it done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/tick-off-prompt-step/tick_off_prompt_step_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\tick-off-prompt-step\tick_off_prompt_step_story.test.py#L54): Then `then the agent is told WRITE_THE_SCENARIOS has three steps`: Then 'then the agent is told WRITE_THE_SCENARIOS has three steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/tick-off-prompt-step/tick_off_prompt_step_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\tick-off-prompt-step\tick_off_prompt_step_story.test.py#L56): Then `and WRITE_THE_SCENARIOS still has no step done`: Then 'and WRITE_THE_SCENARIOS still has no step done' has no observes relationship to Example, which the stories practice schema requires.

### `four-to-nine-children`

Rule text: [stories/stories.md:82](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L82)

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/set-steps-of-queued-prompt/set_steps_of_queued_prompt_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\set-steps-of-queued-prompt\set_steps_of_queued_prompt_story.test.py#L21): Epic `Queue Prompts For Later`: epic 'Queue Prompts For Later': 1 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/set-steps-of-queued-prompt/set_steps_of_queued_prompt_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\set-steps-of-queued-prompt\set_steps_of_queued_prompt_story.test.py#L21): SubEpic `Queue Prompts For Later`: sub-epic 'Queue Prompts For Later': 2 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/set-steps-of-queued-prompt/set_steps_of_queued_prompt_story.test.py](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\set-steps-of-queued-prompt\set_steps_of_queued_prompt_story.test.py#L22): SubEpic `Nest Prompt Steps In Queue`: sub-epic 'Nest Prompt Steps In Queue': 1 children (target 4-9)

### `keep-classes-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:230](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L230)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-simple-queue-enhancement\tools\prompt_queue\prompt_queue.py#L71): OoadClass `PromptQueue`: Class 'PromptQueue' exposes 13 public operations (budget ~9). Split responsibilities.

## Judgment — `tools/prompt_queue/prompt_queue.py`

### `keep-classes-single-responsibility` — Fail
- prompt_queue.py:71 `PromptQueue` has 13 public operations against a budget of about 9. It had 11 before this change (show, add, add_all, edit, move, remove, clear, done, queue_handoff, load, of_chat); set_steps and step_done add two. The steps belong to a queued prompt, which is a TypedDict here; giving QueuedPrompt a class of its own that holds its steps would take both operations off the queue. Not done in this pass.

### `use-intention-revealing-names` — Fail
- prompt_queue.py:131 `move(prompt, to)`: `to` predates this change and is the name the queue mod sends; renaming it means changing the mod's call in the same change. Left as it was.

Fixed in this pass, after the run: `provide-meaningful-context` at prompt_queue.py:118, the id length 12 is now `_PROMPT_ID_LENGTH`.

Passes for the new code (set_steps, step_done, PromptStep, StepNotPlanned): hide-inner-details, hold-state-on-the-object-not-in-parameters, keep-operations-small-focused, prefer-instance-operations, simplify-control-flow (the step out of range is refused first), use-exceptions-properly (StepNotPlanned names the prompt, the step and how many steps it has), errors-out-of-existence (a prompt with no steps answers an empty list), operation-has-a-proving-test and every-branch-taken-by-a-test (both story tests call each operation and take the refusal), vocabulary-traces-to-source (step, steps, done as on the map).
